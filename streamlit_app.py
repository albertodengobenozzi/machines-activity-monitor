import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import calendar

# ------------------------------------------------------------
# Configurazione pagina
st.set_page_config(
    page_title='Monitoraggio Attività delle macchine',
    page_icon=':earth_americas:',
    layout="wide"
)

# ------------------------------------------------------------
# Funzione per caricare i dati dal CSV
@st.cache_data
def load_data():
    file_path = r"/workspaces/activity-monitor-19-integrex-j200/Machines Activity Monitor.csv"
    df = pd.read_csv(file_path, sep=";", parse_dates=["Data"])
    df['Anno'] = df['Data'].dt.year
    df['Settimana'] = df['Data'].dt.isocalendar().week
    df['Mese'] = df['Data'].dt.month
    return df

df = load_data()

# ------------------------------------------------------------
# Traduzioni
translations = {
    "it": {"Work": "Lavoro", "Pause": "Pausa", "Alarm": "Allarme", "Down": "Spenta"},
    "en": {"Work": "Work", "Pause": "Pause", "Alarm": "Alarm", "Down": "Down"},
}

mesi_nome = {i: calendar.month_name[i] for i in range(1,13)}

# ------------------------------------------------------------
# Sidebar solo per il periodo
with st.sidebar.expander("Seleziona periodo", expanded=True):
    tipo_periodo = st.radio(
        "Periodo",
        ["Giorno", "Settimana", "Mese", "Periodo personalizzato"]
    )

st.title(":earth_americas: Monitoraggio attività delle macchine")

# ------------------------------------------------------------
# Funzione per selezionare i filtri di un grafico
def filtri_grafico(label, tipo_periodo, df):
    st.subheader(label)
    macchine = df["DescrMacchina"].unique()
    macchina = st.selectbox(f"Macchina - {label}", macchine, key=f"macchina_{label}")

    oggi = datetime.today()
    if tipo_periodo == "Giorno":
        giorno_sel = st.date_input(f"Seleziona giorno - {label}", oggi.date(), key=f"giorno_{label}")
        start_date = pd.to_datetime(giorno_sel)
        end_date = start_date

    elif tipo_periodo == "Settimana":
        anno_sel = st.selectbox(f"Anno - {label}", df['Anno'].unique(), index=0, key=f"anno_{label}")
        settimane_disponibili = df[df['Anno']==anno_sel]['Settimana'].unique()
        settimana_sel = st.selectbox(f"Settimana - {label}", sorted(settimane_disponibili), key=f"settimana_{label}")
        start_date = pd.to_datetime(f"{anno_sel}-W{settimana_sel}-1", format="%Y-W%W-%w")
        end_date = start_date + timedelta(days=6)

    elif tipo_periodo == "Mese":
        anno_sel = st.selectbox(f"Anno - {label}", df['Anno'].unique(), index=0, key=f"annoM_{label}")
        mesi_disponibili = df[df['Anno']==anno_sel]['Mese'].unique()
        mese_sel = st.selectbox(f"Mese - {label}", sorted(mesi_disponibili), format_func=lambda x: mesi_nome[x], key=f"mese_{label}")
        start_date = pd.to_datetime(f"{anno_sel}-{mese_sel:02d}-01")
        if mese_sel == 12:
            end_date = pd.to_datetime(f"{anno_sel+1}-01-01") - timedelta(days=1)
        else:
            end_date = pd.to_datetime(f"{anno_sel}-{mese_sel+1:02d}-01") - timedelta(days=1)

    elif tipo_periodo == "Periodo personalizzato":
        start_date = pd.to_datetime(st.date_input(f"Data di inizio - {label}", oggi - timedelta(days=7), key=f"start_{label}"))
        end_date = pd.to_datetime(st.date_input(f"Data di fine - {label}", oggi, key=f"end_{label}"))

    return macchina, start_date, end_date

# ------------------------------------------------------------
# Funzione per filtrare dati
def filter_data(df, macchina, start_date, end_date):
    mask = (
        (df["DescrMacchina"] == macchina) &
        (df["Data"] >= start_date) &
        (df["Data"] <= end_date)
    )
    return df.loc[mask]

# ------------------------------------------------------------
# Funzione per il grafico con colori personalizzati
def draw_pie(sums, title, key):
    # Mappa colori fissi
    color_map = {
        "Lavoro": "green",
        "Allarme": "red",
        "Pausa": "yellow",
        "Spenta": "gray"
    }

    fig = px.pie(
        names=sums.index,
        values=sums.values,
        title=title,
        color=sums.index,
        color_discrete_map=color_map
    )
    fig.update_traces(
        textinfo='label+percent+value',
        texttemplate="%{label}: %{value:.2f} (%{percent})",
        textposition='inside'
    )
    fig.update_layout(width=1000, height=800, legend=dict(orientation="h"))
    st.plotly_chart(fig, use_container_width=True, key=key)

# ------------------------------------------------------------
# Modalità confronto
modalita_confronto = st.checkbox("Attiva modalità confronto")

if not modalita_confronto:
    # singolo grafico
    macchina, start_date, end_date = filtri_grafico("Grafico", tipo_periodo, df)
    df_filtered = filter_data(df, macchina, start_date, end_date)
    sums = df_filtered[["Work", "Pause", "Alarm", "Down"]].sum()
    sums.index = [translations["it"][col] for col in sums.index]
    draw_pie(sums, f"Macchina {macchina} - Periodo selezionato", key=f"{macchina}_{tipo_periodo}")

else:
    # confronto due grafici affiancati
    col1, col2 = st.columns(2)

    with col1:
        macchina1, start1, end1 = filtri_grafico("Grafico 1", tipo_periodo, df)
        df1 = filter_data(df, macchina1, start1, end1)
        sums1 = df1[["Work", "Pause", "Alarm", "Down"]].sum()
        sums1.index = [translations["it"][col] for col in sums1.index]
        draw_pie(sums1, f"Macchina {macchina1} - Periodo selezionato", key=f"{macchina1}_{tipo_periodo}_1")

    with col2:
        macchina2, start2, end2 = filtri_grafico("Grafico 2", tipo_periodo, df)
        df2 = filter_data(df, macchina2, start2, end2)
        sums2 = df2[["Work", "Pause", "Alarm", "Down"]].sum()
        sums2.index = [translations["it"][col] for col in sums2.index]
        draw_pie(sums2, f"Macchina {macchina2} - Periodo selezionato", key=f"{macchina2}_{tipo_periodo}_2")
