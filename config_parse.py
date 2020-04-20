# coding=utf-8

import configparser
import easygui as gui


def get_map_name(path):
    config_file = path + r"/config/VehicleConfig.ini"
    print ("config file: ", config_file)
    config = configparser.ConfigParser()
    config.read(config_file, encoding='utf-8')
    sections = config.sections()
    if not config.has_option('MAP', 'name'):
        msg_str = '获取地图配置失败，请检查配置文件 ' + config_file
        gui.msgbox(msg=msg_str, title='加载地图', ok_button='OK')
        exit(-1)
    map_name = config.get('MAP', 'name')
    config.clear()
    return map_name


def get_serial_config(path):
    config_file = path + r"/config/SensorConfig.ini"
    config = configparser.ConfigParser()
    config.read(config_file, encoding='utf-8')
    if (not config.has_option('GNSS', 'port_name')) or (not config.has_option('GNSS', 'baud')):
        gui.msgbox(msg='获取串口配置失败，请检查配置文件', title='加载地图', ok_button='OK')
        exit(-1)
    serial_name = config.get('GNSS', 'port_name')
    serial_baud = config.get('GNSS', 'baud')
    config.clear()
    return serial_name, serial_baud


def set_map_name_in_config(path, name):
    config_file = path + r"/config/VehicleConfig.ini"
    config = configparser.ConfigParser()
    config.read(config_file, encoding='utf-8')
    if not config.has_section('MAP'):
        config.add_section('MAP')
    if config.has_option('MAP', 'name'):
        config.remove_option('MAP', 'name')
    config.set("MAP", "name", name)
    file_save = open(config_file, 'w')
    config.write(file_save)
    file_save.close()
    config.clear()
