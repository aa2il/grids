#! /usr/bin/python3
################################################################################
#
# grids.py - Rev 2.0
# Copyright (C) 2021-2 by Joseph B. Attili, aa2il AT arrl DOT net
#
# GUI to plot confirmed 6m & Satellite states & grids.
# New version to use cartopy instead of basemap.
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
import xlrd
import sys
import os
from unidecode import unidecode
import argparse
from pprint import pprint

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import matplotlib.patches as mpatches
import cartopy.io.shapereader as shpreader
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from shapely import geometry

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
        args = arg_proc.parse_args()

        self.SAT  = args.sat

        self.SETTINGS,junk = read_settings('.keyerrc')
            
################################################################################


print("\n\n***********************************************************************************")
print("\nStarting Grid Plotter  ...")
P=PARAMS()
print("\nP=",end=' ')
#print "\nP=",
pprint(vars(P))

# Init
DATE = datetime.now().strftime('%m/%d/%y')
MY_CALL=P.SETTINGS['MY_CALL']
if P.SAT:
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
confirmed_states=[]
for i in range(1, sheet1.nrows):
    state = unidecode( sheet1.cell(i,0).value )
    if len(state)>0 and 'Paper' not in state:
        a=state.split('(')
        confirmed_states.append( a[0].strip() )
print('Confirmed States:',confirmed_states,len(confirmed_states))

# Digest confirmed grids
grids=[]
for i in range(1, sheet1.nrows):
    grid = unidecode( sheet1.cell(i,3).value )
    if len(grid)>0 and 'Paper' not in grid:
        grids.append( grid.upper() )
grids.sort()
print('Grids:',grids,len(grids))
                      
# Digest confirmed countries
dxccs=[]
for i in range(1, sheet1.nrows):
    dxcc = unidecode( sheet1.cell(i,6).value )
    if len(dxcc)>0 and 'Paper' not in dxcc:
        dxccs.append( dxcc.upper() )
dxccs.sort()
print('DXCCs:',dxccs,len(dxccs))
#sys.exit(0)

################################################################################

# Create the map
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1,
                     projection=ccrs.PlateCarree(central_longitude=-75))

# Put a background image on for nice sea rendering.
ax.stock_img()

# Create a feature for States/Admin 1 regions at 1:50m from Natural Earth
states_provinces = cfeature.NaturalEarthFeature(
    category='cultural',
    name='admin_1_states_provinces_lines',
    scale='50m',
    facecolor='none')

# Add boundaries
#ax.add_feature(cfeature.OCEAN)
ax.add_feature(cfeature.LAND)
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.BORDERS)
ax.add_feature(states_provinces, edgecolor='gray')

ax.set_title(MY_CALL+' - '+band + \
             ' Confirmed \n DXCCs ('+str(len(dxccs)) + \
             '), States ('+str(len(confirmed_states))+ \
             ') & Grids ('+str(len(grids))+') as of '+DATE)

# Read country and state shape data
shpfilename = shpreader.natural_earth(resolution='110m',
                                      category='cultural',
                                      name='admin_0_countries')
countries = shpreader.Reader(shpfilename).records()

shpfilename = shpreader.natural_earth(resolution='110m',
                                      category='cultural',
                                      name='admin_1_states_provinces_lakes')

states = shpreader.Reader(shpfilename).records()

# Plot confirmed countries
for country in countries:
    name=country.attributes['NAME_LONG'].replace('\0',' ').strip().upper()
    #print(name,len(name))
    #print(country.geometry)
    if name in dxccs:
        print(name)
        try:
            ax.add_geometries(country.geometry,
                              ccrs.PlateCarree(),
                              facecolor='red' ,alpha=0.5)
        except Exception as e: 
            print(e)
            print('Problem drawing country - Oh well')

# Plot confirmed states
for state in states:
    name = state.attributes['name'].replace('\0',' ').strip()
    if name in confirmed_states:
        try:
            ax.add_geometries(state.geometry, ccrs.PlateCarree(),
                              facecolor='red',
                              edgecolor='#FFFFFF',
                              linewidth=.25)
        except Exception as e: 
            print(e)
            print('Problem drawing state - name=',name)


# Plot confirmed grids
for grid in grids:
    try:
        lat,lon = locator_to_latlong(grid)
    except:
        print('Problem with grid',grid)
        sys.exit(0)

    geom = geometry.box(minx=lon-1,maxx=lon+1,
                        miny=lat-0.5,maxy=lat+0.5)
    ax.add_geometries([geom], ccrs.PlateCarree(),
                          facecolor='blue',
                          edgecolor='#FFFFFF',
                          linewidth=.25)
    
plt.show()
