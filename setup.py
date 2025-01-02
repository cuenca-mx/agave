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
        'cuenca-validations==2.0.0.dev9',
    ],
    extras_require={
        'chalice': [
            'chalice==1.31.3',
            'blinker==1.4',
            'mongoengine==0.27.0',
            'dnspython==2.1.0',
        ],
        'fastapi': [
            'aiobotocore==2.16.1',
            'types-aiobotocore-sqs==2.5.0',
            'fastapi==0.115.6',
            'mongoengine-plus==0.2.3.dev1',
            'starlette-context==0.3.3',
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
