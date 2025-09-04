import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import os

# ------------------------------------------------------------
# Configurazione pagina
st.set_page_config(
    page_title='Monitoraggio Attività delle macchine',
    page_icon=':earth_americas:',
    layout="wide"
)

# ------------------------------------------------------------
# Funzione per caricare i dati dal SQL Server
@st.cache_data
def load_data():
    try:
        from sqlalchemy import create_engine

        # Connessione al server SQL usando SQLAlchemy + pyodbc
        conn_str = (
            "mssql+pyodbc://sa:BIRoccio@192.168.50.243/BENOZZIPROD?driver=SQL+Server"
        )
        engine = create_engine(conn_str)

        # Leggi direttamente la vista
        query = "SELECT * FROM [dbo].[RiepilogoPerMacchinaData]"
        df = pd.read_sql(query, engine)

        # --------------------------------------------------------
        # Trasforma le colonne in ore corrette
        for col in ["Work", "Pause", "Alarm", "Down"]:
            df[col] = df[col]  # / 100_000_000 se necessario

        # --------------------------------------------------------
        df['Anno'] = df['Data'].dt.year
        df['Settimana'] = df['Data'].dt.isocalendar().week
        df['Mese'] = df['Data'].dt.month

        return df

    except Exception as e:
        st.error(f"Errore nel caricamento dei dati: {e}")
        return pd.DataFrame()  # ritorna un DataFrame vuoto se fallisce

# ------------------------------------------------------------
# Esempio di utilizzo
df = load_data()

# ------------------------------------------------------------
# Traduzioni
translations = {
    "it": {"Work": "Lavoro", "Pause": "Pausa", "Alarm": "Allarme", "Down": "Spenta"},
    "en": {"Work": "Work", "Pause": "Pause", "Alarm": "Alarm", "Down": "Down"},
}

# ------------------------------------------------------------
# Gruppi di macchine per macro-selezioni
gruppi_macchine = {
    "FRESE ITALIA": [
        "1-PFG", "18-MCM_CLOCK", "24-MCM_CONCEPT", "33-VTC800_MAZAK",
        "36-DMG_NMV_3000", "72-VARIAXIS_J500", "73-VARIAXIS_J500",
        "103-DMG_NMV_5000", "104-DMG_NMV_3000", "136_DMG", "158-DMG"
    ],
    "TORNI ITALIA": [
        "7-SL25", "8-SL150MC", "19-INTEGREX_J200", "26-INTEGREX_J200",
        "27-INTEGREX_200", "30-LYNX_300M", "31-QTN_200_MSY", "34-INTEGREX_I300",
        "66-QTN_200_MSY", "70-PUMA_GT2600LM", "71-INTEGREX", "77-INTEGREX"
    ],
    "ELETTROEROSIONE ITALIA": [
        "16-ALFA1_IA_FANUC", "81-MITSUBISHI_MV1200S", 
        "115-MITSUBISHI_MV1200R", "161-MITSUBISHI_MV1200R"
    ],
    "TUTTE ITALIA": [
        "1-PFG", "7-SL25", "8-SL150MC", "16-ALFA1_IA_FANUC", "18-MCM_CLOCK",
        "19-INTEGREX_J200", "24-MCM_CONCEPT", "26-INTEGREX_J200", "27-INTEGREX_200",
        "33-VTC800_MAZAK", "103-DMG_NMV_5000", "30-LYNX_300M", "31-QTN_200_MSY",
        "34-INTEGREX_I300", "36-DMG_NMV_3000", "66-QTN_200_MSY", "70-PUMA_GT2600LM",
        "71-INTEGREX", "72-VARIAXIS_J500", "73-VARIAXIS_J500", "77-INTEGREX",
        "81-MITSUBISHI_MV1200S", "104-DMG_NMV_3000", "115-MITSUBISHI_MV1200R",
        "136_DMG", "158-DMG", "161-MITSUBISHI_MV1200R"
    ],
    "FRESE TUNISIA": ["F03"],
    "TORNI TUNISIA": ["T15", "T22"],
    "TUTTE TUNISIA": ["F03", "T15", "T22"]
}

mesi_nome = {
    1: "Gennaio", 2: "Febbraio", 3: "Marzo", 4: "Aprile",
    5: "Maggio", 6: "Giugno", 7: "Luglio", 8: "Agosto",
    9: "Settembre", 10: "Ottobre", 11: "Novembre", 12: "Dicembre"
}

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
    import re

   # Lista dei nomi macchina originali
    macchine = df["DescrMacchina"].unique()

    # Aggiungi i gruppi definiti
    macchine = list(macchine) + list(gruppi_macchine.keys())

    # Ordina i nomi macchina numericamente (solo per quelli che hanno un numero)
    def estrai_numero(nome):
        match = re.match(r"[A-Za-z]*?(\d+)", nome)
        if match:
            return int(match.group(1))
        # Metti in fondo i gruppi o nomi senza numero
        return 9999

    macchine_sorted = sorted(macchine, key=lambda x: estrai_numero(x))

    # Selectbox mostra i nomi originali
    macchina = st.selectbox(f"Macchina - {label}", macchine_sorted, key=f"macchina_{label}")

    if tipo_periodo == "Giorno":
        giorni_disponibili = sorted(df['Data'].dt.date.unique())  # tutti i giorni disponibili nel dataset

        # Trova il penultimo giorno disponibile
        if len(giorni_disponibili) >= 2:
            default_giorno = giorni_disponibili[-2]
        else:
            default_giorno = giorni_disponibili[0]

        giorno_sel = st.date_input(
            f"Seleziona giorno - {label}",
            default_giorno,
            key=f"giorno_{label}"
        )

        start_date = pd.to_datetime(giorno_sel)
        end_date = start_date

    elif tipo_periodo == "Settimana":
        anno_sel = st.selectbox(
            f"Anno - {label}", 
            df['Anno'].unique(), 
            index=0, 
            key=f"anno_{label}"
        )

        settimane_disponibili = sorted(df[df['Anno'] == anno_sel]['Settimana'].unique())

        # Trova la penultima settimana disponibile
        if len(settimane_disponibili) >= 2:
            default_index = len(settimane_disponibili) - 2  # penultima
        else:
            default_index = 0  # se c'è solo una settimana disponibile

        settimana_sel = st.selectbox(
            f"Settimana - {label}", 
            settimane_disponibili, 
            index=default_index, 
            key=f"settimana_{label}"
        )

        # Calcola le date di inizio e fine settimana
        start_date = pd.to_datetime(f"{anno_sel}-W{settimana_sel}-1", format="%Y-W%W-%w")
        end_date = start_date + timedelta(days=6)

    elif tipo_periodo == "Mese":
        anno_sel = st.selectbox(
            f"Anno - {label}",
            df['Anno'].unique(),
            index=0,
            key=f"annoM_{label}"
        )

        mesi_disponibili = sorted(df[df['Anno'] == anno_sel]['Mese'].unique())

        # Trova l'indice del penultimo mese disponibile
        if len(mesi_disponibili) >= 2:
            default_index = len(mesi_disponibili) - 2  # penultimo mese
        else:
            default_index = 0  # se c'è solo un mese disponibile

        mese_sel = st.selectbox(
            f"Mese - {label}",
            mesi_disponibili,
            format_func=lambda x: mesi_nome[x],
            index=default_index,
            key=f"mese_{label}"
        )

        start_date = pd.to_datetime(f"{anno_sel}-{mese_sel:02d}-01")
        if mese_sel == 12:
            end_date = pd.to_datetime(f"{anno_sel+1}-01-01") - timedelta(days=1)
        else:
            end_date = pd.to_datetime(f"{anno_sel}-{mese_sel+1:02d}-01") - timedelta(days=1)

    elif tipo_periodo == "Periodo personalizzato":
        giorni_disponibili = sorted(df['Data'].dt.date.unique())

        if len(giorni_disponibili) >= 2:
            default_start = giorni_disponibili[-2]
            default_end = giorni_disponibili[-1]
        else:
            default_start = giorni_disponibili[0]
            default_end = giorni_disponibili[0]

        intervallo = st.date_input(
            f"Seleziona periodo - {label}",
            (default_start, default_end),
            key=f"periodo_{label}"
        )

        # Caso: utente ha selezionato solo 1 data
        if isinstance(intervallo, tuple) and len(intervallo) == 2:
            start_date, end_date = intervallo
        else:
            # Evita errori: non filtrare ancora
            st.warning("Seleziona entrambe le date per il periodo personalizzato.")
            return macchina, None, None

        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

    return macchina, start_date, end_date

# ------------------------------------------------------------
# Funzione per filtrare dati
def filter_data(df, macchina, start_date, end_date):
    if macchina in gruppi_macchine:
        macchine_da_usare = gruppi_macchine[macchina]
        mask = (
            df["DescrMacchina"].isin(macchine_da_usare) &
            (df["Data"] >= start_date) &
            (df["Data"] <= end_date)
        )
    else:
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

    if start_date is not None and end_date is not None:
        df_filtered = filter_data(df, macchina, start_date, end_date)

        if df_filtered.empty:
            if tipo_periodo == "Giorno":
                st.warning("Dati non presenti in questo giorno")
            else:
                st.warning("Dati non presenti in questo periodo")
        else:
            sums = df_filtered[["Work", "Pause", "Alarm", "Down"]].sum()
            sums.index = [translations["it"][col] for col in sums.index]
            draw_pie(sums, f"Macchina {macchina} - Periodo selezionato", key=f"{macchina}_{tipo_periodo}")

else:
    # confronto due grafici affiancati
    col1, col2 = st.columns(2)

    with col1:
        macchina1, start1, end1 = filtri_grafico("Grafico 1", tipo_periodo, df)
        if start1 is not None and end1 is not None:
            df1 = filter_data(df, macchina1, start1, end1)

            if df1.empty:
                if tipo_periodo == "Giorno":
                    st.warning("Dati non presenti in questo giorno")
                else:
                    st.warning("Dati non presenti in questo periodo")
            else:
                sums1 = df1[["Work", "Pause", "Alarm", "Down"]].sum()
                sums1.index = [translations["it"][col] for col in sums1.index]
                draw_pie(sums1, f"Macchina {macchina1} - Periodo selezionato", key=f"{macchina1}_{tipo_periodo}_1")

    with col2:
        macchina2, start2, end2 = filtri_grafico("Grafico 2", tipo_periodo, df)
        if start2 is not None and end2 is not None:
            df2 = filter_data(df, macchina2, start2, end2)

            if df2.empty:
                if tipo_periodo == "Giorno":
                    st.warning("Dati non presenti per questo giorno")
                else:
                    st.warning("Dati non presenti per questo periodo")
            else:
                sums2 = df2[["Work", "Pause", "Alarm", "Down"]].sum()
                sums2.index = [translations["it"][col] for col in sums2.index]
                draw_pie(sums2, f"Macchina {macchina2} - Periodo selezionato", key=f"{macchina2}_{tipo_periodo}_2")
