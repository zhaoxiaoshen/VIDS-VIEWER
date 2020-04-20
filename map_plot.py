# coding=utf-8

import matplotlib.pyplot as plt
import numpy as np
import time
from math import *
import json


def position_monitor(parameter):
    if 'maps' not in parameter:
        return
    latitude = float(parameter['maps']['latitude'])
    longitude = float(parameter['maps']['longitude'])
    plt.subplot(2, 2, 1)
    plt.plot(latitude, longitude, '.', color='r')
    plt.pause(0.01)
    return


def get_distance_between_gps_point(latitude_a, longtitude_a, latitude_b, longitude_b):
    jl_jd = 102834.74258026089786013677476285
    jl_wd = 111712.69150641055729984301412873
    b = fabs((latitude_a - latitude_b) * jl_jd)
    a = fabs((longtitude_a - longitude_b) * jl_wd)
    distance = sqrt((a * a + b * b))
    return distance


def find_min_distance_point(latitude_all, longitude_all, latitude, longitude):
    lat_length = len(latitude_all)
    lon_length = len(longitude_all)
    if lat_length != lon_length:
        print ("paramters error")
    min_distance = get_distance_between_gps_point(latitude_all[0], longitude_all[0], latitude, longitude)
    min_index = 0
    for i in range(1, lat_length):
        distance = get_distance_between_gps_point(latitude_all[i], longitude_all[i], latitude, longitude)
        if distance < min_distance:
            min_distance = distance
            min_index = i
    print ("min distance index ", min_index)
    print ("min distance ", min_distance, latitude_all[min_index], " ", longitude_all[min_index])


def show_map(latitudes, longitudes):
    plt.title("load map")
    plt.xlabel("latitude")
    plt.ylabel("longitude")
    if (len(latitudes) == 0):
        return
    step = 1 #距离分割，画点
    latitude_a = latitudes[0]
    longitude_a = longitudes[0]
    plt.plot(latitude_a, longitude_a, '.', color='r')

    count = 0
    min_distance_for_show = 0.2
    # ax = plt.gca()
    # ax.get_xaxis().get_major_formatter().set_useOffset(False)
    for i in range(0, len(latitudes), step):
        if fabs(latitude_a - latitudes[i]) < 0.000001 and fabs(longitude_a - longitudes[i]) < 0.000001:
            count += 1
            continue
        if get_distance_between_gps_point(latitude_a, longitude_a, latitudes[i], longitudes[i]) > min_distance_for_show:
            plt.plot(latitudes[i], longitudes[i], '.', color='r')
            latitude_a = latitudes[i]
            longitude_a = longitudes[i]
        else:
            count += 1
        if (i%(step*30) == 0):
            plt.pause(0.00000001)
        if (i > 200000):
            break
        
    print("skip point num: ", count)


def map_load(name):
    file = open(name, 'r')
    latitude = []
    longitude = []
    while True:
        line = file.readline()
        if not line:
            break
        elements = line.split(',')
        if elements[0] == "$GPFPD" and len(elements) > 8:
            latitude.append(float(elements[6]))
            longitude.append(float(elements[7]))
    print ('map loading...')
    show_map(latitude, longitude)


    # latitude_a = 29.6729211627
    # longitude_a = 106.4778578257
    #
    # latitude_b = 29.672438962
    # longitude_b = 106.478483337
    # length = get_distance_between_gps_point(latitude_a, longitude_a, latitude_b, longitude_b)
    # print('road length ', length)
    print ('map load success')
# plt.ion() #开启interactive mode 成功的关键函数
# fig = plt.figure(1)
# plt.suptitle('map')

