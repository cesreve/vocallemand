import streamlit as st
import pandas as pd
from database import fetch_answers_from_db

# Database connection URL (from Streamlit secrets)
DATABASE_URL = st.secrets["my_database"]["DATABASE_URL"]

def fetch_and_join_data(user_id, selected_categories, selected_subcategories):
    """Récupère les données du CSV et de la base de données, les joint et renvoie un DataFrame."""
    try:
        # 1. Lire les données CSV
        df_csv = pd.read_csv("data.csv")
        print("Read data: ", __file__)
        # --- Appliquer les filtres de catégorie et de sous-catégorie au DataFrame CSV en premier ---
        if selected_categories:
            df_csv = df_csv[df_csv["Category"].isin(selected_categories)]
        if selected_subcategories:
            df_csv = df_csv[df_csv["Subcategory"].isin(selected_subcategories)]

        # 2. Récupérer les réponses de la base de données
        df_answers = fetch_answers_from_db(user_id)
        if df_answers is None:
            return None  # Arrêter si une erreur de base de données s'est produite

        # 3. Joindre les DataFrames
        merged_df = pd.merge(df_csv, df_answers, left_on="Allemand", right_on="german_word", how='left')
        
        return merged_df

    except (FileNotFoundError, pd.errors.MergeError) as e:
        st.error(f"Erreur: {e}")
        return None

# Streamlit app
st.title("Merged Data (CSV and Database)")

# --- Sidebar Filters ---
with st.sidebar:
    st.header("Filtres")
    selected_categories = st.multiselect("Categories", pd.read_csv("data.csv")["Category"].unique())
    subcategories_df = pd.read_csv("data.csv")
    available_subcategories = subcategories_df[subcategories_df["Category"].isin(selected_categories)]["Subcategory"].unique().tolist()
    selected_subcategories = st.multiselect("Subcategories", available_subcategories)

# Get user_id from session state (ensure user authentication is in place)
user_id = st.session_state.get("user_id")

if user_id: # Display only if user is logged in
    merged_df = fetch_and_join_data(user_id, selected_categories, selected_subcategories)
    merged_df['answer_date'] = pd.to_datetime(merged_df['answer_date'], errors='coerce')
    merged_df['greater_than_3_days'] = (pd.Timestamp.now() - merged_df['answer_date']) > pd.Timedelta(days=3)
    merged_df = merged_df[["Allemand", "is_correct", "answer_date", "greater_than_3_days"]].sort_values(by=['Allemand', 'answer_date'])
    filtered_df = merged_df[ (merged_df['greater_than_3_days']) | (merged_df['answer_date'].isnull()) ]
    if filtered_df is not None:
        st.dataframe(filtered_df)
else:
    st.warning("Please log in to view your data.")