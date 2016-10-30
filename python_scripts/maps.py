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
    files = glob.glob('../temp/MD_????_??.png')
    for file in files:
        img = Image.open(file)
        draw = ImageDraw.Draw(img)
        font1 = ImageFont.truetype('../temp/ABeeZee-Regular.otf', 24)
        font2 = ImageFont.truetype('../temp/ABeeZee-Regular.otf', 18)
        fname, fext = os.path.basename(file).split('.')
        
        draw.text((20, 700),fname,(0,0,0),font=font1)
        draw.text((900, 40),'Median prices of sold homes (quartiles)',(0,0,0),font=font2)
        img.save('../temp/'+fname+'_corrected.png')
        
            
def makemovie():
    """
    NAME:
        makemovie
    PURPOSE:
        Make pngs into a movie
    """
    os.system('ffmpeg -y -pattern_type glob -i "../temp/*_corrected.png" -filter:v "setpts=15.0*PTS" ../images/housing.m4v')
    
def usmaps(month='1996_06'):
    """
    NAME:
        usmaps
    PURPOSE:
        Uses folium to make interactive map with data for the US (each state average of 
        median sold houses, removing those with no sold houses).
        Makes an html page and then uses selenium to take a screenshot
    INPUTS:
        month - month to use in YYYY_MM format
    """
    
    # Get pandas dataframe
    ush = sql_functions.ushouse(month=month)
    stateabbr = sql_functions.stateabbr()
    # Only grab relevant columns (toss any zip codes where there were no sold houses)
    data = ush[['state','avg_house']]
    
    # Read in geo_json files for state
    json_path = '../topo_files/us.json'
    gdf = gpd.read_file(json_path)
    
    # Geojson file only has full state name, so merge to get state abbreviations
    statemerge = gdf.merge(stateabbr, left_on='NAME', right_on='state_name')
    statemerge = statemerge[['geometry', 'state_abbv']]
    
    # Merge data on zip codes (keep the geometry, zip code, and sold house info)
    # this is because folium doesn't work well if there is extraneous information in
    # the geo_json file
    merged = statemerge.merge(data, left_on='state_abbv', right_on='state')
    spatial_gdf = gpd.GeoDataFrame(merged.iloc[:, [0, 2]])
    data_f = merged.iloc[:, [0,2,3]]
    geo_str = spatial_gdf.to_json()


    # Center on a city and choose map style
    map = folium.Map(location=[39.833, -97.0], zoom_start=5)
    folium.TileLayer('cartodbpositron').add_to(map)
    
    # Set threshold scales to be quantiles
    min_val = data['avg_house'].min()
    q1 = data['avg_house'].quantile( .25)
    q2 = data['avg_house'].quantile( .5)
    q3 = data['avg_house'].quantile( .75)
    
    # Make choropleth maps
    map.choropleth(geo_str=geo_str,
              data=data_f,
              columns=['state','avg_house'],
              fill_color='YlOrRd',
              key_on='feature.properties.state',
              threshold_scale=[min_val, q1, q2, q3],
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
    browser.set_window_position(0, 0)
    browser.set_window_size(1500, 1000)
    browser.get(tmpurl)
    #Give the map tiles some time to load
    time.sleep(delay)
    browser.save_screenshot('../temp/US'+month+'.png')
    browser.quit()
    
def thenandnow():
    """
    NAME:
        thenandnow
    PURPOSE:
        Add labels to png images to make more easily understood image
    """

    images = map(Image.open, ['../temp/US1996_06.png', '../temp/US2016_06.png'])
    widths, heights = zip(*(i.size for i in images))

    total_width = sum(widths)
    max_height = max(heights)

    new_im = Image.new('RGB', (total_width, max_height))

    font1 = ImageFont.truetype('../temp/ABeeZee-Regular.otf', 24)
    font2 = ImageFont.truetype('../temp/ABeeZee-Regular.otf', 18)

    x_offset = 0
    for im in images:
        new_im.paste(im, (x_offset,0))
        x_offset += im.size[0]
        
    draw = ImageDraw.Draw(new_im)    
    draw.text((20, 800),'1996_06',(0,0,0),font=font1)
    draw.text((1010, 40),'Average of median sold home prices for state (quartiles)',(0,0,0),font=font2)
    
    draw.text((1520, 800),'2016_06',(0,0,0),font=font1)
    draw.text((2510, 40),'Average of median sold home prices for state (quartiles)',(0,0,0),font=font2)

    new_im.save('../images/UShouses_thenandnow.png')
      