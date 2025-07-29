import pandas as pd
import numpy as np
import sympy as sp
from geopy.distance import geodesic
import matplotlib.pyplot as plt
import os
import rasterio
from scipy.interpolate import interp1d
from scipy.ndimage import distance_transform_edt
from globalwaterbodycalculator.data_manager import ensure_equation_csv

from osgeo import ogr, gdal
from osgeo.gdalnumeric import CopyDatasetInfo, BandWriteArray

class WaterBodyCalculator:
    def __init__(self, equations_file=None):
        try:
            if equations_file is None:
                equations_file = ensure_equation_csv()
            self.equations = pd.read_csv(equations_file)
            print(f"Successfully loaded equations from: {equations_file}")
        except Exception as e:
            raise FileNotFoundError(f"Error loading equations file: {e}")

    def parse_equation(self, equation_str):
        x = sp.symbols('x')
        return sp.sympify(equation_str.replace('^', '**'))

    def find_closest_id(self, latitude, longitude):
        min_distance = float('inf')
        closest_id = None

        for index, row in self.equations.iterrows():
            row_latitude = row['Latitude']
            row_longitude = row['Longitude']
            distance = geodesic((latitude, longitude), (row_latitude, row_longitude)).kilometers
            if distance < min_distance:
                min_distance = distance
                closest_id = row['ID']

        print(f"Closest water body ID: {closest_id}, Distance: {min_distance:.2f} km")
        return closest_id, min_distance

    def calculate_area_volume(self, id=None, latitude=None, longitude=None, depth=10):
        if id is None:
            if latitude is None or longitude is None:
                raise ValueError("Must provide either ID or both latitude and longitude")
            id, distance = self.find_closest_id(latitude, longitude)
            print(f"Using water body ID: {id}, Distance: {distance:.2f} km")

        eqs_id = self.equations[self.equations['ID'] == id]
        if eqs_id.empty:
            raise ValueError(f"No equations found for ID: {id}")

        def evaluate_equation(equation, x_value):
            x = sp.symbols('x')
            return float(equation.subs(x, x_value))

        # 准备插值的深度点
        depth_values = np.round(np.arange(0, depth + 0.1, 0.1), 1)
        results = {'Depth': depth_values}

        for degree in range(1, 6):
            area_equation_str = eqs_id[f'Degree {degree} Area Equation'].values[0]
            volume_equation_str = eqs_id[f'Degree {degree} Volume Equation'].values[0]
            area_eq = self.parse_equation(area_equation_str)
            volume_eq = self.parse_equation(volume_equation_str)

            area_values = [evaluate_equation(area_eq, d) for d in depth_values]
            volume_values = [evaluate_equation(volume_eq, d) for d in depth_values]

            results[f'Area Degree {degree}'] = area_values
            results[f'Volume Degree {degree}'] = volume_values

        power_area_equation_str = eqs_id['Power Area Equation'].values[0]
        power_volume_equation_str = eqs_id['Power Volume Equation'].values[0]
        power_area_eq = self.parse_equation(power_area_equation_str)
        power_volume_eq = self.parse_equation(power_volume_equation_str)

        power_area_values = [evaluate_equation(power_area_eq, d) for d in depth_values]
        power_volume_values = [evaluate_equation(power_volume_eq, d) for d in depth_values]

        results['Area Power'] = power_area_values
        results['Volume Power'] = power_volume_values

        result_df = pd.DataFrame(results)
        print(f"Calculated area and volume for water body ID: {id}")
        return result_df, id

    def save_results_to_csv(self, result_df, water_body_id, output_dir='.'):
        filename = os.path.join(output_dir, f'water_body_{water_body_id}_results.csv')
        result_df.to_csv(filename, index=False)
        print(f'Results saved to {filename}')

    def plot_results(self, result_df, water_body_id, output_dir='.'):
        fig, axes = plt.subplots(2, 1, figsize=(10, 12))

        # 绘制面积随深度变化图
        for degree in range(1, 6):
            axes[0].plot(result_df['Depth'], result_df[f'Area Degree {degree}'], label=f'Area Degree {degree}')
        axes[0].plot(result_df['Depth'], result_df['Area Power'], label='Area Power', linestyle='--')
        axes[0].set_xlabel('Depth (m)')
        axes[0].set_ylabel('Area (m^2)')
        axes[0].set_title('Area vs Depth')
        axes[0].legend()

        # 绘制体积随深度变化图
        for degree in range(1, 6):
            axes[1].plot(result_df['Depth'], result_df[f'Volume Degree {degree}'], label=f'Volume Degree {degree}')
        axes[1].plot(result_df['Depth'], result_df['Volume Power'], label='Volume Power', linestyle='--')
        axes[1].set_xlabel('Depth (m)')
        axes[1].set_ylabel('Volume (m^3)')
        axes[1].set_title('Volume vs Depth')
        axes[1].legend()

        # 保存图表为文件
        filename = os.path.join(output_dir, f'water_body_{water_body_id}_results.png')
        plt.savefig(filename)
        print(f'Plot saved to {filename}')

        # 显示图表
        plt.show()

    def plot3D(self, tiff_path):
        # Read bathymetry raster
        with rasterio.open(tiff_path) as dataset:
            elevation = dataset.read(1)
            nodata_val = dataset.nodata if dataset.nodata is not None else -9999.0

        # Mask no-data values
        elevation = np.where(elevation == nodata_val, np.nan, elevation)

        # Determine max depth
        max_depth = np.nanmax(elevation)

        # Create coordinate grid and flip axes
        cols = np.arange(elevation.shape[1])
        rows = np.arange(elevation.shape[0])
        X, Y = np.meshgrid(cols, rows)

        # plot it without transposing
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        surf = ax.plot_surface(
            X, Y, elevation,
            cmap='viridis',
            edgecolor='none',
            vmin=0,
            vmax=max_depth
        )
        # Create colorbar with default scale
        cbar = fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)
        cbar.set_label('Depth (m)')
        # Customize ticks: remove 0 and any above max_depth, ensure max_depth included
        try:
            ticks = [t for t in cbar.get_ticks() if t > 0 and t <= max_depth]
            if max_depth not in ticks:
                ticks.append(max_depth)
            ticks = sorted(ticks)
            cbar.set_ticks(ticks)
            cbar.set_ticklabels([f"{t:.1f}" for t in ticks])
        except Exception:
            # Fallback: only max_depth
            cbar.set_ticks([max_depth])
            cbar.set_ticklabels([f"{max_depth:.1f}"])

        # Labels and title with axes flipped
        ax.set_xlabel('X Axis (km)')
        ax.set_ylabel('Y Axis (km)')
        ax.set_zlabel('Depth (m)')
        ax.set_title('3D Bathymetry Visualization')

        # Set Z-axis limits
        ax.set_zlim(0, max_depth)

        plt.show()
        # ax.view_init(elev=45, azim=10)
        # plt.savefig(f'3D_Plot.png', dpi=600)

    
    def generate_bathymetry_tiff(self, lake_id, shapefile, id_field, depth=10, output_dir='.', driver_name='ESRI Shapefile', cellsize=1/3600, nodata_val=-9999, plot_3d=False):
        """
        Returns a list of paths to the tiff generated
        """

        if not os.path.exists(shapefile):
            raise FileNotFoundError(f"Shapefile not found at: {shapefile}")
        
        # 1) Compute the area-depth curve via the Power fit
        result_df, _ = self.calculate_area_volume(id=lake_id, depth=depth)
        depths = result_df['Depth'].values
        areas = result_df['Area Power'].values
        # A0 = areas[0] if areas[0] > 0 else 1.0
        A0 = areas.max()
        frac = areas / A0

        # fraction->depth interpolator
        idx = np.argsort(frac)
        frac_sorted = frac[idx]
        depth_sorted = depths[idx]
        interp_depth = interp1d(
            frac_sorted,
            depth_sorted,
            bounds_error=False,
            fill_value=(depth_sorted[0], depth_sorted[-1])
        )

        # 2) Open shapefile and filter to the desired lake

        gdal.UseExceptions()
        OutDrv = gdal.GetDriverByName('GTiff')
        TempDrv = gdal.GetDriverByName('Mem')
        os.makedirs(output_dir, exist_ok=True)

        drv = ogr.GetDriverByName(driver_name)
        ds = drv.Open(shapefile, 0)
        if ds is None:
            raise FileNotFoundError(f"Could not open shapefile: {shapefile}")
        lyr = ds.GetLayer()
        # apply attribute filter for performance
        # numeric vs string ID handled automatically by OGR
        lyr.SetAttributeFilter(f"{id_field} = '{lake_id}'")
        feat = lyr.GetNextFeature()
        if feat is None:
            raise ValueError(f"Lake ID {lake_id} not found in {shapefile}")
        srs_wkt = lyr.GetSpatialRef().ExportToWkt()

        # raster grid definition
        geom = feat.GetGeometryRef()
        cols, rows, env = self.getgrid(geom.GetEnvelope(), cellsize)
        gt = (env[0], cellsize, 0, env[3], 0, -cellsize)

        # rasterize mask polygon
        mask_ds = TempDrv.Create('', cols, rows, 1, gdal.GDT_Byte)
        mask_ds.SetProjection(srs_wkt)
        mask_ds.SetGeoTransform(gt)
        mem_ds = ogr.GetDriverByName('Memory').CreateDataSource('')
        mem_lyr = mem_ds.CreateLayer('', geom_type=ogr.wkbPolygon, srs=lyr.GetSpatialRef())
        fcopy = ogr.Feature(mem_lyr.GetLayerDefn())
        fcopy.SetGeometry(geom.Clone())
        mem_lyr.CreateFeature(fcopy)
        gdal.RasterizeLayer(mask_ds, [1], mem_lyr, burn_values=[1])

        # 3) Distance transform
        mask_arr = mask_ds.GetRasterBand(1).ReadAsArray()
        dist_arr = distance_transform_edt(mask_arr == 1)

        # 4) Hypsometric remapping
        water = mask_arr == 1
        flat_d = dist_arr[water]
        N = flat_d.size
        order = np.argsort(-flat_d)
        frac_vals = np.arange(1, N+1) / N
        depths_sorted = interp_depth(frac_vals)
        flat_depth = np.empty_like(flat_d, dtype=float)
        flat_depth[order] = depths_sorted

        bathy = np.full(dist_arr.shape, nodata_val, dtype=float)
        bathy[water] = flat_depth
        
        # Transpose the array
        bathy = bathy.T
        # Swap cols and rows
        cols, rows = rows, cols

        gt = (env[2], 0,        cellsize,
              env[1], -cellsize, 0)
        mask_ds.SetGeoTransform(gt)

        # 5) Write GeoTIFF
        out_path = os.path.join(output_dir, f"{lake_id}_bathymetry.tif")
        out_ds = OutDrv.Create(out_path, cols, rows, 1, gdal.GDT_Float32, options=['COMPRESS=LZW'])
        CopyDatasetInfo(mask_ds, out_ds)
        BandWriteArray(out_ds.GetRasterBand(1), bathy)
        out_ds.GetRasterBand(1).SetNoDataValue(nodata_val)
        out_ds.FlushCache()

        # cleanup
        out_ds = None
        mask_ds = None
        ds = None
        lyr = None
        mem_ds = None

        if plot_3d:
            self.plot3D(out_path)

        return [out_path]

    def getgrid(self, envelope, cellsize):
        """
        Compute the dimensions and extent of a raster grid based on a geometry envelope and cell resolution.
        """
        xmin, xmax, ymin, ymax = envelope

        # Convert geographic coordinates to grid indices
        i_min = int((xmin + 180.0) // cellsize)
        i_max = int((xmax + 180.0) // cellsize) + 1
        j_min = int((ymin + 90.0) // cellsize)
        j_max = int((ymax + 90.0) // cellsize) + 1

        # Compute grid size
        cols = i_max - i_min
        rows = j_max - j_min

        # Compute aligned geographic extent
        aligned_xmin = (i_min * cellsize) - 180.0
        aligned_xmax = (i_max * cellsize) - 180.0
        aligned_ymin = (j_min * cellsize) - 90.0
        aligned_ymax = (j_max * cellsize) - 90.0

        grid_envelope = (aligned_xmin, aligned_xmax, aligned_ymin, aligned_ymax)

        return cols, rows, grid_envelope
