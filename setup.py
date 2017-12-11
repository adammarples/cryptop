# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.rst', encoding="utf-8") as f:
    readme = f.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='cryptop',
    version='0.2.1',
    description='Command line Cryptocurrency Portfolio',
    long_description=readme,
    author='huwwp',
    author_email='adammarples@gmail.com',
    url='https://github.com/adammarples/cryptop',
    license='MIT',
    keywords='crypto cli portfolio curses cryptocurrency bitcoin',
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    packages=find_packages(),
    install_requires=requirements,
    package_data={'cryptop': ['config.ini']},
    entry_points = {
        'console_scripts': ['cryptop = cryptop.cryptop:main'],
    }
)
