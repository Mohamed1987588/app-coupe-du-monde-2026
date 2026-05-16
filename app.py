import streamlit as st
import pandas as pd

# 1. Configuration de la page
st.set_page_config(
    # --- Ajout de l'arrière-plan personnalisé ---
url_image = "https://lematin.ma/lematin/uploads/images/2025/10/20/457027.jpg"

page_bg_img = f"""
<style>
.stApp {{
    background-image: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)), url("{url_image}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)
# -------------------------------------------
    page_title="Sélection Coupe du Monde 2026",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Fonction de nettoyage intelligente pour vos fichiers spécifiques
@st.cache_data
def load_and_clean_data(file_path, is_global_list=True):
    df_raw = None
    # Test des encodages pour éviter l'erreur d'accent (UnicodeDecodeError)
    for encoding in ['utf-8', 'latin-1', 'cp1252']:
        try:
            df_raw = pd.read_csv(file_path, sep=';', header=None, encoding=encoding, on_bad_lines='skip')
            break
        except UnicodeDecodeError:
            continue
        except FileNotFoundError:
            st.error(f"❌ Le fichier '{file_path}' est introuvable. Assurez-vous qu'il est exactement dans le même dossier que app.py.")
            return pd.DataFrame()
            
    if df_raw is None or df_raw.empty:
        return pd.DataFrame()

    cleaned_rows = []
    current_poste = "Inconnu"

    # Parcours et restructuration ligne par ligne pour rendre le tout professionnel
    for idx, row in df_raw.iterrows():
        val_0 = str(row.get(0, '')).strip()
        val_1 = str(row.get(1, '')).strip()
        val_2 = str(row.get(2, '')).strip()
        
        # --- CAS 1 : Traitement du fichier global ---
        if is_global_list:
            if val_0.lower() == 'poste' and val_1.lower() == 'club':
                continue # Ignore la ligne d'en-tête répétée
            if val_0 and val_0.lower() not in ['nan', '']:
                current_poste = val_0 # Capture le poste (ex: Gardien, Défenseurs)
            if not val_2 or val_2.lower() == 'nan':
                continue # Saute les lignes vides
                
            cleaned_rows.append({
                "Poste": current_poste,
                "Club": val_1,
                "Nom": val_2,
                "Âge": str(row.get(3, '')).strip(),
                "Minutes": str(row.get(4, '')).strip(),
                "Stats (Buts/Passes)": str(row.get(5, '')).strip(),
                "Lien Fotmob": str(row.get(7, '')).strip()
            })
            
        # --- CAS 2 : Traitement de "Ma Liste" (avec numérotation en colonne 0) ---
        else:
            # Détection des lignes de catégories isolées (ex: Gardien;;;;;)
            if val_0 and (val_1 == '' or val_1.lower() == 'nan') and (val_2 == '' or val_2.lower() == 'nan'):
                if val_0.lower() == 'diffence':
                    current_poste = "Défenseurs"
                elif val_0.lower() == 'gardien':
                    current_poste = "Gardiens"
                else:
                    current_poste = val_0
                continue
                
            if val_1.lower() == 'club' or not val_2 or val_2.lower() == 'nan':
                continue # Ignore les en-têtes internes et les lignes vides
                
            cleaned_rows.append({
                "Poste": current_poste,
                "Club": val_1,
                "Nom": val_2,
                "Âge": str(row.get(3, '')).strip(),
                "Minutes": str(row.get(4, '')).strip(),
                "Passes": str(row.get(5, '')).strip(),
                "Buts": str(row.get(6, '')).strip(),
                "Lien Fotmob": str(row.get(7, '')).strip()
            })

    df_final = pd.DataFrame(cleaned_rows)
    return df_final

# Noms des fichiers (doivent être dans le même dossier)
FILE_GLOBAL = "listes des joueurs Coupe du Monde 2026.csv"
FILE_MY_LIST = "Ma liste des joueurs Coupe du Monde 2026.csv"

# Chargement des bases nettoyées
df_my_list = load_and_clean_data(FILE_MY_LIST, is_global_list=False)
df_global = load_and_clean_data(FILE_GLOBAL, is_global_list=True)

# 3. Interface Utilisateur (Sidebar)
st.sidebar.title("⚽ World Cup 2026")
st.sidebar.markdown("Filtrez et analysez vos effectifs.")
st.sidebar.markdown("---")

search_query = st.sidebar.text_input("🔍 Rechercher un joueur, un club ou un poste :")

# 4. Zone Principale
st.title("🏆 Plateforme de Gestion des Effectifs - CM 2026")
st.markdown("Interface de visualisation propre et structurée de vos listes de joueurs.")

tab1, tab2 = st.tabs(["📋 Ma Liste Définitive", "🌍 Liste Globale des Pressentis"])

def filter_data(df, query):
    if df.empty or not query:
        return df
    mask = df.astype(str).apply(lambda x: x.str.contains(query, case=False, na=False)).any(axis=1)
    return df[mask]

with tab1:
    st.subheader("Effectif sélectionné")
    df_my_list_filtered = filter_data(df_my_list, search_query)
    if not df_my_list_filtered.empty:
        st.dataframe(df_my_list_filtered, use_container_width=True, hide_index=True)
        st.info(f"💡 Total de joueurs dans cette sélection : {len(df_my_list_filtered)}")
    else:
        st.warning("Aucun joueur ne correspond à la recherche ou le fichier est vide.")

with tab2:
    st.subheader("Base de données complète")
    df_global_filtered = filter_data(df_global, search_query)
    if not df_global_filtered.empty:
        st.dataframe(df_global_filtered, use_container_width=True, hide_index=True)
        st.info(f"💡 Total de joueurs disponibles : {len(df_global_filtered)}")
    else:
        st.warning("Aucun joueur ne correspond à la recherche ou le fichier est vide.")

st.markdown("---")
st.markdown("<div style='text-align: center; color: gray; font-size: 12px;'>Dashboard Professionnel • Coupe du Monde 2026</div>", unsafe_allow_html=True)
