#===================================================================================
# LIBRAIRIES
#===================================================================================

# Built-in packages
import json
import xml.etree.ElementTree as ET # To be used to generate the xml filter

# Third party packages
import requests
import geopandas as gpd
import pandas as pd
from shapely.geometry import mapping

# Local (project specific) modules
from xml_builder import data_to_post


#======================================================================================
# INITIAL CONFIGURATION
#======================================================================================
# Paths to necessary input file
study_area_input_file = "C:/Users/ilung/Documents/Portfolio/diagnostic_tool/test_area/s6.shp" # The input file
config_urls_file = "config_urls.json"
config_dataset_file = "config_dataset.json"

# Path to where the results will be saved
output_file = "C:/Users/ilung/Documents/Portfolio/diagnostic_tool/diagnostic_tool/output/results_of_analysis.csv"

# Loading relevant files
study_area = gpd.read_file(study_area_input_file)
with open(config_urls_file) as f:
    urls_dict = json.load(f)
    
with open(config_dataset_file) as f:
    dataset_dict = json.load(f)

# Preparing the necessary urls
wfs_url = urls_dict["wfs_url"]


#========================================================================================
# Running the diagnostic
#=========================================================================================

# Checking if the study area is in WGS84. If not, a conversion is run
if study_area.crs.to_epsg() != 4326: 
    study_area = study_area.to_crs(epsg=4326)

analysis_results = {item: [] for item in dataset_dict} 

for item in dataset_dict:
        # Retrieving information from dictionnary of the environmental layers
        layer_name = dataset_dict[item]["layer_name"] # The name of the layer as per IGN standard
        layer_geometry = dataset_dict[item]["geometry_key"] # The geometry_key as per IGN standard
        information = dataset_dict[item]["interested_column"] # The column in the environmental layer dataset that contains the information we want

        # Building and sending the POST request
        data = data_to_post(study_area, layer_name, layer_geometry) # This is where lies the heart of the code. The xml filter is here.
        headers = {"Content-Type": "text/xml"}
        params={"outputFormat": "application/json"}
        response = requests.post(wfs_url, headers=headers, data=data, params=params)  # Sending the POST request

        # Process to run if status code == 200
        if response.status_code == 200:
            if response.json()["features"] == []: # If the response content is empty, then the study area does not intersect the environmental layer
                    print(f"L'aire d'étude n'intersecte pas de {item}")
                    analysis_results[item].append("-")

            else: # If the response content is not empty, then the study area intersects the environmental layer
                     print(f"L'aire d'étude est concernée par des éléments du {item}")
                     data_gdf = gpd.read_file(response.content) # Constructing a geodataframe from the response content
                     analysis_results[item].extend(data_gdf[information].tolist())

            # The process to run if response status is not 200
        elif response.status_code != 200:
            print(response.status_code, flush=True)
            analysis_results[item].append(f"{response.status_code}")

# Exporting the result into a appropriate format
results_df = pd.DataFrame(list(analysis_results.items()), columns=["PERIMETRE", "VALEUR"])
results_df.to_csv(output_file, index=False)
print ("Analyse terminé.")                 
