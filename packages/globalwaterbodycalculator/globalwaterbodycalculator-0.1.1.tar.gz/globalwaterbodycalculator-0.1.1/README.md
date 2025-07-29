# Global Waterbody Calculator

**Global Waterbody Calculator** is an open-source Python package for estimating storage curves and bathymetry of **freshwater** bodies.
Given a HydroLAKES ID or geographic coordinates, the tool fits global depth–area–volume (D-A-V) relationships, exports results, and generates high-resolution GeoTIFFs plus interactive 3-D visualizations.

[![PyPI](https://img.shields.io/pypi/v/globalwaterbodycalculator.svg)](https://pypi.org/project/globalwaterbodycalculator/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](#license)

## Features

| Capability                 | Details                               |
| -------------------------- | ------------------------------------- |
| Global D-A & D-V retrieval | Based on HydroLAKES, GLOBathy, GLRDAV |
| 0.1 m resolution           | Area & volume at 0.1 m depth steps    |
| Publication-ready plots    | CSV and PNG outputs                   |
| Bathymetric GeoTIFF        | Raster created from lake polygons     |
| Interactive 3-D view       | Matplotlib/Plotly surface rendering   |

## Installation

```bash
# PyPI
pip install globalwaterbodycalculator

## Requirements

- Python ≥ 3.7
- Required packages (automatically installed via pip):
  - `numpy`
  - `pandas`
  - `matplotlib`
  - `scipy`
  - `geopy`
  - `rasterio`
  - `scikit-learn`
  - `gdal`
  - `ogr`
  - `shapely`

Ensure `GDAL` and `OGR` are installed and configured correctly on your system. These are required for raster and vector operations (e.g., shapefile processing and TIFF output).

## Quick Start (Python API)

```python
from globalwaterbodycalculator.calculator import WaterBodyCalculator

# Initialize the calculator
calculator = WaterBodyCalculator()

# Calculate area-volume relationships by waterbody ID
result_df, water_body_id = calculator.calculate_area_volume(id=7, depth=244)
calculator.save_results_to_csv(result_df, water_body_id, output_dir='.')
calculator.plot_results(result_df, water_body_id, output_dir='.')

# Alternatively, calculate using latitude and longitude
result_df, water_body_id = calculator.calculate_area_volume(latitude=45.59193, longitude=47.71771, depth=10)
calculator.save_results_to_csv(result_df, water_body_id, output_dir='.')
calculator.plot_results(result_df, water_body_id, output_dir='.')
```

## Bathymetric Mapping and 3D Visualization

You can generate bathymetric maps and 3D plots from shapefiles:

```python
# Generate bathymetric GeoTIFF and optionally plot 3D visualization
calculator.generate_bathymetry_tiff(
    lake_id=7,			# Hylak_id of the waterbody
    shapefile='lakes.shp',	# Location of the shp file
    id_field='Hylak_id',	# Name of the id column
    depth=244,			# Max depth of the waterbody
    output_dir='output/',
    plot_3d=True  		# Set to True to enable 3D plotting
)
```

This will:

- Compute the depth raster from the lake polygon and fitted D-A relationship
- Save the bathymetric map as a GeoTIFF
- Display an interactive 3D surface plot of the lake basin
- If "plot_3d" is not set to True (default=False), only a GeoTIFF file will be generated

Input & Output

| Item                                        | Format         | Description                                        |
| ------------------------------------------- | -------------- | -------------------------------------------------- |
| **Input**                             |                |                                                    |
| `id` **or** `latitude, longitude` | int / float    | HydroLAKES ID or WGS-84 coordinates                |
| `depth`                                   | float          | Maximum depth (m)                                  |
| Lake polygon (optional)                     | ESRI Shapefile | Must include an `id_field` matching `Hylak_id` |
| **Output**                            |                |                                                    |
| `<id>_dav.csv`                            | CSV            | Depth, area (m²), volume (m³)                    |
| `<id>_dav.png`                            | PNG            | Area / volume curves                               |
| `<id>_bathy.tif`                          | GeoTIFF        | Bathymetric raster                                 |
| `<id>_3d.html`                            | HTML           | Interactive 3-D view (optional)                    |

Directory Layout
globalwaterbodycalculator/
├─ calculator.py
├─ equations/          # reference equations
├─ examples/
└─ docs/

Citation
Please cite Global Waterbody Calculator in your publications as:
@software{Yu_Liao_Wu_GWC_2025,
  author       = {Shengde Yu and Yukai Wu and Weikun Liao},
  title        = {{Global Waterbody Calculator}: Freshwater Depth–Area–Volume Estimator},
  year         = {2025},
  version      = {`<current-version>`},
  url          = {https://pypi.org/project/globalwaterbodycalculator/}
}

Yu, S., Wu, Y，& Liao, W. (2025). *Global Waterbody Calculator: A Python package for freshwater depth–area–volume estimation* (Version `<current-version>`) [Software]. Available from https://pypi.org/project/globalwaterbodycalculator/

Authors
Shengde Yu — Ecohydrology Research Group, Department of Earth & Environmental Sciences, University of Waterloo, Waterloo, ON, Canada — s228yu@uwaterloo.ca

Yukai Wu — The Edward S. Rogers Sr. Department of Electrical & Computer Engineering, University of Toronto, Toronto, ON, Canada — yukai.wu@mail.utoronto.ca

Weikun Liao — Department of Chemical Engineering & Applied Chemistry, University of Toronto, Toronto, ON, Canada — weikun.liao@mail.utoronto.ca
