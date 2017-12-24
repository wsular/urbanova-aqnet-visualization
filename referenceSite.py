def readReferenceSiteData(filename):
	"""This function reads data stored on the logger at the Urbanova
	Air Quality Reference Site.

	Input
		filename - name of the datalogger file

	Output
		refSite  - pandas dataframe that contains the Reference Site data.

	Written by Von P. Walden, Washington State University
			   23 Dec 2017
	"""

	import numpy  as np
	import pandas as pd

	refSite = pd.read_csv('stats.dat',skiprows=[0,2,3],parse_dates=['TIMESTAMP'],index_col='TIMESTAMP')

	return refSite

def plotReferenceSiteMetData(df):
	"""This function plots data from the meteorological tower at the Urbanova
	Air Quality Reference Site.

	Input
		df - pandas dataframe that contains the Reference Site data.

	Output
		no output; just creates and shows the plots.

	Written by Von P. Walden, Washington State University
			   23 Dec 2017
	"""

	import pandas as pd
	import matplotlib.pyplot as plt

	plt.figure(figsize=(12,12))
	plt.subplot(511)
	plt.plot(df.index,df.gmx600_P_Avg)
	plt.grid()
	plt.ylabel('Pressure (mb)')
	plt.title('Meteorological Tower Data, Urbanova AQ Reference Site')
	plt.subplot(512)
	plt.plot(df.index,df.gmx600_T_Avg,df.index,df.gmx600_dewpt_Avg)
	plt.grid()
	plt.ylabel('Temperature (C)')
	plt.subplot(513)
	plt.plot(df.index,df.gmx600_RH_Avg)
	plt.grid()
	plt.ylabel('Relative Humidity (%)')
	plt.subplot(514)
	plt.plot(df.index,df.gmx600_rel_WS_Avg)
	plt.grid()
	plt.ylabel('Wind Speed (m s-1)')
	plt.subplot(515)
	plt.plot(df.index,df.gmx600_rel_WD_unit_Avg)
	plt.grid()
	plt.ylabel('Wind Dir (deg)')
	plt.xlabel('Time (local)')

	plt.show()
	return

def plotReferenceSiteLicorData(df):
	"""This function plots data from the Licor 840A CO2/H2O sensor 
	at the Urbanova Air Quality Reference Site.

	Input
		df - pandas dataframe that contains the Reference Site data.

	Output
		no output; just creates and shows the plots.

	Written by Von P. Walden, Washington State University
			   23 Dec 2017
	"""

	import pandas as pd
	import matplotlib.pyplot as plt

	plt.figure(figsize=(12,12))
	plt.subplot(511)
	plt.plot(df.index,df.li840a_cell_P)
	plt.grid()
	plt.ylabel('Cell Pressure (mb)')
	plt.title('Licor Sensor Data, Urbanova AQ Reference Site')
	plt.subplot(512)
	plt.plot(df.index,df.li840a_cell_T)
	plt.grid()
	plt.ylabel('Cell Temp (C)')
	plt.subplot(513)
	plt.plot(df.index,df.li840a_H2O)
	plt.grid()
	plt.ylabel('H2O conc (ppmv)')
	plt.subplot(514)
	plt.plot(df.index,df.li840a_CO2)
	plt.grid()
	plt.ylabel('CO2 conc (ppmv)')
	plt.xlabel('Time (local)')

	plt.show()
	return







