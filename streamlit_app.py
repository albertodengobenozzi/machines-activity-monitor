import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

# ------------------------------------------------------------
# Configurazione pagina
st.set_page_config(
    page_title='Activity Monitor 19-INTEGREX_J200',
    page_icon=':earth_americas:',
    layout="wide"
)

# ------------------------------------------------------------
# Funzione per caricare i dati dal CSV
@st.cache_data
def load_data():
    file_path = r"P:\AREA LEAN\KPI\Naldoni\TEMPI PER MACCHINA\DA CIMCO\Activity Monitor T19.csv"
    df = pd.read_csv(file_path, sep=";", parse_dates=["Data"])
    return df

df = load_data()

# ------------------------------------------------------------
# Traduzioni
translations = {
    "it": {"Work": "Lavoro", "Pause": "Pausa", "Alarm": "Allarme", "Down": "Spenta"},
    "en": {"Work": "Work", "Pause": "Pause", "Alarm": "Alarm", "Down": "Down"},
    "fr": {"Work": "Travail", "Pause": "Pause", "Alarm": "Alarme", "Down": "Éteinte"},
    "es": {"Work": "Trabajo", "Pause": "Pausa", "Alarm": "Alarma", "Down": "Apagada"},
    "de": {"Work": "Arbeit", "Pause": "Pause", "Alarm": "Alarm", "Down": "Aus"}
}

# ------------------------------------------------------------
# Sidebar
st.sidebar.header("Impostazioni")

lingua = st.sidebar.selectbox("Lingua", ["it", "en", "fr", "es", "de"], format_func=lambda x: {
    "it": "Italiano", "en": "English", "fr": "Français", "es": "Español", "de": "Deutsch"
}[x])

macchine = df["DescrMacchina"].unique()
macchina = st.sidebar.selectbox("Macchina", macchine)

modalita_confronto = st.sidebar.checkbox("Attiva modalità confronto")

periodo = st.sidebar.radio(
    "Periodo",
    ["Giorno", "Settimana", "Mese", "Periodo personalizzato"]
)

oggi = datetime.today()
if periodo == "Giorno":
    start_date = oggi
    end_date = oggi
elif periodo == "Settimana":
    start_date = oggi - timedelta(days=7)
    end_date = oggi
elif periodo == "Mese":
    start_date = oggi - timedelta(days=30)
    end_date = oggi
elif periodo == "Periodo personalizzato":
    start_date = st.sidebar.date_input("Data di inizio", oggi - timedelta(days=7))
    end_date = st.sidebar.date_input("Data di fine", oggi)

# ------------------------------------------------------------
# Filtraggio dati
mask = (
    (df["DescrMacchina"] == macchina) &
    (df["Data"] >= pd.to_datetime(start_date)) &
    (df["Data"] <= pd.to_datetime(end_date))
)
df_filtered = df.loc[mask]

# Somma dei dati
sums = df_filtered[["Work", "Pause", "Alarm", "Down"]].sum()

# Traduzioni
sums.index = [translations[lingua][col] for col in sums.index]

# ------------------------------------------------------------
# Disegno grafico
def draw_pie(sums, title):
    fig = px.pie(
        names=sums.index,
        values=sums.values,
        title=title
    )
    st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------------------
# Layout pagina
st.title(":earth_americas: Activity Monitor 19-INTEGREX_J200")

if modalita_confronto:
    col1, col2 = st.columns(2)

    with col1:
        draw_pie(sums, f"Macchina {macchina} - Periodo selezionato")

    with col2:
        # Se in confronto puoi prevedere un secondo filtro (es. altra macchina)
        altra_macchina = st.sidebar.selectbox("Seconda macchina per confronto", macchine)
        mask2 = (
            (df["DescrMacchina"] == altra_macchina) &
            (df["Data"] >= pd.to_datetime(start_date)) &
            (df["Data"] <= pd.to_datetime(end_date))
        )
        df2 = df.loc[mask2]
        sums2 = df2[["Work", "Pause", "Alarm", "Down"]].sum()
        sums2.index = [translations[lingua][col] for col in sums2.index]
        draw_pie(sums2, f"Macchina {altra_macchina} - Periodo selezionato")

else:
    draw_pie(sums, f"Macchina {macchina} - Periodo selezionato")

