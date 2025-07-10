import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import altair as alt
from datetime import datetime, timedelta

st.set_page_config(page_title="Heffernan Motors")


tab1, tab2, tab3, tab4 = st.tabs(["New Cars", "Used Cars", "Car Aftercare", "Contact Us"])

with tab2:
    st.write("Coming Soon")
with tab3:
    st.write("Coming Soon")
with tab4:
    st.write("PHONE: 044 93 XXXXX")
    st.write("EMAIL: heffernanmotors@gmail.com")


st.title("Heffernan Motors")

with st.expander("About Us"):
    st.markdown("""
    **Heffernan Motors: Your Trusted Car Partner Across Ireland.**
    
    For over 35 years, Heffernan Motors has been a leading name in the Irish car market. 
    With five conveniently located showrooms nationwide, we offer an extensive selection 
    of new and quality used vehicles. Our dedicated team across Ireland is committed to 
    providing exceptional service, expert advice, and genuine value, making your car journey 
    seamless. Discover your perfect drive with Heffernan Motors today.
    """)


#Load data
@st.cache_data
def load_data():
	return pd.read_csv("car_data.csv")

data= load_data()
st.markdown("---")

#Displays the dataset
#st.dataframe(data.reset_index(drop=True))

#ADDING SIDEBAR FILTERS
st.sidebar.header("Filter Options")

make_options = ["All"] + sorted(data["make"].unique().tolist())
model_options = ["All"] + sorted(data["model"].unique().tolist())
engine_options = ["All"] + sorted(data["engine"].dropna().unique().tolist())
fuel_options = ["All"] + sorted(data["fuelType"].dropna().unique().tolist())
body_options = ["All"] + sorted(data["body"].dropna().unique().tolist())

make_filter= st.sidebar.selectbox("Select Make", options= make_options)
model_filter= st.sidebar.selectbox("Select Model", options= model_options)
year_filter= st.sidebar.slider("Year Range", min_value=int(data["year"].min()),
		max_value=int(data["year"].max()), value=(int(data["year"].min()), int(data["year"].max())))
price_filter= st.sidebar.slider("Price Range", min_value=int(data["standardPrice"].min()),
		max_value=int(data["standardPrice"].max()), value=(int(data["standardPrice"].min()), int(data["standardPrice"].max())))
engine_filter = st.sidebar.selectbox("Select Engine", options=engine_options)
fuel_filter = st.sidebar.selectbox("Select Fuel Type", options=fuel_options)
body_filter = st.sidebar.selectbox("Select Body Type", options=body_options)

filtered_data = data[
    ((data["make"] == make_filter) | (make_filter == "All")) &
    ((data["model"] == model_filter) | (model_filter == "All")) &
    ((data["engine"] == engine_filter) | (engine_filter == "All")) &
    ((data["fuelType"] == fuel_filter) | (fuel_filter == "All")) &
    ((data["body"] == body_filter) | (body_filter == "All")) &
    (data["year"].between(year_filter[0], year_filter[1])) &
    (data["standardPrice"].between(price_filter[0], price_filter[1]))]


#st.write("### Filtered Results", filtered_data)

left_col, right_col = st.columns([3, 2])  

with left_col:
    st.write("### Filtered Results", filtered_data.drop(columns=["image_url"]))

with right_col:
    st.header("Optional Add-Ons")
    gps = st.checkbox("GPS Navigation System (€500)")
    heated_seats = st.checkbox("Heated Seats (€1,200)")
    extended_warranty = st.checkbox("Extended Warranty (€1,000)")
    tinted_windows = st.checkbox("Tinted Windows (€400)")
    parking_assist = st.checkbox("360 Parking Assist (€300)")

    addons_total = 0
    if gps: addons_total += 500
    if heated_seats: addons_total += 1200
    if extended_warranty: addons_total += 1000
    if tinted_windows: addons_total += 400
    if parking_assist: addons_total += 300

    st.markdown(f"**Total Add-Ons Cost:** €{addons_total:,}")

#DISPLAYING IMAGE OF CAR
st.markdown("---")
if not filtered_data.empty:
    car_selector = filtered_data.apply(lambda row: f"{row['make']} {row['model']} ({row['year']})", axis=1)
    selected_car = st.selectbox("Select a Car to View Details", car_selector)

    selected_row = filtered_data[
        filtered_data.apply(lambda row: f"{row['make']} {row['model']} ({row['year']})" == selected_car, axis=1)].iloc[0]

    st.subheader(f"{selected_row['make']} {selected_row['model']} ({selected_row['year']})")

    if pd.notna(selected_row.get('image_url', None)):
        st.image(selected_row['image_url'], caption="Car Image", use_column_width=True)
    else:
        st.info("No image available for this car.")

    st.markdown(f"**Engine:** {selected_row['engine']}")
    st.markdown(f"**Fuel Type:** {selected_row['fuelType']}")
    st.markdown(f"**Body Type:** {selected_row['body']}")
    total_price = selected_row['standardPrice'] + addons_total
    st.markdown(f"**Standard Price (€):** {selected_row['standardPrice']:,}")
    st.markdown(f"**Add-Ons Cost:** €{addons_total:,}")
    st.markdown(f"**Total Price (€):** {total_price:,}")
else:
    st.warning("No cars match your filter criteria.")

#FAQ SECTION
st.markdown("---")
st.subheader("🧠 Frequently Asked Questions")

faq_options = [
    "Select a Question",
    "Where are your showrooms located?",
    "I would like to speak to a Sales Rep.",
    "What are the Most Popular Cars?"
    ]

selected_faq = st.selectbox("Select a question", faq_options)

if selected_faq == "Where are your showrooms located?":
    st.subheader("📍 Showroom Locations")
    st.write("We have 5 locations in Ireland: Dublin, Cork, Galway, Belfast and Westmeath")

    showroom_locations = pd.DataFrame({
        "showroom": ["Dublin", "Cork", "Galway", "Belfast", "Westmeath"],
        "lat": [53.3498, 51.8985, 53.2707, 54.5973, 53.5346],
        "lon": [-6.2603, -8.4756, -9.0568, -5.9301, -7.3436]})

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=showroom_locations,
        get_position='[lon, lat]',
        get_color='[255, 140, 0, 160]', 
        get_radius=10000, 
        pickable=True,
    )

    view_state = pdk.ViewState(
        latitude=53.5,
        longitude=-7,
        zoom=6,
        pitch=0,
    )

    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        #map_style="mapbox://styles/mapbox/satellite-v9"
        #map_style="mapbox://styles/mapbox/dark-v10"
        map_style="mapbox://styles/mapbox/outdoors-v11" 
    )

    st.pydeck_chart(deck)
    #st.map(showroom_locations.rename(columns={"lat": "latitude", "lon": "longitude"}))
    #st.dataframe(showroom_locations, use_container_width=True)

elif selected_faq == "Select a Question":
    st.info("Please select a question from the dropdown above.")

if selected_faq == "I would like to speak to a Sales Rep.":
    st.subheader("User Information Form")
    st.markdown("Please fill out this form and a Sales Representitive will be in contact")

    form_values = {"name": None, "contact_info": None, "car_info": None, "location": None}

    with st.form(key="user_info_form"):
        form_values["name"] = st.text_input("Enter your name: ")
        form_values["contact_info"] = st.text_input("Enter a phone or email address: ")
        form_values["car_info"] = st.text_input("What car are you interested in: ")
        form_values["location"] = st.selectbox("Nearest Location", ["Dublin","Cork","Galway","Belfast","Westmeath"])

        submit_button = st.form_submit_button()
        if submit_button:
            if not all(form_values.values()):
                st.warning("Please fill in all of the fields")
            else:
                st.balloons()
                st.write("Thank you, one of our Sales Reps. will be in contact with you")

if selected_faq == "What are the Most Popular Cars?":
    #st.subheader("🚗 Top Selling Cars")

    @st.cache_data
    def load_orders():
        df = pd.read_csv("popular_cars.csv")
        df['order_date'] = pd.to_datetime(df['order_date'])  
        return df

    orders_df = load_orders()

    min_date = orders_df['order_date'].min()
    max_date = orders_df['order_date'].max()

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", min_value=min_date.date(), max_value=max_date.date(), value=min_date.date())
    with col2:
        end_date = st.date_input("End Date", min_value=min_date.date(), max_value=max_date.date(), value=max_date.date())

    mask = (orders_df['order_date'] >= pd.to_datetime(start_date)) & (orders_df['order_date'] <= pd.to_datetime(end_date))
    filtered_df = orders_df[mask]

    top_cars = filtered_df['Car'].value_counts().head(10).reset_index()
    top_cars.columns = ['Car', 'Orders']

    start_str = start_date.strftime("%d/%m/%Y")
    end_str = end_date.strftime("%d/%m/%Y")

    chart = alt.Chart(top_cars).mark_bar(
        cornerRadiusTopLeft=8,
        cornerRadiusTopRight=8
    ).encode(
        x=alt.X('Orders:Q', title='Number of Orders'),
        y=alt.Y('Car:N', sort='-x', title='Car Model'),
        color=alt.Color('Car:N', legend=None, scale=alt.Scale
                        #(scheme='category20b')),
                        #(scheme='tableau10')),
                        (scheme='darkblue')),
        tooltip=['Car', 'Orders']
    ).properties(
        title=f'🚗 Top Selling Cars ({start_str} to {end_str})',
        height=600
    ).configure_axis(
        labelFontSize=13,
        titleFontSize=15
    ).configure_title(
        fontSize=20,
        font='Helvetica',
        anchor='start',
        color='white'
    )

    st.altair_chart(chart, use_container_width=True)
