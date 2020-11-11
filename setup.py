from importlib.machinery import SourceFileLoader

from setuptools import find_packages, setup

version = SourceFileLoader('version', 'agave/version.py').load_module()


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
    package_data=dict(cuenca_validations=['py.typed']),
    python_requires='>=3.8',
    install_requires=[
        'chalice>=1.16.0,<1.21.3',
        'cuenca-validations>=0.4,<0.7',
        'blinker>=1.4,<1.5',
        'boto3>=1.14.42,<1.15.0',
        'mongoengine>=0.20.0,<0.21.0',
        'dnspython>=2.0.0,<2.1.0',
        'dataclasses>=0.6;python_version<"3.7"',
    ],
    classifiers=[
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
