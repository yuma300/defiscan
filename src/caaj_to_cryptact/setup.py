"""caaj_to_cryptact"""

from setuptools import setup, find_packages
from glob import glob
from os.path import splitext
from os.path import basename
import sys

def _requires_from_file(filename):
    return open(filename).read().splitlines()

sys.path.append("test/caaj_to_cryptact")

setup(
    name='caaj_to_cryptact',
    version='0.1.0',
    license='mit',
    description='converting caaj to cryptact',

    author='bitblt',
    author_email='ywakimoto1s@gmail.com',
    url='https://github.com/yuma300/defiscan/tree/master/src/caaj_to_cryptact',

    #install_requires=_requires_from_file('requirements.txt'),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    test_suite = 'test'
)