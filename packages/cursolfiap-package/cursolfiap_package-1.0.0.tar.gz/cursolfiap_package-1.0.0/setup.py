from setuptools import setup, find_packages
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setup(
    name='cursolfiap-package',
    version='1.0.0',
    packages=find_packages(),
    description='Minha Primeira Lib Curso FIAP',
    author='Bruno Amorim',
    author_email='rm365279@fiap.com.br',
    url='https://github.com/bwasistemas/fiap',  
    license='MIT',  
    long_description=long_description,
    long_description_content_type='text/markdown'
)
