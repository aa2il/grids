#! /usr/bin/python3
################################################################################
#
# grids.py - Rev 1.0 - Depricated
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# GUI to plot confirmed 6m & Satellite states & grids.
# This version is being depricated in favor of a new version that uses cartopy.
# It is being kept around for posterity.
#
# Notes:
#    Linux:
#          pip install pyhamtools
#    Windoz:
#          pip install xlrd unidecode pyhamtools serial
#
################################################################################
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
################################################################################

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import xlrd
import sys
import os
from unidecode import unidecode
import argparse
from pprint import pprint

import mpl_toolkits
mpl_toolkits.__path__.append('/usr/lib/python2.7/dist-packages/mpl_toolkits/')
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from datetime import timedelta,datetime

from pyhamtools.locator import locator_to_latlong
from settings import *

################################################################################

# User params
ATOLL_CUTOFF = 0.005
US_ONLY=False
#US_ONLY=True

################################################################################

# Structure to contain processing params
class PARAMS:
    def __init__(self):

        # Process command line args
        # Can add required=True to anything that is required
        arg_proc = argparse.ArgumentParser()
        arg_proc.add_argument('-sat', action='store_true',help='Satellites Confirmed')
        arg_proc.add_argument('-sat_all', action='store_true',help='Satellites All')
        args = arg_proc.parse_args()

        self.SAT  = args.sat
        self.SAT2 = args.sat_all
        if self.SAT:
            self.offset=0
            self.states_offset=0
        elif self.SAT2:
            self.offset=0
            self.states_offset=0
        else:
            self.offset=0
            self.states_offset=0

        self.SETTINGS,junk = read_settings('.keyerrc')
            
################################################################################

print("\n\n***********************************************************************************")
print("\nStarting Grid Plotter  ...")
P=PARAMS()
print("\nP=",end=' ')
#print "\nP=",
pprint(vars(P))

if P.SAT or P.SAT2:
    band='Satellites'
else:
    band='6-meters'

# Read XLS format spreadsheet and pull out sheet with confirmation data
MY_CALL = P.SETTINGS['MY_CALL'].replace('/','_')
print('MY_CALL=',MY_CALL)
fname = os.path.expanduser('~/'+MY_CALL+'/states.xls')
print('fname=',fname)
book  = xlrd.open_workbook(fname,formatting_info=True)
sheet1 = book.sheet_by_name(band)

# Digest confirmed states
states=[]
for i in range(1, sheet1.nrows):
    #print(i,sheet1.cell(i, P.states_offset) )
    state = unidecode( sheet1.cell(i, P.states_offset).value )
    if len(state)>0 and 'Paper' not in state:
        a=state.split('(')
        states.append( a[0].strip() )
print('States:',states,len(states))

# Digest confirmed grids
grids=[]
for i in range(1, sheet1.nrows):
    grid = unidecode( sheet1.cell(i, 3+P.offset).value )
    if len(grid)>0 and 'Paper' not in grid:
        grids.append( grid.upper() )
grids.sort()
print('Grids:',grids,len(grids))
#sys.exit(0)

################################################################################

# Create the map
if US_ONLY:
    m = Basemap(llcrnrlon=-121,llcrnrlat=20,urcrnrlon=-62,urcrnrlat=51,
                projection='lcc',lat_1=32,lat_2=45,lon_0=-95)
elif 0:
    m = Basemap(llcrnrlon=-120.,llcrnrlat=20.,urcrnrlon=-62.,urcrnrlat=51.,\
            rsphere=(6378137.00,6356752.3142),\
            resolution='l',projection='merc',\
            lat_0=40.,lon_0=-20.,lat_ts=20.)
elif 0:
    #m = Basemap(projection='mill',lon_0=180)
    #m = Basemap(llcrnrlon=-171,llcrnrlat=10,urcrnrlon=-62,urcrnrlat=61,resolution='c',
    #            projection='mill',lat_1=32,lat_2=45,lon_0=-95)
    m = Basemap(width=1.1*6000000,height=2*4500000,resolution='c',
                projection='mill',lat_1=35.,lat_2=45,
                lon_0=-100,lat_0=40)
else:
    m = Basemap(width=1.1*12000000,height=2*4500000,resolution='c',
                projection='aea',lat_1=35.,lat_2=50,
                lon_0=-130,lat_0=40)
#    m = Basemap(width=1.1*12000000,height=2*4500000,resolution='c',
#                projection='aea',lat_1=35.,lat_2=45,
#                lon_0=-100,lat_0=40)
#    m = Basemap(width=1.1*6000000,height=2*4500000,resolution='c',
#                projection='aea',lat_1=35.,lat_2=45,
#                lon_0=-100,lat_0=40)
#    m = Basemap(llcrnrlon=-131,llcrnrlat=-10,urcrnrlon=-60,urcrnrlat=70,
#                projection='aea',lat_1=32,lat_2=45,lon_0=-95)
    m.drawcoastlines(linewidth=0.5)
    #m.fillcontinents(color='tan',lake_color='lightblue')

    # draw parallels and meridians.
    m.drawparallels(np.arange(-90.,91.,15.),labels=[True,True,False,False],dashes=[2,2])
    m.drawmeridians(np.arange(-180.,181.,15.),labels=[False,False,False,True],dashes=[2,2])
    m.drawmapboundary(fill_color='lightblue')
    try:
        m.drawcountries(linewidth=2, linestyle='solid', color='k' ) 
        m.drawstates(linewidth=0.5, linestyle='solid', color='k')
    except:
        pass

ax = plt.gca()
DATE = datetime.now().strftime('%m/%d/%y')
MY_CALL=P.SETTINGS['MY_CALL']
ax.set_title(MY_CALL+' - '+band+' Confirmed \n States ('+str(len(states))+ \
             ') & Grids ('+str(len(grids))+') as of '+DATE)

# Load the shapefile, use the name 'states'
m.readshapefile('st99_d00', name='states', drawbounds=True)

# Plot confirmed states
for i, shapedict in enumerate(m.states_info):
    print(shapedict['NAME'])
    
    seg=None
    color='white'
    if shapedict['NAME'] in states:
        seg = m.states[int(shapedict['SHAPENUM'] - 1)]
        color='red'
        #print(shapedict['NAME'])
        #print(seg)
            
    # Translate the noncontiguous states:
    # Only include the 8 main islands of Hawaii so that we don't put dots in the western states.
    if US_ONLY and shapedict['NAME'] == 'Hawaii' and float(shapedict['AREA']) > ATOLL_CUTOFF:
        if not seg:
            seg = m.states[int(shapedict['SHAPENUM'] - 1)]
        seg = list(map( lambda x,y : (x + 5200000, y-1400000), seg))
                    
    # Alaska is large - rescale it
    elif US_ONLY and shapedict['NAME'] == 'Alaska':
        if not seg:
            seg = m.states[int(shapedict['SHAPENUM'] - 1)]
        seg = list(map(lambda x,y : (0.35*x + 1100000, 0.35*y-1300000), seg))

    if seg:
        poly = Polygon(seg, facecolor=color, edgecolor='black', linewidth=.5)
        ax.add_patch(poly)


# Plot confirmed grids
# A grid square measures 1-deg latitude by 2-deg longitude and measures approximately 70x100 miles
# in the continental US.
for grid in grids:
    try:
        lat,lon = locator_to_latlong(grid)
    except:
        print('Problem with grid',grid)
        sys.exit(0)
        
    #x,y = m(lon,lat)
    xy1 = m(lon-1,lat-0.5)
    xy2 = m(lon-1,lat+0.5)
    xy3 = m(lon+1,lat+0.5)
    xy4 = m(lon+1,lat-0.5)
    seg=[xy1,xy2,xy3,xy4]
    
    #print seg
    poly = Polygon(seg, facecolor='blue', edgecolor='black', linewidth=.5)
    ax.add_patch(poly)

plt.show()
