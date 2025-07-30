# Licensed under the BSD 3-Clause License
# Copyright (C) 2021 GeospaceLab (geospacelab)
# Author: Lei Cai, Space Physics and Astronomy, University of Oulu

__author__ = "Lei Cai"
__copyright__ = "Copyright 2021, GeospaceLab"
__license__ = "BSD-3-Clause License"
__email__ = "lei.cai@oulu.fi"
__docformat__ = "reStructureText"


import h5py
import numpy as np
import cftime
import re
import datetime

import geospacelab.toolbox.utilities.pylogging as mylog
import geospacelab.toolbox.utilities.pydatetime as dttool

pulse_code_dict = {
    'alternating': 97,
    'barker': 98,
    'single pulse': 115,
}

antenna_code_dict = {
    'zenith': 32,
    'misa': 31,
}

var_name_dict = {
    'n_pp_log': 'popl',
    'n_pp_log_err': 'dpopl',
    'n_e': 'ne',
    'n_e_err': 'dne',
    'v_i_UP': 'vi3',
    'v_i_UP_err': 'dvi3',
    'T_i': 'ti',
    'T_i_err': 'dti',
    'T_r': 'tr',
    'T_r_err': 'dtr',
    'comp_mix': 'pm',
    'comp_mix_err': 'pm',
    'coef_T_i_T_r': 'cctitr',
    'coef_T_i_T_r_err': 'dcctitr',
    'GEO_LAT': 'gdlat',
    'GEO_LON': 'glon',
    'TEC': 'tec',
    'n_e_max': 'nemax',
    'h_max': 'hmax',
    'GEO_ALT': 'gdalt',
}


class Loader:
    """
    :param file_path: the file's full path
    :type file_path: pathlib.Path object
    :param file_type: the specific file type for the file being loaded. Options: ['TEC-MAT'], 'TEC-LOS', 'TEC-sites')
    :type file_type: str
    :param load_data: True, load without calling the method "load_data" separately.
    :type load_data: bool
    """
    def __init__(self, file_path, load_data=True):
        self.file_path = file_path
        self.variables = {}
        self.metadata = {}

        self.done = False
        if load_data:
            self.load()

    def load(self):
        variables = {}
        with h5py.File(self.file_path, 'r') as fh5:
            data_fh5 = fh5['Data']
            vars_fh5 = {}
            fh5_vars_1d = data_fh5['Array Layout']['1D Parameters']
            for var_name in fh5_vars_1d.keys():
                if var_name == 'Data Parameters':
                    continue
                vars_fh5[var_name] = np.array(fh5_vars_1d[var_name])[:, np.newaxis]
            fh5_vars_2d = data_fh5['Array Layout']['2D Parameters']
            for var_name in fh5_vars_2d.keys():
                if var_name == 'Data Parameters':
                    continue
                vars_fh5[var_name] = np.array(fh5_vars_2d[var_name]).T
            vars_fh5['gdalt'] = np.array(data_fh5['Array Layout']['gdalt'])[np.newaxis, :]
            vars_fh5['timestamps'] = np.array(data_fh5['Array Layout']['timestamps'])[:, np.newaxis]
            for var_name, var_name_fh5 in var_name_dict.items():
                if var_name_fh5 not in vars_fh5.keys():
                    mylog.StreamLogger.warning(
                        f"The requested variable {var_name_fh5} does not exist in the data file!")
                    variables[var_name] = None
                    continue
                variables[var_name] = vars_fh5[var_name_fh5]
            variables['DATETIME'] = dttool.convert_unix_time_to_datetime_cftime(vars_fh5['timestamps'])
            variables['HEIGHT'] = np.tile(variables['GEO_ALT'], (variables['DATETIME'].shape[0], 1))
            variables['T_e'] = variables['T_i'] * variables['T_r']
            variables['T_e_err'] = variables['T_e'] * np.sqrt((variables['T_i_err'] / variables['T_i']) ** 2
                                                              + (variables['T_r_err'] / variables['T_r']) ** 2)
        self.variables = variables


if __name__ == "__main__":
    import pathlib
    fp = pathlib.Path("/home/lei/afys-data/Madrigal/Millstone_ISR/2016/20160314/Millstone_ISR_combined_20160314.005.hdf5")
    Loader(file_path=fp)