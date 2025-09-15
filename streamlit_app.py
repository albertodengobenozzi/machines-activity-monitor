import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import os
import socket
from streamlit_autorefresh import st_autorefresh

# Mappa IP → macchina di default
default_macchine_ip = {
    #"": "1-PFG",
    #"": "F03",
    "192.168.50.109": "7-SL25",
    "192.168.50.118": "8-SL150MC",
    #"": "T15",
    #"": "16-ALFA1_IA_FANUC",
    "192.168.50.70": "18-MCM_CLOCK",
    "192.168.50.7": "19-INTEGREX_J200",
    "192.168.50.34": "19-INTEGREX_J200",   # Alberto
    "192.168.50.199": "19-INTEGREX_J200", # Mirko
    #"": "T22",
    "192.168.50.100": "24-MCM_CONCEPT",
    "192.168.50.119": "26-INTEGREX_J200",
    "192.168.50.98": "27-INTEGREX_200",
    "192.168.50.97": "30-LYNX_300M",
    "192.168.50.113": "31-QTN_200_MSY",
    "192.168.50.39": "33-VTC800_MAZAK",
    "192.168.50.106": "34-INTEGREX_I300",
    "192.168.50.107": "36-DMG_NMV_3000",
    "192.168.50.122": "66-QTN_200_MSY",
    "192.168.50.173": "70-PUMA_GT2600LM",
    "192.168.50.182": "71-INTEGREX",
    "192.168.50.108": "72-VARIAXIS_J500",
    "192.168.50.112": "73-VARIAXIS_J500",
    "192.168.50.5": "77-INTEGREX",
    "192.168.50.57": "81-MITSUBISHI_MV1200S",
    "192.168.50.126": "103-DMG_NMV_5000",
    "192.168.50.56": "104-DMG_NMV_3000",
    "192.168.50.125": "115-MITSUBISHI_MV1200R",
    "192.168.50.30": "136_DMG",
    "192.168.50.110": "158-DMG",
    "192.168.50.134": "161-MITSUBISHI_MV1200R",
    None: "19-INTEGREX_J200"              # fallback se non rileva l'IP
    # aggiungi altri PC con i loro IP
}

# Target minimi per macchina (valori base)
target_macchine = {
    "1-PFG": 8.00,
    "F03": 8.00,
    "7-SL25": 6.00,
    "8-SL150MC": 6.00,
    "T15":14.00,
    "16-ALFA1_IA_FANUC":9.00,
    "18-MCM_CLOCK":15.00,
    "19-INTEGREX_J200": 13.00,
    "T22":14.00,
    "24-MCM_CONCEPT": 22.00,
    "26-INTEGREX_J200":12.00,
    "27-INTEGREX_200":11.00,
    "30-LYNX_300M":8.00,
    "31-QTN_200_MSY":12.00,
    "33-VTC800_MAZAK":8.00,
    "34-INTEGREX_I300":14.00,
    "36-DMG_NMV_3000":20.00,
    "66-QTN_200_MSY":13.00,
    "70-PUMA_GT2600LM":6.00,
    "71-INTEGREX":12.00,
    "72-VARIAXIS_J500":11.00,
    "73-VARIAXIS_J500":10.00,
    "77-INTEGREX":12.00,
    "81-MITSUBISHI_MV1200S":13.00,
    "103-DMG_NMV_5000":10.00,
    "104-DMG_NMV_3000":20.00,
    "115-MITSUBISHI_MV1200R":10.00,
    "136_DMG":20.00,
    "158-DMG":20.00,
    "161-MITSUBISHI_MV1200R":13.00,
    # aggiungi altre macchine qui...
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
# Aggiorna ogni 15 minuti
st_autorefresh(interval=900*1000, key="dataframe_refresh")

# Funzione per recuperare l'IP del client
def get_client_ip():
    try:
        # streamlit runtime context
        from streamlit.web.server.browser_websocket_handler import BrowserWebSocketHandler
        from streamlit.web.server.server import Server

        # elenco delle connessioni
        session_info = Server.get_current()._session_info_by_id
        for _, si in session_info.items():
            if isinstance(si.ws, BrowserWebSocketHandler):
                # "si.ws.request.remote_ip" contiene l'IP del client
                return si.ws.request.remote_ip
    except Exception:
        return None

def get_min_max(macchina, tipo_periodo, start_date, end_date):
    giorni_periodo = (end_date - start_date).days + 1

    # Calcolo max_barra sempre come prima
    if macchina in gruppi_macchine:
        # max per gruppo: 24 ore * giorni * numero macchine
        max_barra = 24 * giorni_periodo * len(gruppi_macchine[macchina])
    else:
        max_barra = 24 * giorni_periodo

    # Calcolo minimo
    if macchina in gruppi_macchine:
        # somma dei target di tutte le macchine del gruppo
        minimo = 0
        for m in gruppi_macchine[macchina]:
            if m in target_macchine:
                minimo += target_macchine[m] * giorni_periodo
            else:
                # fallback alla regola generale per singola macchina
                if tipo_periodo == "Giorno":
                    minimo += 12
                elif tipo_periodo == "Settimana":
                    minimo += 84
                else:
                    minimo += 12 * giorni_periodo
    else:
        # singola macchina
        if macchina in target_macchine:
            minimo = target_macchine[macchina] * giorni_periodo
        else:
            if tipo_periodo == "Giorno":
                minimo = 12
            elif tipo_periodo == "Settimana":
                minimo = 84
            else:
                minimo = 12 * giorni_periodo

    return minimo, max_barra

# ------------------------------------------------------------
# Configurazione pagina
st.set_page_config(
    page_title='Monitoraggio Attività delle macchine',
    page_icon=':earth_americas:',
    layout="wide"
)

# ------------------------------------------------------------
# Funzione per caricare i dati dal SQL Server 
@st.cache_data(ttl=600) # tempo di vita della cache; il risultato viene considerato valido per xxx secondi.
# Dopo xxx secondi la cache scade, quindi la funzione verrà eseguita di nuovo per aggiornare i dati.
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

    # Ordina i nomi macchina numericamente
    def estrai_numero(nome):
        match = re.match(r"[A-Za-z]*?(\d+)", nome)
        return int(match.group(1)) if match else 9999

    macchine_sorted = sorted(macchine, key=lambda x: estrai_numero(x))

    # --- Recupera l'IP del PC client da link personalizzato per ogni macchina---
    query_params = st.query_params
    client_ip_raw = query_params.get("pc", None)  # può essere lista o stringa

    # gestisci entrambi i casi
    if isinstance(client_ip_raw, list):
        client_ip = client_ip_raw[0] if client_ip_raw else None
    else:
        client_ip = client_ip_raw

    macchina_default = default_macchine_ip.get(client_ip, None)
    
    if macchina_default and macchina_default in macchine_sorted:
        default_index = macchine_sorted.index(macchina_default)
    else:
        default_index = 0

    macchina = st.selectbox(
        f"Macchina - {label}",
        macchine_sorted,
        index=default_index,
        key=f"macchina_{label}"
    )

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
        # Lista anni disponibili ordinata
        anni_disponibili = sorted(df['Anno'].unique())

        # Trova l'indice dell'anno corrente
        anno_corrente = datetime.now().year
        if anno_corrente in anni_disponibili:
            default_index_anno = anni_disponibili.index(anno_corrente)
        else:
            default_index_anno = 0  # se l'anno corrente non è nei dati

        # Selectbox per l'anno
        anno_sel = st.selectbox(
            f"Anno - {label}",
            anni_disponibili,
            index=default_index_anno,
            key=f"anno_{label}"
        )

        # Lista settimane disponibili per l'anno selezionato
        settimane_disponibili = sorted(df[df['Anno'] == anno_sel]['Settimana'].unique())

        # Calcola settimana precedente a quella corrente
        oggi = datetime.now()
        anno_corrente_iso, settimana_corrente_iso, _ = oggi.isocalendar()
        settimana_precedente = settimana_corrente_iso - 1
        anno_settimana_precedente = anno_corrente_iso

        if settimana_precedente == 0:  # se la settimana corrente è la 1, vai all'ultima settimana dell'anno precedente
            anno_settimana_precedente -= 1
            settimana_precedente = datetime(anno_settimana_precedente, 12, 28).isocalendar()[1]  # ultima settimana ISO dell'anno precedente

        # Imposta l'indice della settimana di default se presente nei dati
        if anno_sel == anno_settimana_precedente and settimana_precedente in settimane_disponibili:
            default_index_settimana = settimane_disponibili.index(settimana_precedente)
        else:
            # Se la settimana precedente non è nei dati, usa l'ultima disponibile
            default_index_settimana = len(settimane_disponibili) - 1 if settimane_disponibili else 0

        # Selectbox per la settimana
        settimana_sel = st.selectbox(
            f"Settimana - {label}",
            settimane_disponibili,
            index=default_index_settimana,
            key=f"settimana_{label}"
        )

        # Calcola le date di inizio e fine settimana
        start_date = datetime.fromisocalendar(anno_sel, settimana_sel, 1)  # lunedì
        end_date = start_date + timedelta(days=6)  # domenica

    elif tipo_periodo == "Mese":
        anni_disponibili = sorted(df['Anno'].unique())

        # Trova l'indice dell'anno corrente
        anno_corrente = datetime.now().year
        if anno_corrente in anni_disponibili:
            default_index_anno = anni_disponibili.index(anno_corrente)
        else:
            default_index_anno = 0

        # Selectbox per l'anno
        anno_sel = st.selectbox(
            f"Anno - {label}",
            anni_disponibili,
            index=default_index_anno,
            key=f"annoM_{label}"
        )

        # Lista mesi disponibili per l'anno selezionato
        mesi_disponibili = sorted(df[df['Anno'] == anno_sel]['Mese'].unique())

        # Trova il mese precedente a quello corrente
        mese_corrente = datetime.now().month
        mese_precedente = mese_corrente - 1 if mese_corrente > 1 else 12

        if mese_precedente in mesi_disponibili:
            default_index_mese = mesi_disponibili.index(mese_precedente)
        else:
            # Se il mese precedente non è nei dati, prendi l'ultimo disponibile
            default_index_mese = len(mesi_disponibili) - 1

        # Selectbox per il mese
        mese_sel = st.selectbox(
            f"Mese - {label}",
            mesi_disponibili,
            format_func=lambda x: mesi_nome[x],
            index=default_index_mese,
            key=f"mese_{label}"
        )

        # Calcola inizio e fine mese
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
        textposition='inside',
        hoverinfo="skip",        # <-- disattiva i tooltip
        hovertemplate=None       # <-- ulteriore sicurezza
    )

    fig.update_layout(
        width=None,
        height=550,
        legend=dict(orientation="h", y=-0.2)
    )

    st.plotly_chart(fig, use_container_width=True, key=key)

def draw_barra(macchina, tipo_periodo, start_date, end_date, work_value, key=None):
    minimo, max_barra = get_min_max(macchina, tipo_periodo, start_date, end_date)

    import plotly.graph_objects as go
    fig = go.Figure()

    # Colore: verde se lavoro >= minimo, rosso se lavoro < minimo
    colore = "green" if work_value >= minimo else "red"

    # barra con lavoro effettivo
    fig.add_trace(go.Bar(
        x=[work_value],
        y=["Lavoro"],
        orientation='h',
        marker=dict(color=colore),
        name="Lavoro"
    ))

    # linea minima
    fig.add_vline(
        x=minimo,
        line=dict(color="blue", dash="dash"),  # linea minima evidenziata in blu
        annotation_text=f"Min {minimo:.2f}h",  # <-- due cifre decimali
        annotation_position="top"
    )

    tickvals = [max_barra * i/4 for i in range(1, 5)]  # 1/4, 2/4, 3/4, max
    tickvals = [round(v, 2) for v in tickvals]         # se vuoi due decimali

    fig.update_layout(
        xaxis=dict(
            range=[0, max_barra],
            title="Ore",
            tickmode="array",
            tickvals=tickvals
        ),
        yaxis=dict(showticklabels=False),
        height=150,
        margin=dict(l=20, r=20, t=20, b=20)
    )


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
            col_pie, col_bar = st.columns([2,1])
            with col_pie:
                draw_pie(sums, f"Macchina {macchina} - Periodo selezionato", key=f"{macchina}_{tipo_periodo}")
            with col_bar:
                draw_barra(macchina, tipo_periodo, start_date, end_date, sums["Lavoro"], key=f"bar_{macchina}_{tipo_periodo}")

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
                col_pie, col_bar = st.columns([2,1])
                with col_pie:
                    draw_pie(sums1, f"Macchina {macchina1} - Periodo selezionato", key=f"pie1_{macchina1}_{tipo_periodo}")
                with col_bar:
                    draw_barra(macchina1, tipo_periodo, start1, end1, sums1["Lavoro"],key=f"bar1_{macchina1}_{tipo_periodo}")

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
                col_pie, col_bar = st.columns([2,1])
                with col_pie:
                    draw_pie(sums2, f"Macchina {macchina2} - Periodo selezionato", key=f"pie2_{macchina2}_{tipo_periodo}")
                with col_bar:
                    draw_barra(macchina2, tipo_periodo, start2, end2, sums2["Lavoro"],key=f"bar2_{macchina2}_{tipo_periodo}")

# ------------------------------------------------------------
# Data/Ora ultimo aggiornamento
st.markdown(
    f"<div style='position: fixed; bottom: 10px; right: 10px; color: gray; font-size: 12px;'>"
    f"Aggiornato in data {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
    f"</div>", unsafe_allow_html=True
)