import os

from setuptools import setup, find_packages


setup(
    name='django_orm_views',
    version='2.0.3',
    description='Package to define manage Postgres views on a Django server',
    author='iwoca',
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    python_requires='>=3.6',
    install_requires=[
        'django>=2.1,<5.0',
        'dataclasses>=0.7; python_version < "3.7.0"',
    ],
    extras_require={
        'test': [
            'psycopg2-binary==2.8.6'
        ]
    },
    zip_safe=False,  # We need this for the management commands to work
)

