# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 11:34:48 2017

@author: Von P. Walden, Washington State University
"""

from AqnetSensor import acquireAqnetSensorData
from datetime import datetime, timedelta

# !! NOTE that the start and end times for the Itron cloud API query must be in UTC.
btime = (datetime.utcnow()-timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
etime = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

# Acquire data from Itron cloud.
aq221,df221 = acquireAqnetSensorData(221,btime, etime)
aq224,df224 = acquireAqnetSensorData(224,btime, etime)

# CO2
figure(figsize=(12,6))
plot(aq221['k30_CO2']['data'].index, aq221['k30_CO2']['data'])
plot(aq224['k30_CO2']['data'].index, aq224['k30_CO2']['data'])
grid()
xlabel('Date/Time (local)')
ylabel('CO2 concentration (ppmv)')
title('CO2 Analysis for week of ' + btime[0:10] + ' to ' + etime[0:10])
legend(('North Sensor','South Sensor'),loc='best')
savefig('/Users/vonw/work/software/aqnet/data/WeeklyAnalysis_CO2.png')

# PM2.5
figure(figsize=(12,6))
semilogy(aq221['opcn2_PM2.5']['data'].index, aq221['opcn2_PM2.5']['data'])
semilogy(aq224['opcn2_PM2.5']['data'].index, aq224['opcn2_PM2.5']['data'])
grid()
xlabel('Date/Time (local)')
ylabel('PM2.5 concentration (ug/m^3)')
title('PM2.5 Analysis for week of ' + btime[0:10] + ' to ' + etime[0:10])
legend(('North Sensor','South Sensor'),loc='best')
savefig('/Users/vonw/work/software/aqnet/data/WeeklyAnalysis_PM2.5.png')
