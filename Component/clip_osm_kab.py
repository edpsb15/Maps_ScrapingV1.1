import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import folium
from folium.plugins import MarkerCluster
import os
import glob
import sys


def show_map(input_1):
    base_path = os.path.dirname(os.path.abspath(__file__))  # Path ke folder skrip saat ini
    

    # Load and Clean Data
    if input_1 == "All" :
        #Cek apakah peta all ada    
        input_folder = os.path.join(base_path, '..', 'Inputan', 'SLS')
        # Find shapefile (.shp), geojson (.geojson), and json (.json) files
        file_paths = (
            glob.glob(os.path.join(input_folder, "*.[sS][hH][pP]")) + 
            glob.glob(os.path.join(input_folder, "*.[gG][eE][oO][jJ][sS][oO][nN]")) + 
            glob.glob(os.path.join(input_folder, "*.[jJ][sS][oO][nN]"))
        )

        # Select the first file found (or handle if none are found)
        if file_paths:
            shapefile_path = file_paths[0]  # Use the first matching file found
        else:
            shapefile_path = None
            print("No .shp or .geojson file found in the specified folder.")

        print("Selected file:", shapefile_path)

        shape_gdf = gpd.read_file(shapefile_path)
        shape_gdf = shape_gdf.sort_values(by='kd_gabungan',ascending=True)
        first_row = shape_gdf.iloc[0]

        excel_path = os.path.join(base_path, '..', 'Output', 'Scraping',f"{first_row['kdprov']}{first_row['kdkab']}.xlsx")  # Path ke folder OCR
        if os.path.exists(excel_path):
            df = pd.read_excel(excel_path)
            kolom_duplikat  = ['Actual Place Name', 'Address', 'Phone Number', 'Place Type']
            # Hapus duplikat
            df = df.drop_duplicates(subset=kolom_duplikat)
            print("Excel file loaded successfully.")
        else:
            print("Seluruh kabupaten belum selesai")
            return None

        # Convert Latitude and Longitude to numeric, remove NaNs and duplicates
        df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
        df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
        df = df.dropna(subset=['Latitude', 'Longitude'])#.drop_duplicates(subset=['Latitude', 'Longitude'])
        print("Data cleaned: removed rows with invalid coordinates and duplicates.")

        # Create Points as GeoDataFrame
        geometry = [Point(xy) for xy in zip(df['Longitude'], df['Latitude'])]
        gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
        print("GeoDataFrame created with latitude and longitude points.")

        # Load Kecamatan Polygon Data from a Shapefile
        shape_gdf = shape_gdf.to_crs(gdf.crs)
        print("Kecamatan shapefile data loaded and coordinate reference systems matched.")

        # Clip Points within Kecamatan Polygons and Join Data
        clipped_gdf = gpd.sjoin(gdf, shape_gdf, how="inner", predicate="intersects")
        print("Spatial join completed: points clipped within Kecamatan boundaries.")

        # Create Interactive Map with Marker Clustering
        center_lat = clipped_gdf['Latitude'].mean() if not clipped_gdf['Latitude'].empty else -8.2192
        center_lon = clipped_gdf['Longitude'].mean() if not clipped_gdf['Longitude'].empty else 114.3691

        m = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles='OpenStreetMap')
        marker_cluster = MarkerCluster().add_to(m)

        for _, row in clipped_gdf.iterrows():    
            # Define popup content with HTML styling
            popup_content = folium.Popup(
                html=f'<div style="font-size:13px;">'
                    f'<b>{row["Actual Place Name"]}</b><br>'
                    f'Jenis: {row["Place Type"]}<br>'
                    f'Telepon: {row["Phone Number"]}<br>'
                    f'Review Terakhir: {row["Review Date"]}'  # Add review date here
                    f'</div>',
                max_width=300,  # Adjust as needed
                min_width=200   # Adjust as needed
            )
            
            # Add marker with custom popup to the MarkerCluster
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=popup_content,
                icon=folium.Icon(color='red')
            ).add_to(marker_cluster)

        print("Markers added with formatted popup content.")

        # Simplify geometries and add Kecamatan Boundary Polygons
        shape_gdf['simplified'] = shape_gdf.geometry.simplify(tolerance=0.000)

        for _, row in shape_gdf.iterrows():
            geo_json = gpd.GeoSeries(row['simplified']).to_json()
            folium.GeoJson(
                geo_json,
                style_function=lambda x: {
                    'fillColor': 'blue',
                    'color': 'blue',
                    'weight': 1,
                    'fillOpacity': 0.1
                },
                tooltip=f"{row['nmkec']} - {row['nmdesa']} - {row['nmsls']}"
            ).add_to(m)
        print("Kecamatan boundary polygons added with simplified geometry.")

        # Save and Display the Map
        output_path =  os.path.join(base_path, '..', 'Output', 'Map',f"{first_row['kdprov']}{first_row['kdkab']}.html")  # Path ke folder OCR
        os.makedirs(os.path.dirname(output_path), exist_ok=True)  # Membuat direktori jika belum ada
        m.save(output_path)
        print(f"Interactive map with detailed pop-ups saved as {output_path}")

        # Save the filtered_gdf DataFrame to an Excel file
        clip_path = os.path.join(base_path, '..', 'Output', 'Clipping',f"{first_row['kdprov']}{first_row['kdkab']}_Bersih.xlsx")
        os.makedirs(os.path.dirname(clip_path), exist_ok=True)
        clipped_gdf.to_excel(clip_path, index=False) #JANGAN LUPA GANTI PATH
        print("Data saved as 'clipped_data_output.xlsx'.")
        return None

    else:
        excel_path = os.path.join(base_path, '..', 'Output', 'Scraping',input_1[:-3],f"{input_1}.xlsx")  # Path ke folder OCR
        df = pd.read_excel(excel_path)
        print("Excel file loaded successfully.")
        # print(df)
        # return None
        
        # Convert Latitude and Longitude to numeric, remove NaNs and duplicates
        df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
        df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
        df = df.dropna(subset=['Latitude', 'Longitude']).drop_duplicates(subset=['Latitude', 'Longitude'])
        print("Data cleaned: removed rows with invalid coordinates and duplicates.")

        # Create Points as GeoDataFrame
        geometry = [Point(xy) for xy in zip(df['Longitude'], df['Latitude'])]
        gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
        print("GeoDataFrame created with latitude and longitude points.")

                # Extract codes from input_1
        kdprov = input_1[:2]     # First 2 characters
        kdkab = input_1[2:4]     # Characters 3 and 4
        kdkec = input_1[4:7]     # Characters 5 to 7
        kddesa = input_1[-3:]    # Last 3 characters


        # Load Kecamatan Polygon Data from a Shapefile
        input_folder = os.path.join(base_path, '..', 'Inputan', 'SLS')
        file_paths = (
            glob.glob(os.path.join(input_folder, "*.[sS][hH][pP]")) + 
            glob.glob(os.path.join(input_folder, "*.[gG][eE][oO][jJ][sS][oO][nN]")) + 
            glob.glob(os.path.join(input_folder, "*.[jJ][sS][oO][nN]"))
        )


        # Select the first file found (or handle if none are found)
        if file_paths:
            shapefile_path = file_paths[0]  # Use the first matching file found
        else:
            shapefile_path = None
            print("No .shp or .geojson file found in the specified folder.")

        print("Selected file:", shapefile_path)

        shape_gdf = gpd.read_file(shapefile_path)
        shape_gdf = shape_gdf.to_crs(gdf.crs)
        shape_gdf = shape_gdf[
            (shape_gdf['kdprov'] == kdprov) &
            (shape_gdf['kdkab'] == kdkab) &
            (shape_gdf['kdkec'] == kdkec) &
            (shape_gdf['kddesa'] == kddesa)
        ]
        print("Kecamatan shapefile data loaded and coordinate reference systems matched.")

        # Clip Points within Kecamatan Polygons and Join Data
        clipped_gdf = gpd.sjoin(gdf, shape_gdf, how="inner", predicate="intersects")
        print("Spatial join completed: points clipped within Kecamatan boundaries.")

        # print(clipped_gdf)
        # Filter clipped_gdf based on extracted codes
        filtered_gdf = clipped_gdf[
            (clipped_gdf['kdprov'] == kdprov) &
            (clipped_gdf['kdkab'] == kdkab) &
            (clipped_gdf['kdkec'] == kdkec) &
            (clipped_gdf['kddesa'] == kddesa)
        ]

        # Create Interactive Map with Marker Clustering
        center_lat = filtered_gdf['Latitude'].mean() if not filtered_gdf['Latitude'].empty else -8.2192
        center_lon = filtered_gdf['Longitude'].mean() if not filtered_gdf['Longitude'].empty else 114.3691

        m = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles='OpenStreetMap')
        marker_cluster = MarkerCluster().add_to(m)

        for _, row in filtered_gdf.iterrows():    
            # Define popup content with HTML styling
            popup_content = folium.Popup(
                html=f'<div style="font-size:13px;">'
                    f'<b>{row["Actual Place Name"]}</b><br>'
                    f'Jenis: {row["Place Type"]}<br>'
                    f'Telepon: {row["Phone Number"]}<br>'
                    f'Review Terakhir: {row["Review Date"]}'  # Add review date here
                    f'</div>',
                max_width=300,  # Adjust as needed
                min_width=200   # Adjust as needed
            )
            
            # Add marker with custom popup to the MarkerCluster
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=popup_content,
                icon=folium.Icon(color='red')
            ).add_to(marker_cluster)

        print("Markers added with formatted popup content.")

        # Simplify geometries and add Kecamatan Boundary Polygons
        shape_gdf['simplified'] = shape_gdf.geometry.simplify(tolerance=0.000)

        for _, row in shape_gdf.iterrows():
            geo_json = gpd.GeoSeries(row['simplified']).to_json()
            folium.GeoJson(
                geo_json,
                style_function=lambda x: {
                    'fillColor': 'blue',
                    'color': 'blue',
                    'weight': 1,
                    'fillOpacity': 0.1
                },
                tooltip=f"{row['nmkec']} - {row['nmdesa']} - {row['nmsls']}"
            ).add_to(m)
        print("Kecamatan boundary polygons added with simplified geometry.")

        # Save and Display the Map
        output_path =  os.path.join(base_path, '..', 'Output', 'Map',input_1[:-3],f"{input_1}.html")  # Path ke folder OCR
        os.makedirs(os.path.dirname(output_path), exist_ok=True)  # Membuat direktori jika belum ada
        m.save(output_path)
        print(f"Interactive map with detailed pop-ups saved as {output_path}")

        # Save the filtered_gdf DataFrame to an Excel file
        clip_path = os.path.join(base_path, '..', 'Output', 'Clipping',input_1[:-3],f"{input_1}_Bersih.xlsx")
        os.makedirs(os.path.dirname(clip_path), exist_ok=True)
        filtered_gdf.to_excel(clip_path, index=False) #JANGAN LUPA GANTI PATH
        print("Data saved as 'clipped_data_output.xlsx'.")
        save_selesai = os.path.join(base_path, '..', 'save', input_1[:-3],f"{input_1}_3_2.txt")
        # Ensure the directory exists
        os.makedirs(os.path.dirname(save_selesai), exist_ok=True)

        # Write a blank file at the specified path
        with open(save_selesai, 'w') as file:
            pass  # This creates an empty file