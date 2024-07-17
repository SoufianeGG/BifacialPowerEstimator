from setuptools import setup, find_packages
import pathlib

# here = pathlib.Path(__file__).parent.resolve()

# # Get the long description from the README file
# long_description = (here / "README.md").read_text(encoding="utf-8")

if __name__ == '__main__':
    setup( name =  'BifacialPowerEstimator', 
          version  = '0.2.0',
          description= 'Estimate the power production of bifacial modules',
          packages  = find_packages('src'), 
          package_dir={'': 'src'}, 
          author_email  =  'soufiane.ghafiri@usherbrooke.ca',
          author  = 'Soufiane Ghafir'
          )