import os
from dotenv import load_dotenv
import streamlit as st
from textblob import TextBlob
import requests
import pandas as pd
from serpapi import GoogleSearch
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import random



# --- Lataa API-avaimet ympäristömuuttujista tai .env-tiedostosta ---
# Asenna python-dotenv: pip install python-dotenv
load_dotenv(dotenv_path="config/.env")  # Polku .env-tiedostoon
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

# Varmista, että avaimet löytyivät; jos eivät, näytä virhe ja pysäytä suoritus
st.set_page_config(layout="wide", page_title="Kilpailija-analytiikka")
if not NEWS_API_KEY or not SERPAPI_KEY:
    st.error("Puuttuvat API-avaimet. Lisää NEWS_API_KEY ja SERPAPI_KEY ympäristömuuttujiksi tai config/.env-tiedostoon.")
    st.stop()

# Piilotetaan valikko ja footer + tyylit
st.markdown("""
    <style>
    #MainMenu, footer {visibility: hidden;}
    .block-container {padding: 2rem;}
    .small-text {font-size: 0.85rem;}
    </style>
""", unsafe_allow_html=True)

# Navigointi
st.sidebar.title("Valikko")
page = st.sidebar.radio("Valitse sivu:", ["Pääsivu – uutiset", "Vertailu"], label_visibility='visible')

# Sivupohja: uutissivu
if page == "Pääsivu – uutiset":
    st.title("Kilpailija-analytiikka – uutiset (viimeiset 6 kk)")
    hakusana = st.text_input("Kilpailijan nimi", "Valio")
    if hakusana:
        end_date = datetime.today().date()
        start_date = end_date - timedelta(days=180)
        # Hae uutiset
        news_url = (
            f"https://newsapi.org/v2/everything?"
            f"q={hakusana}&from={start_date}&to={end_date}&"
            "sortBy=publishedAt&language=fi&"
            f"apiKey={NEWS_API_KEY}"
        )
        news_resp = requests.get(news_url)

        # Tulosta uutisotsikot
        st.subheader("Uutisotsikot")
        if news_resp.status_code == 200 and news_resp.json().get("status") == "ok":
            articles = news_resp.json().get("articles", [])[:5]
            if articles:
                for art in articles:
                    title = art.get('title','')
                    desc = art.get('description','') or ''
                    url = art.get('url','')
                    pol = TextBlob(desc).sentiment.polarity
                    senti = pol>0.1 and "Positiivinen 😊" or (pol<-0.1 and "Negatiivinen 😠" or "Neutraali 😐")
                    st.markdown(f"""
                        <div class='small-text' style='margin-bottom:12px;'>
                            <strong>{title}</strong><br>
                            <em>{desc}</em><br>
                            Tunnelma: {senti}<br>
                            <a href='{url}' target='_blank'>Lue lisää</a>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Ei uutisia haun perusteella.")
        else:
            st.error(f"Uutisten hakeminen epäonnistui: HTTP {news_resp.status_code}")

        # Hakutrendi (simuloitu)
        st.subheader("Hakutrendi (simuloitu)")
        dates = [datetime.now() - timedelta(weeks=i) for i in range(26)][::-1]
        vals = [random.randint(20,100) for _ in dates]
        fig, ax = plt.subplots(figsize=(8,3))
        ax.set_facecolor("white"); fig.patch.set_facecolor("white")
        ax.plot(dates, vals, marker='o')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %y'))
        fig.autofmt_xdate()
        st.pyplot(fig)

# Sivupohja: vertailu
elif page == "Vertailu":
    st.title("Usean kilpailijan vertailu")
    # Ajanjakso-painikkeet
    col_a, col_b, col_c = st.columns(3)
    if 'window_days' not in st.session_state:
        st.session_state.window_days = 180
    if col_a.button("3 kk"): st.session_state.window_days = 90
    if col_b.button("6 kk"): st.session_state.window_days = 180
    if col_c.button("12 kk"): st.session_state.window_days = 365

    end_date = datetime.today().date()
    start_date = end_date - timedelta(days=st.session_state.window_days)
    st.write(f"Näytetään data ajalta: {start_date} – {end_date}")

    brands = ["Valio","Fazer","Arla","Nalle","Sunnuntai"]
    selected = st.multiselect("Valitse brändit", brands, default=["Valio","Fazer"])
    if selected:
        col1, col2, col3 = st.columns(3)
        # Uutismäärä
        with col1:
            st.subheader("Uutismäärä per brändi")
            counts = {b: random.randint(5,20) for b in selected}
            df_count = pd.DataFrame.from_dict(counts, orient='index', columns=['Uutismäärä'])
            fig3, ax3 = plt.subplots(figsize=(4,2.5))
            ax3.set_facecolor("black"); fig3.patch.set_facecolor("black")
            ax3.tick_params(colors='white'); ax3.yaxis.label.set_color('white')
            for spine in ax3.spines.values(): spine.set_edgecolor('white')
            df_count.plot.bar(ax=ax3, color='tab:blue')
            st.pyplot(fig3)
        # Trendikäyrät
        with col2:
            st.subheader("Trendikäyrät")
            dates = [datetime.now() - timedelta(weeks=i) for i in range(int(st.session_state.window_days/7)+1)][::-1]
            fig4, ax4 = plt.subplots(figsize=(4,2.5))
            ax4.set_facecolor("black"); fig4.patch.set_facecolor("black")
            for b in selected:
                vals = [random.randint(10,100) for _ in dates]
                ax4.plot(dates, vals, marker='o', label=b)
            ax4.xaxis.set_major_formatter(mdates.DateFormatter('%b %y'))
            fig4.autofmt_xdate()
            ax4.tick_params(colors='white'); ax4.yaxis.label.set_color('white')
            for spine in ax4.spines.values(): spine.set_edgecolor('white')
            ax4.legend(facecolor='black', edgecolor='white', labelcolor='white')
            st.pyplot(fig4)
        # Tunnelma-jakaumat
        with col3:
            st.subheader("Tunnelma-jakaumat")
            df_sent2 = pd.DataFrame({b: [random.randint(1,5) for _ in range(3)] for b in selected}, index=["Pos","Neu","Neg"])
            fig5, ax5 = plt.subplots(figsize=(4,2.5))
            ax5.set_facecolor("black"); fig5.patch.set_facecolor("black")
            df_sent2.plot.bar(ax=ax5, color=['tab:green','tab:gray','tab:red'])
            ax5.tick_params(colors='white'); ax5.yaxis.label.set_color('white')
            for spine in ax5.spines.values(): spine.set_edgecolor('white')
            st.pyplot(fig5)
