import numpy as np
import pandas as pd
from django.shortcuts import render
from django.http import JsonResponse
from netCDF4 import Dataset
import xarray as xr
from django.http import JsonResponse
import time
from pathlib import Path
import os
from dateutil import relativedelta, parser
import json
import geopandas as gpd
from shapely.geometry import Point, Polygon
from django.views.decorators.csrf import csrf_exempt



#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def index(request):
    
    return render(request, 'index.html')

#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

DOMAIN = 'WA'
Latest_fcst_file = os.path.join(BASE_DIR,'data/Latest_data/Obs_fcst_combined/CDD/{}_precip_*.daily.nc'.format(DOMAIN))
Latest_FCST = xr.open_mfdataset(Latest_fcst_file, combine='nested', concat_dim='ens')
SDATE = pd.Timestamp((Latest_FCST.coords['time'][0].values)).date()
EDATE = pd.Timestamp((Latest_FCST.coords['time'][-1].values)).date()
print (SDATE, EDATE)
SDATE_JDAY = time.strptime(SDATE.strftime("%Y/%m/%d"), "%Y/%m/%d").tm_yday
EDATE_JDAY = time.strptime(EDATE.strftime("%Y/%m/%d"), "%Y/%m/%d").tm_yday

## Getting observation climatology

'''
LON_MIN, LON_MAX, LAT_MIN, LAT_MAX = get_lat_lon_minmax(DOMAIN)
CLIM_OBS_OUTF_template = os.path.join(BASE_DIR,'data/Latest_data/Obs_fcst_combined/Clim_OBS/{}_{:04d}.nc')
for YEAR in range(1981, 2020):
    output_file = CLIM_OBS_OUTF_template.format('CHIRPS', YEAR)
    if not os.path.exists(output_file): 
        OBS_DATA = xr.open_dataset(os.path.join(BASE_DIR,'data/chc-data-out/products/CHIRPS-2.0/global_daily/netcdf/p05/chirps-v2.0.{}.days_p05.nc'.format(YEAR)))
        #print (YEAR)
        SEL_OBS_DATA = OBS_DATA.sel(longitude=slice(LON_MIN, LON_MAX), latitude=slice(LAT_MIN, LAT_MAX), time=(OBS_DATA.coords['time.dayofyear']>=SDATE_JDAY) & (OBS_DATA.coords['time.dayofyear']<=EDATE_JDAY))
        SEL_OBS_DATA.to_netcdf(CLIM_OBS_OUTF_template.format('CHIRPS', YEAR))
        print(f"File saved : {output_file}")
    else:
            print(f"The file already exists : {output_file}")
SEL_OBS_ALL = xr.open_mfdataset(os.path.join(BASE_DIR,'data/Latest_data/Obs_fcst_combined/Clim_OBS/CHIRPS_*'), concat_dim='time', combine='nested')
SEL_OBS_MEAN = SEL_OBS_ALL.resample(time='YE').sum(dim='time').mean(dim='time')
SEL_OBS_MEAN = SEL_OBS_MEAN.load()'''

## Median weekly total rainfall
print(Latest_FCST["time"].values)
WEEKLY_RAIN_TOTAL = Latest_FCST.copy()
WEEKLY_RAIN_TOTAL.coords['time'] = (np.arange(0, len(WEEKLY_RAIN_TOTAL.time))/7).astype(int) ## Defining time to seperate days into 4 weeks
WEEKLY_RAIN_TOTAL = WEEKLY_RAIN_TOTAL.groupby('time').sum(dim='time')

print(Latest_FCST["time"].values)



## Now plotting CDD forecasts
CDD_INFILE =os.path.join(BASE_DIR,'data/Latest_data/Derived_products/{}_next_30_days_CDD.nc'.format(DOMAIN))
CDD_XR = xr.open_dataset(CDD_INFILE)
CDD_XR = CDD_XR.isel(length=0)
MEDIAN_FCST_CDD = CDD_XR.median(dim='ens')
#MEDIAN_FCST_CDD = MEDIAN_FCST_CDD.where(SEL_OBS_MEAN['precip']>50)

## Now plotting CDD anomaly
CLIM_CDD = xr.open_mfdataset(os.path.join(BASE_DIR,'data/Latest_data/Obs_fcst_combined/CDD/Clim-CDD/{}_OBS_CDD_2*.nc'.format(DOMAIN)), combine='nested', concat_dim='length')
MEDIAN_CLIM_CDD = CLIM_CDD.median(dim='length')
#MEDIAN_CLIM_CDD = MEDIAN_CLIM_CDD.where(SEL_OBS_MEAN['precip']>50)
## Crop data for CILSS countries 
CDD_ANOM = (MEDIAN_FCST_CDD-MEDIAN_CLIM_CDD)
# Replace missing values with 0
CDD_ANOM = CDD_ANOM.fillna(0)




def get_lat_lon_minmax(DOMAIN):
        if DOMAIN == 'Africa':
            LON_MIN, LON_MAX, LAT_MIN, LAT_MAX = -20, 60, -40, 40
        elif (DOMAIN=='EA'):
            LON_MIN, LON_MAX, LAT_MIN, LAT_MAX = 20, 52, -13, 25
        elif (DOMAIN=='SA'):
            LON_MIN, LON_MAX, LAT_MIN, LAT_MAX = 10, 55, -36, -2
        elif DOMAIN=='WA':
            LON_MIN, LON_MAX, LAT_MIN, LAT_MAX = -20, 28, 0, 28
        elif DOMAIN == 'CA-NV':
            LON_MIN, LON_MAX, LAT_MIN, LAT_MAX = -126, -110, 24, 45
        elif DOMAIN =='Cabo':
            LON_MIN, LON_MAX, LAT_MIN, LAT_MAX = -26, -22, 14, 18
        return LON_MIN, LON_MAX, LAT_MIN, LAT_MAX

def get_climate_data(request):
    region = request.GET.get('region', 'WA')  # Par défaut, Afrique de l'Ouest
    variable = request.GET.get('variable', '')
    sub_variable = request.GET.get('sub_variable', '') 
   # data_to_send={}
    data_to_send = {
            'dataValue': [],
            'latitudes': [],
            'longitudes': [],
            'metaData' : [],
        }
    

    if variable == "Total Rainfall in mm" and sub_variable !='':
        if sub_variable == '30-day':
            Total_rainfall = (Latest_FCST.sum(dim='time')) ## Total rainfall
            Total_rainfall=Total_rainfall.median(dim='ens')
            dataValue = Total_rainfall['precip'].values.tolist()  # Convertit en liste
            latitudes = Total_rainfall['latitude'].values.tolist()
            longitudes = Total_rainfall['longitude'].values.tolist()
            metaData1 = 'Multimodel forecast of total rainfall',
            metaData2= '(30 days starting on {})'.format(SDATE.strftime("%Y/%m/%d"))

        else:  
            # WEEKLY_RAIN_TOTAL = WEEKLY_RAIN_TOTAL.where(SEL_OBS_MEAN['precip']>50)
            WEEK= int(sub_variable.split()[1])
            WEEKLY_RAIN_TOTAL2 = WEEKLY_RAIN_TOTAL.median(dim='ens').isel(time=WEEK)
            # Créer un dictionnaire
            dataValue = WEEKLY_RAIN_TOTAL2['precip'].values.tolist()  # Convertit en liste
            latitudes = WEEKLY_RAIN_TOTAL2['latitude'].values.tolist()
            longitudes = WEEKLY_RAIN_TOTAL2['longitude'].values.tolist()
            metaData1= 'Multimodel forecast of total rainfall'
            metaData2= '(Week-{} starting on {})'.format(WEEK+1, (SDATE + relativedelta.relativedelta(days=WEEK*7)).strftime("%Y/%m/%d"))

        data_to_send = {
                'dataValue': dataValue,
                'latitudes': latitudes,
                'longitudes': longitudes,
                'metaData' : [metaData1,metaData2],
            }
    elif variable == "Number of Rainy Days" and sub_variable !='':
        Thresh_rainy_day = int(sub_variable.split()[3])
        WEEK = threshold = int(sub_variable.split()[1])
        NUM_RAINY_DAY = (Latest_FCST>Thresh_rainy_day)
        NUM_RAINY_DAY.coords['time'] = (np.arange(0, len(NUM_RAINY_DAY.time))/7).astype(int) ## Defining time to seperate days into 4 weeks
        WEEKLY_NUM_RAINY_DAY = NUM_RAINY_DAY.groupby('time').sum(dim='time')
        WEEKLY_NUM_RAINY_DAY=WEEKLY_NUM_RAINY_DAY.isel(time=WEEK).median(dim='ens')
       # WEEKLY_NUM_RAINY_DAY = WEEKLY_NUM_RAINY_DAY.where(SEL_OBS_MEAN['precip']>50)
        dataValue = WEEKLY_NUM_RAINY_DAY['precip'].values.tolist()  # Convertit en liste
        latitudes = WEEKLY_NUM_RAINY_DAY['latitude'].values.tolist()
        longitudes = WEEKLY_NUM_RAINY_DAY['longitude'].values.tolist()
        metaData1= 'Multimodel forecast of number of days with precipitation above {} mm'.format(Thresh_rainy_day)
        metaData2= '(Week-{} starting on {})'.format(WEEK+1, (SDATE + relativedelta.relativedelta(days=WEEK*7)).strftime("%Y/%m/%d"))

        data_to_send = {
                'dataValue': dataValue,
                'latitudes': latitudes,
                'longitudes': longitudes,
                'metaData' : [metaData1,metaData2],
            }
    elif variable== 'Consecutive Dry Days' and sub_variable !='':
        if sub_variable == '30-day Plot':
            dataValue = MEDIAN_FCST_CDD['precip'].values.tolist()  # Convertit en liste
            latitudes = MEDIAN_FCST_CDD['latitude'].values.tolist()
            longitudes = MEDIAN_FCST_CDD['longitude'].values.tolist()
            metaData1='Multimodel forecast of consecutive dry days'
            metaData2= '(30 days starting on {})'.format(SDATE.strftime("%Y/%m/%d"))

        elif sub_variable == '30-day Plot + Anomaly':
            dataValue = CDD_ANOM['precip'].values.tolist()  # Convertit en liste
            latitudes = CDD_ANOM['latitude'].values.tolist()
            longitudes = CDD_ANOM['longitude'].values.tolist()
            metaData1= 'Multimodel forecast of consecutive dry days anomaly'
            metaData2= '(30 days starting on {})'.format(SDATE.strftime("%Y/%m/%d"))

        data_to_send = {
                'dataValue': dataValue,
                'latitudes': latitudes,
                'longitudes': longitudes,
                'metaData' : [metaData1, metaData2],
            }

    print("dddddddddddddddddddddddddddddddddddddddddddddddddddddd")
    #print("returning data{},{}".format(data_to_send,5555555))
    return JsonResponse(data_to_send)

#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
@csrf_exempt  # Use this only if you want to disable CSRF protection for this view
def get_polygon_stats(request):
    if request.method == 'POST':
        # Récupération des paramètres de la requête
        body = json.loads(request.body.decode('utf-8'))  # Charger le corps JSON
        longitudes = body.get('longitudes', [])
        latitudes = body.get('latitudes', [])
        sub_variable = body.get('subVariable','')
        variable = body.get('variable','')
        filtered_data_to_send = {
            'dataValue': [],
            'latitudes': [],
            'longitudes': [],
            'metaData' : [],
        }
    
        print(sub_variable)
        print(variable)
        if variable =="Total Rainfall in mm" and sub_variable !='':
            filtered_data = filter_with_coordinates(ds = Latest_FCST.copy(),latitudes= latitudes, longitudes= longitudes)
            filtered_data = filtered_data.median(dim="ens")
            if sub_variable == '30-day':                
                # Convertir en dictionnaire 
                filtered_data_to_send = {
                    "time": filtered_data["time"].values.astype(str).tolist(),
                    "mean": filtered_data.mean(dim=["latitude", "longitude"])['precip'].values.tolist(),
                    "median": filtered_data.median(dim=["latitude", "longitude"])['precip'].values.tolist(),
                    "min": filtered_data.min(dim=["latitude", "longitude"])['precip'].values.tolist(),
                    "max": filtered_data.max(dim=["latitude", "longitude"])['precip'].values.tolist(),
                }
            else:
                WEEK= int(sub_variable.split()[1])-1
                filtered_data= filter_with_week(filtered_data, WEEK)
                filtered_data_to_send = {
                    "time": filtered_data["time"].values.astype(str).tolist(),
                    "mean": filtered_data.mean(dim=["latitude", "longitude"])['precip'].values.tolist(),
                    "median": filtered_data.median(dim=["latitude", "longitude"])['precip'].values.tolist(),
                    "min": filtered_data.min(dim=["latitude", "longitude"])['precip'].values.tolist(),
                    "max": filtered_data.max(dim=["latitude", "longitude"])['precip'].values.tolist(),
                }
                print(filtered_data_to_send['time'])
                print(filtered_data_to_send['median'])
                print(filtered_data_to_send['max'])
                print(filtered_data_to_send['min'])



        

    
    

        # Retourner les données sous forme de réponse JSON
        return JsonResponse({"data": filtered_data_to_send})

        

    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)
   
    


#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# Definition for helping functions
def filter_with_week(ds, week_number):
    """
    Selects up to 7 days from an xarray dataset based on the week number.
    
    Parameters:
    - ds: xarray.Dataset or xarray.DataArray
    - week_number: int, week number (0, 1, 2, 3)
    
    Returns:
    - xarray.Dataset or xarray.DataArray containing the selected days.
    """
    # Check if the week number is valid
    if week_number < 0 or week_number > 3:
        raise ValueError("The week number must be between 0 and 3.")

    # Calculate the start and end indices
    start_index = week_number * 7
    if week_number == 3:
        end_index= len(ds['time'])
    else:
        end_index = start_index + 7

    # Select the days
    selected_data = ds.isel(time=slice(start_index, end_index))

    return selected_data


def filter_with_coordinates(ds, latitudes, longitudes):
    """
    Ouvre un fichier NetCDF et filtre les données en utilisant un polygone défini par des listes de coordonnées.

    Parameters:
    - ncdf_file (str): Chemin vers le fichier NetCDF.
    - latitudes (list): Liste de latitudes définissant le polygone.
    - longitudes (list): Liste de longitudes définissant le polygone.

    Returns:
    - xarray.Dataset: Un ensemble de données filtré.
    """
    ds['time'] = ds['time'].dt.strftime('%Y/%m/%d')
    print(ds.dims)
    # Créer un polygone à partir des listes de coordonnées
    polygon = Polygon(zip(longitudes, latitudes))

    # Créer un GeoDataFrame pour les coordonnées du dataset
    latitudes_ds = ds['latitude'].values
    longitudes_ds = ds['longitude'].values
    points = [Point(lon, lat) for lat in latitudes_ds for lon in longitudes_ds]

    # Créer un GeoDataFrame à partir des points
    points_gdf = gpd.GeoDataFrame(geometry=points)

    # Filtrer les points qui se trouvent dans le polygone
    filtered_points = points_gdf[points_gdf.geometry.within(polygon)]

    # Vérifier si des points ont été filtrés
    if filtered_points.empty:
        raise ValueError("Aucun point trouvé dans le polygone.")

    # Extraire les latitudes et longitudes uniques des points filtrés
    filtered_latitudes = filtered_points.geometry.y.unique()
    filtered_longitudes = filtered_points.geometry.x.unique()

    # Filtrer le dataset en fonction des latitudes et longitudes filtrées
    filtered_ds = ds.sel(latitude=filtered_latitudes, longitude=filtered_longitudes)
    print(filtered_ds.dims)

    return filtered_ds