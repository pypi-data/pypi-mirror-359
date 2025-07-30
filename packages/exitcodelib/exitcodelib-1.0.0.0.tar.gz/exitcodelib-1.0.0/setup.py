from setuptools import setup
from os import path

# Get the absolute path to this file's directory
this_directory = path.abspath(path.dirname(__file__))

# Build the path to README.md and read it
readme_path = path.join(this_directory, "readme.md")
with open(readme_path, encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='exitcodelib',
    version='1.0.0',
    description='Standardized exit code system with messages for Python programs',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='johny eldry',
    author_email='umyashinderu@gmail.com',
    py_modules=['exitcodelib'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
