# coding=utf-8

import easygui as gui
import serial
import matplotlib.pyplot as plt
import os
import datetime
from threading import Thread, Lock
import map_plot
import config_parse
from math import *
import time


def activate_map_show(latitude_a, longitude_a, text):
    ret = False
    min_distance_for_show = 0.2
    frames = text.split('\r\n')
    # print("text befor: ", text)
    for frame in frames:
        text = frame
        if len(frame) < 6:
            continue
        elements = frame.split(',')
        # print (elements[0], " len ", len(elements) )
        if elements[0] == "$GPFPD" and len(elements) > 8:
            latitude_b = float(elements[6])
            longitude_b = float(elements[7])
            # print (latitude_b, longitude_b)
            if fabs(latitude_a - latitude_b) < 0.000001 and fabs(longitude_a - longitude_b) < 0.000001:
                continue
            if latitude_a < 0.00000001 and longitude_a < 0.00000001:
                latitude_a = latitude_b
                longitude_a = longitude_b
                ret = True
                text = ""
                # plt.plot(latitude_a, longitude_a, '.', color='r')
            elif map_plot.get_distance_between_gps_point(latitude_a, longitude_a, latitude_b, longitude_b) > min_distance_for_show:
                latitude_a = latitude_b
                longitude_a = longitude_b
                # plt.plot(latitude_a, longitude_a, '.', color='r')
                text = ""
                ret = True
    return ret, text, latitude_a, longitude_a


def read_from_serial(ser, map_name):
    print ('采集线程启动……')
    map_file = open(map_name, 'w')
    plt.title("collect map")
    plt.xlabel("latitude")
    plt.ylabel("longitude")
    text = ""
    latitude_a = 0.0
    longitude_a = 0.0
    num = 0
    while not is_serial_status_stop():
        if is_serial_status_pause():
            continue
        # time.sleep(0.02)
        if ser.in_waiting:
            # print('ticking……')
            line = ser.read(ser.in_waiting).decode('utf-8')
            map_file.write(line)
            # print("line ", line)
            # continue
            text += str(line)
            if line == 'exit':
                break
            ret, text, latitude_a, longitude_a = activate_map_show(latitude_a, longitude_a, text)
            if ret:
                plt.plot(latitude_a, longitude_a, '.', color='r')
                num += 1
                if (num % 30 == 0):
                    plt.pause(0.00000001)

            # print ("text after: ", text)
  
    map_file.close()
    print("thread is exit")


def is_serial_status_pause():
    global lock
    lock.acquire()
    global is_serial_pause
    is_pause = is_serial_pause
    lock.release()
    return is_pause


def is_serial_status_stop():
    global lock
    lock.acquire()
    global is_serial_stop
    is_stop = is_serial_stop
    lock.release()
    return is_stop


def set_serial_status():
    global is_serial_stop
    global is_serial_pause
    global lock
    if is_serial_pause:
        choice = gui.buttonbox(msg='已暂停，是否继续', title='采集地图', choices=('继续', '停止'))
    else:
        choice = gui.buttonbox(msg='正在采集……', title='采集地图', choices=('暂停', '停止'))
    if choice == '暂停':
        lock.acquire()
        is_serial_pause = True
        lock.release()
    if choice == '停止':
        lock.acquire()
        is_serial_stop = True
        lock.release()
    if choice == '继续':
        lock.acquire()
        is_serial_pause = False
        lock.release()


def collect_map(config_path):
    print ("开始采集程序")
    serial_name, serial_baud = config_parse.get_serial_config(config_path)
    file_path = config_path + r'/map'
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    file_name = r'/' + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + ".map"
    print ("map file name will create: ", file_name)
    ser = serial.Serial(serial_name, int(serial_baud), timeout=None)
    if not ser.is_open:
        serial_error = '串口打开失败，串口号：' + serial_name + ' 波特率：' + serial_baud
        gui.msgbox(msg=serial_error, title='采集地图', ok_button='退出')
        return
    global is_serial_stop
    is_serial_stop = False
    global is_serial_pause
    is_serial_pause = False
    serial_thread = Thread(target=read_from_serial, args=(ser,file_name))
    serial_thread.start()
    while not is_serial_status_stop():
        set_serial_status()
    config_parse.set_map_name_in_config(config_path, file_name)
    serial_thread.join()
    return


def load_map(config_path):
    print ('开始加载地图')
    map_name = config_parse.get_map_name(config_path)
    print ('map name: ', map_name)
    if not os.path.exists(map_name):
        gui.msgbox(msg='地图文件不存在', title='显示地图', ok_button='OK')
        return
    map_plot.map_load(map_name)
    gui.msgbox(msg='加载完成, 是否退出', title='显示地图', ok_button='OK')
    return


def  start_vids(config_path):
    # sudopw = 'zhaoshen'
    cd_cmd = 'cd ' + config_path
    run_cmd = 'sudo -S ./VIDS'
    cmd = "gnome-terminal -e 'bash -c \"%s ; %s; exec bash\"'"%(cd_cmd, run_cmd)
    # cmd = "gnome-terminal -e 'bash -c \"%s ; echo %s|%s\"'"%(cd_cmd, sudopw, run_cmd)
    print(cmd)
    os.system(cmd)
    # os.system(cd_cmd)
    # os.system("gnome-terminal -e 'bash -c \"ls; exec bash\"'")


def main():
    run = "采集地图"
    load = "加载地图"
    run_vids = "无人驾驶"
    config_path = r'/home/nvidia/VIDS'
    # config_path = r'/home/zhaoshen/driver'
    choice = gui.buttonbox(msg='', title='地图采集程序', choices=(run_vids, run, load))
    if choice == run:
        collect_map(config_path)
    if choice == load:
        load_map(config_path)
    if choice == run_vids:
        start_vids(config_path)


lock = Lock()
is_serial_stop = True
is_serial_pause = False
main()
