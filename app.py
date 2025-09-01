# file: app.py
import streamlit as st
import pandas as pd
from geopy.geocoders import Photon
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import folium
from streamlit_folium import st_folium
import time
from io import BytesIO

st.set_page_config(layout="wide")
st.title("Geocoding Data Outlet")
st.write("Aplikasi untuk mencari Latitude & Longitude dari daftar alamat outlet Anda.")

# --- Fungsi Geocoding ---
@st.cache_data
def get_latlon(address):
    geolocator = Photon()
    try:
        if "indonesia" not in address.lower():
            address_with_country = f"{address}, Indonesia"
        else:
            address_with_country = address
        
        loc = geolocator.geocode(address_with_country, timeout=15)
        
        if loc:
            return loc.latitude, loc.longitude
        else:
            return None, None
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        return None, None
    except Exception as e:
        return None, None

# --- Sidebar untuk fitur ---
with st.sidebar:
    st.header("Pilih Fitur")
    feature_choice = st.radio("Pilih salah satu:", ("Geocoding Massal (dari File)", "Pencarian Tunggal"))

    # Pindah bagian pencarian tunggal ke sidebar
    if feature_choice == "Pencarian Tunggal":
        st.subheader("Pencarian Alamat Tunggal")
        single_address = st.text_input("Masukkan alamat yang ingin dicari Lat/Lon-nya:")

        st.info("💡 **Tips:** Untuk hasil terbaik, masukkan alamat selengkap mungkin. Contoh: `Jl. Pahlawan No.115, Tangunan, Kec. Puri, Kabupaten Mojokerto`")

        if st.button("Cari"):
            if single_address:
                with st.spinner('Mencari koordinat...'):
                    lat, lon = get_latlon(single_address)
                if lat and lon:
                    st.success(f"Ditemukan! Latitude: {lat}, Longitude: {lon}")
                else:
                    st.warning("Alamat tidak ditemukan. Coba perbaiki ejaan atau tambahkan detail.")

# --- Konten Utama Aplikasi ---
if feature_choice == "Geocoding Massal (dari File)":
    st.header("Geocoding dari File Excel")
    uploaded_file = st.file_uploader("Unggah file Excel outlet Anda", type=["xlsx"])

    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.subheader("Preview Data Awal")
        st.dataframe(df.head())

        # --- Data Cleaning & Geocoding ---
        df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
        df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
        df.loc[df['Latitude'] == 0, 'Latitude'] = None
        df.loc[df['Longitude'] == 0, 'Longitude'] = None
        
        rows_to_geocode = df[df['Latitude'].isna() | df['Longitude'].isna()]
        total_rows_to_geocode = len(rows_to_geocode)
        
        if total_rows_to_geocode > 0:
            st.info(f"Ditemukan {total_rows_to_geocode} alamat yang memerlukan geocoding.")
            with st.spinner('Sedang melakukan geocoding... Mohon tunggu, proses ini butuh waktu.'):
                for i, row in rows_to_geocode.iterrows():
                    lat, lon = get_latlon(row['Address'])
                    df.at[i, 'Latitude'] = lat
                    df.at[i, 'Longitude'] = lon
                    time.sleep(1.5)
            st.success("Proses geocoding selesai!")
        else:
            st.info("Semua alamat sudah memiliki koordinat.")
        
        # --- Visualisasi Peta ---
        st.subheader("Peta Outlet")
        df_valid = df.dropna(subset=['Latitude', 'Longitude'])
        if not df_valid.empty:
            avg_lat = df_valid['Latitude'].mean()
            avg_lon = df_valid['Longitude'].mean()
            m = folium.Map(location=[avg_lat, avg_lon], zoom_start=12)
            for _, row in df_valid.iterrows():
                folium.Marker([row['Latitude'], row['Longitude']], popup=row['Customer Name']).add_to(m)
            st_folium(m, width=800, height=500)
        else:
            st.warning("Tidak ada alamat yang berhasil di-geocode untuk ditampilkan di peta.")

        # --- Hasil Geocoding ---
        st.subheader("Hasil Geocoding")
        df_success = df.dropna(subset=['Latitude', 'Longitude'])
        df_failed = df[df['Latitude'].isna()]
        
        st.markdown(f"**Ringkasan:**")
        st.info(f"Total Alamat: {len(df)}")
        st.info(f"✅ Berhasil di-geocode: {len(df_success)}")
        st.info(f"❌ Gagal di-geocode: {len(df_failed)}")
        
        if not df_success.empty:
            with st.expander(f"Tampilkan Alamat Berhasil di-geocode ({len(df_success)} data)"):
                st.dataframe(df_success[['Customer Name', 'Address', 'Latitude', 'Longitude']])

        if not df_failed.empty:
            with st.expander(f"Tampilkan Alamat Gagal di-geocode ({len(df_failed)} data)"):
                st.dataframe(df_failed[['Customer Name', 'Address']])
        
        # --- Download hasil ---
        st.subheader("Download Data Clean & Geocoded")
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        output.seek(0)
        
        st.download_button(
            label="Download Excel",
            data=output,
            file_name="outlet_data_clean.xlsx",
            mime="application/vnd.ms-excel"
        )
