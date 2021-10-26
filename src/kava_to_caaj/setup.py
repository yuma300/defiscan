"""kava_to_caaj"""

from setuptools import setup, find_packages
from glob import glob
from os.path import splitext
from os.path import basename
import sys

def _requires_from_file(filename):
    return open(filename).read().splitlines()

sys.path.append("test/kava_to_caaj")

setup(
    name='kava_to_caaj',
    version='0.1.0',
    license='mit',
    description='converting kava transaction to caaj',

    author='bitblt',
    author_email='ywakimoto1s@gmail.com',
    url='https://github.com/yuma300/defiscan/tree/master/src/kava_to_caaj',

    #install_requires=_requires_from_file('requirements.txt'),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    test_suite = 'test'
)