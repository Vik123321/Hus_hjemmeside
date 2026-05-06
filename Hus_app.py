import streamlit as st
import pandas as pd
import numpy as np
import datetime
import requests 

# Konfiguration
st.set_page_config(page_title="Voldgade 19", page_icon="🏡", layout="wide")

# Overskrift
st.title("🏡 Voldgade 19, Skjern")
st.markdown("Husets digitale kontrolpanel med live-data!")
st.divider()

# Layout med tre kolonner
col_strøm, col_skrald, col_vejr = st.columns([2, 1, 1])

with col_strøm:
    st.header("⚡ Strømpriser (DK1 - Jylland)")
    
    try:
        # Henter de nyeste 48 timers priser fra Energi Data Service
        url = 'https://api.energidataservice.dk/dataset/Elspotprices?limit=48&filter={"PriceArea":["DK1"]}&sort=HourDK%20DESC'
        response = requests.get(url)
        data = response.json()
        
        # Udtrækker tider og priser
        records = data.get('records', [])
        
        # Vi vender listen om, så den ældste er først (kronologisk rækkefølge)
        records.reverse()
        
        tider = []
        priser = []
        nu = datetime.datetime.now()
        nu_time_streng = nu.strftime("%Y-%m-%dT%H:00:00") # Format der matcher API'et
        
        for record in records:
            # Omregner fra MWh til kWh og lægger 25% moms på
            pris_kwh = (record['SpotPriceDKK'] / 1000) * 1.25
            priser.append(pris_kwh)
            
            # Formatér tiden pænere til grafen
            tid_obj = datetime.datetime.fromisoformat(record['HourDK'])
            tider.append(f"{tid_obj.day}/{tid_obj.month} kl. {tid_obj.hour:02d}")
        
        # Farver den nuværende time grå, resten gul
        nu_formateret = f"{nu.day}/{nu.month} kl. {nu.hour:02d}"
        farver = ["#808080" if tid == nu_formateret else "#f5c211" for tid in tider]
        
        df_power = pd.DataFrame({
            "Tid": tider, 
            "Pris (DKK/kWh inkl. moms)": priser,
            "Farve": farver
        })
        
        st.bar_chart(df_power, x="Tid", y="Pris (DKK/kWh inkl. moms)", color="Farve")
        
    except Exception as e:
        st.error("Kunne ikke hente live-strømpriser lige nu.")

with col_skrald:
    st.header("🗑️ Skrald")
    st.info("**Rest/Mad:**\nTorsdag d. 14/5")
    st.success("**Genbrug:**\nTirsdag d. 19/5")
    st.caption("Tip: Tjek Ringkøbing-Skjern Kommunes hjemmeside for at tilmelde SMS-service.")

with col_vejr:
    st.header("🌦️ Vejret i Skjern")
    try:
        # Koordinater for Skjern: Latitude 55.948, Longitude 8.496
        vejr_url = "https://api.open-meteo.com/v1/forecast?latitude=55.948&longitude=8.496&daily=temperature_2m_max,temperature_2m_min&timezone=Europe%2FBerlin"
        vejr_response = requests.get(vejr_url)
        vejr_data = vejr_response.json()
        
        dage = vejr_data['daily']['time']
        max_temp = vejr_data['daily']['temperature_2m_max']
        min_temp = vejr_data['daily']['temperature_2m_min']
        
        # Viser de næste 5 dage
        ugedage_navne = ["Man", "Tir", "Ons", "Tor", "Fre", "Lør", "Søn"]
        for i in range(5):
            dato_obj = datetime.datetime.fromisoformat(dage[i])
            ugedag = ugedage_navne[dato_obj.weekday()]
            st.write(f"**{ugedag}:** {min_temp[i]}°C til {max_temp[i]}°C")
            
    except Exception:
        st.error("Kunne ikke hente vejrudsigten.")

# ÅRSHJUL MED TJEKLISTE
st.header("🗓️ Husets Årshjul")
st.write("Kryds opgaverne af, efterhånden som du får dem løst.")

# Initialiserer opgaver som en ordbog (dictionary) fordelt på faste sæsoner
if 'hus_opgaver' not in st.session_state:
    st.session_state.hus_opgaver = {
        "Forår": [{"id": 1, "tekst": "Tjek vinduer og døre for råd", "done": False}],
        "Sommer": [{"id": 2, "tekst": "Mal udendørs træværk", "done": False}],
        "Efterår": [{"id": 3, "tekst": "Rens tagrender", "done": False}],
        "Vinter": [{"id": 4, "tekst": "Tjek loftet for fugt", "done": False}]
    }
    st.session_state.next_id = 5 # Holder styr på unikke ID'er til nye opgaver

# Viser de 4 sæsoner i 4 faste kolonner
saesoner = ["Forår", "Sommer", "Efterår", "Vinter"]
saeson_kolonner = st.columns(4)

for i, saeson in enumerate(saesoner):
    with saeson_kolonner[i]:
        st.subheader(saeson)
        # Gennemgår opgaver for sæsonen og laver en checkbox for hver
        for opgave in st.session_state.hus_opgaver[saeson]:
            # Opdaterer status afhængigt af om den er klikket af
            opgave['done'] = st.checkbox(opgave['tekst'], value=opgave['done'], key=f"task_{opgave['id']}")
            
st.divider()

# Tilføj og Slet sektion
st.subheader("⚙️ Rediger opgaver i årshjulet")
edit_col1, edit_col2 = st.columns(2)

with edit_col1:
    st.markdown("### ➕ Tilføj ny opgave")
    saeson_valg = st.selectbox("Hvilken årstid?", saesoner, key="add_saeson")
    ny_opgave_tekst = st.text_input("Beskrivelse af opgaven")
    
    if st.button("Tilføj til tjekliste"):
        if ny_opgave_tekst:
            ny_opgave = {"id": st.session_state.next_id, "tekst": ny_opgave_tekst, "done": False}
            st.session_state.hus_opgaver[saeson_valg].append(ny_opgave)
            st.session_state.next_id += 1 # Gør klar til næste unikke ID
            st.rerun()

with edit_col2:
    st.markdown("### 🗑️ Slet en opgave")
    del_saeson = st.selectbox("Vælg årstid", saesoner, key="del_saeson")
    
    # Henter opgaverne for den valgte årstid
    valgte_opgaver = st.session_state.hus_opgaver[del_saeson]
    
    if valgte_opgaver:
        # Viser en dropdown med opgavernes tekster i stedet for numre
        opgave_at_slette = st.selectbox(
            "Vælg opgave der skal slettes", 
            valgte_opgaver, 
            format_func=lambda x: x['tekst']
        )
        
        if st.button("Slet valgte opgave"):
            st.session_state.hus_opgaver[del_saeson].remove(opgave_at_slette)
            st.rerun()
    else:
        st.write("Der er ingen opgaver at slette i denne sæson.")
