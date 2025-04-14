import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import time
import random
from datetime import datetime
import base64
from io import BytesIO

# Configuration de la page
st.set_page_config(
    page_title="League of Legends Analytics Hub",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fonction pour générer une image en base64
def get_image_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Fonction pour créer un background avec une image
def add_bg_from_url(url):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("{url}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Styles CSS personnalisés pour le thème LoL amélioré
st.markdown("""
<style>
    /* Styles généraux */
    .main {
        background-color: rgba(10, 20, 40, 0.95);
        color: #E8D8A3;
        font-family: 'Beaufort for LOL', sans-serif;
    }
    
    /* Animation de brillance pour les titres */
    @keyframes glow {
        0% { text-shadow: 0 0 5px #C8AA6E, 0 0 10px #C8AA6E; }
        50% { text-shadow: 0 0 20px #C8AA6E, 0 0 30px #C8AA6E; }
        100% { text-shadow: 0 0 5px #C8AA6E, 0 0 10px #C8AA6E; }
    }
    
    h1 {
        color: #C8AA6E;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2px;
        animation: glow 3s ease-in-out infinite;
        margin-bottom: 30px;
        border-bottom: 2px solid #0397AB;
        padding-bottom: 10px;
    }
    
    h2 {
        color: #0397AB;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 40px;
        margin-bottom: 20px;
    }
    
    h3 {
        color: #C8AA6E;
        font-weight: 500;
        margin-top: 30px;
        border-left: 3px solid #0397AB;
        padding-left: 10px;
    }
    
    /* Onglets stylisés */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(9, 20, 40, 0.7);
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: rgba(9, 20, 40, 0.8);
        border-radius: 8px;
        gap: 1px;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: 1px solid rgba(200, 170, 110, 0.2);
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(3, 151, 171, 0.2);
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #0397AB !important;
        color: white !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(3, 151, 171, 0.5);
    }
    
    /* Boutons stylisés */
    .stButton>button {
        background: linear-gradient(135deg, #0397AB, #005A82);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        letter-spacing: 1px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #005A82, #0397AB);
        color: #C8AA6E;
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(3, 151, 171, 0.4);
    }
    
    /* Sidebar stylisée */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #091428 0%, #0A1428 100%);
        border-right: 1px solid rgba(200, 170, 110, 0.2);
    }
    
    /* Cartes pour les métriques */
    .metric-card {
        background: linear-gradient(135deg, rgba(9, 20, 40, 0.9), rgba(10, 20, 40, 0.8));
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(200, 170, 110, 0.3);
        transition: all 0.3s ease;
        margin-bottom: 20px;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(3, 151, 171, 0.3);
        border: 1px solid rgba(3, 151, 171, 0.5);
    }
    
    .metric-title {
        color: #C8AA6E;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 10px;
    }
    
    .metric-value {
        color: white;
        font-size: 2rem;
        font-weight: 700;
    }
    
    .metric-subtitle {
        color: #0397AB;
        font-size: 0.9rem;
        margin-top: 5px;
    }
    
    /* Conteneurs pour les graphiques */
    .chart-container {
        background: linear-gradient(135deg, rgba(9, 20, 40, 0.9), rgba(10, 20, 40, 0.8));
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(200, 170, 110, 0.3);
        margin-bottom: 30px;
    }
    
    /* Barres de progression */
    .stProgress > div > div {
        background: linear-gradient(90deg, #0397AB, #005A82);
        border-radius: 10px;
    }
    
    /* Sélecteurs et sliders */
    .stSelectbox label, .stSlider label {
        color: #C8AA6E;
        font-weight: 500;
    }
    
    .stSelectbox > div[data-baseweb="select"] > div {
        background-color: rgba(9, 20, 40, 0.8);
        border: 1px solid rgba(200, 170, 110, 0.3);
        border-radius: 8px;
        color: #E8D8A3;
    }
    
    .stSlider > div > div {
        background-color: rgba(9, 20, 40, 0.8);
    }
    
    .stSlider > div > div > div > div {
        background-color: #0397AB;
    }
    
    /* Animation pour les cartes de champions */
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.03); }
        100% { transform: scale(1); }
    }
    
    .champion-card {
        background: linear-gradient(135deg, rgba(9, 20, 40, 0.9), rgba(10, 20, 40, 0.8));
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(200, 170, 110, 0.3);
        transition: all 0.3s ease;
        margin-bottom: 20px;
        animation: pulse 3s infinite ease-in-out;
    }
    
    .champion-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(3, 151, 171, 0.3);
        border: 1px solid rgba(3, 151, 171, 0.5);
    }
    
    /* Tooltip personnalisé */
    .tooltip {
        position: relative;
        display: inline-block;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: rgba(9, 20, 40, 0.95);
        color: #E8D8A3;
        text-align: center;
        border-radius: 6px;
        padding: 10px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
        border: 1px solid #0397AB;
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    
    /* Dataframe stylisé */
    .dataframe-container {
        background: linear-gradient(135deg, rgba(9, 20, 40, 0.9), rgba(10, 20, 40, 0.8));
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(200, 170, 110, 0.3);
        margin-bottom: 30px;
    }
    
    /* Effet de brillance pour les éléments importants */
    .highlight {
        color: #0397AB;
        font-weight: 600;
        text-shadow: 0 0 10px rgba(3, 151, 171, 0.5);
    }
    
    /* Effet de vague pour les séparateurs */
    .wave-separator {
        height: 50px;
        background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 120' preserveAspectRatio='none'%3E%3Cpath d='M0,0V46.29c47.79,22.2,103.59,32.17,158,28,70.36-5.37,136.33-33.31,206.8-37.5C438.64,32.43,512.34,53.67,583,72.05c69.27,18,138.3,24.88,209.4,13.08,36.15-6,69.85-17.84,104.45-29.34C989.49,25,1113-14.29,1200,52.47V0Z' opacity='.25' fill='%230397AB'%3E%3C/path%3E%3Cpath d='M0,0V15.81C13,36.92,27.64,56.86,47.69,72.05,99.41,111.27,165,111,224.58,91.58c31.15-10.15,60.09-26.07,89.67-39.8,40.92-19,84.73-46,130.83-49.67,36.26-2.85,70.9,9.42,98.6,31.56,31.77,25.39,62.32,62,103.63,73,40.44,10.79,81.35-6.69,119.13-24.28s75.16-39,116.92-43.05c59.73-5.85,113.28,22.88,168.9,38.84,30.2,8.66,59,6.17,87.09-7.5,22.43-10.89,48-26.93,60.65-49.24V0Z' opacity='.5' fill='%230397AB'%3E%3C/path%3E%3Cpath d='M0,0V5.63C149.93,59,314.09,71.32,475.83,42.57c43-7.64,84.23-20.12,127.61-26.46,59-8.63,112.48,12.24,165.56,35.4C827.93,77.22,886,95.24,951.2,90c86.53-7,172.46-45.71,248.8-84.81V0Z' fill='%230397AB'%3E%3C/path%3E%3C/svg%3E");
        background-size: cover;
        margin: 30px 0;
    }
    
    /* Animation pour les badges */
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }
    
    .badge {
        display: inline-block;
        background: linear-gradient(135deg, #0397AB, #005A82);
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: 600;
        margin-right: 10px;
        margin-bottom: 10px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
        animation: float 3s ease-in-out infinite;
        animation-delay: calc(var(--i) * 0.5s);
    }
    
    /* Effet de parallaxe pour le fond */
    .parallax-bg {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: url('https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Lux_7.jpg');
        background-size: cover;
        background-position: center;
        z-index: -1;
        opacity: 0.1;
    }
    
    /* Effet de particules */
    .particles {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1;
        pointer-events: none;
    }
    
    /* Effet de vignette */
    .vignette {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        box-shadow: inset 0 0 200px rgba(0, 0, 0, 0.8);
        z-index: -1;
        pointer-events: none;
    }
    
    /* Effet de glitch pour les erreurs */
    @keyframes glitch {
        0% { transform: translate(0); }
        20% { transform: translate(-5px, 5px); }
        40% { transform: translate(-5px, -5px); }
        60% { transform: translate(5px, 5px); }
        80% { transform: translate(5px, -5px); }
        100% { transform: translate(0); }
    }
    
    .error-text {
        color: #FF4655;
        font-weight: 700;
        animation: glitch 1s linear infinite;
        text-shadow: 2px 2px 0 rgba(255, 70, 85, 0.5);
    }
    
    /* Effet de néon pour les boutons spéciaux */
    .neon-button {
        position: relative;
        display: inline-block;
        padding: 15px 30px;
        color: #0397AB;
        font-size: 1.2rem;
        text-transform: uppercase;
        letter-spacing: 4px;
        text-decoration: none;
        overflow: hidden;
        transition: 0.5s;
        background: transparent;
        border: 2px solid #0397AB;
        border-radius: 8px;
        margin: 20px 0;
        font-weight: 700;
        cursor: pointer;
    }
    
    .neon-button:hover {
        background: #0397AB;
        color: #fff;
        box-shadow: 0 0 5px #0397AB, 0 0 25px #0397AB, 0 0 50px #0397AB, 0 0 200px #0397AB;
    }
    
    /* Effet de carte 3D */
    .card-3d {
        transition: transform 0.5s;
        transform-style: preserve-3d;
    }
    
    .card-3d:hover {
        transform: rotateY(10deg) rotateX(10deg);
    }
    
    /* Effet de timeline */
    .timeline {
        position: relative;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    .timeline::after {
        content: '';
        position: absolute;
        width: 6px;
        background-color: #0397AB;
        top: 0;
        bottom: 0;
        left: 50%;
        margin-left: -3px;
        border-radius: 3px;
    }
    
    .timeline-container {
        padding: 10px 40px;
        position: relative;
        background-color: inherit;
        width: 50%;
    }
    
    .timeline-container::after {
        content: '';
        position: absolute;
        width: 20px;
        height: 20px;
        right: -10px;
        background-color: #C8AA6E;
        border: 4px solid #0397AB;
        top: 15px;
        border-radius: 50%;
        z-index: 1;
    }
    
    .left {
        left: 0;
    }
    
    .right {
        left: 50%;
    }
    
    .left::before {
        content: " ";
        height: 0;
        position: absolute;
        top: 22px;
        width: 0;
        z-index: 1;
        right: 30px;
        border: medium solid #0397AB;
        border-width: 10px 0 10px 10px;
        border-color: transparent transparent transparent #0397AB;
    }
    
    .right::before {
        content: " ";
        height: 0;
        position: absolute;
        top: 22px;
        width: 0;
        z-index: 1;
        left: 30px;
        border: medium solid #0397AB;
        border-width: 10px 10px 10px 0;
        border-color: transparent #0397AB transparent transparent;
    }
    
    .right::after {
        left: -10px;
    }
    
    .timeline-content {
        padding: 20px 30px;
        background: linear-gradient(135deg, rgba(9, 20, 40, 0.9), rgba(10, 20, 40, 0.8));
        position: relative;
        border-radius: 10px;
        border: 1px solid rgba(200, 170, 110, 0.3);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    /* Effet de ruban */
    .ribbon {
        position: absolute;
        right: -5px;
        top: -5px;
        z-index: 1;
        overflow: hidden;
        width: 75px;
        height: 75px;
        text-align: right;
    }
    
    .ribbon span {
        font-size: 10px;
        font-weight: bold;
        color: #FFF;
        text-transform: uppercase;
        text-align: center;
        line-height: 20px;
        transform: rotate(45deg);
        -webkit-transform: rotate(45deg);
        width: 100px;
        display: block;
        background: linear-gradient(#0397AB, #005A82);
        box-shadow: 0 3px 10px -5px rgba(0, 0, 0, 1);
        position: absolute;
        top: 19px;
        right: -21px;
    }
    
    .ribbon span::before {
        content: "";
        position: absolute;
        left: 0px;
        top: 100%;
        z-index: -1;
        border-left: 3px solid #005A82;
        border-right: 3px solid transparent;
        border-bottom: 3px solid transparent;
        border-top: 3px solid #005A82;
    }
    
    .ribbon span::after {
        content: "";
        position: absolute;
        right: 0px;
        top: 100%;
        z-index: -1;
        border-left: 3px solid transparent;
        border-right: 3px solid #005A82;
        border-bottom: 3px solid transparent;
        border-top: 3px solid #005A82;
    }
    
    /* Style pour les explications de graphiques */
    .chart-explanation {
        background: linear-gradient(135deg, rgba(9, 20, 40, 0.9), rgba(10, 20, 40, 0.8));
        padding: 15px;
        border-radius: 10px;
        margin-top: 10px;
        border-left: 3px solid #0397AB;
        color: #E8D8A3;
    }
    </style>
""", unsafe_allow_html=True)

# Ajouter un fond parallaxe et des effets visuels
st.markdown("""
<div class="parallax-bg"></div>
<div class="vignette"></div>
""", unsafe_allow_html=True)

# Fonction pour charger les données
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('match_data_v5.csv')
        return df
    except FileNotFoundError:
        st.error("Fichier CSV non trouvé. Veuillez télécharger le dataset depuis Kaggle et le placer dans le même dossier que ce script.")
        st.stop()

# Fonction pour simuler une analyse IA
def analyze_with_ai(data_sample, question):
    # Simuler un délai de traitement
    progress_bar = st.progress(0)
    for i in range(100):
        time.sleep(0.01)
        progress_bar.progress(i + 1)
    
    # Réponses prédéfinies basées sur des questions typiques
    responses = {
        "factors_win": "D'après mon analyse des données, les facteurs les plus déterminants pour la victoire sont: 1) L'avantage en or (blueTeamTotalGold), 2) Le nombre de kills d'équipe (blueTeamTotalKills), et 3) Le contrôle des objectifs comme les dragons (blueTeamDragonKills) et les hérauts (blueTeamHeraldKills). Les équipes avec un avantage en or significatif ont une probabilité de victoire beaucoup plus élevée.",
        "objectives": "Le contrôle des objectifs est crucial pour la victoire. Les données montrent que les équipes qui sécurisent le premier dragon ont un taux de victoire supérieur de 15% en moyenne. De même, obtenir le Héraut permet souvent de détruire la première tourelle, ce qui ouvre la carte et facilite le contrôle de vision.",
        "meta_analysis": "La méta actuelle favorise les compositions d'équipe avec une forte présence en early game. Les équipes qui investissent dans la vision (blueTeamControlWardsPlaced élevé) et qui coordonnent les ganks efficacement obtiennent un avantage significatif. Les données montrent également une corrélation entre le premier sang (blueTeamFirstBlood) et le taux de victoire.",
        "player_improvement": "Pour améliorer vos performances, concentrez-vous sur: 1) L'optimisation du farm (CS) pour maximiser l'or, 2) La participation aux objectifs précoces comme le dragon et le héraut, 3) L'amélioration de votre score de vision avec des wards de contrôle. Les données montrent que même un petit avantage en or peut se traduire par un impact significatif sur le résultat du match."
    }
    
    # Déterminer quelle réponse renvoyer
    if "facteurs" in question.lower() or "victoire" in question.lower():
        return responses["factors_win"]
    elif "objectifs" in question.lower() or "dragon" in question.lower() or "héraut" in question.lower():
        return responses["objectives"]
    elif "meta" in question.lower() or "tendance" in question.lower():
        return responses["meta_analysis"]
    elif "améliorer" in question.lower() or "progresser" in question.lower():
        return responses["player_improvement"]
    else:
        # Analyse générique basée sur les données
        gold_diff = data_sample['blueTeamTotalGold'].mean() - data_sample['redTeamTotalGold'].mean()
        kill_diff = data_sample['blueTeamTotalKills'].mean() - data_sample['redTeamTotalKills'].mean()
        win_rate = data_sample['blueWin'].mean() * 100
        
        return f"Après analyse des données, je constate que les équipes victorieuses ont en moyenne un avantage de {gold_diff:.2f} d'or et de {kill_diff:.2f} kills. Le taux de victoire global de l'équipe bleue est de {win_rate:.2f}%. Les facteurs clés semblent être le contrôle des objectifs précoces (dragons, hérauts) et l'efficacité du farm. Je recommande de se concentrer sur ces aspects pour améliorer vos chances de victoire."

# Fonction pour recommander des champions basés sur le style de jeu
def recommend_champions(playstyle, role):
    # Dictionnaire de champions par rôle et style de jeu
    champions = {
        "top": {
            "aggressive": ["Darius", "Riven", "Fiora", "Jax", "Renekton"],
            "defensive": ["Ornn", "Malphite", "Shen", "Maokai", "Sion"],
            "balanced": ["Garen", "Mordekaiser", "Camille", "Aatrox", "Urgot"]
        },
        "jungle": {
            "aggressive": ["Lee Sin", "Kha'Zix", "Rengar", "Elise", "Nidalee"],
            "defensive": ["Nunu", "Zac", "Sejuani", "Amumu", "Rammus"],
            "balanced": ["Vi", "Jarvan IV", "Hecarim", "Volibear", "Trundle"]
        },
        "mid": {
            "aggressive": ["Zed", "Talon", "Katarina", "Fizz", "LeBlanc"],
            "defensive": ["Galio", "Lissandra", "Malzahar", "Morgana", "Orianna"],
            "balanced": ["Ahri", "Syndra", "Twisted Fate", "Viktor", "Lux"]
        },
        "adc": {
            "aggressive": ["Draven", "Lucian", "Tristana", "Kalista", "Samira"],
            "defensive": ["Ezreal", "Ashe", "Sivir", "Xayah", "Varus"],
            "balanced": ["Jinx", "Caitlyn", "Miss Fortune", "Jhin", "Kai'Sa"]
        },
        "support": {
            "aggressive": ["Pyke", "Thresh", "Blitzcrank", "Leona", "Nautilus"],
            "defensive": ["Soraka", "Janna", "Lulu", "Yuumi", "Sona"],
            "balanced": ["Nami", "Karma", "Bard", "Rakan", "Seraphine"]
        }
    }
    
    # Sélectionner 3 champions aléatoires du rôle et style spécifiés
    if role in champions and playstyle in champions[role]:
        return random.sample(champions[role][playstyle], 3)
    else:
        return ["Garen", "Annie", "Master Yi"]  # Champions par défaut pour les débutants

# Fonction pour générer une timeline d'événements de match
def generate_match_timeline(team_stats):
    events = []
    
    # Générer des événements basés sur les statistiques
    if team_stats['blueTeamFirstBlood'] == 1:
        events.append({
            'time': random.randint(2, 5),
            'event': 'Premier sang obtenu par l\'équipe bleue',
            'team': 'blue'
        })
    else:
        events.append({
            'time': random.randint(2, 5),
            'event': 'Premier sang obtenu par l\'équipe rouge',
            'team': 'red'
        })
    
    # Ajouter des événements pour les dragons
    if team_stats['blueTeamDragonKills'] > 0:
        events.append({
            'time': random.randint(5, 8),
            'event': f'Dragon tué par l\'équipe bleue',
            'team': 'blue'
        })
    
    if team_stats['redTeamDragonKills'] > 0:
        events.append({
            'time': random.randint(5, 8),
            'event': f'Dragon tué par l\'équipe rouge',
            'team': 'red'
        })
    
    # Ajouter des événements pour les hérauts
    if team_stats['blueTeamHeraldKills'] > 0:
        events.append({
            'time': random.randint(8, 10),
            'event': f'Héraut tué par l\'équipe bleue',
            'team': 'blue'
        })
    
    if team_stats['redTeamHeraldKills'] > 0:
        events.append({
            'time': random.randint(8, 10),
            'event': f'Héraut tué par l\'équipe rouge',
            'team': 'red'
        })
    
    # Ajouter des événements pour les tours
    if team_stats['blueTeamTowersDestroyed'] > 0:
        events.append({
            'time': random.randint(7, 10),
            'event': f'Tour détruite par l\'équipe bleue',
            'team': 'blue'
        })
    
    if team_stats['redTeamTowersDestroyed'] > 0:
        events.append({
            'time': random.randint(7, 10),
            'event': f'Tour détruite par l\'équipe rouge',
            'team': 'red'
        })
    
    # Trier les événements par temps
    events.sort(key=lambda x: x['time'])
    
    return events

# Fonction pour créer une carte de chaleur de la jungle
def create_jungle_heatmap(team_stats):
    # Créer une grille pour la carte de la jungle
    jungle_grid = np.zeros((10, 10))
    
    # Simuler des points chauds basés sur les statistiques
    # Plus de kills = plus d'activité dans la jungle
    activity_level = team_stats['blueTeamTotalKills'] / 10
    
    # Générer des points chauds aléatoires
    for _ in range(int(activity_level * 5)):
        x = random.randint(0, 9)
        y = random.randint(0, 9)
        jungle_grid[x, y] += random.uniform(0.5, 2.0)
    
    # Ajouter des points chauds pour les objectifs
    if team_stats['blueTeamDragonKills'] > 0:
        jungle_grid[7, 7] += team_stats['blueTeamDragonKills'] * 2
    
    if team_stats['blueTeamHeraldKills'] > 0:
        jungle_grid[2, 2] += team_stats['blueTeamHeraldKills'] * 2
    
    return jungle_grid

# Logo et titre avec animation
st.markdown("""
<div style="display: flex; align-items: center; margin-bottom: 30px; background: linear-gradient(135deg, rgba(9, 20, 40, 0.9), rgba(10, 20, 40, 0.8)); padding: 20px; border-radius: 15px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2); border: 1px solid rgba(200, 170, 110, 0.3);">
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/LoL_icon.svg/1200px-LoL_icon.svg.png" width="80" style="margin-right: 20px; filter: drop-shadow(0 0 10px rgba(200, 170, 110, 0.7));">
    <div>
        <h1 style="margin: 0; font-size: 2.5rem;">LEAGUE OF LEGENDS ANALYTICS HUB</h1>
        <p style="color: #0397AB; margin: 0; font-size: 1.2rem;">Explorez les données, découvrez les tendances et obtenez des insights IA pour améliorer votre jeu</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Chargement des données
df = load_data()

# Créer des colonnes dérivées pour l'analyse
df = df.assign(
    goldDiff = df['blueTeamTotalGold'] - df['redTeamTotalGold'],
    killDiff = df['blueTeamTotalKills'] - df['redTeamTotalKills'],
    xpDiff = df['blueTeamXp'] - df['redTeamXp'],
    damageDiff = df['blueTeamTotalDamageToChamps'] - df['redTeamTotalDamageToChamps'],
    visionDiff = df['blueTeamControlWardsPlaced'] + df['blueTeamWardsPlaced'] - (df['redTeamControlWardsPlaced'] + df['redTeamWardsPlaced']),
    objectiveScore = df['blueTeamDragonKills'] + df['blueTeamHeraldKills'] + df['blueTeamTowersDestroyed'] + df['blueTeamTurretPlatesDestroyed']/5,
    killsPerGold = (df['blueTeamTotalKills'] / df['blueTeamTotalGold'] * 1000).round(2),
    isHighKDA = df['blueTeamTotalKills'] > df['blueTeamTotalKills'].mean()
)

# Utilisation de value_counts() pour analyser la distribution des premiers sangs
first_blood_distribution = df['blueTeamFirstBlood'].value_counts()
first_blood_percentage = (first_blood_distribution / len(df) * 100).round(1)

# Utilisation de sum() pour calculer le total des kills par équipe
total_blue_kills = df['blueTeamTotalKills'].sum()
total_red_kills = df['redTeamTotalKills'].sum()

# Sidebar pour les filtres avec design amélioré
st.sidebar.markdown("""
<div style="text-align: center; margin-bottom: 20px;">
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/League_of_Legends_2019_vector.svg/1200px-League_of_Legends_2019_vector.svg.png" width="180" style="filter: drop-shadow(0 0 10px rgba(200, 170, 110, 0.5));">
</div>
<h2 style="text-align: center; margin-bottom: 20px; color: #C8AA6E; text-shadow: 0 0 10px rgba(200, 170, 110, 0.3);">FILTRES D'ANALYSE</h2>
""", unsafe_allow_html=True)

# Créer des bins pour les filtres numériques
kill_bins = [0, 5, 10, 15, 20, 100]
kill_labels = ['0-5', '6-10', '11-15', '16-20', '20+']
df['killRange'] = pd.cut(df['blueTeamTotalKills'], bins=kill_bins, labels=kill_labels)

gold_bins = [0, 20000, 30000, 40000, 50000, 1000000]
gold_labels = ['0-20k', '20k-30k', '30k-40k', '40k-50k', '50k+']
df['goldRange'] = pd.cut(df['blueTeamTotalGold'], bins=gold_bins, labels=gold_labels)

# Filtres avec design amélioré
st.sidebar.markdown("""
<div style="background: linear-gradient(135deg, rgba(9, 20, 40, 0.9), rgba(10, 20, 40, 0.8)); padding: 15px; border-radius: 10px; margin-bottom: 20px; border: 1px solid rgba(200, 170, 110, 0.3); box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);">
    <h3 style="margin-top: 0; color: #0397AB; font-size: 1.2rem;">Filtres de Match</h3>
""", unsafe_allow_html=True)

kill_filter = st.sidebar.multiselect("Plage de kills (équipe bleue)", options=kill_labels, default=kill_labels)
gold_filter = st.sidebar.multiselect("Plage d'or (équipe bleue)", options=gold_labels, default=gold_labels)
first_blood_filter = st.sidebar.multiselect("Premier sang", options=[0, 1], default=[0, 1], format_func=lambda x: "Équipe bleue" if x == 1 else "Équipe rouge")

st.sidebar.markdown("</div>", unsafe_allow_html=True)

# Filtres avancés
st.sidebar.markdown("""
<div style="background: linear-gradient(135deg, rgba(9, 20, 40, 0.9), rgba(10, 20, 40, 0.8)); padding: 15px; border-radius: 10px; margin-bottom: 20px; border: 1px solid rgba(200, 170, 110, 0.3); box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);">
    <h3 style="margin-top: 0; color: #0397AB; font-size: 1.2rem;">Filtres Avancés</h3>
""", unsafe_allow_html=True)

# Filtres pour les objectifs
min_dragons = st.sidebar.slider("Nombre min. de dragons (équipe bleue)", 0, 5, 0)
min_heralds = st.sidebar.slider("Nombre min. de hérauts (équipe bleue)", 0, 2, 0)

# Filtre pour la différence d'or
gold_diff_range = st.sidebar.slider("Différence d'or", -20000, 20000, (-20000, 20000))

st.sidebar.markdown("</div>", unsafe_allow_html=True)

# Appliquer les filtres
filtered_df = df[
    (df['killRange'].isin(kill_filter)) & 
    (df['goldRange'].isin(gold_filter)) & 
    (df['blueTeamFirstBlood'].isin(first_blood_filter)) &
    (df['blueTeamDragonKills'] >= min_dragons) &
    (df['blueTeamHeraldKills'] >= min_heralds) &
    (df['goldDiff'] >= gold_diff_range[0]) &
    (df['goldDiff'] <= gold_diff_range[1])
]

# Afficher le nombre d'entrées filtrées avec un design amélioré
st.sidebar.markdown(f"""
<div style="background: linear-gradient(135deg, #0397AB, #005A82); padding: 15px; border-radius: 10px; text-align: center; margin-top: 20px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);">
    <h3 style="margin: 0; color: white; font-size: 1.2rem;">Matchs analysés</h3>
    <p style="margin: 0; font-size: 2rem; font-weight: 700; color: white;">{len(filtered_df)}</p>
</div>
""", unsafe_allow_html=True)

# Recommandation de champions
st.sidebar.markdown("""
<div style="background: linear-gradient(135deg, rgba(9, 20, 40, 0.9), rgba(10, 20, 40, 0.8)); padding: 15px; border-radius: 10px; margin-top: 20px; border: 1px solid rgba(200, 170, 110, 0.3); box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);">
    <h3 style="margin-top: 0; color: #0397AB; font-size: 1.2rem;">Recommandation de Champions</h3>
""", unsafe_allow_html=True)

role = st.sidebar.selectbox("Sélectionnez votre rôle", ["top", "jungle", "mid", "adc", "support"])
playstyle = st.sidebar.selectbox("Sélectionnez votre style de jeu", ["aggressive", "defensive", "balanced"])

if st.sidebar.button("Recommander des champions"):
    recommended_champions = recommend_champions(playstyle, role)
    
    st.sidebar.markdown(f"""
    <div style="margin-top: 15px;">
        <p style="color: #C8AA6E; font-weight: 600;">Champions recommandés pour {role} ({playstyle}):</p>
        <div style="display: flex; flex-wrap: wrap; justify-content: space-between;">
    """, unsafe_allow_html=True)
    
    for champion in recommended_champions:
        st.sidebar.markdown(f"""
        <div class="champion-card" style="width: 30%; text-align: center;">
            <p style="margin: 0; color: #0397AB; font-weight: 600;">{champion}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.sidebar.markdown("</div></div>", unsafe_allow_html=True)

st.sidebar.markdown("</div>", unsafe_allow_html=True)

# Créer des onglets pour organiser le contenu avec un design amélioré
tabs = st.tabs([
    "📊 Vue d'ensemble", 
    "🔍 Analyse détaillée", 
    "🎯 Objectifs", 
    "🧠 Prédictions IA", 
    "💬 Assistant LoL",
    "🌍 Carte de la Jungle",
    "⏱️ Timeline de Match"
])

# Onglet 1: Vue d'ensemble
with tabs[0]:
    st.markdown("""
    <h2 style="text-align: center; margin-bottom: 30px;">STATISTIQUES GÉNÉRALES DES MATCHS</h2>
    """, unsafe_allow_html=True)
    
    # Métriques clés avec design amélioré
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        win_rate_blue = filtered_df['blueWin'].mean() * 100
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Taux de victoire Blue Side</div>
            <div class="metric-value">{win_rate_blue:.2f}%</div>
            <div class="metric-subtitle">sur {len(filtered_df)} matchs</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        first_blood_win_rate = filtered_df[filtered_df['blueTeamFirstBlood'] == 1]['blueWin'].mean() * 100
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Taux de victoire avec First Blood</div>
            <div class="metric-value">{first_blood_win_rate:.2f}%</div>
            <div class="metric-subtitle">impact significatif</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_gold_diff = filtered_df['goldDiff'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Différence d'or moyenne</div>
            <div class="metric-value">{avg_gold_diff:.2f}</div>
            <div class="metric-subtitle">entre équipes bleue et rouge</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg_kills = filtered_df['blueTeamTotalKills'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Kills moyens (Blue)</div>
            <div class="metric-value">{avg_kills:.2f}</div>
            <div class="metric-subtitle">par match</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Utilisation de sum() - Afficher le total des kills
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="chart-container">
            <h3 style="text-align: center; margin-top: 0;">Total des Kills par Équipe</h3>
        """, unsafe_allow_html=True)
        
        # Calculer le total des kills pour les données filtrées
        total_blue_kills_filtered = filtered_df['blueTeamTotalKills'].sum()
        total_red_kills_filtered = filtered_df['redTeamTotalKills'].sum()
        
        # Créer un dataframe pour le graphique
        kills_df = pd.DataFrame({
            'Équipe': ['Blue', 'Red'],
            'Total Kills': [total_blue_kills_filtered, total_red_kills_filtered]
        })
        
        fig = px.bar(
            kills_df, 
            x='Équipe', 
            y='Total Kills',
            color='Équipe',
            color_discrete_map={'Blue': '#0397AB', 'Red': '#C2185B'},
            text='Total Kills'
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#C8AA6E'),
            xaxis=dict(gridcolor='#1E2328'),
            yaxis=dict(gridcolor='#1E2328'),
            showlegend=False,
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Ajout d'une explication pour le graphique
        st.markdown("""
        <div class="chart-explanation">
            <p>Ce graphique présente le nombre total de kills réalisés par chaque équipe sur l'ensemble des matchs analysés. 
            La différence entre les équipes bleue et rouge peut indiquer des avantages spécifiques liés au côté de la carte ou 
            des préférences méta qui favorisent un style de jeu particulier. Un nombre de kills plus élevé est souvent corrélé 
            à un gameplay plus agressif et à une domination dans les phases d'escarmouches.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Utilisation de value_counts() - Distribution du premier sang
    with col2:
        st.markdown("""
        <div class="chart-container">
            <h3 style="text-align: center; margin-top: 0;">Distribution du Premier Sang</h3>
        """, unsafe_allow_html=True)
        
        # Utiliser value_counts sur les données filtrées
        first_blood_counts = filtered_df['blueTeamFirstBlood'].value_counts().reset_index()
        first_blood_counts.columns = ['Premier Sang', 'Nombre']
        first_blood_counts['Premier Sang'] = first_blood_counts['Premier Sang'].map({0: 'Équipe Rouge', 1: 'Équipe Bleue'})
        first_blood_counts['Pourcentage'] = (first_blood_counts['Nombre'] / first_blood_counts['Nombre'].sum() * 100).round(1)
        
        fig = px.pie(
            first_blood_counts, 
            values='Nombre', 
            names='Premier Sang',
            color='Premier Sang',
            color_discrete_map={'Équipe Bleue': '#0397AB', 'Équipe Rouge': '#C2185B'},
            hole=0.4
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#C8AA6E'),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            ),
            height=400
        )
        
        fig.update_traces(
            textinfo='percent+label',
            textfont_color='white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Ajout d'une explication pour le graphique
        st.markdown("""
        <div class="chart-explanation">
            <p>Ce diagramme circulaire illustre la distribution du Premier Sang entre les équipes. 
            Le Premier Sang est un avantage crucial en début de partie qui définit souvent la dominance de lane. 
            Les équipes qui obtiennent le Premier Sang gagnent généralement un avantage psychologique et un lead d'or 
            précoce qui peut être exploité pour contrôler les objectifs et exercer une pression sur la carte.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Distribution des victoires par différence d'or
    st.markdown("""
    <div class="chart-container">
        <h3 style="text-align: center; margin-top: 0;">Taux de victoire par différence d'or</h3>
    """, unsafe_allow_html=True)
    
    # Créer des bins pour la différence d'or
    gold_diff_bins = [-50000, -10000, -5000, -2000, 0, 2000, 5000, 10000, 50000]
    gold_diff_labels = ['< -10k', '-10k à -5k', '-5k à -2k', '-2k à 0', '0 à 2k', '2k à 5k', '5k à 10k', '> 10k']
    filtered_df['goldDiffBin'] = pd.cut(filtered_df['goldDiff'], bins=gold_diff_bins, labels=gold_diff_labels)
    
    # Calculer le taux de victoire par bin
    gold_diff_win_rate = filtered_df.groupby('goldDiffBin')['blueWin'].mean().reset_index()
    gold_diff_win_rate['WinRate'] = gold_diff_win_rate['blueWin'] * 100
    gold_diff_win_rate['Count'] = filtered_df.groupby('goldDiffBin').size().values
    
    # Convertir les Interval en string pour éviter l'erreur JSON
    gold_diff_win_rate['goldDiffBin'] = gold_diff_win_rate['goldDiffBin'].astype(str)
    
    fig = px.bar(
        gold_diff_win_rate, 
        x='goldDiffBin', 
        y='WinRate',
        color='WinRate',
        color_continuous_scale='blues',
        labels={'WinRate': 'Taux de victoire (%)', 'goldDiffBin': 'Différence d\'or'},
        text='Count'
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#C8AA6E'),
        xaxis=dict(gridcolor='#1E2328'),
        yaxis=dict(gridcolor='#1E2328'),
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Ajout d'une explication pour le graphique
    st.markdown("""
    <div class="chart-explanation">
        <p>Ce graphique démontre comment la différence d'or impacte directement les taux de victoire. 
        Observez comment la probabilité de victoire augmente considérablement avec des différences d'or positives, 
        particulièrement au-delà du seuil de 2000 or. Les avantages en or se traduisent par des avantages d'items, 
        qui fournissent une puissance de combat tangible dans les combats d'équipe et les escarmouches. 
        Cette analyse confirme l'importance cruciale du farm et des objectifs qui génèrent de l'or.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Comparaison des métriques clés entre équipes gagnantes et perdantes
    st.markdown("""
    <div class="chart-container">
        <h3 style="text-align: center; margin-top: 0;">Comparaison des métriques clés entre équipes gagnantes et perdantes</h3>
    """, unsafe_allow_html=True)
    
    # Sélectionner la métrique à comparer
    metric_to_compare = st.selectbox(
        "Choisir une métrique", 
        options=[
            "blueTeamTotalGold", "blueTeamTotalKills", "blueTeamDragonKills", 
            "blueTeamHeraldKills", "blueTeamTowersDestroyed", "blueTeamControlWardsPlaced",
            "blueTeamMinionsKilled", "blueTeamTotalDamageToChamps"
        ],
        format_func=lambda x: {
            "blueTeamTotalGold": "Or total",
            "blueTeamTotalKills": "Kills totaux",
            "blueTeamDragonKills": "Dragons tués",
            "blueTeamHeraldKills": "Hérauts tués",
            "blueTeamTowersDestroyed": "Tours détruites",
            "blueTeamControlWardsPlaced": "Wards de contrôle placées",
            "blueTeamMinionsKilled": "CS total",
            "blueTeamTotalDamageToChamps": "Dégâts aux champions"
        }.get(x, x)
    )
    
    # Créer un boxplot comparant les équipes gagnantes et perdantes
    fig = px.box(
        filtered_df, 
        x='blueWin', 
        y=metric_to_compare,
        color='blueWin',
        color_discrete_map={0: '#C2185B', 1: '#0397AB'},
        labels={
            'blueWin': 'Résultat',
            metric_to_compare: {
                "blueTeamTotalGold": "Or total",
                "blueTeamTotalKills": "Kills totaux",
                "blueTeamDragonKills": "Dragons tués",
                "blueTeamHeraldKills": "Hérauts tués",
                "blueTeamTowersDestroyed": "Tours détruites",
                "blueTeamControlWardsPlaced": "Wards de contrôle placées",
                "blueTeamMinionsKilled": "CS total",
                "blueTeamTotalDamageToChamps": "Dégâts aux champions"
            }.get(metric_to_compare, metric_to_compare)
        },
        title=f"Distribution de {metric_to_compare} par résultat",
        category_orders={"blueWin": [0, 1]}
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#C8AA6E'),
        xaxis=dict(gridcolor='#1E2328', ticktext=["Défaite", "Victoire"], tickvals=[0, 1]),
        yaxis=dict(gridcolor='#1E2328'),
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Ajout d'une explication pour le graphique
    st.markdown("""
    <div class="chart-explanation">
        <p>Ce boxplot compare la métrique sélectionnée entre les équipes gagnantes et perdantes. 
        La séparation claire entre les boîtes indique à quel point cette métrique est fortement corrélée aux résultats des matchs. 
        Les équipes victorieuses surpassent systématiquement les équipes perdantes dans ce domaine, ce qui en fait un prédicteur 
        fiable des résultats de match. Analysez les différentes métriques pour identifier les facteurs les plus déterminants 
        pour la victoire dans vos propres parties.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Heatmap des corrélations
    st.markdown("""
    <div class="chart-container">
        <h3 style="text-align: center; margin-top: 0;">Corrélations entre les métriques clés</h3>
    """, unsafe_allow_html=True)
    
    # Sélectionner les colonnes numériques pertinentes
    numeric_cols = [
        'blueTeamTotalKills', 'blueTeamDragonKills', 'blueTeamHeraldKills', 
        'blueTeamTowersDestroyed', 'blueTeamTurretPlatesDestroyed', 'blueTeamFirstBlood',
        'blueTeamMinionsKilled', 'blueTeamJungleMinions', 'blueTeamTotalGold', 
        'blueTeamXp', 'blueTeamTotalDamageToChamps', 'blueWin'
    ]
    
    corr_matrix = filtered_df[numeric_cols].corr()
    
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(
        corr_matrix, 
        annot=True, 
        cmap='coolwarm', 
        center=0,
        linewidths=.5,
        fmt='.2f',
        ax=ax
    )
    plt.title('Matrice de corrélation des métriques de jeu', fontsize=16)
    plt.tight_layout()
    
    # Personnaliser les couleurs pour le thème LoL
    plt.rcParams['text.color'] = '#C8AA6E'
    plt.rcParams['axes.labelcolor'] = '#C8AA6E'
    plt.rcParams['xtick.color'] = '#C8AA6E'
    plt.rcParams['ytick.color'] = '#C8AA6E'
    
    st.pyplot(fig)
    
    # Ajout d'une explication pour le graphique
    st.markdown("""
    <div class="chart-explanation">
        <p>La matrice de corrélation révèle les relations entre les différentes métriques de jeu. 
        Les corrélations positives fortes (bleu foncé) indiquent des métriques qui tendent à augmenter ensemble, 
        tandis que les corrélations négatives (rouge) montrent des relations inverses. 
        Portez une attention particulière aux corrélations avec 'blueWin' pour identifier les prédicteurs de victoire. 
        Cette visualisation permet de comprendre quelles métriques sont interdépendantes et lesquelles ont le plus 
        d'impact sur le résultat final du match.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Onglet 2: Analyse détaillée
with tabs[1]:
    st.markdown("""
    <h2 style="text-align: center; margin-bottom: 30px;">ANALYSE DÉTAILLÉE DES MÉTRIQUES DE JEU</h2>
    """, unsafe_allow_html=True)
    
    # Sélection des métriques à comparer
    col1, col2 = st.columns(2)
    with col1:
        x_metric = st.selectbox(
            "Métrique X", 
            options=[
                "blueTeamTotalGold", "blueTeamTotalKills", "blueTeamDragonKills", 
                "blueTeamHeraldKills", "blueTeamTowersDestroyed", "blueTeamControlWardsPlaced",
                "blueTeamMinionsKilled", "blueTeamTotalDamageToChamps", "goldDiff", "killDiff"
            ],
            format_func=lambda x: {
                "blueTeamTotalGold": "Or total",
                "blueTeamTotalKills": "Kills totaux",
                "blueTeamDragonKills": "Dragons tués",
                "blueTeamHeraldKills": "Hérauts tués",
                "blueTeamTowersDestroyed": "Tours détruites",
                "blueTeamControlWardsPlaced": "Wards de contrôle placées",
                "blueTeamMinionsKilled": "CS total",
                "blueTeamTotalDamageToChamps": "Dégâts aux champions",
                "goldDiff": "Différence d'or",
                "killDiff": "Différence de kills"
            }.get(x, x)
        )
    
    with col2:
        y_metric = st.selectbox(
            "Métrique Y", 
            options=[
                "blueTeamTotalGold", "blueTeamTotalKills", "blueTeamDragonKills", 
                "blueTeamHeraldKills", "blueTeamTowersDestroyed", "blueTeamControlWardsPlaced",
                "blueTeamMinionsKilled", "blueTeamTotalDamageToChamps", "goldDiff", "killDiff"
            ],
            index=1,
            format_func=lambda x: {
                "blueTeamTotalGold": "Or total",
                "blueTeamTotalKills": "Kills totaux",
                "blueTeamDragonKills": "Dragons tués",
                "blueTeamHeraldKills": "Hérauts tués",
                "blueTeamTowersDestroyed": "Tours détruites",
                "blueTeamControlWardsPlaced": "Wards de contrôle placées",
                "blueTeamMinionsKilled": "CS total",
                "blueTeamTotalDamageToChamps": "Dégâts aux champions",
                "goldDiff": "Différence d'or",
                "killDiff": "Différence de kills"
            }.get(x, x)
        )
    
    # Graphique de dispersion avec coloration par résultat
    st.markdown("""
    <div class="chart-container">
        <h3 style="text-align: center; margin-top: 0;">Relation entre métriques par résultat de match</h3>
    """, unsafe_allow_html=True)
    
    fig = px.scatter(
        filtered_df, 
        x=x_metric, 
        y=y_metric,
        color='blueWin',
        color_discrete_map={0: '#C2185B', 1: '#0397AB'},
        labels={
            x_metric: {
                "blueTeamTotalGold": "Or total",
                "blueTeamTotalKills": "Kills totaux",
                "blueTeamDragonKills": "Dragons tués",
                "blueTeamHeraldKills": "Hérauts tués",
                "blueTeamTowersDestroyed": "Tours détruites",
                "blueTeamControlWardsPlaced": "Wards de contrôle placées",
                "blueTeamMinionsKilled": "CS total",
                "blueTeamTotalDamageToChamps": "Dégâts aux champions",
                "goldDiff": "Différence d'or",
                "killDiff": "Différence de kills"
            }.get(x_metric, x_metric),
            y_metric: {
                "blueTeamTotalGold": "Or total",
                "blueTeamTotalKills": "Kills totaux",
                "blueTeamDragonKills": "Dragons tués",
                "blueTeamHeraldKills": "Hérauts tués",
                "blueTeamTowersDestroyed": "Tours détruites",
                "blueTeamControlWardsPlaced": "Wards de contrôle placées",
                "blueTeamMinionsKilled": "CS total",
                "blueTeamTotalDamageToChamps": "Dégâts aux champions",
                "goldDiff": "Différence d'or",
                "killDiff": "Différence de kills"
            }.get(y_metric, y_metric),
            'blueWin': 'Résultat'
        },
        opacity=0.7,
        size='objectiveScore',
        hover_data=['blueTeamTotalGold', 'blueTeamTotalKills', 'objectiveScore']
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#C8AA6E'),
        xaxis=dict(gridcolor='#1E2328'),
        yaxis=dict(gridcolor='#1E2328'),
        height=600,
        legend=dict(
            title="Résultat",
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Ajout d'une explication pour le graphique
    st.markdown("""
    <div class="chart-explanation">
        <p>Ce nuage de points visualise la relation entre deux métriques clés, avec les points colorés selon le résultat du match.
        Le motif de regroupement montre comment ces métriques interagissent pour influencer les résultats de jeu.
        La taille des points représente le score d'objectifs, mettant en évidence comment les équipes qui sécurisent les objectifs
        tendent à performer dans ces métriques. Observez les zones de concentration des points bleus (victoires) pour identifier
        les seuils critiques de performance dans ces métriques.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Comparaison Blue vs Red
    st.markdown("""
    <div class="chart-container">
        <h3 style="text-align: center; margin-top: 0;">Comparaison Blue vs Red</h3>
    """, unsafe_allow_html=True)
    
    # Sélectionner la métrique à comparer
    compare_metric = st.selectbox(
        "Choisir une métrique à comparer", 
        options=[
            "TotalGold", "TotalKills", "DragonKills", "HeraldKills", 
            "TowersDestroyed", "ControlWardsPlaced", "MinionsKilled", "TotalDamageToChamps"
        ],
        format_func=lambda x: {
            "TotalGold": "Or total",
            "TotalKills": "Kills totaux",
            "DragonKills": "Dragons tués",
            "HeraldKills": "Hérauts tués",
            "TowersDestroyed": "Tours détruites",
            "ControlWardsPlaced": "Wards de contrôle placées",
            "MinionsKilled": "CS total",
            "TotalDamageToChamps": "Dégâts aux champions"
        }.get(x, x)
    )
    
    # Créer un dataframe pour la comparaison
    compare_df = pd.DataFrame({
        'Team': ['Blue', 'Red'],
        'Value': [
            filtered_df[f'blueTeam{compare_metric}'].mean(),
            filtered_df[f'redTeam{compare_metric}'].mean()
        ],
        'WinRate': [
            filtered_df['blueWin'].mean() * 100,
            (1 - filtered_df['blueWin'].mean()) * 100
        ]
    })
    
    # Créer un graphique à barres pour la comparaison
    fig = px.bar(
        compare_df, 
        x='Team', 
        y='Value',
        color='Team',
        color_discrete_map={'Blue': '#0397AB', 'Red': '#C2185B'},
        labels={
            'Team': 'Équipe',
            'Value': {
                "TotalGold": "Or total moyen",
                "TotalKills": "Kills totaux moyens",
                "DragonKills": "Dragons tués moyens",
                "HeraldKills": "Hérauts tués moyens",
                "TowersDestroyed": "Tours détruites moyennes",
                "ControlWardsPlaced": "Wards de contrôle placées moyennes",
                "MinionsKilled": "CS total moyen",
                "TotalDamageToChamps": "Dégâts aux champions moyens"
            }.get(compare_metric, compare_metric)
        },
        text='Value'
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#C8AA6E'),
        xaxis=dict(gridcolor='#1E2328'),
        yaxis=dict(gridcolor='#1E2328'),
        height=500,
        showlegend=False
    )
    
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Ajout d'une explication pour le graphique
    st.markdown("""
    <div class="chart-explanation">
        <p>Cette comparaison met en évidence la différence de performance moyenne entre les côtés Bleu et Rouge pour la métrique sélectionnée.
        Les avantages spécifiques à chaque côté peuvent émerger de l'asymétrie de la carte, du positionnement des objectifs et de l'ordre de draft.
        Comprendre ces différences peut vous aider à ajuster votre stratégie en fonction du côté qui vous est assigné.
        Par exemple, le côté bleu peut avoir un accès plus facile à certains objectifs, tandis que le côté rouge peut avoir d'autres avantages stratégiques.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Analyse des métriques dérivées (killsPerGold)
    st.markdown("""
    <div class="chart-container">
        <h3 style="text-align: center; margin-top: 0;">Efficacité des Kills (Kills par 1000 Or)</h3>
    """, unsafe_allow_html=True)
    
    # Créer des bins pour l'efficacité des kills
    filtered_df['killsPerGoldBin'] = pd.cut(
        filtered_df['killsPerGold'], 
        bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0, 2.0],
        labels=['0-0.2', '0.2-0.4', '0.4-0.6', '0.6-0.8', '0.8-1.0', '1.0+']
    )
    
    # Calculer le taux de victoire par bin
    kills_per_gold_win_rate = filtered_df.groupby('killsPerGoldBin')['blueWin'].mean().reset_index()
    kills_per_gold_win_rate['WinRate'] = kills_per_gold_win_rate['blueWin'] * 100
    kills_per_gold_win_rate['Count'] = filtered_df.groupby('killsPerGoldBin').size().values
    
    # Convertir les Interval en string pour éviter l'erreur JSON
    kills_per_gold_win_rate['killsPerGoldBin'] = kills_per_gold_win_rate['killsPerGoldBin'].astype(str)
    
    fig = px.bar(
        kills_per_gold_win_rate, 
        x='killsPerGoldBin', 
        y='WinRate',
        color='WinRate',
        color_continuous_scale='blues',
        labels={
            'killsPerGoldBin': 'Kills par 1000 Or',
            'WinRate': 'Taux de victoire (%)'
        },
        text='Count'
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#C8AA6E'),
        xaxis=dict(gridcolor='#1E2328'),
        yaxis=dict(gridcolor='#1E2328'),
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Ajout d'une explication pour le graphique
    st.markdown("""
    <div class="chart-explanation">
        <p>Ce graphique analyse l'efficacité des kills - comment les équipes convertissent efficacement les kills en avantage d'or.
        Une efficacité plus élevée (plus de kills par 1000 or) suggère des équipes qui excellent à sécuriser des kills sans investir
        des ressources excessives. Une efficacité plus faible pourrait indiquer des équipes qui privilégient les objectifs et le farm
        plutôt que les éliminations de champions. Notez la relation entre cette métrique et le taux de victoire pour comprendre
        si une approche orientée vers les kills ou vers les objectifs est plus efficace dans la méta actuelle.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Tableau des statistiques détaillées
    st.markdown("""
    <div class="dataframe-container">
        <h3 style="text-align: center; margin-top: 0;">Statistiques détaillées par résultat</h3>
    """, unsafe_allow_html=True)
    
    # Créer un tableau récapitulatif par résultat
    stats_df = filtered_df.groupby('blueWin').agg({
        'blueTeamTotalGold': 'mean',
        'blueTeamTotalKills': 'mean',
        'blueTeamDragonKills': 'mean',
        'blueTeamHeraldKills': 'mean',
        'blueTeamTowersDestroyed': 'mean',
        'blueTeamControlWardsPlaced': 'mean',
        'blueTeamMinionsKilled': 'mean',
        'blueTeamTotalDamageToChamps': 'mean',
        'goldDiff': 'mean',
        'killDiff': 'mean',
        'killsPerGold': 'mean'
    }).reset_index()
    
    # Formater les colonnes
    for col in stats_df.columns:
        if col != 'blueWin':
            stats_df[col] = stats_df[col].round(2)
    
    # Renommer les colonnes pour l'affichage
    stats_df.columns = [
        'Résultat', 'Or total', 'Kills', 'Dragons', 'Hérauts', 
        'Tours', 'Wards de contrôle', 'CS', 'Dégâts', 'Diff. Or', 'Diff. Kills', 'Kills/1000 Or'
    ]
    stats_df['Résultat'] = stats_df['Résultat'].map({0: 'Défaite', 1: 'Victoire'})
    
    st.dataframe(stats_df, use_container_width=True)
    
    # Ajout d'une explication pour le tableau
    st.markdown("""
    <div class="chart-explanation">
        <p>Ce tableau présente les valeurs moyennes des métriques clés, segmentées par résultat de match.
        Les différences entre les matchs gagnés et perdus révèlent les écarts de performance critiques qui déterminent l'issue d'une partie.
        Utilisez ces données pour identifier les seuils de performance à atteindre dans vos propres parties.
        Par exemple, observez l'écart d'or moyen entre victoire et défaite pour comprendre quel avantage économique est généralement nécessaire pour l'emporter.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Onglet 3: Objectifs
with tabs[2]:
    st.markdown("""
    <h2 style="text-align: center; margin-bottom: 30px;">ANALYSE DES OBJECTIFS</h2>
    """, unsafe_allow_html=True)
    
    # Impact du premier sang
    st.markdown("""
    <div class="chart-container">
        <h3 style="text-align: center; margin-top: 0;">Impact du premier sang</h3>
    """, unsafe_allow_html=True)
    
    # Calculer le taux de victoire avec et sans premier sang
    first_blood_stats = pd.DataFrame({
        'Premier Sang': ['Équipe bleue', 'Équipe rouge'],
        'Taux de victoire': [
            filtered_df[filtered_df['blueTeamFirstBlood'] == 1]['blueWin'].mean() * 100,
            filtered_df[filtered_df['blueTeamFirstBlood'] == 0]['blueWin'].mean() * 100
        ]
    })
    
    fig = px.bar(
        first_blood_stats, 
        x='Premier Sang', 
        y='Taux de victoire',
        color='Premier Sang',
        color_discrete_map={'Équipe bleue': '#0397AB', 'Équipe rouge': '#C2185B'},
        labels={
            'Premier Sang': 'Équipe avec le premier sang',
            'Taux de victoire': 'Taux de victoire de l\'équipe bleue (%)'
        },
        text=first_blood_stats['Taux de victoire'].round(2)
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#C8AA6E'),
        xaxis=dict(gridcolor='#1E2328'),
        yaxis=dict(gridcolor='#1E2328'),
        height=500,
        showlegend=False
    )
    
    fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Ajout d'une explication pour le graphique
    st.markdown("""
    <div class="chart-explanation">
        <p>Cette visualisation quantifie l'impact de l'obtention du Premier Sang sur le taux de victoire de l'équipe bleue.
        La différence marquée dans les taux de victoire démontre le potentiel d'effet boule de neige des avantages précoces.
        Le Premier Sang fournit à la fois un avantage d'or direct et indique souvent une exécution supérieure en début de partie.
        Cet avantage initial peut être exploité pour établir une domination de vision, contrôler les objectifs et exercer une pression sur les lanes.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Impact des dragons
    st.markdown("""
    <div class="chart-container">
        <h3 style="text-align: center; margin-top: 0;">Impact des dragons</h3>
    """, unsafe_allow_html=True)
    
    # Créer des bins pour le nombre de dragons
    dragon_counts = filtered_df.groupby('blueTeamDragonKills')['blueWin'].agg(['mean', 'count']).reset_index()
    dragon_counts['win_rate'] = dragon_counts['mean'] * 100
    
    fig = px.bar(
        dragon_counts, 
        x='blueTeamDragonKills', 
        y='win_rate',
        color='win_rate',
        color_continuous_scale='blues',
        labels={
            'blueTeamDragonKills': 'Nombre de dragons tués',
            'win_rate': 'Taux de victoire (%)'
        },
        text='count'
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#C8AA6E'),
        xaxis=dict(gridcolor='#1E2328'),
        yaxis=dict(gridcolor='#1E2328'),
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Ajout d'une explication pour le graphique
    st.markdown("""
    <div class="chart-explanation">
        <p>Ce graphique montre comment le contrôle des dragons est corrélé à la victoire.
        Chaque dragon supplémentaire sécurisé augmente significativement la probabilité de victoire, avec des rendements décroissants après 3-4 dragons.
        Les buffs de dragon fournissent des avantages cumulatifs qui deviennent de plus en plus difficiles à surmonter pour les adversaires.
        Le contrôle des dragons est non seulement bénéfique pour les buffs eux-mêmes, mais indique également une équipe qui domine la partie inférieure de la carte
        et coordonne efficacement ses mouvements autour des objectifs.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Impact des hérauts
    st.markdown("""
    <div class="chart-container">
        <h3 style="text-align: center; margin-top: 0;">Impact des hérauts</h3>
    """, unsafe_allow_html=True)
    
    # Créer des bins pour le nombre de hérauts
    herald_counts = filtered_df.groupby('blueTeamHeraldKills')['blueWin'].agg(['mean', 'count']).reset_index()
    herald_counts['win_rate'] = herald_counts['mean'] * 100
    
    fig = px.bar(
        herald_counts, 
        x='blueTeamHeraldKills', 
        y='win_rate',
        color='win_rate',
        color_continuous_scale='blues',
        labels={
            'blueTeamHeraldKills': 'Nombre de hérauts tués',
            'win_rate': 'Taux de victoire (%)'
        },
        text='count'
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#C8AA6E'),
        xaxis=dict(gridcolor='#1E2328'),
        yaxis=dict(gridcolor='#1E2328'),
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Ajout d'une explication pour le graphique
    st.markdown("""
    <div class="chart-explanation">
        <p>Cette analyse démontre l'influence du Héraut sur les résultats des matchs.
        Le contrôle du Héraut permet aux équipes d'ouvrir rapidement la carte, d'accélérer les revenus d'or grâce aux plaques de tourelles
        et de créer une pression sur la carte. L'augmentation du taux de victoire reflète à la fois l'avantage direct du Héraut
        et la coordination d'équipe nécessaire pour le sécuriser. Utiliser efficacement le Héraut peut créer un avantage significatif
        en milieu de partie, particulièrement lorsqu'il est synchronisé avec d'autres objectifs comme le dragon.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Impact des tours
    st.markdown("""
    <div class="chart-container">
        <h3 style="text-align: center; margin-top: 0;">Impact des tours détruites</h3>
    """, unsafe_allow_html=True)
    
    # Créer des bins pour le nombre de tours
    tower_counts = filtered_df.groupby('blueTeamTowersDestroyed')['blueWin'].agg(['mean', 'count']).reset_index()
    tower_counts['win_rate'] = tower_counts['mean'] * 100
    
    fig = px.bar(
        tower_counts, 
        x='blueTeamTowersDestroyed', 
        y='win_rate',
        color='win_rate',
        color_continuous_scale='blues',
        labels={
            'blueTeamTowersDestroyed': 'Nombre de tours détruites',
            'win_rate': 'Taux de victoire (%)'
        },
        text='count'
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#C8AA6E'),
        xaxis=dict(gridcolor='#1E2328'),
        yaxis=dict(gridcolor='#1E2328'),
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Ajout d'une explication pour le graphique
    st.markdown("""
    <div class="chart-explanation">
        <p>La relation entre les tours détruites et la probabilité de victoire est clairement illustrée ici.
        Chaque tour fournit de l'or global, ouvre la carte pour un contrôle de vision plus profond et restreint les mouvements ennemis.
        L'augmentation progressive du taux de victoire montre comment chaque tour supplémentaire amplifie les avantages.
        La destruction des tours extérieures permet d'accéder à la jungle ennemie et aux objectifs, tandis que les tours intérieures
        ouvrent la voie vers les inhibiteurs et le Nexus. Cette progression territoriale est fondamentale pour convertir un avantage en victoire.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Score d'objectifs combiné
    st.markdown("""
    <div class="chart-container">
        <h3 style="text-align: center; margin-top: 0;">Score d'objectifs combiné</h3>
    """, unsafe_allow_html=True)
    
    # Créer des bins pour le score d'objectifs
    filtered_df['objectiveScoreBin'] = pd.cut(
        filtered_df['objectiveScore'], 
        bins=[0, 1, 2, 3, 4, 10],
        labels=['0-1', '1-2', '2-3', '3-4', '4+']
    )
    
    objective_score_counts = filtered_df.groupby('objectiveScoreBin')['blueWin'].agg(['mean', 'count']).reset_index()
    objective_score_counts['win_rate'] = objective_score_counts['mean'] * 100
    
    # Convertir les Interval en string pour éviter l'erreur JSON
    objective_score_counts['objectiveScoreBin'] = objective_score_counts['objectiveScoreBin'].astype(str)
    
    fig = px.bar(
        objective_score_counts, 
        x='objectiveScoreBin', 
        y='win_rate',
        color='win_rate',
        color_continuous_scale='blues',
        labels={
            'objectiveScoreBin': 'Score d\'objectifs',
            'win_rate': 'Taux de victoire (%)'
        },
        text='count'
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#C8AA6E'),
        xaxis=dict(gridcolor='#1E2328'),
        yaxis=dict(gridcolor='#1E2328'),
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Ajout d'une explication pour le graphique
    st.markdown("""
    <div class="chart-explanation">
        <p>Ce graphique combine tous les objectifs en un score unique pour montrer leur impact cumulatif.
        Des scores d'objectifs plus élevés sont fortement corrélés à la victoire, démontrant que les équipes qui privilégient
        le contrôle de la carte par la prise systématique d'objectifs surpassent constamment les équipes focalisées sur les kills.
        Cette métrique composite révèle l'importance d'une approche équilibrée du jeu, où la prise d'objectifs, le contrôle de vision et les éliminations de champions sont coordonnés pour maximiser l'avantage global. Les équipes qui excellent dans cette coordination ont généralement des taux de victoire nettement supérieurs.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Comparaison de l'impact des différents objectifs
    st.markdown("""
    <div class="chart-container">
        <h3 style="text-align: center; margin-top: 0;">Comparaison de l'impact des objectifs sur la victoire</h3>
    """, unsafe_allow_html=True)
    
    # Calculer l'impact de chaque objectif sur le taux de victoire
    objective_impact = pd.DataFrame({
        'Objectif': ['Premier Sang', 'Dragon', 'Héraut', 'Tour'],
        'Impact sur la victoire (%)': [
            (filtered_df[filtered_df['blueTeamFirstBlood'] == 1]['blueWin'].mean() - 
             filtered_df[filtered_df['blueTeamFirstBlood'] == 0]['blueWin'].mean()) * 100,
            (filtered_df[filtered_df['blueTeamDragonKills'] > 0]['blueWin'].mean() - 
             filtered_df[filtered_df['blueTeamDragonKills'] == 0]['blueWin'].mean()) * 100,
            (filtered_df[filtered_df['blueTeamHeraldKills'] > 0]['blueWin'].mean() - 
             filtered_df[filtered_df['blueTeamHeraldKills'] == 0]['blueWin'].mean()) * 100,
            (filtered_df[filtered_df['blueTeamTowersDestroyed'] > 0]['blueWin'].mean() - 
             filtered_df[filtered_df['blueTeamTowersDestroyed'] == 0]['blueWin'].mean()) * 100
        ]
    })
    
    fig = px.bar(
        objective_impact, 
        x='Objectif', 
        y='Impact sur la victoire (%)',
        color='Impact sur la victoire (%)',
        color_continuous_scale='blues',
        text=objective_impact['Impact sur la victoire (%)'].round(2)
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#C8AA6E'),
        xaxis=dict(gridcolor='#1E2328'),
        yaxis=dict(gridcolor='#1E2328'),
        height=500
    )
    
    fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Ajout d'une explication pour le graphique
    st.markdown("""
    <div class="chart-explanation">
        <p>Cette comparaison révèle l'impact relatif des différents objectifs sur le taux de victoire.
        Comprendre quels objectifs fournissent le plus grand avantage aide les équipes à prioriser efficacement leurs ressources.
        Notez comment certains objectifs peuvent avoir une importance disproportionnée par rapport à leur valeur apparente en jeu.
        Cette analyse permet d'optimiser la prise de décision stratégique, en identifiant les moments clés où il faut contester
        certains objectifs ou les échanger contre d'autres avantages sur la carte.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Onglet 4: Prédictions IA
with tabs[3]:
    st.markdown("""
    <h2 style="text-align: center; margin-bottom: 30px;">PRÉDICTIONS ET ANALYSE IA</h2>
    """, unsafe_allow_html=True)
    
    # Sélectionner les caractéristiques pertinentes
    features = [
        'blueTeamTotalKills', 'blueTeamDragonKills', 'blueTeamHeraldKills', 
        'blueTeamTowersDestroyed', 'blueTeamFirstBlood', 'blueTeamMinionsKilled',
        'blueTeamJungleMinions', 'blueTeamTotalGold', 'blueTeamXp', 
        'blueTeamTotalDamageToChamps', 'goldDiff', 'killDiff', 'xpDiff'
    ]
    
    # Fonction pour entraîner un modèle prédictif
    @st.cache_resource
    def train_prediction_model(df, features, target_col):
        # Sélectionner les caractéristiques et la cible
        X = df[features]
        y = df[target_col]
        
        # Diviser les données
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Normaliser les données
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Entraîner un modèle RandomForest
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)
        
        # Évaluer le modèle
        y_pred = model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Importance des caractéristiques
        feature_importance = pd.DataFrame({
            'Feature': features,
            'Importance': model.feature_importances_
        }).sort_values('Importance', ascending=False)
        
        return model, scaler, accuracy, feature_importance, X_test, y_test
    
    # Entraîner le modèle
    model, scaler, accuracy, feature_importance, X_test, y_test = train_prediction_model(filtered_df, features, 'blueWin')
    
    # Afficher la précision du modèle
    st.markdown(f"""
    <div class="metric-card" style="text-align: center;">
        <div class="metric-title">Précision du modèle de prédiction</div>
        <div class="metric-value" style="font-size: 3rem; color: #0397AB;">{accuracy*100:.2f}%</div>
        <div class="metric-subtitle">basée sur {len(X_test)} matchs de test</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Importance des caractéristiques
    st.markdown("""
    <div class="chart-container">
        <h3 style="text-align: center; margin-top: 0;">Importance des facteurs pour prédire la victoire</h3>
    """, unsafe_allow_html=True)
    
    # Renommer les caractéristiques pour l'affichage
    feature_importance['Feature'] = feature_importance['Feature'].map({
        'blueTeamTotalKills': 'Kills totaux',
        'blueTeamDragonKills': 'Dragons tués',
        'blueTeamHeraldKills': 'Hérauts tués',
        'blueTeamTowersDestroyed': 'Tours détruites',
        'blueTeamFirstBlood': 'Premier sang',
        'blueTeamMinionsKilled': 'CS total',
        'blueTeamJungleMinions': 'CS jungle',
        'blueTeamTotalGold': 'Or total',
        'blueTeamXp': 'Expérience totale',
        'blueTeamTotalDamageToChamps': 'Dégâts aux champions',
        'goldDiff': 'Différence d\'or',
        'killDiff': 'Différence de kills',
        'xpDiff': 'Différence d\'expérience'
    })
    
    fig = px.bar(
        feature_importance, 
        x='Importance', 
        y='Feature',
        orientation='h',
        color='Importance',
        color_continuous_scale='blues',
        labels={'Importance': 'Importance (%)', 'Feature': 'Facteur'},
        text=feature_importance['Importance'].round(3)
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#C8AA6E'),
        xaxis=dict(gridcolor='#1E2328'),
        yaxis=dict(gridcolor='#1E2328'),
        height=600
    )
    
    fig.update_traces(texttemplate='%{text:.3f}', textposition='outside')
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Ajout d'une explication pour le graphique
    st.markdown("""
    <div class="chart-explanation">
        <p>Ce graphique classe les facteurs selon leur pouvoir prédictif pour les résultats des matchs.
        Les caractéristiques avec une importance plus élevée ont une plus grande influence sur les prédictions du modèle d'apprentissage automatique.
        Ces insights révèlent quels aspects du gameplay déterminent le plus fiablement la victoire, au-delà de la sagesse conventionnelle.
        Utilisez ces informations pour concentrer vos efforts sur les métriques qui ont le plus d'impact sur le résultat final,
        et pour comprendre quels aspects du jeu méritent le plus d'attention lors de l'analyse de vos propres performances.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Simulateur de prédiction
    st.markdown("""
    <div class="chart-container">
        <h3 style="text-align: center; margin-top: 0;">Simulateur de prédiction de victoire</h3>
        <p style="text-align: center; color: #C8AA6E;">Ajustez les valeurs ci-dessous pour voir comment elles affectent la probabilité de victoire</p>
    """, unsafe_allow_html=True)
    
    # Créer des sliders pour chaque caractéristique
    prediction_values = {}
    
    # Organiser les sliders en colonnes
    col1, col2 = st.columns(2)
    
    # Mapping pour l'affichage des noms de caractéristiques
    feature_display_names = {
        'blueTeamTotalKills': 'Kills totaux',
        'blueTeamDragonKills': 'Dragons tués',
        'blueTeamHeraldKills': 'Hérauts tués',
        'blueTeamTowersDestroyed': 'Tours détruites',
        'blueTeamFirstBlood': 'Premier sang (0=Non, 1=Oui)',
        'blueTeamMinionsKilled': 'CS total',
        'blueTeamJungleMinions': 'CS jungle',
        'blueTeamTotalGold': 'Or total',
        'blueTeamXp': 'Expérience totale',
        'blueTeamTotalDamageToChamps': 'Dégâts aux champions',
        'goldDiff': 'Différence d\'or',
        'killDiff': 'Différence de kills',
        'xpDiff': 'Différence d\'expérience'
    }
    
    for i, feature in enumerate(features):
        # Déterminer les valeurs min, max et par défaut
        min_val = float(filtered_df[feature].min())
        max_val = float(filtered_df[feature].max())
        default_val = float(filtered_df[feature].mean())
        
        # Arrondir les valeurs pour une meilleure lisibilité
        step = (max_val - min_val) / 100
        if feature == 'blueTeamFirstBlood':
            step = 1
            min_val = 0
            max_val = 1
            default_val = round(default_val)
        
        # Alterner entre les colonnes
        with col1 if i % 2 == 0 else col2:
            # Formater le nom de la caractéristique pour l'affichage
            display_name = feature_display_names.get(feature, feature)
            prediction_values[feature] = st.slider(
                display_name, 
                min_value=min_val,
                max_value=max_val,
                value=default_val,
                step=step
            )
    
    # Créer un échantillon pour la prédiction
    prediction_sample = pd.DataFrame({feature: [value] for feature, value in prediction_values.items()})
    
    # Normaliser l'échantillon
    prediction_sample_scaled = scaler.transform(prediction_sample)
    
    # Faire la prédiction
    win_probability = model.predict_proba(prediction_sample_scaled)[0][1]
    
    # Afficher le résultat
    st.subheader("Résultat de la prédiction")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Probabilité de victoire", f"{win_probability*100:.2f}%")
    
    with col2:
        prediction = "Victoire" if win_probability > 0.5 else "Défaite"
        st.metric("Prédiction", prediction)
    
    # Jauge de probabilité
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = win_probability * 100,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Probabilité de victoire"},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': "#0397AB"},
            'steps': [
                {'range': [0, 30], 'color': "#C2185B"},
                {'range': [30, 70], 'color': "#FFC107"},
                {'range': [70, 100], 'color': "#4CAF50"}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': 50
            }
        }
    ))
    fig.update_layout(
        height=300,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#C8AA6E')
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Ajout d'une explication pour le simulateur
    st.markdown("""
    <div class="chart-explanation">
        <p>La jauge de prédiction visualise la probabilité de victoire estimée en fonction de l'état actuel du jeu.
        Cette évaluation en temps réel combine plusieurs facteurs pondérés par leur importance prédictive.
        Les équipes peuvent utiliser cet outil pour comprendre leur position actuelle et identifier quelles métriques
        nécessitent une amélioration. Expérimentez avec différentes valeurs pour voir comment des changements dans
        certaines métriques peuvent affecter dramatiquement les chances de victoire, et utilisez ces informations
        pour prioriser vos objectifs en jeu.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Matrice de confusion
    st.markdown("""
    <div class="chart-container">
        <h3 style="text-align: center; margin-top: 0;">Performance du modèle sur les données de test</h3>
    """, unsafe_allow_html=True)
    
    y_pred = model.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)
    
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        cm, 
        annot=True, 
        fmt='d',
        cmap='Blues',
        xticklabels=['Défaite', 'Victoire'],
        yticklabels=['Défaite', 'Victoire'],
        ax=ax
    )
    plt.xlabel('Prédiction')
    plt.ylabel('Réalité')
    plt.title('Matrice de confusion')
    
    # Personnaliser les couleurs pour le thème LoL
    plt.rcParams['text.color'] = '#C8AA6E'
    plt.rcParams['axes.labelcolor'] = '#C8AA6E'
    plt.rcParams['xtick.color'] = '#C8AA6E'
    plt.rcParams['ytick.color'] = '#C8AA6E'
    
    st.pyplot(fig)
    
    # Ajout d'une explication pour la matrice de confusion
    st.markdown("""
    <div class="chart-explanation">
        <p>La matrice de confusion évalue la précision du modèle de prédiction en comparant les résultats prédits avec les résultats réels.
        Les vrais positifs et vrais négatifs (diagonale) représentent les prédictions correctes, tandis que les valeurs hors diagonale montrent les erreurs.
        Cette visualisation aide à évaluer la fiabilité des prédictions du modèle dans différents scénarios de jeu.
        Un modèle équilibré devrait avoir une bonne précision tant pour les prédictions de victoire que de défaite,
        indiquant qu'il capture efficacement les facteurs déterminants dans les deux cas.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Onglet 5: Assistant LoL
with tabs[4]:
    st.markdown("""
    <h2 style="text-align: center; margin-bottom: 30px;">ASSISTANT LoL - ANALYSE IA</h2>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="chart-container">
        <p style="text-align: center; font-size: 1.2rem; color: #C8AA6E;">
            Posez des questions à notre assistant IA pour obtenir des insights sur les données de League of Legends.
            L'assistant peut analyser les tendances, suggérer des stratégies et vous aider à comprendre les facteurs clés de victoire.
        </p>
    """, unsafe_allow_html=True)
    
    # Exemples de questions
    st.subheader("Exemples de questions")
    questions_examples = [
        "Quels sont les facteurs les plus importants pour la victoire ?",
        "Quel est l'impact des objectifs comme les dragons et les hérauts ?",
        "Quelles sont les tendances actuelles de la méta ?",
        "Comment puis-je améliorer mes performances en early game ?"
    ]
    
    selected_question = st.selectbox("Sélectionnez une question ou écrivez la vôtre", [""] + questions_examples)
    
    # Zone de texte pour la question
    user_question = st.text_input("Votre question", value=selected_question)
    
    if st.button("Analyser", key="analyze_button"):
        if user_question:
            st.subheader("Réponse de l'IA")
            
            # Obtenir un échantillon des données pour l'analyse
            data_sample = filtered_df.sample(min(1000, len(filtered_df)))
            
            # Obtenir la réponse de l'IA
            ai_response = analyze_with_ai(data_sample, user_question)
            
            # Afficher la réponse dans un conteneur stylisé
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(9, 20, 40, 0.9), rgba(10, 20, 40, 0.8)); padding: 25px; border-radius: 10px; border-left: 5px solid #0397AB; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);">
                <p style="color: #E8D8A3; font-size: 1.1rem; line-height: 1.6;">{ai_response}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Afficher un graphique pertinent basé sur la question
            st.subheader("Analyse graphique")
            
            if "facteurs" in user_question.lower() or "victoire" in user_question.lower():
                # Afficher l'importance des caractéristiques
                fig = px.bar(
                    feature_importance.head(6), 
                    x='Importance', 
                    y='Feature',
                    orientation='h',
                    color='Importance',
                    color_continuous_scale='blues',
                    labels={'Importance': 'Importance (%)', 'Feature': 'Facteur'},
                    title="Top 6 des facteurs déterminants pour la victoire"
                )
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#C8AA6E'),
                    xaxis=dict(gridcolor='#1E2328'),
                    yaxis=dict(gridcolor='#1E2328'),
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Ajout d'une explication pour le graphique
                st.markdown("""
                <div class="chart-explanation">
                    <p>Ce graphique présente les six facteurs les plus déterminants pour la victoire selon notre modèle d'apprentissage automatique.
                    L'importance de chaque facteur est calculée en fonction de son pouvoir prédictif dans le modèle.
                    Concentrez votre attention sur ces métriques clés pour maximiser vos chances de victoire.
                    Notez que certains facteurs peuvent avoir une importance surprenante par rapport aux idées reçues sur le jeu.</p>
                </div>
                """, unsafe_allow_html=True)
            
            elif "objectifs" in user_question.lower() or "dragon" in user_question.lower() or "héraut" in user_question.lower():
                # Afficher l'impact des objectifs
                objective_metrics = pd.DataFrame({
                    'Objectif': ['Premier Sang', 'Dragon', 'Héraut', 'Tour'],
                    'Impact sur la victoire (%)': [
                        (filtered_df[filtered_df['blueTeamFirstBlood'] == 1]['blueWin'].mean() - 
                         filtered_df[filtered_df['blueTeamFirstBlood'] == 0]['blueWin'].mean()) * 100,
                        (filtered_df[filtered_df['blueTeamDragonKills'] > 0]['blueWin'].mean() - 
                         filtered_df[filtered_df['blueTeamDragonKills'] == 0]['blueWin'].mean()) * 100,
                        (filtered_df[filtered_df['blueTeamHeraldKills'] > 0]['blueWin'].mean() - 
                         filtered_df[filtered_df['blueTeamHeraldKills'] == 0]['blueWin'].mean()) * 100,
                        (filtered_df[filtered_df['blueTeamTowersDestroyed'] > 0]['blueWin'].mean() - 
                         filtered_df[filtered_df['blueTeamTowersDestroyed'] == 0]['blueWin'].mean()) * 100
                    ]
                })
                
                fig = px.bar(
                    objective_metrics, 
                    x='Objectif', 
                    y='Impact sur la victoire (%)',
                    color='Impact sur la victoire (%)',
                    color_continuous_scale='blues',
                    title="Impact des objectifs sur le taux de victoire"
                )
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#C8AA6E'),
                    xaxis=dict(gridcolor='#1E2328'),
                    yaxis=dict(gridcolor='#1E2328'),
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Ajout d'une explication pour le graphique
                st.markdown("""
                <div class="chart-explanation">
                    <p>Ce graphique quantifie l'impact de chaque objectif majeur sur le taux de victoire.
                    La valeur représente la différence de taux de victoire entre les équipes qui obtiennent l'objectif et celles qui ne l'obtiennent pas.
                    Ces données permettent de prioriser les objectifs en fonction de leur impact réel sur l'issue du match.
                    Utilisez ces informations pour optimiser vos rotations et votre prise de décision autour des objectifs.</p>
                </div>
                """, unsafe_allow_html=True)
            
            elif "meta" in user_question.lower() or "tendance" in user_question.lower():
                # Afficher les métriques clés
                fig = px.scatter(
                    filtered_df.sample(min(500, len(filtered_df))), 
                    x='blueTeamTotalGold', 
                    y='blueTeamTotalKills',
                    color='blueWin',
                    color_discrete_map={0: '#C2185B', 1: '#0397AB'},
                    size='objectiveScore',
                    opacity=0.7,
                    labels={
                        'blueTeamTotalGold': 'Or total',
                        'blueTeamTotalKills': 'Kills totaux',
                        'blueWin': 'Résultat',
                        'objectiveScore': 'Score d\'objectifs'
                    },
                    title="Relation entre l'or, les kills et les objectifs"
                )
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#C8AA6E'),
                    xaxis=dict(gridcolor='#1E2328'),
                    yaxis=dict(gridcolor='#1E2328'),
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Ajout d'une explication pour le graphique
                st.markdown("""
                <div class="chart-explanation">
                    <p>Ce graphique illustre les tendances actuelles de la méta en montrant la relation entre l'or total, les kills et le score d'objectifs.
                    Les points bleus représentent les victoires, tandis que les points rouges représentent les défaites.
                    La taille des points indique le score d'objectifs, révélant comment les équipes qui dominent les objectifs tendent à accumuler plus d'or et de kills.
                    Cette visualisation aide à comprendre l'équilibre actuel entre les différentes stratégies de jeu et leur efficacité.</p>
                </div>
                """, unsafe_allow_html=True)
            
            else:
                # Afficher une visualisation générique
                fig = px.scatter(
                    filtered_df.sample(min(500, len(filtered_df))),
                    x='goldDiff',
                    y='killDiff',
                    color='blueWin',
                    color_discrete_map={0: '#C2185B', 1: '#0397AB'},
                    opacity=0.7,
                    labels={
                        'goldDiff': 'Différence d\'or',
                        'killDiff': 'Différence de kills',
                        'blueWin': 'Résultat'
                    },
                    title="Relation entre la différence d'or et la différence de kills"
                )
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#C8AA6E'),
                    xaxis=dict(gridcolor='#1E2328'),
                    yaxis=dict(gridcolor='#1E2328'),
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Ajout d'une explication pour le graphique
                st.markdown("""
                <div class="chart-explanation">
                    <p>Ce graphique montre la relation entre la différence d'or et la différence de kills, colorée par le résultat du match.
                    On observe une forte corrélation entre ces deux métriques, mais également des cas où une équipe peut gagner malgré un déficit dans l'une ou l'autre.
                    Les points bleus (victoires) tendent à se concentrer dans le quadrant supérieur droit, indiquant qu'une avance dans ces deux métriques
                    augmente considérablement les chances de victoire. Cependant, notez les exceptions qui révèlent l'importance d'autres facteurs comme
                    le timing des objectifs et les décisions stratégiques.</p>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Onglet 6: Carte de la Jungle (Nouvelle fonctionnalité)
with tabs[5]:
    st.markdown("""
    <h2 style="text-align: center; margin-bottom: 30px;">CARTE DE LA JUNGLE - ANALYSE D'ACTIVITÉ</h2>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="chart-container">
        <p style="text-align: center; font-size: 1.2rem; color: #C8AA6E;">
            Cette carte de chaleur montre les zones d'activité dans la jungle basées sur les statistiques du match.
            Les zones plus chaudes indiquent une plus grande activité (combats, objectifs, etc.).
        </p>
    """, unsafe_allow_html=True)
    
    # Sélectionner un match aléatoire pour l'analyse
    if len(filtered_df) > 0:
        selected_match = filtered_df.sample(1).iloc[0]
        
        # Créer une carte de chaleur de la jungle
        jungle_grid = create_jungle_heatmap(selected_match)
        
        # Afficher les statistiques du match
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Kills (Blue)", f"{selected_match['blueTeamTotalKills']}")
        with col2:
            st.metric("Dragons (Blue)", f"{selected_match['blueTeamDragonKills']}")
        with col3:
            st.metric("Hérauts (Blue)", f"{selected_match['blueTeamHeraldKills']}")
        with col4:
            st.metric("Résultat", "Victoire" if selected_match['blueWin'] == 1 else "Défaite")
        
        # Créer la carte de chaleur
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Ajouter une image de fond de la carte de la jungle (simulée)
        plt.imshow(np.ones((10, 10, 3)) * 0.1, extent=[0, 10, 0, 10], alpha=0.5)
        
        # Ajouter la carte de chaleur
        heatmap = sns.heatmap(
            jungle_grid, 
            cmap='YlOrRd', 
            alpha=0.7,
            cbar_kws={'label': 'Niveau d\'activité'},
            ax=ax
        )
        
        # Ajouter des marqueurs pour les objectifs
        if selected_match['blueTeamDragonKills'] > 0:
            plt.scatter([7], [7], s=300, c='#0397AB', marker='o', edgecolors='white', linewidths=2, label='Dragon')
        
        if selected_match['blueTeamHeraldKills'] > 0:
            plt.scatter([2], [2], s=300, c='#C8AA6E', marker='s', edgecolors='white', linewidths=2, label='Héraut')
        
        # Ajouter des étiquettes
        plt.text(7, 7, 'Dragon', fontsize=12, ha='center', va='center', color='white', fontweight='bold')
        plt.text(2, 2, 'Héraut', fontsize=12, ha='center', va='center', color='white', fontweight='bold')
        plt.text(0.5, 9.5, 'Base Bleue', fontsize=12, ha='left', va='center', color='#0397AB', fontweight='bold')
        plt.text(9.5, 0.5, 'Base Rouge', fontsize=12, ha='right', va='center', color='#C2185B', fontweight='bold')
        
        # Personnaliser l'apparence
        plt.title('Carte d\'activité de la Jungle', fontsize=16, color='#C8AA6E')
        plt.xlabel('Coordonnée X', color='#C8AA6E')
        plt.ylabel('Coordonnée Y', color='#C8AA6E')
        plt.legend(loc='upper right')
        
        # Personnaliser les couleurs pour le thème LoL
        plt.rcParams['text.color'] = '#C8AA6E'
        plt.rcParams['axes.labelcolor'] = '#C8AA6E'
        plt.rcParams['xtick.color'] = '#C8AA6E'
        plt.rcParams['ytick.color'] = '#C8AA6E'
        
        st.pyplot(fig)
        
        # Ajout d'une explication pour la carte
        st.markdown(f"""
        <div class="chart-explanation">
            <p>Cette carte de chaleur visualise les points chauds d'activité dans la jungle pour ce match.
            Les zones plus intenses (rouge-orange) indiquent une plus grande activité, généralement autour des objectifs majeurs
            comme le dragon ({selected_match['blueTeamDragonKills']} tué(s) par l'équipe bleue) et le héraut ({selected_match['blueTeamHeraldKills']} tué(s)).
            L'équipe bleue a {"sécurisé" if selected_match['blueTeamDragonKills'] > 0 else "manqué"} le contrôle du dragon et 
            {"obtenu" if selected_match['blueTeamHeraldKills'] > 0 else "perdu"} le héraut.
            Les zones les plus actives révèlent les chemins de gank préférés et les points de contestation fréquents.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("Aucune donnée disponible pour créer la carte de la jungle. Veuillez ajuster les filtres.")
    
    st.markdown("</div>", unsafe_allow_html=True)

# Onglet 7: Timeline de Match (Nouvelle fonctionnalité)
with tabs[6]:
    st.markdown("""
    <h2 style="text-align: center; margin-bottom: 30px;">TIMELINE DES ÉVÉNEMENTS DE MATCH</h2>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="chart-container">
        <p style="text-align: center; font-size: 1.2rem; color: #C8AA6E;">
            Cette timeline montre les événements clés d'un match basés sur les statistiques.
            Vous pouvez voir comment les objectifs et les avantages ont été obtenus au fil du temps.
        </p>
    """, unsafe_allow_html=True)
    
    # Sélectionner un match aléatoire pour l'analyse
    if len(filtered_df) > 0:
        selected_match = filtered_df.sample(1).iloc[0]
        
        # Générer une timeline d'événements
        events = generate_match_timeline(selected_match)
        
        # Afficher les statistiques du match
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Kills (Blue)", f"{selected_match['blueTeamTotalKills']}")
        with col2:
            st.metric("Or (Blue)", f"{selected_match['blueTeamTotalGold']}")
        with col3:
            st.metric("Objectifs", f"{selected_match['objectiveScore']:.1f}")
        with col4:
            st.metric("Résultat", "Victoire" if selected_match['blueWin'] == 1 else "Défaite")
        
        # Créer un graphique de timeline
        fig = go.Figure()
        
        # Ajouter une ligne pour l'or
        minutes = list(range(11))
        gold_values = [0]
        for i in range(1, 11):
            if i < 5:
                # Croissance plus lente au début
                gold_values.append(selected_match['blueTeamTotalGold'] * (i / 10) ** 2)
            else:
                # Croissance plus rapide vers la fin
                gold_values.append(selected_match['blueTeamTotalGold'] * (i / 10) ** 1.5)
        
        fig.add_trace(go.Scatter(
            x=minutes,
            y=gold_values,
            mode='lines',
            name='Or (Blue)',
            line=dict(color='#C8AA6E', width=3)
        ))
        
        # Ajouter des marqueurs pour les événements
        for event in events:
            if event['team'] == 'blue':
                color = '#0397AB'
            else:
                color = '#C2185B'
            
            fig.add_trace(go.Scatter(
                x=[event['time']],
                y=[gold_values[event['time']]],
                mode='markers+text',
                marker=dict(size=15, color=color, symbol='star'),
                text=[event['event']],
                textposition='top center',
                name=event['event'],
                hoverinfo='text',
                hovertext=f"{event['time']} min: {event['event']}"
            ))
        
        # Personnaliser l'apparence
        fig.update_layout(
            title='Timeline des événements du match (0-10 minutes)',
            xaxis_title='Temps (minutes)',
            yaxis_title='Or',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#C8AA6E'),
            xaxis=dict(gridcolor='#1E2328'),
            yaxis=dict(gridcolor='#1E2328'),
            height=500,
            hovermode='closest'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Ajout d'une explication pour le graphique
        st.markdown("""
        <div class="chart-explanation">
            <p>Cette timeline visualise la progression de l'or et les événements clés des 10 premières minutes du match.
            La courbe d'or montre comment l'économie de l'équipe se développe, tandis que les étoiles marquent les moments décisifs.
            Les événements en bleu sont favorables à l'équipe bleue, tandis que ceux en rouge sont favorables à l'équipe rouge.
            Observez comment chaque événement majeur (Premier Sang, Dragon, Héraut) influence la trajectoire de l'or et crée
            des opportunités pour étendre l'avantage ou revenir dans le match.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Afficher la timeline sous forme de liste
        st.subheader("Événements clés")
        
        st.markdown("""
        <div class="timeline">
        """, unsafe_allow_html=True)
        
        for i, event in enumerate(events):
            position = "left" if i % 2 == 0 else "right"
            team_color = "#0397AB" if event['team'] == 'blue' else "#C2185B"
            
            st.markdown(f"""
            <div class="timeline-container {position}">
                <div class="timeline-content" style="border-color: {team_color};">
                    <h3 style="color: {team_color}; margin-top: 0;">{event['time']} min</h3>
                    <p style="color: #E8D8A3;">{event['event']}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        </div>
        """, unsafe_allow_html=True)
        
        # Ajouter une analyse de la timeline
        st.markdown(f"""
        <div class="chart-explanation">
            <p>Cette chronologie détaille les moments clés du match et leur impact sur le déroulement de la partie.
            {"L'équipe bleue a pris l'avantage tôt avec le premier sang, ce qui a créé un momentum favorable." if selected_match['blueTeamFirstBlood'] == 1 else "L'équipe rouge a pris l'avantage tôt avec le premier sang, créant une pression sur l'équipe bleue."}
            {"Le contrôle des objectifs précoces comme le dragon et le héraut a permis à l'équipe bleue de maintenir son avantage." if selected_match['blueTeamDragonKills'] > 0 or selected_match['blueTeamHeraldKills'] > 0 else "L'équipe bleue n'a pas réussi à sécuriser les objectifs précoces, ce qui a permis à l'équipe rouge de rester dans le match."}
            {"Au final, l'équipe bleue a réussi à convertir son avantage en victoire." if selected_match['blueWin'] == 1 else "Malgré les efforts, l'équipe bleue n'a pas réussi à convertir ses avantages en victoire."}
            Les moments critiques identifiés ici sont typiques des points de bascule dans les matchs de haut niveau.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("Aucune donnée disponible pour créer la timeline. Veuillez ajuster les filtres.")
    
    st.markdown("</div>", unsafe_allow_html=True)

# Pied de page
st.markdown("""
<div style="text-align: center; margin-top: 50px; padding: 30px; background: linear-gradient(135deg, rgba(9, 20, 40, 0.9), rgba(10, 20, 40, 0.8)); border-radius: 10px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);">
    <h3 style="color: #C8AA6E; margin-top: 0;">LEAGUE OF LEGENDS ANALYTICS HUB</h3>
    <p style="color: #C8AA6E; font-size: 1rem;">Données: Kaggle - League of Legends SoloQ Matches 2024</p>
    <div style="display: flex; justify-content: center; margin-top: 20px;">
        <div class="badge" style="--i: 0;">Data Science</div>
        <div class="badge" style="--i: 1;">Machine Learning</div>
        <div class="badge" style="--i: 2;">League of Legends</div>
        <div class="badge" style="--i: 3;">Analytics</div>
    </div>
</div>
""", unsafe_allow_html=True)
