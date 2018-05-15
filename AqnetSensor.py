# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 11:56:02 2017

@author: Von P. Walden, Washington State University
"""
import pandas   as     pd
import numpy    as     np
import xarray   as     xr
from   datetime import datetime, timedelta

def acquireAqnetSensorData(mowr_ID, start_time, end_time):
    """This function reads (acquires) data from the Itron cloud service and 
    returns an xarray Dataset that contains all of the AQnet sensor 
    measurements. The Dataset contains a series of xarray Data Arrays that
    contain both measurement data and metadata attributes."""
    import os
    import json
    import pytz
    
    # Obtained this nifty function from https://stackoverflow.com/questions/19774709/use-python-to-find-out-if-a-timezone-currently-in-daylight-savings-time    
    def is_dst(zonename):
        tz = pytz.timezone(zonename)
        now = pytz.utc.localize(datetime.utcnow())
        return now.astimezone(tz).dst() != timedelta(0)

    # !! NOTE THAT the start and end times of the query must be in UTC. !!
    itron_cloud_token = os.environ['ITRON_CLOUD_TOKEN']
    os.system('curl -s -H "API-TOKEN-BEARER: ' + itron_cloud_token + '" "gateway.itronsensors.com/API/data" -d "format=RAW" -d "device_id=' + str(mowr_ID) + '" -d "start=' + start_time + '" -d "end=' + end_time + '" > /Users/vonw/work/software/aqnet/data/tmp.json');
    
    with open('/Users/vonw/work/software/aqnet/data/tmp.json') as data_file:    
        raw = json.load(data_file)
    
    os.system('rm /Users/vonw/work/software/aqnet/data/tmp.json')
    
    # Convert raw data into a pandas dataframe.
    df = pd.DataFrame({})
    for var in raw:
        name = var['name'][1:].replace('/','_')
        # Extract data.
        arr       = np.array(var['data'])
        if(len(arr)==0): continue   # Nicely handles variables with missing data.
        ind       = np.where(np.char.find(arr[:,1], 'Connection closed by')==-1)[0]

        # Conversion from UTC to Pacific
        if is_dst('US/Pacific'):
          dtime = pd.Timedelta('7 hours')
        else:
          dtime = pd.Timedelta('8 hours')
        time = pd.to_datetime([a for a in arr[ind,0].astype(np.int)], unit='s') - dtime
        
        # Combine into dataframe.
        df = df.combine_first(pd.DataFrame(arr[ind,1].astype(np.float), columns=[name], index=time))
        
    # Convert pandas dataframe to an xarray dataset.
    df.index.name = 'time'
    ds = xr.Dataset.from_dataframe(df)
    
    # Add global attributes.
    ds.attrs['description']       = 'These data were acquired as part of the Urbanova project in Spokane, Washington.'
    ds.attrs['contact_person']    = 'Von P. Walden, Washington State University, Laboratory for Atmospheric Research, Pullman, WA 99164-5845'
    ds.attrs['contact_email']     = 'v.walden@wsu.edu'
    ds.attrs['data_attribution']  = 'Use of these data require the user to contact Prof. Von P. Walden at Washington State University to discuss the specific use of the data and its appropriateness for the desired application.'
    ds.attrs['reference_project'] = 'Urbanova - http://urbanova.org'
    ds.attrs['date_created']      = datetime.now().strftime('%Y-%m-%d')
    
    # Add metadata for each xarray dataset variable.
    for var in raw:
        name                        = var['name'][1:].replace('/','_')
        if len(var['data']) > 0:
            ds[name].attrs['title']     = var['title']
            ds[name].attrs['tolerance'] = var['tolerance']
            ds[name].attrs['units']     = var['uom']
    
    return ds

def plotAqnetSensorData(mowr_ID, ds=xr.Dataset({})):
    from bokeh.models.widgets import Panel, Tabs
    from bokeh.plotting import figure, save
    
    # IMPORTANT: Currently ignoring all Python warnings.
    #            This is done to avoid a couple of Bokeh warnings related to saving html output.
    import warnings
    warnings.filterwarnings('ignore')
    
    # If sensor data are missing, create warning in html file.
    if(len(ds) == 1):
        with open('/Users/vonw/work/software/aqnet/data/sensor' + str(mowr_ID) + '.html','w') as html_file:
            html_file.write('<html>')
            html_file.write('    <body>')
            html_file.write('        <title>!! WARNING !!</title>')
            html_file.write('        <text>WARNING: Data are currently unavailable for AQnet unit.</text>')
            html_file.write('    </body>')
            html_file.write('</html>')
        html_file.close()
        return
    
    ####  TEMPERATURES    
    
    p1 = figure(plot_width=700,plot_height=300,x_axis_type='datetime',title='Unit: ' + str(mowr_ID) + ' - Sensor Temperatures (Preliminary, Uncalibrated Data)')
    #p1.scatter(aq['bmp280_T']['data'].index,aq['bmp280_T']['data'],legend='Enclosure',color='red')
    p1.scatter(ds.time[~np.isnan(ds['htu21d_T'])].values,ds['htu21d_T'][~np.isnan(ds['htu21d_T'])].values,legend='Outside Air',color='blue')
    tab1 = Panel(child=p1, title="Temperature")
    
    ####  BAROMETRIC PRESSURE
    p2 = figure(plot_width=700,plot_height=300,x_axis_type='datetime',title='Unit: ' + str(mowr_ID) + ' - Sensor Pressure (Preliminary, Uncalibrated Data)')
    p2.scatter(ds.time[~np.isnan(ds['bmp280_P'])].values,ds['bmp280_P'][~np.isnan(ds['bmp280_P'])].values,color='cyan')
    tab2 = Panel(child=p2, title="Pressure")
    
    ####  CARBON DIOXIDE
    p3 = figure(plot_width=700,plot_height=300,x_axis_type='datetime',title='Unit: ' + str(mowr_ID) + ' - Carbon Dioxide (Preliminary, Uncalibrated Data)')
    p3.scatter(ds.time[~np.isnan(ds['k30_CO2'])].values,ds['k30_CO2'][~np.isnan(ds['k30_CO2'])].values,color='green')
    tab3 = Panel(child=p3, title="Carbon Dioxide")
    
    ####  PM1, PM2.5 and PM10
    # PM1.0
    p4 = figure(plot_width=700,plot_height=300,x_axis_type='datetime',title='Unit: ' + str(mowr_ID) + ' - PM1.0 (Preliminary, Uncalibrated Data)')
    p4.scatter(ds.time[~np.isnan(ds['opcn2_PM1'])].values,ds['opcn2_PM1'][~np.isnan(ds['opcn2_PM1'])].values,color='blue')
    tab4 = Panel(child=p4, title="PM1.0")
    # PM2.5
    p5 = figure(plot_width=700,plot_height=300,x_axis_type='datetime',title='Unit: ' + str(mowr_ID) + ' - PM2.5 (Preliminary, Uncalibrated Data)')
    p5.scatter(ds.time[~np.isnan(ds['opcn2_PM2.5'])].values,ds['opcn2_PM2.5'][~np.isnan(ds['opcn2_PM2.5'])].values,color='green')
    tab5 = Panel(child=p5, title="PM2.5")
    # PM10
    p6 = figure(plot_width=700,plot_height=300,x_axis_type='datetime',title='Unit: ' + str(mowr_ID) + ' - PM10 (Preliminary, Uncalibrated Data)')
    p6.scatter(ds.time[~np.isnan(ds['opcn2_PM10'])].values,ds['opcn2_PM10'][~np.isnan(ds['opcn2_PM10'])].values,color='red')
    tab6 = Panel(child=p6, title="PM10")
    
    ####  CREATE BOKEH HTML PLOT
    tabs = Tabs(tabs=[tab1, tab2, tab3, tab4, tab5, tab6])
    save(tabs, '/Users/vonw/work/software/aqnet/data/sensor' + str(mowr_ID) + '.html')    

    return

def mapAqnetSensorData():
    import folium
    
    # Coordinates estimated using map from Mike Diedesch and QGIS.
    streetLightLocation   = [[47.66964,-117.40315],
                             [47.65717,-117.41025],
                             [47.65449,-117.39002]]
    referenceSiteLocation =  [47.66081,-117.40446]
    
    # Center map on the Spokane Academic Center (SAC); coordinates obtained from QGIS.
    m = folium.Map([47.66141,-117.40579], zoom_start=14)
    
    html221=open('/Users/vonw/work/software/aqnet/data/sensor221.html').read()
    html223=open('/Users/vonw/work/software/aqnet/data/sensor223.html').read()
    html224=open('/Users/vonw/work/software/aqnet/data/sensor224.html').read()
    
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

    m.save('/Users/vonw/Sites/urbanova/AQnetMap.html')
    
    return

def copyAQnetMapToAWS_S3():
    """
    For use with Amazon Web Services. This functions simply copies the AQnet map from
    the AWS EC2 instance to the AWS S3 bucket called urbanova-air-quality-network.
    
        Written by Von P. Walden
                   Washington State University
                   31 May 2017
    """
    import os
    os.system('/Users/vonw/.local/bin/aws s3 cp /Users/vonw/Sites/urbanova/AQnetMap.html s3://urbanova-air-quality-network/data/AQnetMap.html --profile vonw --acl public-read')
    return

def saveAqnetSensorData(filename, mowr_ID, start_time, end_time):
    """Reads in Aqnet data and saves data variables into either a netCDF or a 
        CSV file, depending on the extension giving to the filename variable.
        If filename ends in csv, a comma-separated-variable file is exported. 
        Otherwise a netCDF file is exported.
    
        Written by Von P. Walden
        Washington State University
        27 April 2017
        11 May   2018 - Edited to export either netCDF or CSV files.
    """
    ds = acquireAqnetSensorData(mowr_ID, start_time, end_time)
    
    if ((filename[-3:] == 'csv') or (filename[-3:] == 'CSV')):
        header=[attr + ': ' + ds.attrs[attr] + '\n' for attr in ds.attrs]
        f=open(filename,'w')
        f.writelines(header)
        f.writelines(['\n'])
        f.close()
        ds.to_dataframe().to_csv(filename, mode='a')
    else:
        ds.to_netcdf(filename)
    
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
    from bokeh.plotting import figure, save, output_file, vplot
    from bokeh.models   import Range1d
    
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
    ds221 = acquireAqnetSensorData(221,btime, etime)
    ds224 = acquireAqnetSensorData(224,btime, etime)
    
    # Met
    t = figure(plot_width=1200,
               plot_height=400,
               x_axis_type ='datetime',
               x_axis_label='Date (local)',
               y_axis_label='Temperature (C)',
               title='Weather Measurements for week of ' + btime[0:10] + ' to ' + etime[0:10] + ' (Preliminary, Uncalibrated Data)')
    t.scatter(ds221.time, ds221['htu21d_T']['data'],color='blue',  legend='North Sensor')
    t.scatter(ds224.time, ds224['htu21d_T']['data'],color='orange',legend='South Sensor')
    
    u = figure(plot_width=1200,
               plot_height=400,
               x_axis_type ='datetime',
               x_axis_label='Date (local)',
               y_axis_label='Relative Humidity (%)',
               x_range=t.x_range)
    u.scatter(ds221.time, ds221['htu21d_RH'],color='blue',  legend='North Sensor')
    u.scatter(ds224.time, ds224['htu21d_RH'],color='orange',legend='South Sensor')
    
    p = figure(plot_width=1200,
               plot_height=400,
               x_axis_type ='datetime',
               x_axis_label='Date (local)',
               y_axis_label='Pressure (mb)',
               x_range=t.x_range)
    p.scatter(ds221.time, ds221['bmp280_P'],color='blue',  legend='North Sensor')
    p.scatter(ds224.time, ds224['bmp280_P'],color='orange',legend='South Sensor')
    
    p = vplot(t,u,p)
    
    output_file('/Users/vonw/Sites/urbanova/weekly/UrbanovaWeekly_Met_' + btime[0:10] + '_' + etime[0:10] + '.html',
                title='Weather Measurements for week of ' + btime[0:10] + ' to ' + etime[0:10])
    save(p)
    
    # CO2
    p = figure(plot_width=1200,
               plot_height=600,
               x_axis_type ='datetime',
               x_axis_label='Date (local)',
               y_axis_label='CO2 concentration (ppmv)',
               title='CO2 Measurements for week of ' + btime[0:10] + ' to ' + etime[0:10] + ' (Preliminary, Uncalibrated Data)')
    p.scatter(ds221.time, ds221['k30_CO2'],color='blue',  legend='North Sensor')
    p.scatter(ds224.time, ds224['k30_CO2'],color='orange',legend='South Sensor')
    output_file('/Users/vonw/Sites/urbanova/weekly/UrbanovaWeekly_CO2_' + btime[0:10] + '_' + etime[0:10] + '.html',
                title='CO2 Measurements for week of ' + btime[0:10] + ' to ' + etime[0:10])
    save(p)
    
    # PM2.5
    p = figure(plot_width=1200,
               plot_height=600,
               x_axis_type ='datetime',
               x_axis_label='Date (local)',
               y_axis_label='PM2.5 concentration (ug/m^3)',
               title='PM2.5 Measurements for week of ' + btime[0:10] + ' to ' + etime[0:10] + ' (Preliminary, Uncalibrated Data)')
    p.scatter(ds221.time, ds221['opcn2_PM2.5'],   color='blue',  legend='North Sensor')
    p.scatter(ds224.time, ds224['opcn2_PM2.5']+10,color='orange',legend='South Sensor + 10 ug/m^3')
    p.y_range = Range1d(0, 30)
    output_file('/Users/vonw/Sites/urbanova/weekly/UrbanovaWeekly_PM2.5_' + btime[0:10] + '_' + etime[0:10] + '.html',
                title='PM2.5 Measurements for week of ' + btime[0:10] + ' to ' + etime[0:10])
    save(p)
    
    # dB
    p = figure(plot_width=1200,
               plot_height=600,
               x_axis_type ='datetime',
               x_axis_label='Date (local)',
               y_axis_label='dB',
               title='Audio Measurements for week of ' + btime[0:10] + ' to ' + etime[0:10] + ' (Preliminary, Uncalibrated Data)')
    p.scatter(ds221.time, ds221['dB'],   color='blue',  legend='North Sensor')
    p.scatter(ds224.time, ds224['dB']+30,color='orange',legend='South Sensor + 30 dB')
    output_file('/Users/vonw/Sites/urbanova/weekly/UrbanovaWeekly_dB_' + btime[0:10] + '_' + etime[0:10] + '.html',
                title='Audio Measurements for week of ' + btime[0:10] + ' to ' + etime[0:10])
    save(p)
    
    return
