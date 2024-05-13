import logging

import csv

from iris.cube import CubeList

from ..native_datasets import NativeDatasetFix

from esmvalcore.cmor.check import cmor_check

logger = logging.getLogger(__name__)

import os

class tas(NativeDatasetFix):

    # def fix_height2m(self,cube,cubes):
    #     if cube.coords('height'):
    #         # In case a scalar height is required, remove it here (it is added
    #         # at a later stage). The step _fix_height() is designed to fix
    #         # non-scalar height coordinates.
    #         if (cube.coord('height').shape[0] == 1 and (
    #                 'height2m' in self.vardef.dimensions or
    #                 'height10m' in self.vardef.dimensions)):
    #             # If height is a dimensional coordinate with length 1, squeeze
    #             # the cube.
    #             # Note: iris.util.squeeze is not used here since it might
    #             # accidentally squeeze other dimensions.
    #             if cube.coords('height', dim_coords=True):
    #                 slices = [slice(None)] * cube.ndim
    #                 slices[cube.coord_dims('height')[0]] = 0
    #                 cube = cube[tuple(slices)]
    #             cube.remove_coord('height')
    #         else:
    #             cube = self._fix_height(cube, cubes)
    #         return cube
    # def fix_height_name(self, cube):
    #     if cube.coord('height').var_name!='height':
    #         cube.coord('height').var_name='height'
    #     return cube
    
    # def fix_long_name(self, cube):
    #     cube.long_name ='Near-Surface Air Temperature'
    #     return cube

    # def fix_var_name(self,cube):
    #     cube.var_name='tas'
    #     return cube

    # def fix_metadata(self, cubes):

    #     master_map_path='./master_map.csv'

    #     with open (master_map_path,'r') as map:
    #         reader=csv.reader(map, delimiter=',')
    #         for raw in reader:
    #             if raw[0]=='tas':
    #                 tas_map=raw
    #                 break

    #     # original_short_name='air_temperature'
    #     original_short_name='fld_s03i236'

    #     cube= self.get_cube(cubes, var_name=original_short_name)

    #     print('Successfully get the cube(tas)')

    #     # print('self.vardef:',self.vardef.dimensions)

    #     # print('height shape:',cube.coord('height').shape[0])

    #     # print(cube)
    #     # cube=self.fix_height2m(cube,cubes)

    #     cube = self.fix_height_name(cube)

    #     cube = self.fix_long_name(cube)

    #     print('standard_name:',cube.standard_name)

    #     print('long_name:',cube.long_name)

    #     cube_checked= cmor_check(cube=cube,cmor_table='CMIP6',mip='Amon',short_name='tas',check_level=1)
        

    #     return CubeList([cube_checked])
    def __init__(self,vardef,
        extra_facets,
        session,
        frequency):

        super().__init__(vardef,extra_facets,session,frequency)

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
        
        self.cube=None
        self.lon_vals=None
        self.lat_vals=None
        self.lon_name=None
        self.lat_name=None
        self.mip=self.extra_facets['mip']
        # cmvme is current file dir
        #self.cmvme_path=os.getcwd()
        self.current_dir=os.path.dirname(__file__)
    
    def _load_master_map(self, short_name,path=os.path.dirname(__file__)):
        path=self.current_dir
        with open(f'{path}/master_map.csv') as csv_file:
            reader=csv.reader(csv_file,delimiter=',')
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
    def _app_get_timeshot(self):
        try:
            with open(f'{self.current_dir}/cmvme_all_piControl_3_3.csv','r') as file:
                cmvme_reader=csv.reader(file,delimiter='\t')
                for row in cmvme_reader:
                    if row[0]==self.mip and row[6]==self.vardef.short_name:
                        if 'Pt' in row[14]:
                            timeshot='inst'
                            freq=str(freq)[:-2]
                        elif row[14] == 'monC':
                            timeshot='clim'
                            freq='mon'
                        else:
                            timeshot='mean'
                        return timeshot
                raise Exception('unable to find timeshot for this variable, please check recipe')
        except Exception as e:
            print(repr(e))
    
    def _app_fix_axis(self):
        dim_list=[num for num in self.cube._dim_coords_and_dims]
        for dim_object,dim_num in dim_list:
            if self.vardef.coordinates[dim_object.standard_name]._json_data['axis'] != -1:
                axis_name=self.vardef.coordinates[dim_object.standard_name]._json_data['axis']
            else:
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
                                # print ('WARNING: dodgy bounds for dimension: {}'.format(dim))
                    
                                min_vals=dim_values[:]-15
                                max_vals=dim_values[:]+15
                            dim_val_bounds=np.column_stack((min_vals,max_vals))
            except:
                pass
            
            # print('axis_name:',axis_name)
            try:
    
                if (axis_name == 'T') and (self.attrs_dict['axes_modifier'].find('dropT') == -1) and (self.mip.find('fx') == -1):
                    #identify some variable which gonna use in this section
                    cmor_tname=''
                    min_tvals=[]
                    max_tvals=[]

                    self.timeshot=self._app_get_timeshot()
                    if self.timeshot.find('mean') != -1:
                        cmor_tName='time'
                    elif self.timeshot.find('inst') != -1:
                        cmor_tName='time1'
                    elif self.timeshot.find('clim') != -1:
                        cmor_tName='time2'
                    else:
                        #assume timeshot is mean
                        print('timeshot unknown or incorrectly specified')
                        cmor_tName='time'

                    if self.attrs_dict['axes_modifier'].find('tMonOverride') == -1:
                        #convert times to days since reference_date
                        # PP temporarily comment as I'm not sure what this is for
                        #tvals = np.array(inrange_access_times) + cdtime.reltime(0,refString).torel('days since {r:04d}-01-01'.format(r=opts['reference_date']),cdtime.DefaultCalendar).value
                        # print(f"time values converted to days since 01,01,{opts['reference_date']:04d}: {tvals[0:5]}...{tvals[-5:-1]}")
                        tvals=[d.points for d in self.vardef.coordinates if d.var_name.find('time')][0]
                        if self.mip.find('A10day') != -1:
                            print('Aday10: selecting 1st, 11th, 21st days')
                            a10_tvals = []
                            for a10 in tvals:
                                #a10_comp = cdtime.reltime(a10,'days since {r:04d}-01-01'.format(r=opts['reference_date'])).tocomp(cdtime.DefaultCalendar)
                                a10_comp = a10.date()
                                #print(a10, a10_comp, a10_comp.day)
                                if a10_comp.day in [1,11,21]:
                                    a10_tvals.append(a10)
                            tvals = a10_tvals
                    else:
                        #this part is for 'tMonOverride', I don't find any variable have this axes_modifier.
                        #temporarily ignore this part

                        raise Exception(f'unable to create time axis for this variable:{self.vardef.short_name}')
                        # print 'manually create time axis'
                        # tvals=[]
                        # if opts['frequency'] == 'yr':
                        #     print 'yearly'
                        #     for year in range(opts['tstart'],opts['tend']+1):
                        #         tvals.append(cdtime.comptime(year,07,02,12).torel(refString,cdtime.DefaultCalendar).value)
                        # elif opts['frequency'] == 'mon':
                        #     print 'monthly'
                        #     for year in range(opts['tstart'],opts['tend']+1):
                        #         for mon in range(1,13):
                        #             tvals.append(cdtime.comptime(year,mon,15).torel(refString,cdtime.DefaultCalendar).value)
                        # elif opts['frequency'] == 'day':
                        #     print 'daily'
                        #     newstarttime=cdtime.comptime(opts['tstart'],1,1,12).torel(refString,cdtime.DefaultCalendar).value
                        #     difftime=inrange_access_times[0] - newstarttime
                        #     newendtimeyear=cdtime.comptime(opts['tend'],12,31,12).torel(refString,cdtime.DefaultCalendar).value
                        #     numdays_cal=int(newendtimeyear - newstarttime + 1)
                        #     numdays_tvals=len(inrange_access_times)
                        #     #diff_days=numdays_cal - numdays_tvals
                        #     if numdays_cal == 366 and numdays_tvals == 365: 
                        #         print 'adjusting for single leap year offset'
                        #         difftime=inrange_access_times[0] - newstarttime - 1
                        #     else: difftime=inrange_access_times[0] - newstarttime
                        #     tvals=np.array(inrange_access_times) - difftime
                        # else: 
                        #     print 'cannot manually create axis for this frequency, {}'.format(opts['frequency'])
                    print(f'first test successful: {cmor_tName},{tvals}')

            except Exception as e:
                print(repr(e))


        return
            

    def fix_metadata(self, cubes: logging.Sequence) -> logging.Sequence:

        self._load_master_map(short_name=self.vardef.short_name)

        self.cube = self.get_cube(cubes, var_name=self.attrs_dict['access_var'])

        self._app_get_dimention()

        self._app_fix_axis()

        return CubeList([self.cube])


class pr(NativeDatasetFix):

    def fix_height2m(self,cube,cubes):
        if cube.coords('height'):
            # In case a scalar height is required, remove it here (it is added
            # at a later stage). The step _fix_height() is designed to fix
            # non-scalar height coordinates.
            if (cube.coord('height').shape[0] == 1 and (
                    'height2m' in self.vardef.dimensions or
                    'height10m' in self.vardef.dimensions)):
                # If height is a dimensional coordinate with length 1, squeeze
                # the cube.
                # Note: iris.util.squeeze is not used here since it might
                # accidentally squeeze other dimensions.
                if cube.coords('height', dim_coords=True):
                    slices = [slice(None)] * cube.ndim
                    slices[cube.coord_dims('height')[0]] = 0
                    cube = cube[tuple(slices)]
                cube.remove_coord('height')
            else:
                cube = self._fix_height(cube, cubes)
            return cube
        else:
            return cube
    # def fix_height_name(self, cube):
    #     for coord in cube.dim_coords:
    #         if coord.var_name=='height':
    #             if cube.coord('height').var_name!='height':
    #                 cube.coord('height').var_name='height'
    #     return cube

    def fix_var_name(self,cube):
        cube.var_name='pr'
        return cube
    
    def fix_long_name(self, cube):
        cube.long_name ='Precipitation'
        return cube

    # def fix_coord_system(self,cube):
    #     cube.coords('latitude')[0].coord_system=

    def fix_metadata(self, cubes):

        master_map_path='./master_map.csv'

        with open (master_map_path,'r') as map:
            reader=csv.reader(map, delimiter=',')
            for raw in reader:
                if raw[0]=='pr':
                    pr_map=raw
                    break

        # original_short_name='air_temperature'
        original_short_name='fld_s05i216'

        cube= self.get_cube(cubes, var_name=original_short_name)

        cube=self.fix_var_name(cube)

        cube=self.fix_long_name(cube)

        cube_checked= cmor_check(cube=cube,cmor_table='CMIP6',mip='Amon',short_name='pr',check_level=1)

        print('Successfully get the cube(pr)')

        # print('self.vardef:',self.vardef.dimensions)

        # print('height shape:',cube.coord('height').shape[0])

        # print(cube)
        # cube=self.fix_height2m(cube,cubes)

        # cube= self.fix_height_name(cube)
        

        return CubeList([cube_checked])


class psl(NativeDatasetFix):

    def fix_metadata(self, cubes):

        master_map_path='./master_map.csv'

        with open (master_map_path,'r') as map:
            reader=csv.reader(map, delimiter=',')
            for raw in reader:
                if raw[0]=='pr':
                    pr_map=raw
                    break

        # original_short_name='air_temperature'
        original_short_name='fld_s16i222'

        cube= self.get_cube(cubes, var_name=original_short_name)

        print('Successfully get the cube(psl)')

        # print('self.vardef:',self.vardef.dimensions)

        # print('height shape:',cube.coord('height').shape[0])

        # print(cube)
        # cube=self.fix_height2m(cube,cubes)

        # cube= self.fix_height_name(cube)
        

        return CubeList([cube])

class sftlf(NativeDatasetFix):

    def fix_metadata(self,cubes):
        original_short_name='fld_s03i395'

        cube= self.get_cube(cubes, var_name=original_short_name)

        print('Successfully get the cube(sftlf)')

        return CubeList([cube])


