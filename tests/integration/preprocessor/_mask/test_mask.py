"""
Test mask.

Integration tests for the :func:`esmvalcore.preprocessor._mask`
module.

"""

import os
import tempfile
import unittest

import iris
import numpy as np

import tests
from esmvalcore.preprocessor import (PreprocessorFile, mask_fillvalues,
                                     mask_landsea, mask_landseaice)


class Test(tests.Test):
    """Test class."""

    def setUp(self):
        """Assemble a stock cube."""
        fx_data = np.empty((3, 3))
        fx_data[:] = 60.
        fx_data[1, 2] = 30.
        self.new_cube_data = np.empty((3, 3))
        self.new_cube_data[:] = 200.
        crd_sys = iris.coord_systems.GeogCS(iris.fileformats.pp.EARTH_RADIUS)
        self.lons = iris.coords.DimCoord([0, 1.5, 3],
                                         standard_name='longitude',
                                         bounds=[[0, 1], [1, 2], [2, 3]],
                                         units='degrees_east',
                                         coord_system=crd_sys)
        self.lats = iris.coords.DimCoord([0, 1.5, 3],
                                         standard_name='latitude',
                                         bounds=[[0, 1], [1, 2], [2, 3]],
                                         units='degrees_north',
                                         coord_system=crd_sys)
        self.times = iris.coords.DimCoord([0, 1.5, 2.5, 3.5],
                                          standard_name='time',
                                          bounds=[[0, 1], [1, 2], [2, 3],
                                                  [3, 4]],
                                          units='hours')
        self.time2 = iris.coords.DimCoord([0, 1.5, 2.5],
                                          standard_name='time',
                                          bounds=[[0, 1], [1, 2], [2, 3]],
                                          units='hours')
        self.coords_spec = [(self.lats, 0), (self.lons, 1)]
        self.fx_mask = iris.cube.Cube(fx_data,
                                      dim_coords_and_dims=self.coords_spec)
        self.mock_data = np.ma.empty((4, 3, 3))
        self.mock_data[:] = 10.

    def test_mask_landsea(self):
        """Test mask_landsea func."""
        iris.save(self.fx_mask, 'sftlf_test.nc')
        new_cube_land = iris.cube.Cube(self.new_cube_data,
                                       dim_coords_and_dims=self.coords_spec)
        new_cube_sea = iris.cube.Cube(self.new_cube_data,
                                      dim_coords_and_dims=self.coords_spec)

        # mask with fx files
        result_land = mask_landsea(new_cube_land, ['sftlf_test.nc'], 'land')
        result_sea = mask_landsea(new_cube_sea, ['sftlf_test.nc'], 'sea')
        expected = np.ma.empty((3, 3))
        expected.data[:] = 200.
        expected.mask = np.ones((3, 3), bool)
        expected.mask[1, 2] = False
        # set fillvalues so we are sure they are equal
        np.ma.set_fill_value(result_land.data, 1e+20)
        np.ma.set_fill_value(result_sea.data, 1e+20)
        np.ma.set_fill_value(expected, 1e+20)
        self.assert_array_equal(result_land.data, expected)
        expected.mask = np.zeros((3, 3), bool)
        expected.mask[1, 2] = True
        self.assert_array_equal(result_sea.data, expected)

        # Mask with shp files although sftlf is available
        new_cube_land = iris.cube.Cube(self.new_cube_data,
                                       dim_coords_and_dims=self.coords_spec)
        new_cube_sea = iris.cube.Cube(self.new_cube_data,
                                      dim_coords_and_dims=self.coords_spec)
        result_land = mask_landsea(new_cube_land, ['sftlf_test.nc'],
                                   'land',
                                   always_use_ne_mask=True)
        result_sea = mask_landsea(new_cube_sea, ['sftlf_test.nc'],
                                  'sea',
                                  always_use_ne_mask=True)

        # Bear in mind all points are in the ocean
        np.ma.set_fill_value(result_land.data, 1e+20)
        np.ma.set_fill_value(result_sea.data, 1e+20)
        expected.mask = np.zeros((3, 3), bool)
        self.assert_array_equal(result_land.data, expected)
        expected.mask = np.ones((3, 3), bool)
        self.assert_array_equal(result_sea.data, expected)

        # remove the fx.nc temporary file
        os.remove('sftlf_test.nc')

        # mask with shp files
        new_cube_land = iris.cube.Cube(self.new_cube_data,
                                       dim_coords_and_dims=self.coords_spec)
        new_cube_sea = iris.cube.Cube(self.new_cube_data,
                                      dim_coords_and_dims=self.coords_spec)
        result_land = mask_landsea(new_cube_land, None, 'land')
        result_sea = mask_landsea(new_cube_sea, None, 'sea')

        # bear in mind all points are in the ocean
        np.ma.set_fill_value(result_land.data, 1e+20)
        np.ma.set_fill_value(result_sea.data, 1e+20)
        expected.mask = np.zeros((3, 3), bool)
        self.assert_array_equal(result_land.data, expected)
        expected.mask = np.ones((3, 3), bool)
        self.assert_array_equal(result_sea.data, expected)

    def test_mask_landseaice(self):
        """Test mask_landseaice func."""
        iris.save(self.fx_mask, 'sftgif_test.nc')
        new_cube_ice = iris.cube.Cube(self.new_cube_data,
                                      dim_coords_and_dims=self.coords_spec)
        result_ice = mask_landseaice(new_cube_ice, ['sftgif_test.nc'], 'ice')
        expected = np.ma.empty((3, 3))
        expected.data[:] = 200.
        expected.mask = np.ones((3, 3), bool)
        expected.mask[1, 2] = False
        np.ma.set_fill_value(result_ice.data, 1e+20)
        np.ma.set_fill_value(expected, 1e+20)
        self.assert_array_equal(result_ice.data, expected)
        os.remove('sftgif_test.nc')

    def test_mask_fillvalues(self):
        """Test the fillvalues mask: func mask_fillvalues."""
        data_1 = data_2 = self.mock_data
        data_2.mask = np.ones((4, 3, 3), bool)
        coords_spec = [(self.times, 0), (self.lats, 1), (self.lons, 2)]
        cube_1 = iris.cube.Cube(data_1, dim_coords_and_dims=coords_spec)
        cube_2 = iris.cube.Cube(data_2, dim_coords_and_dims=coords_spec)
        filename_1 = tempfile.NamedTemporaryFile().name + '.nc'
        filename_2 = tempfile.NamedTemporaryFile().name + '.nc'
        product_1 = PreprocessorFile(attributes={'filename': filename_1},
                                     settings={})
        product_1.cubes = [cube_1]
        product_2 = PreprocessorFile(attributes={'filename': filename_2},
                                     settings={})
        product_2.cubes = [cube_2]
        results = mask_fillvalues({product_1, product_2},
                                  0.95,
                                  min_value=-1.e10,
                                  time_window=1)
        result_1, result_2 = None, None
        for product in results:
            if product.filename == filename_1:
                result_1 = product.cubes[0]
            if product.filename == filename_2:
                result_2 = product.cubes[0]
        self.assert_array_equal(result_2.data.mask, data_2.mask)
        self.assert_array_equal(result_1.data, data_1)

    def test_mask_fillvalues_zero_threshold(self):
        """Test the fillvalues mask: func mask_fillvalues for 0-threshold"""
        data_1 = self.mock_data
        data_2 = self.mock_data[0:3]
        data_1.mask = np.ones((4, 3, 3), bool)
        data_1.mask[0] = False
        data_1.mask[2] = False
        data_2.mask = np.ones((3, 3, 3), bool)
        data_2.mask[0] = False
        data_2.mask[1] = False
        coords_spec = [(self.times, 0), (self.lats, 1), (self.lons, 2)]
        coords_spec2 = [(self.time2, 0), (self.lats, 1), (self.lons, 2)]
        cube_1 = iris.cube.Cube(data_1, dim_coords_and_dims=coords_spec)
        cube_2 = iris.cube.Cube(data_2, dim_coords_and_dims=coords_spec2)
        filename_1 = tempfile.NamedTemporaryFile().name + '.nc'
        filename_2 = tempfile.NamedTemporaryFile().name + '.nc'
        product_1 = PreprocessorFile(attributes={'filename': filename_1},
                                     settings={})
        product_1.cubes = [cube_1]
        product_2 = PreprocessorFile(attributes={'filename': filename_2},
                                     settings={})
        product_2.cubes = [cube_2]
        results = mask_fillvalues({product_1, product_2},
                                  0.,
                                  min_value=-1.e20)
        result_1, result_2 = None, None
        for product in results:
            if product.filename == filename_1:
                result_1 = product.cubes[0]
            if product.filename == filename_2:
                result_2 = product.cubes[0]
        # identical masks
        self.assert_array_equal(result_2.data[0, ...].mask,
                                result_1.data[0, ...].mask)
        # identical masks with cumluative
        cumulative_mask = cube_1[0].data.mask | cube_2[0].data.mask
        self.assert_array_equal(result_1[0].data.mask, cumulative_mask)
        self.assert_array_equal(result_2[0].data.mask, cumulative_mask)


if __name__ == '__main__':
    unittest.main()
