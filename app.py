import streamlit as st
import ccxt
import requests
import pandas as pd
from datetime import datetime
import time
from groq import Groq

st.set_page_config(page_title="CryptoSpark AI", layout="wide", initial_sidebar_state="expanded")
st.title("🚀 CryptoSpark AI - Tu Sala de Control Trader")
st.markdown("**BTC • ETH • SOL • BNB Futures** | Alertas IA en tiempo real")

# ==================== CONFIG ====================
# Pon tus claves en Settings → Secrets (ver paso 5)
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
TELEGRAM_TOKEN = st.secrets.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = st.secrets.get("TELEGRAM_CHAT_ID", "")

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Binance Futures
exchange = ccxt.binanceusdm({'enableRateLimit': True})

# ==================== FUNCIONES ====================
def get_futures_data(symbol):
    try:
        ticker = exchange.fetch_ticker(f"{symbol}/USDT:USDT")
        funding = exchange.fetch_funding_rate(f"{symbol}/USDT:USDT")
        oi = exchange.fetch_open_interest(f"{symbol}/USDT:USDT")
        return {
            "price": ticker['last'],
            "change": ticker['percentage'],
            "funding": funding['fundingRate'] * 100,
            "oi": oi['openInterestAmount'],
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
    except:
        return {"price": 0, "change": 0, "funding": 0, "oi": 0, "timestamp": "Error"}

def defillama_tvl(chain="solana"):
    try:
        r = requests.get("https://api.llama.fi/v2/chains")
        data = r.json()
        for c in data:
            if c["name"].lower() == chain.lower():
                return c["tvl"]
        return 0
    except:
        return 0

def get_crypto_news():
    try:
        r = requests.get("https://cryptopanic.com/api/free/v1/posts/?auth_token=free&currencies=BTC,ETH,SOL,BNB&filter=important")
        return r.json()["results"][:5]
    except:
        return []

def ia_explica(texto):
    if not client:
        return "IA no configurada aún"
    try:
        chat = client.chat.completions.create(
            messages=[{"role": "user", "content": f"Explica en español sencillo y trader-friendly este evento cripto: {texto}"}],
            model="llama-3.3-70b-versatile",
            max_tokens=400
        )
        return chat.choices[0].message.content
    except:
        return "Error IA (revisa clave Groq)"

# ==================== SIDEBAR ====================
with st.sidebar:
    st.header("⚙️ Configuración Rápida")
    st.caption("Ve a Settings → Secrets para agregar claves")
    auto_refresh = st.checkbox("Auto-actualizar cada 20s", value=True)
    if st.button("🔄 Actualizar ahora"):
        st.rerun()

# ==================== TABS ====================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📊 Pulse Vivo", "🔔 Alertas IA", "⛓️ On-Chain", "📰 News + Sentimiento", "🌍 Macro Global", "🤖 AI Analyst"])

with tab1:
    st.subheader("Pulse Vivo - BTC ETH SOL BNB")
    cols = st.columns(4)
    symbols = ["BTC", "ETH", "SOL", "BNB"]
    for i, sym in enumerate(symbols):
        data = get_futures_data(sym)
        with cols[i]:
            st.metric(
                f"{sym}/USDT",
                f"${data['price']:,.0f}" if data['price'] else "Error",
                f"{data['change']:+.2f}%"
            )
            st.caption(f"Funding: {data['funding']:+.3f}% | OI: {data['oi']:,.0f}")

with tab2:
    st.subheader("🔔 Centro de Alertas Inteligentes")
    st.info("Aquí se encenderán las alertas automáticas (MVP muestra ejemplos + botón IA)")
    alertas_demo = [
        ("🟢 OPORTUNIDAD", "ETH: Whale inflow +120M USDT + funding negativo → setup largo probable"),
        ("🔴 RIESGO", "SOL: Funding +0.085% → posible long squeeze en 2-4h"),
        ("🟡 INFO", "Próximo dato CPI en 45 min - espera volatilidad")
    ]
    for color, title, desc in alertas_demo:
        with st.expander(f"{color} {title}"):
            st.write(desc)
            if st.button("🤖 Explicar con IA", key=desc):
                st.write(ia_explica(desc))

with tab3:
    st.subheader("⛓️ On-Chain & Whale Radar")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("TVL Solana", f"${defillama_tvl('solana')/1e9:.1f}B")
    with col2:
        st.metric("TVL Ethereum", f"${defillama_tvl('ethereum')/1e9:.1f}B")
    st.caption("Datos DeFiLlama actualizados en vivo")

with tab4:
    st.subheader("📰 Noticias Relevantes")
    news = get_crypto_news()
    for item in news:
        with st.expander(item["title"]):
            st.write(item["domain"])
            st.caption(item["published_at"])

with tab5:
    st.subheader("🌍 Macro Global")
    st.info("Próximos eventos (ejemplo - actualiza con API real después)")
    st.write("• CPI USA → en 45 min")
    st.write("• DXY actual: 103.45")
    st.write("• Flujos ETF BTC hoy: +$87M")

with tab6:
    st.subheader("🤖 AI Analyst")
    pregunta = st.text_input("Pregúntale a la IA cualquier cosa (ej: ¿qué significa funding +0.07% en SOL?)")
    if st.button("Preguntar") and pregunta:
        with st.spinner("Pensando..."):
            respuesta = ia_explica(pregunta)
            st.success(respuesta)

# ==================== AUTO REFRESH ====================
if auto_refresh:
    time.sleep(20)
    st.rerun()
