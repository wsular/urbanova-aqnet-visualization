# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 11:56:02 2017

@author: Von P. Walden, Washington State University
"""
import pandas   as     pd
import numpy    as     np
from   datetime import datetime

def acquireAqnetSensorData(mowr_ID, start_time, end_time):
    import os
    import json
    
    # !! NOTE THAT the start and end times of the query must be in UTC. !!
    os.system('curl -s -H "API-TOKEN-BEARER: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" "gateway.itronsensors.com/API/data" -d "format=RAW" -d "device_id="' + str(mowr_ID) + ' -d "start=' + start_time + '" -d "end=' + end_time + '" > /Users/vonw/work/software/aqnet/data/tmp.json');
    
    with open('/Users/vonw/work/software/aqnet/data/tmp.json') as data_file:    
        raw = json.load(data_file)
    
    os.system('rm /Users/vonw/work/software/aqnet/data/tmp.json')
    
    df = pd.DataFrame(raw)
    
    # Create a dictionary of pandas Series that contain the sensor data variables.
    #      Variables are accessed according by key.
    aq = {}
    for i in list(range(len(df))):
        arr       = np.array(df.iloc[i]['data'])
        if(len(arr)==0): continue   # Nicely handles variables with missing data.
        ind       = np.where(np.char.find(arr[:,1], 'Connection closed by')==-1)[0]
        time      = [datetime.fromtimestamp(a) for a in arr[ind,0].astype('int')]
        aq[df.iloc[i]['name'][1:].replace('/','_')] = {'data': pd.Series(arr[ind,1].astype('float'), index=time)}

    return aq, df

def plotAqnetSensorData(mowr_ID, aq={}):
    from bokeh.models.widgets import Panel, Tabs
    from bokeh.plotting import figure, save
    
    # IMPORTANT: Currently ignoring all Python warnings.
    #            This is done to avoid a couple of Bokeh warnings related to saving html output.
    import warnings
    warnings.filterwarnings('ignore')
    
    # If sensor data are missing, create warning in html file.
    if(len(aq) != 49):
        with open('/Users/vonw/work/software/aqnet/data/sensor' + str(mowr_ID) + '.html','w') as html_file:
            html_file.write('<html>')
            html_file.write('    <body>')
            html_file.write('        <title>!! WARNING !!</title>')
            html_file.write('        <text>WARNING: Data is missing for AQnet unit.</text>')
            html_file.write('    </body>')
            html_file.write('</html>')
        html_file.close()
        return
    
    ####  TEMPERATURES    
    
    p1 = figure(plot_width=700,plot_height=300,x_axis_type='datetime',title='Unit: ' + str(mowr_ID) + ' - Sensor Temperatures')
    p1.scatter(aq['bmp280_T']['data'].index,aq['bmp280_T']['data'],legend='Enclosure',color='red')
    p1.scatter(aq['htu21d_T']['data'].index,aq['htu21d_T']['data'],legend='Outside Air',color='blue')
    tab1 = Panel(child=p1, title="Temperature")
    
    ####  BAROMETRIC PRESSURE
    p2 = figure(plot_width=700,plot_height=300,x_axis_type='datetime',title='Unit: ' + str(mowr_ID) + ' - Sensor Pressure')
    p2.scatter(aq['bmp280_P']['data'].index,aq['bmp280_P']['data'],color='cyan')
    tab2 = Panel(child=p2, title="Pressure")
    
    ####  CARBON DIOXIDE
    p3 = figure(plot_width=700,plot_height=300,x_axis_type='datetime',title='Unit: ' + str(mowr_ID) + ' - Carbon Dioxide')
    p3.scatter(aq['k30_CO2']['data'].index,aq['k30_CO2']['data'],color='green')
    tab3 = Panel(child=p3, title="Carbon Dioxide")
    
    ####  PM1, PM2.5 and PM10
    # PM1.0
    p4 = figure(plot_width=700,plot_height=300,x_axis_type='datetime',title='Unit: ' + str(mowr_ID) + ' - PM1.0')
    p4.scatter(aq['opcn2_PM1']['data'].index,aq['opcn2_PM1']['data'],color='blue')
    tab4 = Panel(child=p4, title="PM1.0")
    # PM2.5
    p5 = figure(plot_width=700,plot_height=300,x_axis_type='datetime',title='Unit: ' + str(mowr_ID) + ' - PM2.5')
    p5.scatter(aq['opcn2_PM2.5']['data'].index,aq['opcn2_PM2.5']['data'],color='green')
    tab5 = Panel(child=p5, title="PM2.5")
    # PM10
    p6 = figure(plot_width=700,plot_height=300,x_axis_type='datetime',title='Unit: ' + str(mowr_ID) + ' - PM10')
    p6.scatter(aq['opcn2_PM10']['data'].index,aq['opcn2_PM10']['data'],color='red')
    tab6 = Panel(child=p6, title="PM10")
    
    ####  CREATE BOKEH HTML PLOT
    tabs = Tabs(tabs=[tab1, tab2, tab3, tab4, tab5, tab6])
    save(tabs, '/Users/vonw/work/software/aqnet/data/sensor' + str(mowr_ID) + '.html')    

    return

def mapAqnetSensorData():
    import folium
    
    # Coordinates estimated using map from Mike Diedesch and QGIS.
    streetLightLocation = [[47.66964,-117.40315],
                           [47.65717,-117.41025],
                           [47.65449,-117.39002]]
    
    # Center map on the Spokane Academic Center (SAC); coordinates obtained from QGIS.
    m = folium.Map([47.66141,-117.40579], zoom_start=15)
    
    html221=open('/Users/vonw/work/software/aqnet/data/sensor221.html').read()
    html223=open('/Users/vonw/work/software/aqnet/data/sensor223.html').read()
    html224=open('/Users/vonw/work/software/aqnet/data/sensor224.html').read()
    
    iframe221 = folium.IFrame(html=html221, width=800, height=450)
    iframe223 = folium.IFrame(html=html223, width=800, height=450)
    iframe224 = folium.IFrame(html=html224, width=800, height=450)
    popup0 = folium.Popup(iframe221, max_width=1000)
    popup1 = folium.Popup(iframe223, max_width=1000)
    popup2 = folium.Popup(iframe224, max_width=1000)
    
    folium.Marker(streetLightLocation[0], popup=popup0, icon=folium.Icon(color='green',icon='info-sign')).add_to(m)
    folium.Marker(streetLightLocation[1], popup=popup1, icon=folium.Icon(color='red',  icon='info-sign')).add_to(m)
    folium.Marker(streetLightLocation[2], popup=popup2, icon=folium.Icon(color='green',icon='info-sign')).add_to(m)
    
    m.save('/Users/vonw/Sites/urbanova/AQnetMap.html')
    
    return

