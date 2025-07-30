from setuptools import setup, find_packages

setup(
    name='mygeniuspackage',
    version='0.2',
    packages=find_packages(),
    description='A demo Python package that prints stored data',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='you@example.com',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    keywords='custom text demo',
    python_requires='>=3.6',
)
