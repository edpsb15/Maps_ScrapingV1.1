import geopandas as gpd
import os
import glob

current_directory = os.path.dirname(__file__)

# Navigate two levels up to get to the root where Inputan is located
inputan_directory = os.path.join(current_directory, os.pardir, 'Inputan', 'Desa')

# Create the path to the JSON files in the Inputan directory
json_files_path = os.path.join(inputan_directory, '*.json')

# Get the list of all JSON files in the specified directory
json_files = glob.glob(json_files_path)


def read_geopandas_json():
    try:
        gdf = gpd.read_file(json_files[0])
        # gdf = gdf.sort_values(by='kd_gabungan',ascending=True)
        
        if 'nmdesa' in gdf.columns:
            gdf['kd_gabungan'] = gdf['kdprov'].astype(str) + gdf['kdkab'].astype(str) + gdf['kdkec'].astype(str) + gdf['kddesa'].astype(str)
            gdf = gdf.sort_values(by='kd_gabungan',ascending=True)
            # nmdesa_list = gdf['nmdesa'].tolist()
            # Prepend the additional list to the nmdesa_list
            kdgab_list = gdf['kd_gabungan'].tolist()

            # combined_list = ['All'] + nmdesa_list
            combined_list = ['All'] + kdgab_list
            return combined_list
        else:
            print("'nmdesa' column not found in the GeoDataFrame.")
            return None
    except Exception as e:
        print(f"Error reading the GeoJSON file: {e}")
        return None
    
