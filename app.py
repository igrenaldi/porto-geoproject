# file: app.py
import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium
import time

st.title("Geocoding Outlet Data")

# Upload file Excel
uploaded_file = st.file_uploader("Upload file Excel outlet Anda", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.subheader("Preview Data Awal")
    st.dataframe(df.head())

    # --- Data Cleaning ---
    st.subheader("Cleaning Latitude & Longitude")
    df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
    df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
    df.loc[df['Latitude'] == 0, 'Latitude'] = None
    df.loc[df['Longitude'] == 0, 'Longitude'] = None

    st.write("Data setelah cleaning:")
    st.dataframe(df.head())

    # --- Geocoding ---
    st.subheader("Geocoding alamat yang kosong")
    geolocator = Nominatim(user_agent="geoapi")
    
    failed_addresses = []

    def get_latlon(address):
        try:
            loc = geolocator.geocode(address, timeout=10)
            if loc:
                return loc.latitude, loc.longitude
        except:
            pass
        return None, None

    # Update koordinat kosong
    for i, row in df.iterrows():
        if pd.isna(row['Latitude']) or pd.isna(row['Longitude']):
            lat, lon = get_latlon(row['Address'])
            df.at[i, 'Latitude'] = lat
            df.at[i, 'Longitude'] = lon
            if lat is None or lon is None:
                failed_addresses.append(row['Address'])
            st.write(f"Updated {row['Customer Name']} → {lat}, {lon}")
            time.sleep(1)  # delay agar tidak diblokir server

    # Preview hasil geocoding
    st.subheader("Preview Data Hasil Geocoding")
    st.dataframe(df.head())

    # --- Visualisasi Peta ---
    st.subheader("Peta Outlet")
    avg_lat = df['Latitude'].dropna().mean() if df['Latitude'].notna().any() else -7.5
    avg_lon = df['Longitude'].dropna().mean() if df['Longitude'].notna().any() else 110.0
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=12)

    for _, row in df.iterrows():
        if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
            folium.Marker(
                [row['Latitude'], row['Longitude']],
                popup=row['Customer Name']
            ).add_to(m)

    st_folium(m, width=700, height=500)

    # --- Alamat gagal geocode ---
    if failed_addresses:
        st.subheader("Alamat gagal geocode")
        st.write(failed_addresses)
    else:
        st.write("Semua alamat berhasil geocode!")

    # --- Download hasil ---
    st.subheader("Download Data Clean & Geocoded")
    df.to_excel("outlet_data_clean.xlsx", index=False)
    st.download_button(
        label="Download Excel",
        data=open("outlet_data_clean.xlsx", "rb").read(),
        file_name="outlet_data_clean.xlsx"
    )
