# -*- coding: utf-8 -*-
"""
MAGPY: A Python module for visualizing magnetometer data using 
       an accelerometer-based tilt-compenstation algorithm. This module uses 
       pyqtgraph's plotting functionality.

Created on Sun Dec 14 01:15:57 2014

@author: Dan Sweeney (sweeneyd@vt.edu)
"""
import numpy as np

class MagPy(object):
    def __init__(self, 
                 filename = 'DATA-021-SpinTest.txt', 
                 #filename = 'DATA-190-4-30-14-1248-ToDan2.txt',
                 filepath = '/Users/Dan/Desktop/',
                 delimiter = '\t'):
        self.parseData(self.readData(filename, filepath, delimiter))
        self.norm_a = np.sqrt(self.ax**2 + self.ay**2 + self.az**2)
        self.norm_a_cal = 2*np.pi*(self.norm_a-np.average(self.norm_a))/(np.max(self.norm_a)-np.min(self.norm_a))
        
    def readData(self, filename, filepath, delimiter, serial = False):
        f = open(filepath + filename)
        fline = f.readlines()
        f.close()
        if len(fline) == 1:
            fline = fline[0].split('\r')
        data = []
        for line in fline:
            if line[0] != ';':
                    point = line.split(delimiter)
                    if len(point) > 4 and point[4] != '':
                        if '\n' in point[6]:
                            point[6].split('\n')
                            #point[6] = point[6].split('\n')[0]
                        data.append([point[0], point[1], point[2], point[3], point[4], point[5], point[6]])
        data = np.array(data)
        data = {'data': data, 
                't': data[:, 0], 
                'ax': data[:, 1], 
                'ay': data[:, 2],
                'az': data[:, 3],
                'mx': data[:, 4],
                'my': data[:, 5],
                'mz': data[:, 6]}
        return data
        
    def parseData(self, data):
        [self.ax, mx] = self.getAccelMagPairs(data['ax'], data['mx'])
        [self.ay, my] = self.getAccelMagPairs(data['ay'], data['my'])
        [self.az, mz] = self.getAccelMagPairs(data['az'], data['mz'])
        self.mx = self.centerData(mx)
        self.my = self.centerData(my)
        self.mz = self.centerData(mz)
        [self.yaw, self.pitch, self.roll] = self.getYPR(self.ax, 
                                                        self.ay, 
                                                        self.az, 
                                                        self.mx, 
                                                        self.my,
                                                        self.mz)
    
    def rmMt(self, data):
        for i in range(len(data)):
            if data[i] == '':
                data[i] = None
        data = np.array([i for i in data if i != 'None'])
        return data
        
    def getAccelMagPairs(self, accel_data, mag_data):
        for i in range(len(mag_data)):
            if mag_data[i] == '':
                mag_data[i] = None
                accel_data[i] = None
        mag_data = np.array([i for i in mag_data if i != 'None'])
        accel_data = np.array([i for i in accel_data if i != 'None'])     
        return [accel_data.astype(np.float), mag_data.astype(np.float)]
        
    def getLogicArray(self, mag_data):
        logic = np.ones(len(mag_data))
        for i in mag_data:
            if i == '':
                logic = None
        return logic
    
    '''
    ================ DSP FUNCTIONS ========================== 
    Functions handling digital signal processing of data
    '''
        
    def centerData(self, data):
        data = np.array(data).astype(np.float).tolist()
        centered_data = [i - np.average(data) for i in data]
        return centered_data
        
    def vectorNorm(self, x, y, z):
        x = np.array(x).astype(np.float)
        y = np.array(y).astype(np.float)
        z = np.array(z).astype(np.float)
        norm_x = np.zeros(len(x))
        norm_y = np.zeros(len(y))
        norm_z = np.zeros(len(z))
        if len(x) == len(y) and len(y) == len(z):
            for i in range(len(x)):
                [norm_x[i], norm_y[i], norm_z[i]] = [x[i], y[i], z[i]] / np.sqrt(x[i]**2 + y[i]**2 + z[i]**2)   
        return [norm_x, norm_y, norm_z]
        
    def getYPR(self, ax, ay, az, mx, my, mz):
        [mx_cal, my_cal, mz_cal] = self.vectorNorm(mx, my, mz)
        [ax_cal, ay_cal, az_cal] = self.vectorNorm(ax, ay, az)
        pitch = np.arcsin(np.multiply(-1, ax_cal))
        roll = np.arcsin([np.round(i, 12) for i in np.divide(ay_cal, np.cos(pitch))])
        yaw = np.arctan2(np.multiply(-1, mx_cal, np.cos(pitch)) + np.multiply(mz_cal, np.sin(pitch)), 
                         np.multiply(mx_cal, np.sin(roll), np.sin(pitch)) + np.multiply(my_cal, np.cos(roll)) - np.multiply(mz_cal, np.sin(roll), np.cos(pitch)))
        return [yaw, pitch, roll]
        
if __name__ == '__main__':
    a = MagPy()