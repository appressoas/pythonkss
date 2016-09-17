class SectionTreeNode(object):
    """
    A node in the :class:`.SectionTree`.

    .. attribute:: reference

        The reference of the section.
        This is set even if we have no section.

    .. attribute:: segment_text

        The text after the last ``.`` in the reference.

    .. attribute:: section

        A :class:`pythonkss.section.Section` if any is available at this
        location in the tree. If not, this is ``None``.

    .. attribute:: root

        The root of the tree. A :class:`.SectionTree` object.

    .. attribute:: level

        The level in the tree starting at 0 for the topmost nodes in the tree.
        The root (:class:`.SectionTree` object)  is level ``-1``.

    .. attribute:: children

        A dict mapping :attr:`~.SectionTreeNode.segment_text` to
        :class:`.SectionTreeNode` objects.
    """
    def __init__(self, segment_text=None, reference=None, level=-1, root=None):
        self.children = {}
        self.segment_text = segment_text
        self.reference = reference
        self.section = None
        self.level = level
        self.root = root
        self.numbered_path_list = None
        if self.root:
            self.root.register_node_in_root(node=self)

    def __getitem__(self, segment_text):
        return self.children[segment_text]

    def add_section(self, remaining_segments, parent_segments, section, root):
        segment_text = remaining_segments[0]
        current_segments = parent_segments + [segment_text]
        if segment_text not in self.children:
            self.children[segment_text] = SectionTreeNode(
                segment_text=segment_text,
                reference='.'.join(current_segments),
                level=self.level + 1,
                root=root)

        if len(remaining_segments) == 1:
            self.children[segment_text].section = section
        else:
            self.children[segment_text].add_section(
                remaining_segments=remaining_segments[1:],
                section=section,
                parent_segments=current_segments,
                root=root)

    def _sort(self, numbered_path_list=None):
        """
        Sort the tree.

        This is called automatically by :meth:`.sorted_children`
        the first time it is called, so you should not need
        to call this directly.
        """
        self._sorted_children = sorted(self.children.values(), key=lambda node: node.sortkey)
        self.numbered_path_list = numbered_path_list or []
        for number, child in enumerate(self._sorted_children, 1):
            child._sort(
                numbered_path_list = self.numbered_path_list + [number]
            )

    @property
    def dotted_numbered_path(self):
        """
        Get the dotted numbered path for this node in sorted order.

        I.E.: If the node is sorted at the third child of the second sorted
        toplevel node, this will be ``"2.3"``.
        """
        return '.'.join(map(str, self.numbered_path_list))

    @property
    def title(self):
        """
        Get the section title, falling back to :attr:`.segment_text` capitalized.
        """
        if self.section:
            return self.section.title
        else:
            return self.segment_text.capitalize()

    @property
    def sortkey(self):
        """
        Get the sort key for the node within its parent.

        If this node has no :attr:`.section`, or if the
        sortkey of the section is ``None``, we return
        the :attr:`.segment_text` prefixed with ``"9999"``.
        If the section has a sortkey, we will return that prefixed with zeroes.

        Will always return a sortable string, so this is well suited
        for usage in the key function for ``sorted()``.
        """
        if self.section:
            sortkey = self.section.sortkey
        else:
            sortkey = None
        if sortkey is None:
            return '9999{}'.format(self.segment_text)
        else:
            return str(sortkey).zfill(4)

    @property
    def sorted_children(self):
        """
        Get children sorted by :meth:`.sortkey`.
        """
        if not hasattr(self, '_sorted_children'):
            self._sort()
        return self._sorted_children

    def collect_descendants_sorted(self, result):
        """
        Add all descendants in the provided result list
        in sorted order.

        This runs recursively, and adds each direct child and all its descendants
        before adding the next child (and all its descendants).

        Args:
            result: A list.
        """
        for child in self.sorted_children:
            result.append(child)
            child.collect_descendants_sorted(result=result)

    def sorted_all_descendants_flat(self):
        """
        Get a flat list of all descendants in sorted order.

        Uses :meth:`.collect_descendants_sorted` to build the list.
        """
        result = []
        self.collect_descendants_sorted(result=result)
        return result

    def prettyformat(self, indent_level=False):
        """
        Pretty-format the node.

        Args:
            indent_level: If this is True, the string includes :attr:`.level` * 4 spaces of indentation.

        Returns:
            str: Pretty formatted information about the node on a single line.
        """
        if self.section:
            meta = 'sortkey={}, title={}'.format(self.section.sortkey, self.section.title)
        else:
            meta = '<Not a section>'
        if indent_level:
            indent = '   ' * self.level
        else:
            indent = ''
        return '{indent}{dotted_numbered_path} {segment_text} - level:{level} reference:{reference} ({meta})'.format(
            indent=indent,
            dotted_numbered_path=self.dotted_numbered_path,
            segment_text=self.segment_text,
            level=self.level,
            reference=self.reference,
            meta=meta)

    def __str__(self):
        return 'TreeNode({})'.format(self.prettyformat())

    def prettyprint_tree(self):
        """
        Prettyprint all the descendants of this node.
        """
        if self.segment_text:
            print(self.prettyformat(indent_level=True))
        for child in self.sorted_children:
            child.prettyprint_tree()


class SectionTree(SectionTreeNode):
    """
    Builds a tree of sections.

    Includes virtual sections - I.E.: if we have the ``lists.numbered`` reference,
    but we do not have the ``lists`` reference, the ``lists`` reference will still
    be a node in the tree. It will just have :attr:`.Node.section` set to ``None``.

    .. note:: This extends :class:`.SectionTreeNode`. This means that
        the tree is just the root node with a different constructor
        and some extra functionality.
    """
    def __init__(self, sections):
        """
        Args:
            sections: An iterable of :class:`pythonkss.section.Section`.
                Must be sorted by :class:`pythonkss.section.Section.reference`.
        """
        super(SectionTree, self).__init__()
        self.sections = sections
        self._all_nodes_map = {}
        self._build_tree()

    def _build_tree(self):
        for section in self.sections:
            self.add_section(remaining_segments=section.reference_segment_list,
                             parent_segments=[],
                             section=section,
                             root=self)
        self._sort()

    def register_node_in_root(self, node):
        self._all_nodes_map[node.reference] = node

    def get_node_by_reference(self, reference):
        """
        Get a :class:`.TreeNode` by its reference.

        The node can be anywhere in the tree.

        Args:
            reference: The Section reference.
        """
        return self._all_nodes_map[reference]
