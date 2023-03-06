from setuptools import setup

setup(
    name='canvasGlossary',
    version='0.0.1',
    url='   ',
    license='MIT License',
    author='CISG Lee',
    author_email='clee@rsm.nl',
    description='Add tool tips with descriptions to terms on Canvas, getting the terms and descriptions from a glossary page on Canvas.',
    packages=['canvasGlossary'],
    requires=['beautifulsoup4', 'canvasapi', 'confuse', 'htmlmin']
)
