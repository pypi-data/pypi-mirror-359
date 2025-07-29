from setuptools import setup, find_packages

setup(
    name='globalwaterbodycalculator',
    version='0.1.2',
    description='A package for calculating water storage based on global water body depth-area-volume equation and visualizing waterbody geometries.',
    author='Shengde Yu',
    author_email='s228yu@uwaterloo.ca',
    url='https://github.com/SYubaby/Globalwaterbodycalculator',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'globalwaterbodycalculator': ['data/all_equations.csv', 'data/HydroLAKES_polys_v10_shp/*'],
    },
    install_requires=[
        'pandas',
        'numpy',
        'sympy',
        'geopy',
        'matplotlib',
        'scipy',
        'rasterio',
        'sympy',
        'scikit-learn',
        'gdal',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)

