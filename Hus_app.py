import streamlit as st
import pandas as pd
import numpy as np
import datetime
from zoneinfo import ZoneInfo # <-- NY: Til at styre dansk tidszone
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
    st.header("⚡ Strømpriser (DK1)")
    try:
        # 1. Hent data fra Energi Data Service
        url = 'https://api.energidataservice.dk/dataset/Elspotprices?limit=100&filter={"PriceArea":["DK1"]}&sort=HourDK%20DESC'
        res = requests.get(url).json()
        records = res.get('records', [])
        records.reverse() # Sorter så vi går fra fortid mod fremtid
        
        import datetime
        from zoneinfo import ZoneInfo
        import altair as alt
        
        # 2. Find "NU" i dansk tid (9. maj 2026)
        tz_dk = ZoneInfo("Europe/Copenhagen")
        nu = datetime.datetime.now(tz_dk).replace(minute=0, second=0, microsecond=0)
        
        data_list = []
        
        # 3. Gennemgå priserne og find de 6 timer bagud og 12 timer frem
        for r in records:
            # Konverter tidspunkt fra API til dansk tid
            t_obj = datetime.datetime.fromisoformat(r['HourDK'].replace('Z', '')).replace(tzinfo=tz_dk)
            
            # Beregn tidsforskel fra nuværende time
            diff = int((t_obj - nu).total_seconds() / 3600)
            
            # Filter: Præcis -6 timer til +12 timer
            if -6 <= diff <= 12:
                pris_med_moms = (r['SpotPriceDKK'] / 1000) * 1.25
                tid_label = t_obj.strftime("%H:00")
                
                # Sæt farve: Grå for nu (diff 0), gul for alle andre
                farve = "#808080" if diff == 0 else "#f5c211"
                
                data_list.append({
                    "Tid": tid_label, 
                    "Pris": pris_med_moms, 
                    "Farve": farve, 
                    "Sortering": diff
                })

        # 4. Lav grafen
        df_el = pd.DataFrame(data_list)

        if not df_el.empty:
            # Vi bruger Altair for at sikre os, at farverne og sorteringen er 100% korrekt
            chart = alt.Chart(df_el).mark_bar().encode(
                x=alt.X('Tid:N', sort=alt.SortField('Sortering'), title='Klokkeslæt'),
                y=alt.Y('Pris:Q', title='Pris (kr/kWh inkl. moms)'),
                color=alt.Color('Farve:N', scale=None) # Bruger de hex-koder vi har defineret
            ).properties(height=300)
            
            st.altair_chart(chart, use_container_width=True)
            
            # Vis den nuværende pris som tekst nedenunder
            nu_række = df_el[df_el['Sortering'] == 0]
            if not nu_række.empty:
                st.write(f"**Pris lige nu:** {nu_række['Pris'].values[0]:.2f} kr/kWh inkl. moms")
        else:
            st.warning(f"Ingen data fundet for {nu.strftime('%d/%m-%Y')}. Tjek om API'en er opdateret.")

    except Exception as e:
        st.error(f"Kunne ikke hente elpriser: {e}")
        
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
