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

