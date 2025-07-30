from setuptools import setup, find_packages

setup(
    name='simplemath_ashay',           # must be unique on PyPI
    version='0.1.0',
    packages=find_packages(),
    install_requires=[],
    author='Ashay K A',
    author_email='ashayka68@email.com',
    description='A small Python library to add two numbers',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.6',
)
