# app.py
import streamlit as st
import json
import os
from PIL import Image

# --- App Configuration ---
st.set_page_config(layout="wide", page_title="OCR Data Viewer")

# --- Caching ---
@st.cache_data
def load_data(json_path):
    """Loads the JSON data from the specified file path."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

# NEW: Cached function to get unique languages
@st.cache_data
def get_unique_languages(data):
    """Extracts unique languages from the dataset."""
    return ["All"] + sorted(list(set(item['lang'] for item in data)))


# --- Main Application Logic ---
st.title("🖼️ OCR Data Viewer")
st.markdown("Use the sidebar to filter by language and the buttons to navigate.")

# --- Data Loading ---
JSON_FILE_PATH = 'data.json'
IMAGE_BASE_DIR = 'images'

data = load_data(JSON_FILE_PATH)

if data is None:
    st.error(f"Error: The file '{JSON_FILE_PATH}' was not found.")
    st.stop()

# --- State Management ---
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0

# --- Sidebar for Filtering ---
st.sidebar.header("Filter Options")
unique_langs = get_unique_languages(data)
selected_lang = st.sidebar.selectbox(
    "Filter by Language",
    options=unique_langs,
    key='selected_language' # Use a key to access this widget's value
)

# --- Filtering Logic ---
# NEW: Filter the data based on the sidebar selection
if selected_lang == "All":
    filtered_data = data
else:
    filtered_data = [item for item in data if item['lang'] == selected_lang]

# NEW: Reset index if the filter changes or the index is out of bounds
if 'last_lang' not in st.session_state or st.session_state.last_lang != selected_lang:
    st.session_state.current_index = 0
st.session_state.last_lang = selected_lang

if not filtered_data:
    st.warning("No data found for the selected language.")
    st.stop()


# --- Navigation ---
nav_cols = st.columns([0.1, 0.8, 0.1])

def change_index(change):
    """Function to update the index, wrapping around."""
    new_index = st.session_state.current_index + change
    st.session_state.current_index = new_index % len(filtered_data) # Use filtered_data length

with nav_cols[0]:
    if st.button("⬅️ Previous"):
        change_index(-1)

with nav_cols[2]:
    if st.button("Next ➡️"):
        change_index(1)

st.divider()

# --- Data Display ---
index = st.session_state.current_index
# Ensure index is not out of bounds after filtering
if index >= len(filtered_data):
    index = 0
    st.session_state.current_index = 0

item = filtered_data[index]

st.write(f"Showing item **{index + 1}** of **{len(filtered_data)}** (filtered)")

col1, col2 = st.columns(2)

with col1:
    st.subheader(f"Image ({item['category'].capitalize()})")
    image_filename = os.path.basename(item["image"])
    image_path = os.path.join(IMAGE_BASE_DIR, image_filename)

    if os.path.exists(image_path):
        st.image(image_path, use_column_width=True, caption=f"Image: {image_filename}")
    else:
        st.error(f"Image not found at path: {image_path}")
        st.warning("Please check your IMAGE_BASE_DIR and ensure image files exist.")

    

with col2:
    st.subheader("Instruction")
    st.info(item["instruction"])

    st.subheader("Output")
    st.text_area(
        "Transcription",
        value=item["output"],
        height=250,
        disabled=True,
        label_visibility="collapsed"
    )

st.divider()

# --- Metadata Display ---
meta_cols = st.columns(2)
# meta_cols[0].metric("Language", item["lang"].upper())
# meta_cols[0].metric("Category", item["category"].capitalize())