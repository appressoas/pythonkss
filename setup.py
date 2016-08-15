import json
import os

from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'pythonkss', 'version.json')) as f:
    version = json.loads(f.read())


setup(
    name='pythonkss',
    version=version,
    description='Python implementation of KSS',
    long_description='See https://github.com/appressoas/pythonkss',
    author='Espen Angell Kristiansen',
    author_email='espen@appresso.no',
    url='https://github.com/appressoas/pythonkss',
    license='BSD',
    packages=find_packages(exclude=['tests', 'examples']),
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    zip_safe=False,
    test_suite='runtests.runtests',
    install_requires=[
        'Markdown',
        'Pygments',
        'beautifulsoup4',
        'html5lib',
        'pyyaml'
    ],
    extras_require={
        'tests': [
            'flake8',
            'mock',
            'pytest',
        ],
    },
)
