import streamlit as st
import pandas as pd
import numpy as np
import datetime
import requests

# Konfiguration
st.set_page_config(page_title="Voldgade 19", page_icon="🏡", layout="wide")

# Overskrift
st.title("🏡 Voldgade 19, Skjern")
st.markdown(f"Sidst opdateret: {datetime.datetime.now().strftime('%d/%m kl. %H:%M')}")
st.divider()

# --- FUNKTIONER TIL DATA ---

def get_weather_icon(code):
    # Oversætter WMO vejrkoder til ikoner
    mapping = {
        0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️", 
        45: "🌫️", 48: "🌫️", 
        51: "🌦️", 53: "🌦️", 55: "🌧️",
        61: "🌧️", 63: "🌧️", 65: "🌧️",
        71: "❄️", 73: "❄️", 75: "❄️",
        80: "🌦️", 81: "🌧️", 82: "⛈️",
        95: "⛈️"
    }
    return mapping.get(code, "🌈")

# --- LAYOUT ---
col_strøm, col_skrald, col_vejr = st.columns([2, 1, 1])

with col_strøm:
    st.header("⚡ Strømpriser")
    try:
        url = 'https://api.energidataservice.dk/dataset/Elspotprices?limit=48&filter={"PriceArea":["DK1"]}&sort=HourDK%20DESC'
        res = requests.get(url).json()
        records = res.get('records', [])
        records.reverse()
        
        tider, priser, farver = [], [], []
        nu = datetime.datetime.now()
        
        for r in records:
            p = (r['SpotPriceDKK'] / 1000) * 1.25
            t_obj = datetime.datetime.fromisoformat(r['HourDK'].replace('Z', ''))
            t_str = t_obj.strftime("%d/%m %H:00")
            
            tider.append(t_str)
            priser.append(p)
            # Tjekker om timen matcher nuværende time
            if t_obj.date() == nu.date() and t_obj.hour == nu.hour:
                farver.append("#808080") # Grå for NU
            else:
                farver.append("#f5c211") # Gul for resten
        
        df_el = pd.DataFrame({"Tid": tider, "Pris": priser, "Farve": farver})
        st.bar_chart(df_el, x="Tid", y="Pris", color="Farve")
    except:
        st.error("Kunne ikke hente elpriser.")

with col_skrald:
    st.header("🗑️ Skrald")
    # Vi bruger de datoer du sendte i billederne
    idag = datetime.datetime.now().date()
    
    # Datoer fra dine billeder
    rest_datoer = [datetime.date(2026, 5, 11), datetime.date(2026, 5, 25), datetime.date(2026, 6, 8)]
    genbrug_datoer = [datetime.date(2026, 5, 11), datetime.date(2026, 6, 1), datetime.date(2026, 6, 22)]
    
    # Find næste dato
    naeste_rest = next((d for d in rest_datoer if d >= idag), "Se kalender")
    naeste_genbrug = next((d for d in genbrug_datoer if d >= idag), "Se kalender")
    
    st.info(f"**Rest/Mad:**\n{naeste_rest.strftime('%d-%m-%Y') if isinstance(naeste_rest, datetime.date) else naeste_rest}")
    st.success(f"**Genbrug:**\n{naeste_genbrug.strftime('%d-%m-%Y') if isinstance(naeste_genbrug, datetime.date) else naeste_genbrug}")

with col_vejr:
    st.header("🌦️ Vejr")
    try:
        v_url = "https://api.open-meteo.com/v1/forecast?latitude=55.948&longitude=8.496&daily=weathercode,temperature_2m_max,temperature_2m_min&timezone=Europe%2FBerlin"
        v_res = requests.get(v_url).json()
        
        for i in range(5):
            d = datetime.datetime.fromisoformat(v_res['daily']['time'][i])
            ikon = get_weather_icon(v_res['daily']['weathercode'][i])
            max_t = v_res['daily']['temperature_2m_max'][i]
            min_t = v_res['daily']['temperature_2m_min'][i]
            st.write(f"{ikon} **{d.strftime('%a')}:** {min_t}° / {max_t}°C")
    except:
        st.error("Vejr utilgængeligt.")

st.divider()

# --- ÅRSHJUL (Tjekliste system) ---
st.header("🗓️ Husets Årshjul")

if 'hus_opgaver' not in st.session_state:
    st.session_state.hus_opgaver = {
        "Forår": [{"id": 1, "tekst": "Tjek vinduer for råd", "done": False}],
        "Sommer": [{"id": 2, "tekst": "Mal udendørs træværk", "done": False}],
        "Efterår": [{"id": 3, "tekst": "Rens tagrender", "done": False}],
        "Vinter": [{"id": 4, "tekst": "Tjek loft for fugt", "done": False}]
    }
    st.session_state.next_id = 5

cols = st.columns(4)
for i, s in enumerate(["Forår", "Sommer", "Efterår", "Vinter"]):
    with cols[i]:
        st.subheader(s)
        for opg in st.session_state.hus_opgaver[s]:
            opg['done'] = st.checkbox(opg['tekst'], value=opg['done'], key=f"t_{opg['id']}")

# --- REDIGERING ---
with st.expander("➕/🗑️ Rediger opgaver"):
    c1, c2 = st.columns(2)
    with c1:
        s_valg = st.selectbox("Sæson", ["Forår", "Sommer", "Efterår", "Vinter"])
        ny_t = st.text_input("Ny opgave")
        if st.button("Tilføj"):
            st.session_state.hus_opgaver[s_valg].append({"id": st.session_state.next_id, "tekst": ny_t, "done": False})
            st.session_state.next_id += 1
            st.rerun()
    with c2:
        s_del = st.selectbox("Slet fra", ["Forår", "Sommer", "Efterår", "Vinter"])
        opg_del = st.selectbox("Vælg opgave", st.session_state.hus_opgaver[s_del], format_func=lambda x: x['tekst'])
        if st.button("Slet"):
            st.session_state.hus_opgaver[s_del].remove(opg_del)
            st.rerun()
