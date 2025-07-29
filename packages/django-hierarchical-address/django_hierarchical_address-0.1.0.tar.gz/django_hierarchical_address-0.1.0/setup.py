from setuptools import setup, find_packages

setup(
    name='django-hierarchical-address',
    version='0.1.0',
    description='A reusable Django app for hierarchical address fields.',
    author='Your Name',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'django>=3.2',
        'djangorestframework',
    ],
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)
