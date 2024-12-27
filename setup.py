import sys
from importlib.machinery import SourceFileLoader

from setuptools import find_packages, setup

version = SourceFileLoader('version', 'agave/version.py').load_module()

SKIP_VALIDATION_COMMANDS = {"sdist", "bdist_wheel", "egg_info"}

if not SKIP_VALIDATION_COMMANDS.intersection(sys.argv):
    if not any(arg.startswith('agave[') for arg in sys.argv):
        sys.stderr.write(
            "Error: You must install agave with either"
            " [chalice_support] or [fast_support].\nExample:\n"
            "  pip install 'agave[chalice_support]'\n"
            "  pip install 'agave[fast_support]'\n"
        )
        sys.exit(1)

with open('README.md', 'r') as f:
    long_description = f.read()


setup(
    name='agave',
    version=version.__version__,
    author='Cuenca',
    author_email='dev@cuenca.com',
    description='Rest_api',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/cuenca-mx/agave',
    packages=find_packages(),
    include_package_data=True,
    package_data=dict(agave=['py.typed']),
    python_requires='>=3.8',
    install_requires=[
        'cuenca-validations===2.0.0.dev7',
    ],
    extras_require={
        'chalice_support': [
            'chalice>=1.16.0,<1.25.1',
            'blinker>=1.4,<1.5',
            'mongoengine>=0.20.0,<0.23.0',
            'dnspython>=2.0.0,<2.2.0',
        ],
        'fast_support': [
            'aiobotocore>=2.0.0,<2.2.0',
            'types-aiobotocore-sqs>=2.1.0.post1,<3.0.0',
            'fastapi>=0.115.0,<0.120.0',
            'mongoengine-plus>=0.0.2,<1.0.0',
            'starlette-context>=0.3.2,<0.4.0',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
