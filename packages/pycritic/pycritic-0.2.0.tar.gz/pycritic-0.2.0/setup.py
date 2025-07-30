from setuptools import setup, find_packages

setup(
    name='pycritic',
    version='0.2.0',
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
