from setuptools import setup, find_packages

setup(
    name='pypi_url_validator',
    version='0.1.0',
    packages=find_packages(),
    description='A simple library to validate URLs.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Manus',
    author_email='manus@example.com',
    url='https://github.com/manus/pypi_url_validator',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)

