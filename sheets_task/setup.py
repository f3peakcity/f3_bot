import glob
from posixpath import basename, splitext
from setuptools import setup, find_packages

setup(
    name="sheets_task",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    # py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
)