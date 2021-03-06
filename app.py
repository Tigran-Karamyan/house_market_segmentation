import streamlit as st
import pandas as pd
import pydeck as pdk
from urllib.error import URLError

st.set_page_config(layout="wide")

# Import Csv
df = pd.read_csv("data/prices_usd.csv")

# Preprocess House Data
streamlit_df = df[['addr', 'num_rooms', 'ruler', 'num_floor', 'num_price',
                   'sale_category', 'lat', 'lon', 'dominant_topic', 'topic_percentage_contrib']]
streamlit_df.dominant_topic = streamlit_df.dominant_topic.apply(int)
streamlit_df.lon = streamlit_df.lon.apply(float)
streamlit_df.lat = streamlit_df.lat.apply(float)

st.title("Housing Market Segmentation")
st.write("Description")

cluster_sidebar_selectobox_input = sorted(list(set(streamlit_df.dominant_topic.tolist())))
st.sidebar.markdown('### Select Cluster and Sale Category')
cluster_selected = [topic for topic in cluster_sidebar_selectobox_input if st.sidebar.checkbox(f"Cluster: {topic + 1}", True)]
sale_category_selected = st.sidebar.radio("Category", set(streamlit_df.sale_category))

# Create a Dataset for Layers Cities Location and Cities Names
filtered_data = streamlit_df[(streamlit_df.dominant_topic.isin(cluster_selected)) & (streamlit_df.sale_category == sale_category_selected)]

try:
    ALL_LAYERS = {
        "House Location": pdk.Layer(
            "ScatterplotLayer",
            data=filtered_data,
            auto_highlight=True,
            pickable=True,
            opacity=0.8,
            stroked=True,
            filled=True,
            radius_scale=5,
            radius_min_pixels=1,
            radius_max_pixels=100,
            line_width_min_pixels=1,
            get_position=["lon", "lat"],
            get_fill_color=["255 / (dominant_topic + 1) ", "(dominant_topic + 1) * 42", "255 / (dominant_topic + 1) * 2"],
            get_line_color=[0, 0, 0],
            get_radius='topic_percentage_contrib * 10'

        ),
        "Floor": pdk.Layer(
            "TextLayer",
            data=filtered_data,
            get_position=["lon", "lat - 0.0001"],
            get_text="num_floor",
            get_color=[0, 0, 0],
            get_size=15,
            get_alignment_baseline="'bottom'",
        ),
        "Rooms": pdk.Layer(
            "TextLayer",
            data=filtered_data,
            get_position=["lon", "lat  - 0.0002"],
            get_text="num_rooms",
            get_color=[0, 0, 0],
            get_size=15,
            get_alignment_baseline="'bottom'",
        ),
        "House Price": pdk.Layer(
            "TextLayer",
            data=filtered_data,
            get_position=["lon", "lat"],
            get_text="num_price",
            get_color=[0, 0, 0],
            get_size=15,
            get_alignment_baseline="'bottom'",
        )
    }
    st.sidebar.markdown('### Map Layers')
    selected_layers = [layer for layer_name, layer in ALL_LAYERS.items() if st.sidebar.checkbox(layer_name, True)]
    if selected_layers:
        st.pydeck_chart(pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state={"latitude": 40.1872,
                                "longitude": 44.5152, "zoom": 10, "pitch": 50},
            layers=selected_layers,
        ))
    else:
        st.error("Please choose at least one layer above.")
except URLError as e:
    st.error("""
        **This demo requires internet access.**

        Connection error: %s
    """ % e.reason)