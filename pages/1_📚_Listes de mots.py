import streamlit as st
import pandas as pd
from gtts import gTTS
import base64
from io import BytesIO

# --- Helper Function for TTS ---
@st.cache_data
def get_audio_base64(text):
    tts = gTTS(text=text, lang='de') 
    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    b64 = base64.b64encode(fp.read()).decode()
    return f'<audio controls src="data:audio/mpeg;base64,{b64}"/>'

# --- Load CSV Data ---
@st.cache_data
def load_data():
    try:
        data = pd.read_csv("data.csv")
        return data
    except FileNotFoundError:
        st.error("Error: Data file 'data.csv' not found.")
        st.stop()

# --- Streamlit App ---
#st.title(':flag-fr: Français-Allemand :flag-de:')
st.set_page_config(page_title="Vocabulaire Allemand", page_icon=":de:", layout="centered")

st.title('My streamlit app')
df = load_data()
# --- Initial Values for Filters and Checkbox ---
if "show_french" not in st.session_state:
    st.session_state.show_french = True
categories = df["Category"].unique()  
subcategories = df["Subcategory"].unique()

# --- Sidebar ---
with st.sidebar:
    st.header("Filtres")

    # --- Filter Available Categories ---
    selected_categories = st.multiselect(
        "Categories",
        df["Category"].unique(),
        default=None,
        key="selected_categories",
    )

    available_subcategories = df.loc[df["Category"].isin(selected_categories), "Subcategory"].unique()

    selected_subcategories = st.multiselect('Sous-categories', available_subcategories, default=None)

# --- Filter DataFrame ---
if not len(selected_categories)>0 and not len(available_subcategories)>0:
    st.warning("Please select at least one category or subcategory.")
    filtered_df = pd.DataFrame(columns=df.columns)  # Empty DataFrame
else:
    filtered_df = df[
        (df["Category"].isin(selected_categories))
        & (df["Subcategory"].isin(selected_subcategories))
    ].copy()

    # --- Add TTS Column --- (unchanged)
    filtered_df.loc[:, 'Écouter'] = filtered_df['Allemand'].apply(get_audio_base64)


# --- Show/Hide Columns ---
col1, col2 = st.columns(2)
with col1:
    show_allemand = st.checkbox('Montrer Allemand', value=True)
with col2:
    show_french = st.checkbox('Montrer Français', value=st.session_state.show_french)

columns_to_show = ['Category', 'Subcategory', 'Écouter', 'Phrase'] 
if show_french and not show_allemand:
    columns_to_show = ['French', 'Écouter'] 
if show_allemand and not show_french:
    columns_to_show = ['Allemand', 'Écouter', 'Phrase'] 
if show_allemand and show_french:
    columns_to_show = ['French', 'Allemand', 'Écouter', 'Phrase'] 


# --- Slider ---
if len(filtered_df) > 0:
    num_words = st.slider('Nombre de mots', min_value=1, max_value=len(filtered_df), value=5)
    displayed_df = filtered_df[columns_to_show].head(num_words)

# --- Display DataFrame with HTML for Audio ---
if not filtered_df.empty:
    st.write(
        displayed_df.to_html(
            escape=False, formatters={"Écouter": lambda x: x}
        ),
        unsafe_allow_html=True,
    )