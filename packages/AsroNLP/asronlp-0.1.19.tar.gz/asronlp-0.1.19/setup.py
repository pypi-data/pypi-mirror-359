from setuptools import setup, find_packages
import os

# Baca README.md dengan encoding utf-8
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='AsroNLP',
    version='0.1.19',
    author='Asro',
    author_email='982024204@student.uksw.edu',
    description='Paket NLP untuk pengolahan teks Bahasa Indonesia',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/asroharun6/asronlp',
    packages=find_packages(),
    package_data={'asro_nlp': ['data/*']},
    include_package_data=True,
    install_requires=[
        'pandas',
        'nltk',
        'openpyxl',
        'rich',
        'regex',
        'swifter',
        'Sastrawi',
        'matplotlib',
        'wordcloud',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: Indonesian',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
