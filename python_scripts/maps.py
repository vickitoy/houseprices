import folium
import sys
import pandas as pd
import geopandas as gpd
import sql_functions
import sys
import re
import os
import subprocess
import time
import glob
from selenium import webdriver
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw

def statemaps(month='1996_06', state='MD'):
    """
    NAME:
        statemaps
    PURPOSE:
        Uses folium to make interactive map with data for a single state broken up based 
        on zip code overlaid. Makes an html page and then uses selenium to take a screenshot
    INPUTS:
        month - month to use in YYYY_MM format
        state - state abbreviation code to use
    """

    # Check to see if month is in the right format and that it is included in our dataset
    if not re.match("\d\d\d\d_\d\d", month):
        sys.exit('Invalid format. Month should be in format YYYY_MM')

    testyear, testmonth = month.split('_') 
    if int(testyear) not in range(1996, 2017):
        sys.exit('Data does not exist for '+testyear)
    
    if int(testmonth) not in range(1,13):
        sys.exit('Invalid format. Month should be in format YYYY_MM')
    
    if (int(testyear) == 1996 and int(testmonth) < 6) or (int(testyear) == 2016 and int(testmonth) > 6):
        sys.exit('Data does not exist for ' + month)
    
    # Check to see that we have JSON data for state
    if not os.path.isfile('../topo_files/'+state+'_zip.json'):
        sys.exit('State geo_json file does not exist for '+state) 
    
    # Get pandas dataframe
    sh = sql_functions.statehouse()
    
    # Only grab relevant columns (toss any zip codes where there were no sold houses)
    data = sh[['regionName',month]]
    data = data[data[month] > 0]
    
    # Read in geo_json files for state
    json_path = '../topo_files/'+state+'_zip.json'
    gdf = gpd.read_file(json_path)
    
    # Merge data on zip codes (keep the geometry, zip code, and sold house info)
    # this is because folium doesn't work well if there is extraneous information in
    # the geo_json file
    merged = gdf.merge(data, left_on='ZCTA5CE10', right_on='regionName')
    merged.iloc[:,[11,12]].head()
    spatial_gdf = gpd.GeoDataFrame(merged.iloc[:, [11, 12]])
    data_f = merged.iloc[:, [11,12,13]]
    geo_str = spatial_gdf.to_json()
    
    # Center on a city and choose map style
    map = folium.Map(location=[38.9784, -76.4922], zoom_start=9)
    folium.TileLayer('cartodbpositron').add_to(map)
    
    # Set threshold scales to be quantiles
    min_val = data[month].min()
    q1 = data[month].quantile( .25)
    q2 = data[month].quantile( .5)
    q3 = data[month].quantile( .75)

    # Make choropleth maps
    map.choropleth(geo_str=geo_str,
              data=data_f,
              columns=['regionName', month],
              fill_color='YlOrRd',
              key_on='feature.properties.regionName',
              threshold_scale=[min_val, q1, q2, q3],
              legend_name='Median of Sold Houses',
              reset=True)
    #map.save('../temp/'+state+'_'+month+'.html')

    # Sets driver for Firefox
    os.environ["PATH"] += ":/Users/vickitoy/research/ind_exe/geckodriver"

    # Save map and read it in a browser (need time delay so map can load) and save
    # screenshot of browser as png
    delay=5
    fn='testmap.html'
    tmpurl='file://{path}/{mapfile}'.format(path=os.getcwd(),mapfile=fn)
    map.save(fn)

    browser = webdriver.Firefox()
    browser.get(tmpurl)
    #Give the map tiles some time to load
    time.sleep(delay)
    browser.save_screenshot('../temp/'+state+'_'+month+'.png')
    browser.quit()
    
def allstatemaps(state='MD'):
    """
    NAME:
        allstatemaps
    PURPOSE:
        Make overlaid maps saved as png for every month available (20 years spaced at
        1 month intervals) for a specific state
    INPUT:
        state - state abbreviation to use
    """
    for iyear in range(1996,2017):
        for imonth in range(1,13):
            if (iyear == 1996 and imonth < 6): continue
            if (iyear == 2016 and imonth > 6): continue
            
            month = str(iyear)+'_'+str(imonth).zfill(2) 
            print month          
            statemaps(month=month, state='MD')

def addmaplabel():
    """
    NAME:
        addmaplabel
    PURPOSE:
        Add labels to png images to make more easily understood image
    """
    files = glob.glob('../temp/MD_1996_06.png')
    for file in files:
        print file
        img = Image.open(file)
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype('../temp/ABeeZee-Regular.otf', 24)
        print file.split('.')
        fname, fext = os.path.basename(file).split('.')
        
        draw.text((20, 700),fname,(0,0,0),font=font)
        draw.text((20, 700),fname,(0,0,0),font=font)
        img.save('test.png')
        
            
def makemovie():
    """
    NAME:
        makemovie
    PURPOSE:
        Make pngs into a movie
    """
    os.system('ffmpeg -y -pattern_type glob -i "../temp/*.png" -filter:v "setpts=20.0*PTS" ../temp/out.m4v')