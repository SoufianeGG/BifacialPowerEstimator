from setuptools import setup, find_packages
import pathlib
import os
import sys 


# # Get the long description from the README file
# long_description = (here / "README.md").read_text(encoding="utf-8")

# read the requirements file --> install the dependencies 
def read_requirements(): 
    with open('requirements.txt') as f:
        return f.read().splitlines()


if __name__ == '__main__':
    setup( name =  'BifacialPowerEstimator', 
          version  = '0.2.0',
          description= 'Estimate the power production of bifacial modules',
          packages  = find_packages(where='src'), 
          package_dir={'': 'src'}, 
          install_requires = read_requirements() ,
          author_email  =  'soufiane.ghafiri@usherbrooke.ca',
          author  = 'Soufiane Ghafiri'
          )