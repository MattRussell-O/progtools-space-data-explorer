import requests
from urllib.error import HTTPError
import ipywidgets as widgets
from datetime import datetime, timezone
import time
import matplotlib.pyplot as plt
import numpy as np
from IPython.display import display, clear_output, Image
import streamlit as st
from io import BytesIO
import zipfile
import time

def sd_CelestialBodies(limit=5, image_width=500, image_height=500, display=True, name_filter=""):
    # Fetch a larger limit to allow for filtering (adjust if API allows more)
    fetch_limit = max(limit, 100)  # Fetch at least 100 for better filtering, but respect the user's limit
    url = f"https://lldev.thespacedevs.com/2.3.0/celestial_bodies/?mode=detailed&limit={fetch_limit}"
    response = requests.get(url)
    if response.status_code != 200:
        st.error("Failed to fetch celestial bodies.")
        return []
    data = response.json()
    results = data["results"]
    
    # Filter results based on name filter
    filtered_results = []
    for celestial_bodies in results:
        name = celestial_bodies["name"]
        
        if not name_filter or name_filter.lower() in name.lower():
            filtered_results.append(celestial_bodies)
    
    # Limit the filtered results to the requested limit
    filtered_results = filtered_results[:limit]
    
    celestial_bodies_images = []
    
    if display:
        for celestial_bodies in filtered_results:
            name = celestial_bodies["name"]
            description = celestial_bodies["description"]
            diameter = celestial_bodies["diameter"]
            mass = celestial_bodies["mass"]
            gravity = celestial_bodies["gravity"]
            image = celestial_bodies.get("image", {}).get("image_url")
            if image:
                celestial_bodies_images.append((name, image))
            st.markdown(
                f"""
                <div style="text-align: center;">
                <img src="{image}" alt="{name}" width="{image_width}" height="{image_height}" style="object-fit: cover;">
                <h3> Celestial Body: {name} </h3>
                <p> Description: {description} </p>
                <p> Diameter: {diameter} km </p>
                <p> Mass: {mass} kg </p>
                <p> Gravity: {gravity} m/s² </p>
                <hr>
                </div>
                """, 
                unsafe_allow_html=True
            )
    else:
        for celestial_bodies in filtered_results:
            name = celestial_bodies["name"]
            image = celestial_bodies.get("image", {}).get("image_url")
            if image:
                celestial_bodies_images.append((name, image))
    
    return celestial_bodies_images
          
def sd_Astronauts(limit=5, image_width=400, image_height=600, display=True, agency_filter=None, nationality_filter=None, min_flights=None, max_flights=None):
    # Fetch a larger limit to allow for filtering (adjust if API allows more)
    fetch_limit = max(limit, 100)  # Fetch at least 100 for better filtering, but respect the user's limit
    url = f"https://lldev.thespacedevs.com/2.3.0/astronauts?limit={fetch_limit}"
    response = requests.get(url)
    if response.status_code != 200:
        st.error("Failed to fetch astronauts.")
        return [], []
    data = response.json()
    results = data["results"]
    
    # Filter results based on provided filters
    filtered_results = []
    for astro in results:
        agency = astro.get("agency", {}).get("name", "Unknown")
        nationality = astro["nationality"]
        nationality_name = nationality[0]['nationality_name'] if nationality else "Unknown"
        f_launch = astro.get("flights_count", 0)  # Assume it's an int, default to 0 if missing
        
        if (agency_filter is None or agency == agency_filter) and \
           (nationality_filter is None or nationality_name == nationality_filter) and \
           (min_flights is None or f_launch >= min_flights) and \
           (max_flights is None or f_launch <= max_flights):
            filtered_results.append(astro)
    
    # Limit the filtered results to the requested limit
    filtered_results = filtered_results[:limit]
    
    astronaut_images = []
    
    if display:
        for astro in filtered_results:
            name = astro["name"]
            nationality = astro["nationality"]
            agency = astro.get("agency", {}).get("name", "Unknown")
            nationality_name = nationality[0]['nationality_name'] if nationality else "Unknown"
            image = astro.get("image", {}).get("image_url")
            age = astro.get("age", "Unknown")
            bday = astro.get("date_of_birth", "Unknown")
            f_launch = astro.get("flights_count", "Unknown")
            l_flight = astro.get("last_flight", "Unknown")
            
            if l_flight != "Unknown":
                try:
                    # Parse the ISO format (replace 'Z' with '+00:00' for UTC)
                    dt = datetime.fromisoformat(l_flight.replace('Z', '+00:00')) #if l_flight else None
                    # Format to a readable string (e.g., "July 21, 1969 at 05:54 PM")
                    l_flight = dt.strftime("%B %d, %Y at %I:%M %p")
                except ValueError:
                    # If parsing fails, keep the original value
                    pass
                finally:
                    if l_flight is None:
                        l_flight = "Unknown"

            if bday != "Unknown":
                try:
                    # Parse the ISO format (replace 'Z' with '+00:00' for UTC if present)
                    dt = datetime.fromisoformat(bday.replace('Z', '+00:00'))
                    # Format to a readable string (e.g., "July 21, 1969")
                    bday = dt.strftime("%B %d, %Y")
                except ValueError:
                    # If parsing fails, keep the original value
                    pass
            if image:
                astronaut_images.append((name, image))
            st.markdown(
                f"""
                <div style="text-align: center;">
                    <img src="{image}" width="{image_width}" height="{image_height}">
                    <h3>{name}</h3>
                    <p><b>Age:</b> {age}</p>
                    <p><b>Date of Birth:</b> {bday}</p>
                    <p><b>Nationality: </b>{nationality_name}</p>
                    <p><b>Agency:</b> {agency}</p>
                    <p><b>Total Launches:</b> {f_launch}</p>
                    <p><b>Last Flight:</b> {l_flight}</p>
                    <hr>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        for astro in filtered_results:
            name = astro["name"]
            image = astro.get("image", {}).get("image_url")
            if image:
                astronaut_images.append((name, image))
    
    return astronaut_images, filtered_results
                 
def sd_Spacecraft(limit=5, image_width=600, image_height=800, display=True, in_space_filter=None, status_filter=None):
    fetch_limit = max(limit, 100)
    url = f"https://lldev.thespacedevs.com/2.3.0/spacecraft/?mode=detailed&limit={fetch_limit}"
    response = requests.get(url)

    if response.status_code != 200:
        st.error("Failed to fetch spacecraft.")
        return []

    data = response.json()
    results = data["results"]

    # Apply filters
    filtered_results = []
    for spacecraft in results:

        in_space = spacecraft.get("in_space", None)
        status = spacecraft.get("status", {}).get("name", "Unknown")

        if (in_space_filter is None or in_space == in_space_filter) and \
           (status_filter is None or status == status_filter):

            filtered_results.append(spacecraft)

    filtered_results = filtered_results[:limit]

    spacecraft_image_urls = []

    # Display results
    if display:
        for spacecraft in filtered_results:
            name = spacecraft.get("name", "Unknown")
            description = spacecraft.get("description", "No description provided.")
            in_space = spacecraft.get("in_space", None)
            status = spacecraft.get("status", {}).get("name", "Unknown")
            image = spacecraft.get("image", {}).get("image_url") if spacecraft.get("image") else None

            if image:
                spacecraft_image_urls.append((name, image))

                st.markdown(
                    f"""
                    <div style="text-align: center; margin: 3px; padding: 3px;">
                        <img src="{image}" alt="{name}" style="object-fit:cover;" width="{image_width}" height="{image_height}">
                        <h3>Spacecraft: {name}</h3>
                        <p><b>Status:</b> {status}</p>
                        <p><b>In Space:</b> {in_space}</p>
                        <p>{description}</p>
                        <hr>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.write(f"No image available for {name}")

    else:
        for spacecraft in filtered_results:
            name = spacecraft.get("name", "Unknown")
            image = spacecraft.get("image", {}).get("image_url") if spacecraft.get("image") else None
            if image:
                spacecraft_image_urls.append((name, image))

    return spacecraft_image_urls
              
def sd_Launchers(
    limit=5,
    image_width=300,
    image_height=300,
    display=True,
    status_filter=None,
    flight_proven_filter=None,
    attempted_landings_filter=None,
    successful_landings_filter=None
):
    """
    Fetch and optionally display launchers. Returns a list of (name, image_url) tuples
    when display=False so the caller can build a zip for downloading.
    Supports filters: status, flight_proven (bool), attempted_landings (int), successful_landings (int).
    """

    # Fetch more items to allow filtering before truncation
    fetch_limit = max(limit * 3, 100)
    url = f"https://lldev.thespacedevs.com/2.3.0/launchers/?mode=detailed&limit={fetch_limit}"
    response = requests.get(url)

    if response.status_code != 200:
        st.error("Failed to fetch launchers.")
        return []

    data = response.json()
    results = data.get("results", [])

    # Apply filters
    filtered = []
    for launcher in results:
        status = launcher.get("status", {}).get("name", "Unknown")
        flight_proven = launcher.get("flight_proven", None)
        attempted_landings = launcher.get("attempted_landings", None)
        successful_landings = launcher.get("successful_landings", None)

        if (status_filter is None or status == status_filter) and \
           (flight_proven_filter is None or flight_proven == flight_proven_filter) and \
           (attempted_landings_filter is None or attempted_landings == attempted_landings_filter) and \
           (successful_landings_filter is None or successful_landings == successful_landings_filter):
            filtered.append(launcher)

    # Trim to requested limit
    filtered = filtered[:limit]

    launcher_image_urls = []

    # Helper to safely get image URL (covers a couple naming variants)
    def _extract_image_url(obj):
        if not obj:
            return None
        # API sometimes returns {"image": {"image_url": ...}} or sometimes "image_url" directly
        if isinstance(obj, dict):
            return obj.get("image_url") or obj.get("image_url") or (obj.get("image") and obj.get("image").get("image_url"))
        return None

    # Display or collect images
    for launcher in filtered:
        # Robust extraction for fields
        # Some launcher objects use 'launcher_config' with 'full_name', others may use 'name'
        name = launcher.get("launcher_config", {}).get("full_name") or launcher.get("name") or "Unknown"
        serial_number = launcher.get("serial_number", "N/A")
        details = launcher.get("details", "No details provided.")
        status = launcher.get("status", {}).get("name", "Unknown")
        flights = launcher.get("flights", 0)
        flight_proven = launcher.get("flight_proven", False)
        attempted_landings = launcher.get("attempted_landings", 0)
        successful_landings = launcher.get("successful_landings", 0)

        # Try several places for the image URL
        image = None
        # common shapes:
        image = launcher.get("image", {}).get("image_url") if launcher.get("image") else None
        if not image:
            image = launcher.get("image_url")
        if not image:
            # fallback if nested differently
            image_field = launcher.get("image")
            if isinstance(image_field, dict):
                image = image_field.get("image_url") or image_field.get("url")

        # If still nothing, skip image collection/display but continue to show info (optional)
        if image:
            launcher_image_urls.append((name, image))

        if display:
            # Always display the card even if image is missing (shows N/A)
            img_tag = f'<img src="{image}" alt="{name}" style="display:block; margin: 0 auto; object-fit:cover;" width="{image_width}" height="{image_height}">' if image else ''
            st.markdown(
                f"""
                <div style="text-align: center; padding: 8px;">
                    {img_tag}
                    <h3>Launcher Name: {name}</h3>
                    <p><b>Serial Number:</b> {serial_number}</p>
                    <p><b>Status:</b> {status}</p>
                    <p><b>Details:</b> {details}</p>
                    <p><b>Flights:</b> {flights}</p>
                    <p><b>Flight Proven:</b> {flight_proven}</p>
                    <p><b>Attempted Landings:</b> {attempted_landings}</p>
                    <p><b>Successful Landings:</b> {successful_landings}</p>
                    <hr>
                </div>
                """,
                unsafe_allow_html=True
            )

    return launcher_image_urls
    
def rows_from_launch_results(results):
    rows = []
    for l in results:
        rows.append({
            "launch_name": l.get("name"),
            "provider": l.get("launch_service_provider", {}).get("name"),
            "rocket_name": l.get("rocket", {}).get("configuration", {}).get("name"),
            "mission_name": l.get("mission", {}).get("name"),
            "mission_type": l.get("mission", {}).get("type"),
            "mission_description": l.get("mission", {}).get("description"),
            "window_start": l.get("window_start"),
            "window_end": l.get("window_end"),
            "pad_name": l.get("pad", {}).get("name"),
            "location_name": l.get("pad", {}).get("location", {}).get("name"),
        })
    return rows

def exportLaunchData():
    url = "https://lldev.thespacedevs.com/2.0.0/launch/"
    response = requests.get(url)
    data = response.json()
    launches = data.get("results", [])
    return rows_from_launch_results(launches)

def saveLaunchData(rows, file_format="csv"):
    import pandas as pd

    df = pd.DataFrame(rows)

    if file_format == "csv":
        return df.to_csv(index=False).encode("utf-8")
    else:
        from io import BytesIO
        buffer = BytesIO()
        df.to_excel(buffer, index=False)
        return buffer.getvalue()

def sdLaunch(limit=5):
    # Fetch from API
    url = f"https://lldev.thespacedevs.com/2.0.0/launch/?limit={limit}"
    response = requests.get(url)
    data = response.json()
    results = data.get("results", [])

    rows = rows_from_launch_results(results)

    # Tabs
    tab_all, tab_provider, tab_year = st.tabs(["All Data", "Filter by Provider", "Filter by Year"])

    # ========================================
    # TAB 1 — ALL DATA
    # ========================================
    with tab_all:
        st.subheader("All Launch Data")

        for l in results:
            name = l.get("launch_service_provider", {}).get("name")
            rocket = l.get("rocket", {}).get("configuration", {}).get("name")
            year = (l.get("window_start") or '')[:4]
            mission = l.get("mission", {}).get("name")
            desc = l.get("mission", {}).get("description")

            st.markdown(f"""
            **Provider:** {name}  
            **Rocket:** {rocket}  
            **Year:** {year}  
            **Mission:** {mission}  

            {desc}
            """)
            st.markdown("---")

        # Export buttons
        st.subheader("Export Launch Data")
        fmt = st.selectbox("Format", ["csv", "xlsx"])
        st.download_button(
            "Download Launch Data",
            data=saveLaunchData(rows, fmt),
            file_name=f"launch_data.{fmt}",
            mime="text/csv" if fmt == "csv" else "application/vnd.ms-excel"
        )

    # ========================================
    # TAB 2 — PROVIDER FILTER
    # ========================================
    with tab_provider:
        st.subheader("Filter Launches by Provider")

        providers = sorted({
            (l.get("launch_service_provider") or {}).get("name")
            for l in results if l.get("launch_service_provider")
        })

        selected = st.selectbox("Choose Provider", providers)

        for l in results:
            name = (l.get("launch_service_provider") or {}).get("name")
            if name == selected:
                rocket = l.get("rocket", {}).get("configuration", {}).get("name")
                year = (l.get("window_start") or '')[:4]
                mission = l.get("mission", {}).get("name")
                desc = l.get("mission", {}).get("description")
                
                st.markdown(f"""
                **Provider:** {name}  
                **Rocket:** {rocket}  
                **Year:** {year}  
                **Mission:** {mission}  

                {desc}
                """)
                st.markdown("---")

    # ========================================
    # TAB 3 — YEAR FILTER
    # ========================================
    with tab_year:
        st.subheader("Filter Launches by Year")

        year_input = st.text_input("Enter Year", "2020")

        found = False
        for launch in results:
            date = launch.get("window_start")
            if date and date.startswith(year_input):
                provider = launch.get("launch_service_provider", {}).get("name")
                rocket = launch.get("rocket", {}).get("configuration", {}).get("name")
                mission = launch.get("mission", {}).get("name")
                desc = launch.get("mission", {}).get("description")

                st.markdown(f"""
                **Provider:** {provider}  
                **Rocket:** {rocket}  
                **Year:** {year_input}  
                **Mission:** {mission}  

                {desc}
                """)
                st.markdown("---")
                found = True

        if not found:
            st.info("No launches found for that year.")

def build_zip_from_images(image_list):
    """image_list must be: [(name, url), (name, url), ...]"""

    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for name, img_url in image_list:
            try:
                img_bytes = requests.get(img_url).content
                safe_name = name.replace(" ", "_")
                zipf.writestr(f"{safe_name}.jpg", img_bytes)
            except:
                pass  # skip failed downloads

    zip_buffer.seek(0)
    return zip_buffer
  
def main():
    st.title("Space Data Explorer")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Celestial Bodies", "Astronauts", "Spacecraft", "Launchers", "Launch Data"])
# TAB 1 — CELESTIAL BODIES
    with tab1:
        st.subheader("Celestial Bodies Data")
        
        # Filter input
        name_filter = st.text_input("Filter by Name (partial match, case-insensitive)", "")
        
        limit = st.slider("Number of Celestial Bodies to Display", min_value=1, max_value=100, value=5)
        
        # Get celestial_bodies_images without displaying
        celestial_bodies_images = sd_CelestialBodies(limit=limit, display=False, name_filter=name_filter)
        
        # Display the download button below the slider
        if celestial_bodies_images:
            zip_buffer = build_zip_from_images(celestial_bodies_images)
            st.download_button(
                "Download All Celestial Bodies Images as ZIP",
                data=zip_buffer,
                file_name="celestial_bodies_images.zip",
                mime="application/zip",
                key="celestial_download"  # Unique key to avoid ID conflict
            )
        else:
            st.info("No celestial body images available for download.")
        
        # Now display the celestial bodies
        sd_CelestialBodies(limit=limit, display=True, name_filter=name_filter)
    
# TAB 2 — ASTRONAUTS
    # TAB 2 — ASTRONAUTS
    with tab2:
        st.subheader("Astronauts Data")
        
        # First, fetch a larger set of data to populate filter options
        _, astronauts_data = sd_Astronauts(limit=100, display=False)
        
        # Extract unique agencies and nationalities for filters
        agencies = sorted(set([a.get("agency", {}).get("name", "Unknown") for a in astronauts_data if a.get("agency", {}).get("name", "Unknown") != "Unknown"]))
        nationalities = sorted(set([a["nationality"][0]['nationality_name'] if a.get("nationality") else "Unknown" for a in astronauts_data if (a.get("nationality") and a["nationality"][0]['nationality_name'] != "Unknown")]))
        
        # Filter inputs
        agency_filter = st.selectbox("Filter by Agency", ["All"] + agencies)
        nationality_filter = st.selectbox("Filter by Nationality", ["All"] + nationalities)
        min_flights = st.number_input("Min Total Flights", min_value=0, value=0, step=1)
        max_flights = st.number_input("Max Total Flights", min_value=0, value=100, step=1)
        
        limit = st.slider("Number of Astronauts to Display", min_value=1, max_value=100, value=5)
        
        # Convert "All" to None for filtering
        agency_filter = None if agency_filter == "All" else agency_filter
        nationality_filter = None if nationality_filter == "All" else nationality_filter
        
        # Get filtered astronaut images and data
        astronaut_images, _ = sd_Astronauts(
            limit=limit, 
            display=False, 
            agency_filter=agency_filter, 
            nationality_filter=nationality_filter, 
            min_flights=min_flights, 
            max_flights=max_flights
        )
        
        # Display the download button
        if astronaut_images:
            zip_buffer = build_zip_from_images(astronaut_images)
            st.download_button(
                "Download All Astronaut Images as ZIP",
                data=zip_buffer,
                file_name="astronaut_images.zip",
                mime="application/zip",
                key="astronaut_download"  # Unique key to avoid ID conflict
            )
        else:
            st.info("No astronaut images available for download.")
        
        # Now display the filtered astronauts
        sd_Astronauts(
            limit=limit, 
            display=True, 
            agency_filter=agency_filter, 
            nationality_filter=nationality_filter, 
            min_flights=min_flights, 
            max_flights=max_flights
        )
               
# TAB 3 — SPACECRAFT 
    with tab3:
        st.subheader("Spacecraft Data")

        # Fetch data for filters
        fetch_limit = 100
        url = f"https://lldev.thespacedevs.com/2.3.0/spacecraft/?mode=detailed&limit={fetch_limit}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            results = data["results"]

            statuses = sorted(set(
                s.get("status", {}).get("name", "Unknown")
                for s in results
                if s.get("status")
            ))

            in_space_values = ["True", "False"]

        else:
            statuses = []
            in_space_values = []

        # Filters
        status_filter = st.selectbox("Filter by Status", ["All"] + statuses)
        in_space_filter = st.selectbox("Filter by In Space", ["All"] + in_space_values)

        limit = st.slider("Number of Spacecraft to Display", 1, 100, 5)

        # Convert text to actual filter values
        status_filter = None if status_filter == "All" else status_filter
        in_space_filter = (
            None if in_space_filter == "All" else
            (True if in_space_filter == "True" else False)
        )

        # Fetch images
        spacecraft_images = sd_Spacecraft(
            limit=limit,
            display=False,
            in_space_filter=in_space_filter,
            status_filter=status_filter
        )

        # Download ZIP
        if spacecraft_images:
            zip_buffer = build_zip_from_images(spacecraft_images)
            st.download_button(
                "Download All Spacecraft Images as ZIP",
                data=zip_buffer,
                file_name="spacecraft_images.zip",
                mime="application/zip",
                key="spacecraft_download"
            )
        else:
            st.info("No spacecraft images available for the selected filters.")

        # Display spacecraft
        sd_Spacecraft(
            limit=limit,
            display=True,
            in_space_filter=in_space_filter,
            status_filter=status_filter
        )


# TAB 4 — LAUNCHERS
    with tab4:
        st.subheader("Launchers Data")

        # --- Fetch data for filter options ---
        fetch_url = "https://lldev.thespacedevs.com/2.3.0/launchers/?mode=detailed&limit=200"
        fetch_response = requests.get(fetch_url)

        if fetch_response.status_code == 200:
            data = fetch_response.json()
            all_launchers = data["results"]

            statuses = sorted(set(
                l.get("status", {}).get("name", "Unknown")
                for l in all_launchers
            ))

            flight_proven_values = ["True", "False"]
            attempted_list = sorted(set(l.get("attempted_landings", 0) for l in all_launchers))
            successful_list = sorted(set(l.get("successful_landings", 0) for l in all_launchers))

        else:
            statuses = []
            flight_proven_values = []
            attempted_list = []
            successful_list = []

        # --- UI FILTERS ---
        status_filter = st.selectbox("Filter by Status", ["All"] + statuses)
        flight_proven_filter = st.selectbox("Filter by Flight Proven", ["All", "True", "False"])
        attempted_landings_filter = st.selectbox("Filter by Attempted Landings", ["All"] + list(map(str, attempted_list)))
        successful_landings_filter = st.selectbox("Filter by Successful Landings", ["All"] + list(map(str, successful_list)))

        # Convert filters
        status_filter = None if status_filter == "All" else status_filter
        flight_proven_filter = None if flight_proven_filter == "All" else (flight_proven_filter == "True")
        attempted_landings_filter = None if attempted_landings_filter == "All" else int(attempted_landings_filter)
        successful_landings_filter = None if successful_landings_filter == "All" else int(successful_landings_filter)

        # --- LIMIT SLIDER ---
        limit = st.slider("Number of Launchers to Display", min_value=1, max_value=100, value=5)

        # --- FIRST CALL: FETCH IMAGES ONLY ---
        launcher_images = sd_Launchers(
            limit=limit,
            display=False,
            status_filter=status_filter,
            flight_proven_filter=flight_proven_filter,
            attempted_landings_filter=attempted_landings_filter,
            successful_landings_filter=successful_landings_filter
        )

        # --- DOWNLOAD BUTTON (below slider) ---
        if launcher_images:
            zip_buffer = build_zip_from_images(launcher_images)
            st.download_button(
                "Download All Launcher Images as ZIP",
                data=zip_buffer,
                file_name="launcher_images.zip",
                mime="application/zip",
                key="launcher_download"
            )
        else:
            st.info("No launcher images available for download.")

        # --- SECOND CALL: DISPLAY RESULTS ---
        sd_Launchers(
            limit=limit,
            display=True,
            status_filter=status_filter,
            flight_proven_filter=flight_proven_filter,
            attempted_landings_filter=attempted_landings_filter,
            successful_landings_filter=successful_landings_filter
        )


# TAB 5 — LAUNCH DATA BROWSER
    with tab5:
        st.subheader("Launch Data Browser")
        limit = st.slider("Number of Data to Display", min_value=1, max_value=100, value=5)
        sdLaunch(limit=limit)

def load_with_spinner(key, message, load_function, *args, **kwargs):
    st.session_state[key] = True
    with st.spinner(message):
        result = load_function(*args, **kwargs)
    st.session_state[key] = False
    return result