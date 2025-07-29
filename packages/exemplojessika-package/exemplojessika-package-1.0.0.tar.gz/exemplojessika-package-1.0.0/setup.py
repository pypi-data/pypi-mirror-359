from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='exemplojessika-package',
    version='1.0.0',
    packages=find_packages(),
    description='Descricao da sua lib jessikaexemplo',
    author='Jessika Morais',
    author_email='jessikamorias.backup@gmail.com',
    url='',  
    license='MIT',  
    long_description=long_description,
    long_description_content_type='text/markdown'
)
