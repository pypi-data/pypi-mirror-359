from setuptools import setup, find_packages
import os

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='AsroNLP',
    version='0.1.20',
    author='Asro',
    author_email='982024204@student.uksw.edu',
    description='Paket NLP untuk pengolahan teks Bahasa Indonesia',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/asroharun6/asronlp',
    packages=find_packages(include=['asro_nlp', 'asro_nlp.*']),
    package_data={'asro_nlp': ['data/*']},
    include_package_data=True,
    install_requires=[
        'pandas>=1.0.0',
        'nltk>=3.5',
        'openpyxl>=3.0.0',
        'rich>=10.0.0',
        'regex>=2020.11.13',
        'swifter>=1.0.0',
        'Sastrawi>=1.0.1',
        'matplotlib>=3.1.0',
        'wordcloud>=1.8.0',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: Indonesian',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
