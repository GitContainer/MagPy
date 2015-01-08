# -*- coding: utf-8 -*-
"""
Created on Wed Jan  7 12:53:09 2015

@author: Dan
"""

import MagPy as mp
import pyqtgraph as pg
import numpy as np
import csv

filename = 'MagJumps'
filetype = '.csv'
filepath = '/Users/Dan/Desktop/'
delimiter = ','
a = mp.MagPy(filename + filetype, filepath, delimiter)

# ================
# Write processed data to file
# ================import csv
with open(filepath +  filename + '_tilt_compensated' + filetype, 'wb') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=delimiter,
                            quotechar=';', quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow([';count', 'accl_x', 'accel_y', 'accel_z', 
                         'mag_x', 'mag_y', 'mag_z', 
                         'accel_cal_norm', 'tilt-comp_compass'])
    for i in range(len(a.norm_a_cal)):
        spamwriter.writerow([i, a.ax[i], a.ay[i], a.az[i], a.mx[i], a.my[i], a.mz[i], a.norm_a_cal[i], np.rad2deg(a.yaw[i] + np.pi)])
    csvfile.close()


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