from setuptools import setup, find_packages

setup(
    name='onescript-kernel',
    version='1.0',
    packages=find_packages(),
    author='Nikolay Krasnov',
    author_email='nikolay@krasnov.cf',
    description='OneScript kernel for Jupyter',
    long_description='A kernel that allows running OneScript code in Jupyter notebooks',
    url='',
    package_data={
        'onescript_kernel': ['kernel.json'],
    },
    include_package_data=True,
)