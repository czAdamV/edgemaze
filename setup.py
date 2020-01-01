from setuptools import setup, find_packages
from Cython.Build import cythonize
import numpy


with open('readme.md') as f:
    long_description = ''.join(f.readlines())


setup(
    name='edgemaze',
    version='0.2',
    description='A simple maze solving library.',
    long_description=long_description,
    author='Adam Volek',
    author_email='volekada@fit.cvut.cz',
    license='GNU GPL v3',
    keywords='maze,path-finding',
    url='https://github.com/czAdamV/edgemaze',
    ext_modules=cythonize([
        'edgemaze/edgemaze.pyx',
        'edgemaze/__init__.pyx'
    ], language_level=3, language='c++'),
    include_dirs=[numpy.get_include()],
    packages=find_packages(),
    setup_requires=['Cython', 'NumPy'],
    install_requires=['numpy'],
    zip_safe=False,
)