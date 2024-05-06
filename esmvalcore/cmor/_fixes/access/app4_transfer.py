import logging

import csv

from iris.cube import CubeList

from ..native_datasets import NativeDatasetFix

from esmvalcore.cmor.check import cmor_check

logger = logging.getLogger(__name__)

class AllVars(NativeDatasetFix):

    def __init__(self):

        self.attrs_dict=dict(
                tstart = None,
                tend = None,
                definable = None,
                cmip_table = None,
                in_unit = None,
                calculation = None,
                axes_modifier = None,
                positive = None,
                notes = None,
                json_file_path = None,
                time_shot = None,
                access_version = None,
                reference_date = None,
                frequency = None,
                exp_description = None,
            )

    def _load_master_map(self, short_name, path='./'):
        with open(path,'r') as csv:
            reader=csv.read(csv,delimiter='r')
            for row in reader:
                if row[0] == short_name:
                    self.attrs_dict['short_name'] = row[0]
                    self.attrs_dict['definable'] = row[1]
                    self.attrs_dict['access_var'] = row[2]
                    self.attrs_dict['calculation'] = row[3]
                    self.attrs_dict['in_unit']=row[4]
                    self.attrs_dict['axes_modifier']=row[5]
                    self.attrs_dict['positive']=row[6]
                    self.attrs_dict['realm']=row[8].split()[0]
                    self.attrs_dict['var_notes']=row[9]
                    return
    
    def _app_get_dimention(self):
        # print 'opened input netCDF file: {}'.format(inrange_access_files[0])
        # print 'checking axes...'
        # sys.stdout.flush()

        var_name=self.attrs_dict['short_name']
        try:
            #
            #Determine which axes are X and Y, and what the values of the latitudes and longitudes are.
            #
            try:
                data_vals=self.cube
                print ('shape of data: {}'.format(np.shape(data_vals)))
            except (Exception):
                print ('E: Unable to read {} from ACCESS file'.format(self.attrs_dict['access_var'][0]))
                raise
            try:
                coord_vals=data_vals.dim_coords
                # coord_vals.extend(data_vals.dimensions)
            except:
                coord_vals=data_vals.dimensions
            # lon_vals=None
            # lat_vals=None
            # lon_name=None
            # lat_name=None
            #search for strings 'lat' or 'lon' in co-ordinate names
            print(coord_vals)
            for coord in coord_vals:
                if coord.var_name.lower().find('lon') != -1:
                    print(coord)
                    self.lon_name=coord.var_name.lower()
                    try:
                        self.lon_vals=coord
                    except:
                        # if os.path.basename(inrange_access_files[0]).startswith('ocean'):
                        #     if opts['access_version'] == 'OM2-025':
                        #         acnfile=ancillary_path+'grid_spec.auscom.20150514.nc'
                        #         acndata=netCDF4.Dataset(acnfile,'r')
                        #         lon_vals=acndata.variables['geolon_t']
                        #     else:
                        #         acnfile=ancillary_path+'grid_spec.auscom.20110618.nc'
                        #         acndata=netCDF4.Dataset(acnfile,'r')
                        #         lon_vals=acndata.variables['x_T']
                        # if os.path.basename(inrange_access_files[0]).startswith('ice'):
                        #     if opts['access_version'] == 'OM2-025':
                        #         acnfile=ancillary_path+'cice_grid_20150514.nc'
                        #     else:
                        #         acnfile=ancillary_path+'cice_grid_20101208.nc'
                        #     acndata=netCDF4.Dataset(acnfile,'r')
                        #     lon_vals=acndata.variables[coord]
                        raise RuntimeError('something wrong while get lon_vals')
                elif coord.var_name.lower().find('lat') != -1:
                    print(coord)
                    self.lat_name=coord.var_name.lower()
                    try:
                        self.lat_vals=coord
                        print('lat from file')
                    except:
                        # print('lat from ancil')
                        # if os.path.basename(inrange_access_files[0]).startswith('ocean'):
                        #     if opts['access_version'] == 'OM2-025':
                        #         acnfile=ancillary_path+'grid_spec.auscom.20150514.nc'
                        #         acndata=netCDF4.Dataset(acnfile,'r')
                        #         lat_vals=acndata.variables['geolat_t']
                        #     else:
                        #         acnfile=ancillary_path+'grid_spec.auscom.20110618.nc'
                        #         acndata=netCDF4.Dataset(acnfile,'r')
                        #         lat_vals=acndata.variables['y_T']
                        # if os.path.basename(inrange_access_files[0]).startswith('ice'):
                        #     if opts['access_version'] == 'OM2-025':
                        #         acnfile=ancillary_path+'cice_grid_20150514.nc'
                        #     else:
                        #         acnfile=ancillary_path+'cice_grid_20101208.nc'
                        #     acndata=netCDF4.Dataset(acnfile,'r')
                        #     lat_vals=acndata.variables[coord]
                        raise RuntimeError('something wrong while get lat_vals')
        except:
            pass
        return

    def _app_fix_axis(self):
        dim_list=[num for num in self.cube._dim_coords_and_dims]
        for dim_object,dim_num in dim_list:
            if dim_object.var_name.find('time'):
                axis_name='T'
            elif dim_object.var_name.find('lat'):
                axis_name='Y'
            elif dim_object.var_name.find('lon'):
                axis_name='X' 
            elif len(dim_list)==4 and dim_num==1:
                axis_name='Z'
            else:
                axis_name='unknown'

            try:
                #
                #Try and get the dimension bounds. The bounds attribute might also be called "edges"
                #If we cannot find any dimension bounds, create default bounds in a sensible way.
                #
                if self.cube.coord(dim_object.var_name).has_bound:
                    dim_val_bounds=self.cube.coord(dim_object.var_name).bounds
                    print('using dimension bounds')
                else:
                    try:
                        self.cube.coord(dim_object.var_name).guess_bounds
                        dim_val_bounds=self.cube.coord(dim_object.var_name).bounds
                    except:
                        dim_vals=self.cube.coord(dim_object.var_name)
                        dim_values=self.cube.coord(dim_object.var_name).points
                        if dim_vals == None:
                            print('No dimension values')
                        else:
                            try:
                                min_vals=np.append((1.5*dim_values[0] - 0.5*dim_values[1]),(dim_values[0:-1] + dim_values[1:])/2)
                                max_vals=np.append((dim_values[0:-1] + dim_values[1:])/2,(1.5*dim_values[-1] - 0.5*dim_values[-2]))
                            except:
                                print ('WARNING: dodgy bounds for dimension: {}'.format(dim))
                    
                                min_vals=dim_values[:]-15
                                max_vals=dim_values[:]+15
                            dim_val_bounds=np.column_stack((min_vals,max_vals))
            except:
                pass

            print ('handling different axes types')

        return
            

    def fix_metadata(self, cubes: logging.Sequence) -> logging.Sequence:

        self.attrs_dict=dict(
            tstart = None,
            tend = None,
            definable = None,
            cmip_table = None,
            in_unit = None,
            calculation = None,
            axes_modifier = None,
            positive = None,
            notes = None,
            json_file_path = None,
            time_shot = None,
            access_version = None,
            reference_date = None,
            frequency = None,
            exp_description = None,
        )

        self._load_master_map()

        print(self.attrs_dict)

        cube= self.get_cube(cubes, var_name=self.attrs_dict['access_var'])



        return CubeList([cube])


    self.map_file='.master_map.csv'
    short_name=self.vardef.short_name

