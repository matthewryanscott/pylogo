from setuptools import setup, find_packages
import sys, os

version = '2.0a'

setup(name='PyLogo',
      version=version,
      description="Logo implemented in Python",
      long_description="""\
""",
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='logo education',
      author='Ian Bicking',
      author_email='ianb@colorstudy.com',
      url='',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'pyparsing',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
      
