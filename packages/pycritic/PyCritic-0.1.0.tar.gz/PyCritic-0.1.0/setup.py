from setuptools import setup, find_packages

setup(
    name='PyCritic',
    version='0.1.0',
    author='Alexander Smirnov',
    author_email='aleqsonder@icloud.com',
    description='A package for estimating a set of parameters',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Alexcoratt/pycritic',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.11',
)
