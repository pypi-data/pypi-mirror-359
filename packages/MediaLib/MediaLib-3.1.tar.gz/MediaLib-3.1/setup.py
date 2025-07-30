from setuptools import setup, find_packages


setup(
    name='MediaLib',
    version='3.1',
    license='MIT',
    author="Jingyun Wang",
    author_email='jingyun.wang@durham.ac.uk',
    long_description="The first cut-down Python library that simplifies multimedia programming.",
    description="The first cut-down Python library that simplifies multimedia programming",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='http://medialib.club',
    keywords='Multimedia',
    install_requires=[
          'pygame',
      ],

)
