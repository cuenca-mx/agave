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
    package_data=dict(agave=['py.typed']),
    python_requires='>=3.9',
    install_requires=[
        'cuenca-validations>=2.0.0,<3.0.0',
    ],
    extras_require={
        'chalice': [
            'chalice>=1.30.0,<1.35.0',
            'mongoengine>=0.29.0,<0.30.0',
        ],
        'fastapi': [
            'fastapi>=0.115.0,<0.120.0',
            'mongoengine-plus>=0.2.3,<1.0.0',
            'python-multipart>=0.0.20,<0.0.30',
            'starlette-context>=0.3.2,<0.4.0',
        ],
        'tasks': [
            'aiobotocore>=2.0.0,<3.0.0',
            'types-aiobotocore-sqs>=2.1.0,<3.0.0',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
