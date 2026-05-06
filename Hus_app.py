import streamlit as st
import pandas as pd
import numpy as np
import datetime

# Konfiguration
st.set_page_config(page_title="Voldgade 19", page_icon="🏡", layout="wide")

# Overskrift
st.title("🏡 Voldgade 19")
st.markdown("Husets digitale kontrolpanel")
st.divider()

# Layout med tre kolonner til toppen
col_strøm, col_skrald, col_vejr = st.columns([2, 1, 1])

with col_strøm:
    st.header("⚡ Strømpriser (Næste 36 timer)")
    
    # Henter den nuværende time (f.eks. kl. 14 bliver til "I dag 14:00")
    nu = datetime.datetime.now()
    nu_time_streng = f"I dag {nu.hour:02d}:00"
    
    timer_idag = [f"I dag {i:02d}:00" for i in range(24)]
    timer_imorgen = [f"I morgen {i:02d}:00" for i in range(12)]
    alle_timer = timer_idag + timer_imorgen
    
    priser = np.random.uniform(0.5, 3.5, 36) # Fiktive priser
    
    # NYT: Vi laver en liste med farver. Hvis timen er lig med nu_time_streng, bliver den grå (#808080), ellers gul (#f5c211)
    farver = ["#808080" if tid == nu_time_streng else "#f5c211" for tid in alle_timer]
    
    df_power = pd.DataFrame({
        "Tid": alle_timer, 
        "Pris (DKK/kWh)": priser,
        "Farve": farver # Tilføjer farven til dataen
    })
    
    # Bruger farve-kolonnen i diagrammet
    st.bar_chart(df_power, x="Tid", y="Pris (DKK/kWh)", color="Farve")

with col_skrald:
    st.header("🗑️ Skrald")
    st.info("**Rest/Mad:**\nTorsdag d. 14/5")
    st.success("**Genbrug:**\nTirsdag d. 19/5")

with col_vejr:
    st.header("🌦️ Vejr i Skjern")
    st.write("📅 **Ugeoversigt:**")
    st.write("☀️ **Ons:** 14°C")
    st.write("🌦️ **Tor:** 12°C")
    st.write("☁️ **Fre:** 11°C")
    st.write("🌧️ **Lør:** 9°C")
    st.write("🌤️ **Søn:** 13°C")

st.divider()

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
