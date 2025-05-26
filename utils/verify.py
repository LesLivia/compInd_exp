import configparser
import os
from datetime import datetime

config = configparser.ConfigParser()
config.sections()
config.read('./resources/config/config.ini')
config.sections()

UPPAAL_PATH = config['UPPAAL SETTINGS']['UPPAAL_PATH']
UPP_SCRIPT_PATH = config['UPPAAL SETTINGS']['UPPAAL_SCRIPT_PATH']
UPP_OUT_PATH = config['UPPAAL SETTINGS']['UPPAAL_OUT_PATH']


def get_ts():
    ts = datetime.now()
    ts_split = str(ts).split('.')[0]
    ts_str = ts_split.replace('-', '_')
    ts_str = ts_str.replace(' ', '_')
    return ts_str


def run_exp(name, model_path, query_path):
    res_name = name.replace('_source.txt', '') + '_' + get_ts()
    os.system('{} {} {} {} {}'.format(UPP_SCRIPT_PATH, UPPAAL_PATH, model_path, query_path,
                                      UPP_OUT_PATH.format(res_name)))
    return UPP_OUT_PATH.format(res_name)


def verify_compatibility(name, model_path, query_path):
    out_file = run_exp(name, model_path, query_path)
    res = False
    with open(out_file, 'r') as f:
        lines = f.readlines()
        try:
            result_line = [line for line in lines if '-- Formula is' in line][0]
            res = 'NOT' not in result_line
        except IndexError:
            print('An error occurred during verification.')
    return res
