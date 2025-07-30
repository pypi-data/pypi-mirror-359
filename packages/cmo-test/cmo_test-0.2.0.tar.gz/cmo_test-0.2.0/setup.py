from setuptools import setup, find_packages

setup(
    name='cmo_test',
    version='0.2.0',
    packages=find_packages(),
    install_requires=[],

    entry_points={
        'console_scripts': [
            'cmo_test = cmo_test.main:hello',
        ],
    },
)