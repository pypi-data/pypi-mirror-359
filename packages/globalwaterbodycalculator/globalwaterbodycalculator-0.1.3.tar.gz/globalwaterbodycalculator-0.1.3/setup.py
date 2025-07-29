from setuptools import setup, find_packages

setup(
    name='globalwaterbodycalculator',
    version='0.1.3',
    description='A package for calculating water storage based on global water body depth-area-volume equation and visualizing waterbody geometries.',
    author='Shengde Yu, Yukai Wu, Weikun Liao, Zhijian Zhuo',
    author_email='s228yu@uwaterloo.ca, yukai.wu@mail.utoronto.ca, weikun.liao@mail.utoronto.ca, zhijian.zhuo@mail.utoronto.ca',
    url='https://github.com/SYubaby/Globalwaterbodycalculator',
    packages=find_packages(),
    include_package_data=False,
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
        "gdown",
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)

