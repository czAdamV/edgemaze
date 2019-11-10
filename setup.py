from setuptools import setup, find_packages


with open('readme.md') as f:
    long_description = ''.join(f.readlines())


setup(
    name='edgemaze',
    version='0.1',
    description='A simple maze solving library.',
    long_description=long_description,
    author='Adam Volek',
    author_email='volekada@fit.cvut.cz',
    license='Public Domain',
    keywords='maze,path-finding',
    url='https://github.com/czAdamV/edgemaze',
    packages=find_packages(),
    install_requires=['numpy'],
    zip_safe=False,
)