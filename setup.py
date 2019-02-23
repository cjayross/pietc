from distutils.core import setup

setup(
        name='pietc',
        description='Compile C into Piet bitmaps',
        long_description=open('README.md').read(),
        url='https://github.com/cjayross/hackutd2019',
        version='0.1-dev',
        packages=['pietc',],
        install_requires=['PLY'],
        )
