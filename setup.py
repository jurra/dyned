from setuptools import setup

setup(name='dined',
      version='0.1',
      description='Dined - Anthropometry in Design',
      url='http://github.com/dined-io/dyned',
      author='Delft University of Technology',
      author_email='dined-io@tudelft.nl',
      license='BSD',
      packages=['dined'],
      packages=find_packages(),
      install_requires=[
            "numpy",
            "pandas",
            "scipy",
            "seaborn",
            "openpyxl"
      ],
      extras_require={
        'dev': [
            'pytest',
            'pytest-pep8',
            'pytest-cov',
            "jupyter,
            "notebook,
        ]
      },
      zip_safe=False)
      
)

