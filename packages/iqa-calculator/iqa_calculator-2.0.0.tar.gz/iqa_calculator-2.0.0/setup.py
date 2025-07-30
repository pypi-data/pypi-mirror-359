from setuptools import setup, find_packages

setup(
    name='iqa_calculator',
    version='2.0.0',
    description='Pacote para calcular o Índice de Qualidade da Água (IQA)',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Djunio Filho',
    author_email='djuniormfilho@gmail.com',
    url='https://github.com/seitbnao/iqa_calculator', 
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[],
)
