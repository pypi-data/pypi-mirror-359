from setuptools import setup, find_packages

setup(
    name='python_string_fuzzy_clustering',
    version='0.0.2',
    description='A simple library for String Grammar Fuzzy C-Medians',
    long_description=open('USAGE.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Atcharin Klomsae',
    author_email='atcharin.k@gmail.com',
    packages=find_packages(),
    install_requires=[
        "pytest"
    ],
    license='GPLv3',
    python_requires='>=3.7',
)