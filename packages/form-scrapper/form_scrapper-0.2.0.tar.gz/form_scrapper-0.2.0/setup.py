from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    description = f.read()

setup(
    name='form_scrapper',
    version='0.2.0',
    author='Yannick Rafael',
    packages=find_packages(),
    install_requires=[
        'requests',
        'beautifulsoup4',
        'regex',
    ],
    description='A package to scrape Google Forms and extract questions.',
    long_description=description,
    long_description_content_type='text/markdown',
)