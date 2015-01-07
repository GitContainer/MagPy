# -*- coding: utf-8 -*-
"""
MAGPY: A Python module for visualizing magnetometer data using 
       an accelerometer-based tilt-compenstation algorithm. This module uses 
       pyqtgraph's plotting functionality.

Created on Sun Dec 14 01:15:57 2014

@author: Dan Sweeney (sweeneyd@vt.edu)
"""
import numpy as np
import pyqtgraph as pg

class MagPy(object):
    def __init__(self, 
                 #filename = 'DATA-021-SpinTest.txt', 
                 filename = 'DATA-190-4-30-14-1248-ToDan2.txt',
                 filepath = '/Users/Dan/Desktop/',
                 delimiter = '\t'):
        self.parseData(self.readData(filename, filepath, delimiter))
        self.norm_a = np.sqrt(self.ax**2 + self.ay**2 + self.az**2)
        self.norm_a_cal = 2*np.pi*(self.norm_a-np.average(self.norm_a))/(np.max(self.norm_a)-np.min(self.norm_a))
        
    def readData(self, filename, filepath, delimiter, serial = False):
        f = open(filepath + filename)
        fline = f.readlines()
        f.close()
        fline = fline[0].split('\r')
        data = []
        for line in fline:
            if line[0] != ';':
                [ts, ax, ay, az, mx, my, mz] = line.split(delimiter)
                data.append([ts, ax, ay, az, mx, my, mz])
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
    
    # ================
    # Setup Bulk Data Explorer Window
    # ================
    win1 = pg.GraphicsWindow(title='Bulk Data')
    win1.resize(1200,1200)
    win1.setWindowTitle('Tilt-Compensated Compass Direction and Accelerometer Data')
    
    tot_plot = win1.addPlot(title='Region Selection', colspan=3)
    tot_plot.plot(a.yaw, pen=(255,255,255,200))
    tot_plot.plot(a.norm_a_cal, pen=(0,100,100,200))
    lr = pg.LinearRegionItem([50,100])
    lr.setZValue(-10)
    tot_plot.addItem(lr)
    tot_plot.setLabel('left', 'Magnitude', units='AU')
    tot_plot.setLabel('bottom', 'Time')
    tot_plot.setMouseEnabled(x=True, y=False)

    # ================
    # Setup Finely Tuned Data Explorer
    # ================
    win1.nextRow()

    # ================
    # Setup Zoomed Magnetometer Plot
    # ================
    zoom_plot = win1.addPlot(title='Tilt-Compensated Magnetometer')
    zoom_plot.plot(a.yaw, pen=(255,255,255,200))
    zoom_plot.setLabel('left', 'Compass Direction', units='rad.')
    zoom_plot.setLabel('bottom', 'Time')
    
    # ================
    # Setup Zoomed Accelerometer Plot
    # ================
    accel_plot = win1.addPlot(title='Normalized Accelerometer')
    accel_plot.plot(a.norm_a_cal, pen=(0,100,100,200))
    accel_plot.setLabel('left', 'Normalized Acceleration', units='AU')
    accel_plot.setLabel('bottom', 'Time', units='s')
    
    # ================
    # Setup Circular Path-tracing Plot
    # ================
    mag_plot = win1.addPlot(title = 'Tilt-Compensated Magnetometer')
    mag_plot.setAspectLocked()
    r = np.linspace(0, 2, len(a.yaw))
    x = np.cos(a.yaw)
    y = np.sin(a.yaw)
    bound = [np.floor(zoom_plot.getViewBox().viewRange()[0]).astype(int)[0], np.floor(zoom_plot.getViewBox().viewRange()[0]).astype(int)[1]]
    x_bound = r[bound[0]:bound[1]]*x[bound[0]:bound[1]]
    y_bound = r[bound[0]:bound[1]]*y[bound[0]:bound[1]]
    mag_plot.plot(x, y, pen=(255,255,255,200))
    mag_plot.addLegend()
    mag_plot.plot([x_bound[0]], [y_bound[0]], symbolBrush=(255,0,0), symbolPen='w', name='Initial Position')
    mag_plot.plot([x_bound[-1]], [y_bound[-1]], symbolBrush=(0,0,255), symbolPen='w', name='Final Position')
    mag_plot.disableAutoRange()
    mag_plot.setRange(xRange=[-2, 2], yRange=[-2, 2])
    
    # ================
    # Setup Crosshairs for Zoomed Magnetometer Plot
    # ================
    label = pg.LabelItem(justify='right')
    vLine = pg.InfiniteLine(angle=90, movable=False)
    hLine = pg.InfiniteLine(angle=0, movable=False)
    mag_plot.addItem(vLine, ignoreBounds=True)
    mag_plot.addItem(hLine, ignoreBounds=True)
    vb = tot_plot.vb    
    
    # ================
    # Update plots as ROI changes
    # ================
    def updatePlot():
        # Update zoom and accel plots with as ROI on large plot is changed
        zoom_plot.setXRange(*lr.getRegion(), padding = 0)
        accel_plot.setXRange(*lr.getRegion(), padding = 0)
        
        # Update magnetometer direction plot with changind data
        mag_plot.clear()
        bound = [np.floor(zoom_plot.getViewBox().viewRange()[0]).astype(int)[0], np.floor(zoom_plot.getViewBox().viewRange()[0]).astype(int)[1]]
        r = np.linspace(0, 2, len(range(bound[0], bound[1])))
        x_bound = r*np.cos(a.yaw[bound[0]:bound[1]])
        y_bound = r*np.sin(a.yaw[bound[0]:bound[1]])
        mag_plot.plot([x_bound[0]], [y_bound[0]], symbolBrush=(255,0,0), symbolPen='w')
        mag_plot.plot([x_bound[-1]], [y_bound[-1]], symbolBrush=(0,0,255), symbolPen='w')
        mag_plot.plot(x_bound, y_bound, pen=(255,255,255,200))
     
    # ================
    # Update ROI with user input
    # ================ 
    def updateRegion():
        lr.setRegion(zoom_plot.getViewBox().viewRange()[0])
     
    # ================
    # Update Plots with User Scroll-Zoom
    # ================  
    def mouseMoved(evt):
        pos = evt[0]  ## using signal proxy turns original arguments into a tuple
        if mag_plot.sceneBoundingRect().contains(pos):
            mousePoint = vb.mapSceneToView(pos)
            index = int(mousePoint.x())
            if index > 0 and index < len(a.yaw):
                label.setText("<span style='font-size: 12pt'>x=%0.1f,   <span style='color: red'>y1=%0.1f</span>,   <span style='color: green'>y2=%0.1f</span>" % (mousePoint.x(), a.yaw[index], a.norm_a_cal[index]))
            vLine.setPos(mousePoint.x())
            hLine.setPos(mousePoint.y())

    # ================
    # Connect everything
    # ================     
    lr.sigRegionChanged.connect(updatePlot)
    proxy = pg.SignalProxy(tot_plot.scene().sigMouseMoved, rateLimit=60, slot=mouseMoved)
    zoom_plot.sigXRangeChanged.connect(updateRegion)
    accel_plot.sigXRangeChanged.connect(updateRegion)
    updatePlot()
    exit