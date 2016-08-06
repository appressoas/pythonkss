from pkg_resources import resource_string
import json
import sys
from pythonkss.parser import Parser  # NOQA

if sys.version_info.major == 2:  # pragma: no cover
    __version__ = json.loads(resource_string(__name__, 'version.json'))
else:  # pragma: no cover
    __version__ = json.loads(resource_string(__name__, 'version.json').decode('utf-8'))
