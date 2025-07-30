from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")


setup(
    name='RFIViz',
    version='0.2.1',
    author='Timothy H Bell',
    author_email='timothy.bell@etu.unice.fr',
    description='A visualisation tool for Random Forests',
    packages=find_packages(),
    install_requires=[
    'aiohttp',
    'qasync',
    'pandas',
    'numpy',
    'sklearn',
    'PyQt5'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)