# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 11:56:02 2017

@author: Von P. Walden, Washington State University
"""
import pandas   as     pd
import numpy    as     np
from   datetime import datetime, timedelta

def acquireAqnetSensorData(API_key, mowr_ID, start_time, end_time):
    import os
    import json
    import pytz

    # Obtained this nifty function from https://stackoverflow.com/questions/19774709/use-python-to-find-out-if-a-timezone-currently-in-daylight-savings-time    
    def is_dst(zonename):
      tz = pytz.timezone(zonename)
      now = pytz.utc.localize(datetime.utcnow())
      return now.astimezone(tz).dst() != timedelta(0)

    # !! NOTE THAT the start and end times of the query must be in UTC. !!
    os.system('curl -s -H "API-TOKEN-BEARER: ' + API_key + '" "gateway.itronsensors.com/API/data" -d "format=RAW" -d "device_id="' + str(mowr_ID) + ' -d "start=' + start_time + '" -d "end=' + end_time + '" > tmp.json');
    
    with open('tmp.json') as data_file:    
        raw = json.load(data_file)
    
    os.system('rm tmp.json')
    
    df = pd.DataFrame(raw)
    
    # Create a dictionary of pandas Series that contain the sensor data variables.
    #      Variables are accessed according by key.
    aq = {}
    for i in list(range(len(df))):
        arr       = np.array(df.iloc[i]['data'])
        if(len(arr)==0): continue   # Nicely handles variables with missing data.
        ind       = np.where(np.char.find(arr[:,1], 'Connection closed by')==-1)[0]
        # Conversion from UTC to Pacific
        if is_dst('US/Pacific'):
          dtime = pd.Timedelta('7 hours')
        else:
          dtime = pd.Timedelta('8 hours')
        time = pd.to_datetime([a for a in arr[ind,0].astype('int')], unit='s') - dtime
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
        with open('html/sensor' + str(mowr_ID) + '.html','w') as html_file:
            html_file.write('<html>')
            html_file.write('    <body>')
            html_file.write('        <title>!! WARNING !!</title>')
            html_file.write('        <text>WARNING: Data is missing for AQnet unit.</text>')
            html_file.write('    </body>')
            html_file.write('</html>')
        html_file.close()
        return
    
    ####  TEMPERATURES    
    
    p1 = figure(plot_width=700,plot_height=300,x_axis_type='datetime',title='Unit: ' + str(mowr_ID) + ' - Sensor Temperatures (Preliminary, Uncalibrated Data)')
    p1.scatter(aq['bmp280_T']['data'].index,aq['bmp280_T']['data'],legend='Enclosure',color='red')
    p1.scatter(aq['htu21d_T']['data'].index,aq['htu21d_T']['data'],legend='Outside Air',color='blue')
    tab1 = Panel(child=p1, title="Temperature")
    
    ####  BAROMETRIC PRESSURE
    p2 = figure(plot_width=700,plot_height=300,x_axis_type='datetime',title='Unit: ' + str(mowr_ID) + ' - Sensor Pressure (Preliminary, Uncalibrated Data)')
    p2.scatter(aq['bmp280_P']['data'].index,aq['bmp280_P']['data'],color='cyan')
    tab2 = Panel(child=p2, title="Pressure")
    
    ####  CARBON DIOXIDE
    p3 = figure(plot_width=700,plot_height=300,x_axis_type='datetime',title='Unit: ' + str(mowr_ID) + ' - Carbon Dioxide (Preliminary, Uncalibrated Data)')
    p3.scatter(aq['k30_CO2']['data'].index,aq['k30_CO2']['data'],color='green')
    tab3 = Panel(child=p3, title="Carbon Dioxide")
    
    ####  PM1, PM2.5 and PM10
    # PM1.0
    p4 = figure(plot_width=700,plot_height=300,x_axis_type='datetime',title='Unit: ' + str(mowr_ID) + ' - PM1.0 (Preliminary, Uncalibrated Data)')
    p4.scatter(aq['opcn2_PM1']['data'].index,aq['opcn2_PM1']['data'],color='blue')
    tab4 = Panel(child=p4, title="PM1.0")
    # PM2.5
    p5 = figure(plot_width=700,plot_height=300,x_axis_type='datetime',title='Unit: ' + str(mowr_ID) + ' - PM2.5 (Preliminary, Uncalibrated Data)')
    p5.scatter(aq['opcn2_PM2.5']['data'].index,aq['opcn2_PM2.5']['data'],color='green')
    tab5 = Panel(child=p5, title="PM2.5")
    # PM10
    p6 = figure(plot_width=700,plot_height=300,x_axis_type='datetime',title='Unit: ' + str(mowr_ID) + ' - PM10 (Preliminary, Uncalibrated Data)')
    p6.scatter(aq['opcn2_PM10']['data'].index,aq['opcn2_PM10']['data'],color='red')
    tab6 = Panel(child=p6, title="PM10")
    
    ####  CREATE BOKEH HTML PLOT
    tabs = Tabs(tabs=[tab1, tab2, tab3, tab4, tab5, tab6])
    save(tabs, 'html/sensor' + str(mowr_ID) + '.html')    

    return

def mapAqnetSensorData():
    import folium
    
    # Coordinates estimated using map from Mike Diedesch and QGIS.
    streetLightLocation   = [[47.66964,-117.40315],
                             [47.65717,-117.41025],
                             [47.65449,-117.39002]]
    referenceSiteLocation =  [47.66081,-117.40446]
    
    # Center map on the Spokane Academic Center (SAC); coordinates obtained from QGIS.
    m = folium.Map([47.66141,-117.40579], zoom_start=15)
    
    html221=open('html/sensor221.html').read()
    html223=open('html/sensor223.html').read()
    html224=open('html/sensor224.html').read()
    
    iframe221 = folium.IFrame(html=html221, width=800, height=450)
    iframe223 = folium.IFrame(html=html223, width=800, height=450)
    iframe224 = folium.IFrame(html=html224, width=800, height=450)
    popup0 = folium.Popup(iframe221, max_width=1000)
    popup1 = folium.Popup(iframe223, max_width=1000)
    popup2 = folium.Popup(iframe224, max_width=1000)
    
    folium.Marker(streetLightLocation[0], popup=popup0,           icon=folium.Icon(color='green',icon='info-sign')).add_to(m)
    folium.Marker(streetLightLocation[1], popup=popup1,           icon=folium.Icon(color='green',icon='info-sign')).add_to(m)
    folium.Marker(streetLightLocation[2], popup=popup2,           icon=folium.Icon(color='green',icon='info-sign')).add_to(m)
    folium.Marker(referenceSiteLocation , popup='Reference Site', icon=folium.Icon(color='blue' ,icon='info-sign')).add_to(m)

    m.save('html/AQnetMap.html')
    
    return

def saveAqnetSensorData(filename, API_key, mowr_ID, start_time, end_time):
    """
    Reads in Aqnet data and saves data variables in CSV file.
    These data are averaged into 2-minute averages to eliminate gaps in the time series.
    
        Written by Von P. Walden
        Washington State University
        27 April 2017
    """
    aq, tdf = acquireAqnetSensorData(API_key, mowr_ID, start_time, end_time)
    
    # Currently only outputs T, U, P, CO2, PM2.5, and dB.
    df = pd.concat([aq['htu21d_T']['data'], aq['htu21d_RH']['data'], aq['bmp280_P']['data'], aq['k30_CO2']['data'], aq['opcn2_PM2.5']['data'], aq['dB']['data'] ], axis=1)
    df = df.resample('2T').mean()
    df.columns = ['Air Temperature (C)', 'Relative Humidity (%)', 'Pressure (mb)', 'CO2 (ppmv)', 'PM2.5 (ug/m^3)', 'dB']
    df.index.name = 'Datetime'
    df.to_csv(filename)
    
    return

def saveWeeklyAqnetSensorData(end_time):
    """
    Reads in Aqnet data FOR THE PREVIOUS WEEK and generates HTML graphics.
    
    Input:
        end_time - local time for end of week (typically Monday at 00:00:00)
    
        Written by Von P. Walden
        Washington State University
        2 May 2017
    """
    import pytz
    from bokeh.plotting import figure, save, output_file
    from bokeh.layouts  import column
    from bokeh.models   import Range1d, HoverTool
    
    # IMPORTANT: Currently ignoring all Python warnings.
    #            This is done to avoid a couple of Bokeh warnings related to saving html output.
    import warnings
    warnings.filterwarnings('ignore')
    
    utc   = pytz.timezone('UTC')
    etime = datetime.strptime(end_time,'%Y-%m-%d %H:%M:%S').astimezone(utc)
    btime = etime - timedelta(weeks=1)
    btime = btime.strftime('%Y-%m-%d %H:%M:%S')
    etime = etime.strftime('%Y-%m-%d %H:%M:%S')
    # Acquire data from Itron cloud.
    aq221,df221 = acquireAqnetSensorData(221,btime, etime)
    aq223,df223 = acquireAqnetSensorData(223,btime, etime)
    aq224,df224 = acquireAqnetSensorData(224,btime, etime)
    
    # Met
    t = figure(plot_width=1200,
               plot_height=400,
               x_axis_type ='datetime',
               x_axis_label='Date (local)',
               y_axis_label='Temperature (C)',
               title='Weather Measurements for week of ' + btime[0:10] + ' to ' + etime[0:10] + ' (Preliminary, Uncalibrated Data)')
    t.line(aq221['htu21d_T']['data'].index, aq221['htu21d_T']['data'],color='blue',  legend='North')
    t.line(aq223['htu21d_T']['data'].index, aq223['htu21d_T']['data'],color='purple',legend='Southwest')
    t.line(aq224['htu21d_T']['data'].index, aq224['htu21d_T']['data'],color='orange',legend='Southeast')
    t.add_tools(HoverTool())
    
    u = figure(plot_width=1200,
               plot_height=400,
               x_axis_type ='datetime',
               x_axis_label='Date (local)',
               y_axis_label='Relative Humidity (%)',
               x_range=t.x_range)
    u.line(aq221['htu21d_RH']['data'].index, aq221['htu21d_RH']['data'],color='blue',  legend='North')
    u.line(aq223['htu21d_RH']['data'].index, aq223['htu21d_RH']['data'],color='purple',legend='Southwest')
    u.line(aq224['htu21d_RH']['data'].index, aq224['htu21d_RH']['data'],color='orange',legend='Southeast')
    u.add_tools(HoverTool())
    
    p = figure(plot_width=1200,
               plot_height=400,
               x_axis_type ='datetime',
               x_axis_label='Date (local)',
               y_axis_label='Pressure (mb)',
               x_range=t.x_range)
    p.line(aq221['bmp280_P']['data'].index, aq221['bmp280_P']['data'],color='blue',  legend='North')
    p.line(aq223['bmp280_P']['data'].index, aq223['bmp280_P']['data'],color='purple',legend='Southwest')
    p.line(aq224['bmp280_P']['data'].index, aq224['bmp280_P']['data'],color='orange',legend='Southeast')
    p.add_tools(HoverTool())

    p = column(t,u,p)
    
    output_file('html/UrbanovaWeekly_Met_' + btime[0:10] + '_' + etime[0:10] + '.html',
                title='Weather Measurements for week of ' + btime[0:10] + ' to ' + etime[0:10])
    save(p)
    
    # CO2
    p = figure(plot_width=1200,
               plot_height=600,
               x_axis_type ='datetime',
               x_axis_label='Date (local)',
               y_axis_label='CO2 concentration (ppmv)',
               title='CO2 Measurements for week of ' + btime[0:10] + ' to ' + etime[0:10] + ' (Preliminary, Uncalibrated Data)')
    p.line(aq221['k30_CO2']['data'].index, aq221['k30_CO2']['data'],color='blue',  legend='North')
    p.line(aq223['k30_CO2']['data'].index, aq223['k30_CO2']['data'],color='purple',legend='Southwest')
    p.line(aq224['k30_CO2']['data'].index, aq224['k30_CO2']['data'],color='orange',legend='Southeast')
    p.add_tools(HoverTool())
    output_file('html/UrbanovaWeekly_CO2_' + btime[0:10] + '_' + etime[0:10] + '.html',
                title='CO2 Measurements for week of ' + btime[0:10] + ' to ' + etime[0:10])
    save(p)
    
    # PM2.5
    p1 = figure(plot_width=1200,
               plot_height=400,
               x_axis_type ='datetime',
               x_axis_label='Date (local)',
               y_axis_label='PM2.5 concentration (ug/m^3)',
               title='PM2.5 Measurements for week of ' + btime[0:10] + ' to ' + etime[0:10] + ' (Preliminary, Uncalibrated Data)')
    p1.line(aq221['opcn2_PM2.5']['data'].index, aq221['opcn2_PM2.5']['data'],   color='blue',  legend='North')
    p1.y_range = Range1d(0, 30)
    p1.add_tools(HoverTool())
    p2 = figure(plot_width=1200,
               plot_height=400,
               x_axis_type ='datetime',
               x_axis_label='Date (local)',
               y_axis_label='PM2.5 concentration (ug/m^3)',
               x_range=p1.x_range,
               y_range=p1.y_range)
    p2.line(aq223['opcn2_PM2.5']['data'].index, aq223['opcn2_PM2.5']['data'],   color='purple',legend='Southwest')
    p2.add_tools(HoverTool())
    p3 = figure(plot_width=1200,
               plot_height=400,
               x_axis_type ='datetime',
               x_axis_label='Date (local)',
               y_axis_label='PM2.5 concentration (ug/m^3)',
               x_range=p1.x_range,
               y_range=p1.y_range)
    p3.line(aq224['opcn2_PM2.5']['data'].index, aq224['opcn2_PM2.5']['data'],color='orange',legend='Southeast')
    p3.add_tools(HoverTool())
    
    p = column(p1,p2,p3)
    
    output_file('html/UrbanovaWeekly_PM2.5_' + btime[0:10] + '_' + etime[0:10] + '.html',
                title='PM2.5 Measurements for week of ' + btime[0:10] + ' to ' + etime[0:10])
    save(p)
    
    # dB
    p1 = figure(plot_width=1200,
               plot_height=400,
               x_axis_type ='datetime',
               x_axis_label='Date (local)',
               y_axis_label='dB',
               title='Audio Measurements for week of ' + btime[0:10] + ' to ' + etime[0:10] + ' (Preliminary, Uncalibrated Data)')
    p1.line(aq221['dB']['data'].index, aq221['dB']['data'],   color='blue',  legend='North')
    p1.add_tools(HoverTool())
    p2 = figure(plot_width=1200,
               plot_height=400,
               x_axis_type ='datetime',
               x_axis_label='Date (local)',
               y_axis_label='dB',
               x_range=p1.x_range,
               y_range=p1.y_range)
    p2.line(aq223['dB']['data'].index, aq223['dB']['data'],color='purple',legend='Southwest')
    p2.add_tools(HoverTool())
    p3 = figure(plot_width=1200,
               plot_height=400,
               x_axis_type ='datetime',
               x_axis_label='Date (local)',
               y_axis_label='dB',
               x_range=p1.x_range,
               y_range=p1.y_range)
    p3.line(aq224['dB']['data'].index, aq224['dB']['data'],color='orange',legend='Southeast')
    p3.add_tools(HoverTool())
    
    p = column(p1,p2,p3)
    
    output_file('html/UrbanovaWeekly_dB_' + btime[0:10] + '_' + etime[0:10] + '.html',
                title='Audio Measurements for week of ' + btime[0:10] + ' to ' + etime[0:10])
    save(p)
    
    return
