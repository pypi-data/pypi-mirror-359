from setuptools import setup, find_packages

setup(
    name='utilfab',
    version='1.3.0',
    author='Bautista Fabris, V4FAB',
    description='Utilidades generales para procesamiento de texto, decisiones y formato',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
