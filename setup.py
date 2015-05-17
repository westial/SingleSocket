from distutils.core import setup

version_file = open('VERSION', 'r')
version = version_file.readline()

setup(
    name='SingleSocket',
    version=version,
    packages=['SingleSocket'],
    url='https://github.com/westial/SingleSocket',
    license='GPL v3',
    author='Jaume Mila',
    author_email='jaume@westial.com',
    description='Python module for unidirectional socket communication, from '
                'server to client, for only one concurrent client.'
)
