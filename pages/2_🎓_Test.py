import streamlit as st
import pandas as pd
import random
from database import insert_answer

############################
# 1. Charger et préparer les données
@st.cache_data
def load_data():
    try:
        data = pd.read_csv("data.csv")
        return data
    except FileNotFoundError:
        st.error("Error: Data file 'data.csv' not found.")
        st.stop()
df = load_data()

categories = df["Category"].unique()  
subcategories = df["Subcategory"].unique()


##########
if 'username' in st.session_state:
    st.write(f"Bienvenue, {st.session_state.username}!")
if 'username' not in st.session_state:
    st.write("No username found in session state.")

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
    filtered_df=df
    #filtered_df = pd.DataFrame(columns=df.columns)  # Empty DataFrame

else:
    filtered_df = df[
        (df["Category"].isin(selected_categories))
        & (df["Subcategory"].isin(selected_subcategories))
    ].copy()
#######################################
mots_francais = filtered_df['French'].tolist()
mots_allemands = filtered_df['Allemand'].tolist()
vocabulaire = dict(zip(mots_francais, mots_allemands))
#######################################
def on_change_callback():
    """This function will be called when the text input's value changes."""
    st.session_state.is_disabled = False
    is_correct = st.session_state.input_text == vocabulaire[st.session_state.mot_francais]
    if is_correct:
        st.success('Bien joué!', icon="✅")
    else:
        st.error('À réviser!', icon="🚨")

    st.session_state.answers.append(st.session_state.input_text)
    st.session_state.questions.append(st.session_state.mot_francais)
    # Write the result into the database
    # --- Get the word ---
    german_word = vocabulaire[st.session_state.mot_francais]
    # --- Insert Answer into Database ---
    
    # Replace with your actual user ID retrieval method (e.g., from session state, etc.):
    user_id = st.session_state.get("user_id")
    if user_id:
        insert_answer(st.session_state.user_id, german_word, is_correct)
    else:
        st.warning("User ID not found. Answer not saved to database.")
    

# Initialize session state
if "mot_francais" not in st.session_state:
    st.session_state.mot_francais = ""
if "mot_allemand" not in st.session_state:
    st.session_state.mot_allemand = ""
if "input_text" not in st.session_state:
    st.session_state.input_text = ""
if "answers" not in st.session_state:
    st.session_state.answers = []
if "questions" not in st.session_state:
    st.session_state.questions = []
if 'is_disabled' not in st.session_state:
    st.session_state.is_disabled = False
if 'mot_deja_donnes' not in st.session_state:
    st.session_state.mot_deja_donnes = []

# 2. Initialiser les compteurs de bonnes/mauvaises réponses
if 'bonnes_reponses' not in st.session_state:
    st.session_state.bonnes_reponses = 0
if 'mauvaises_reponses' not in st.session_state:
    st.session_state.mauvaises_reponses = 0


# 3. Fonction pour choisir un mot français aléatoire
def choisir_mot():
    if len(st.session_state.mot_deja_donnes) == len(mots_francais):
        st.warning("Tous les mots ont été utilisés !")
        return None  # Or handle this case differently
    
    while True:
        mot_aleatoire = random.choice(mots_francais)
        if mot_aleatoire not in st.session_state.mot_deja_donnes:
            st.session_state.mot_deja_donnes.append(mot_aleatoire)
            return mot_aleatoire

# Fonction pour verouiller le bouton nouveau mot tant qu'une réponse n'est pas entrée
def lock_button():
    st.session_state.is_disabled = True

# Reset button
if st.button("Nouveau mot", type="secondary", icon="💥", disabled = st.session_state.is_disabled, on_click=lock_button):
    st.session_state.mot_francais = choisir_mot()
    st.session_state.input_text = ""
    st.write("Entrez la traduction en allemand (ß):")
    st.write(st.session_state.mot_francais)
    st.text_input("Enter some text:", key="input_text", on_change=on_change_callback)
    
if st.button("Nouvelle session", type="primary"):
    st.session_state.answers = []
    st.session_state.questions = []
    st.session_state.mot_deja_donnes = []
    st.session_state.is_disabled = False
    st.rerun()

# Create a dataframe from session state data
df_answers = pd.DataFrame({
    "Question (Français)": st.session_state.questions,
    "Réponse de l'utilisateur": st.session_state.answers,
})

# Add a column to indicate correct/incorrect answers
df_answers["Correct ?"] = df_answers["Question (Français)"].apply(lambda x: vocabulaire.get(x)) == df_answers["Réponse de l'utilisateur"]

# Display the dataframe
st.dataframe(df_answers)