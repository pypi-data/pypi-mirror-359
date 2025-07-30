from setuptools import setup, find_packages

setup(
    name='form_scrapper',
    version='0.1.0',
    author='Yannick Rafael',
    packages=find_packages(),
    install_requires=[
        'requests',
        'beautifulsoup4',
        'regex',
    ],
    description='A package to scrape Google Forms and extract questions.',
    long_description=open('README.md').read()
)