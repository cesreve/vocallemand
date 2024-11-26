import streamlit as st
from auth import authenticate#, create_user

# session state
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
# if "username" not in st.session_state:
#     st.session_state["username"] = None
# if "user_id" not in st.session_state:
#     st.session_state["user_id"] = None

st.set_page_config(page_title="Vocabulaire Allemand", page_icon=":de:", layout="centered")

st.title("Bienvenue sur l'application de vocabulaire français-allemand !")

st.write("""
Cette application web simple vous aide à apprendre et à pratiquer le vocabulaire français-allemand. 
Elle charge les données de vocabulaire à partir d'un fichier CSV (`data.csv`) et fournit une interface conviviale 
pour parcourir, filtrer et écouter les mots et les phrases.
""")

st.header("Fonctionnalités")
st.markdown("""
- **Filtrer le vocabulaire :** Filtrez les mots et les phrases par catégorie et sous-catégorie.
- **Écouter la prononciation :** Écoutez la prononciation allemande de chaque mot ou expression à l'aide de la synthèse vocale.
- **Afficher/Masquer les colonnes :** Choisissez d'afficher les colonnes français, allemand ou les deux.
- **Contrôler le nombre de mots :** Utilisez un curseur pour ajuster le nombre d'éléments de vocabulaire affichés.
""")

st.write("Commencez votre apprentissage dès aujourd'hui !")

# --- Sidebar with Login/Signup ---
with st.sidebar:
    st.subheader("Authentification")

    if not st.session_state["authenticated"]:
        st.session_state.username = st.text_input("Nom d'utilisateur")
        st.text_input("Mot de passe", type="password", key="password", on_change=authenticate )
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Connexion"):
                if authenticate():
                    st.success("Connecté avec succès!")
                    st.rerun()  # Rerun to show authenticated content
                else:
                    st.error("Nom d'utilisateur ou mot de passe incorrect.")
        #with col2:
        #   if st.button("Créer"):
        #        create_user(st.session_state.username, st.session_state.password)
    else:
        if 'username' in st.session_state:
            st.write(f"Bienvenue, {st.session_state.username}!")
        if st.button("Déconnexion"):
            st.session_state["authenticated"] = False
            st.rerun()  # Rerun to show login screen