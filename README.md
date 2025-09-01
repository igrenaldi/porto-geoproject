Porto GeoProject
This project is an interactive web-based application built with Streamlit, designed to help you geocode a large number of addresses and visualize them on an interactive map. This application is highly useful for efficiently managing your outlet or business location data.

Key Features
Bulk Geocoding: Upload an Excel file containing your address data, and the application will automatically find the Latitude & Longitude for addresses that are missing coordinates.

Single Address Search: Instantly find the Latitude & Longitude for a single address via the provided search box.

Interactive Map Visualization: View all successfully geocoded locations on an interactive map. You can zoom in, zoom out, and see details for each location.

Data Download: Download an updated Excel file with complete coordinate data.

Automated Data Management: The application intelligently processes only addresses that lack coordinate data, saving time and resources.

Application Preview
Here is a general overview of what the application looks like:

Requirements and How to Use
To run this project on your local machine, ensure you have Python installed. Then, follow these steps:

Clone the Repository:

Bash

git clone https://github.com/igrenaldi/porto-geoproject.git
cd porto-geoproject
Install Required Libraries:
Install all libraries listed in the requirements.txt file.

Bash

pip install -r requirements.txt
If you don't have a requirements.txt file, you can install the necessary libraries manually:

Bash

pip install streamlit pandas geopy folium streamlit-folium XlsxWriter
Run the Application:
Run the Streamlit application with the following command:

Bash

streamlit run app.py
The application will automatically open in your web browser.

Skills Demonstrated
Python: Use of the Pandas library for data manipulation, Geopy for geocoding, and Folium/Streamlit-Folium for interactive mapping.

Data Science: Data cleaning, handling missing values, and geocoding automation.

Web Development: Building an interactive user interface using Streamlit.

Contributions
This project is open-source and open for contributions. If you have ideas for new features or improvements, feel free to open an issue or submit a pull request.
