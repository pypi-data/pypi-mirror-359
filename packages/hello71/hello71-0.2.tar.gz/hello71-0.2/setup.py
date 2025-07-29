from setuptools import setup, find_packages

setup(
    name='hello71',
    version='0.2',
    packages=find_packages(),
    install_requires=[
        # add dependencies here
        # will install on its own
    ],
    entry_points={
        'console_scripts': [
            'hello71 = hello71.main:hello'
        ]
    }
)