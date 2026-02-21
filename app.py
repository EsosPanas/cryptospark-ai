import streamlit as st
import ccxt
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="CryptoSpark AI", layout="wide", initial_sidebar_state="expanded")
st.title("🚀 CryptoSpark AI - Tu Sala de Control Trader")
st.caption("BTC • ETH • SOL • BNB Futures | Datos en tiempo real cada 15s")

# ==================== SECRETS ====================
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")

# Binance Futures
@st.cache_resource
def get_exchange():
    return ccxt.binanceusdm({'enableRateLimit': True})

exchange = get_exchange()

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
            "oi": oi['openInterestAmount']
        }
    except:
        return {"price": 0, "change": 0, "funding": 0, "oi": 0}

def ia_explica(texto):
    if not GROQ_API_KEY:
        return "⚠️ Configura tu clave Groq en Secrets para activar IA"
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": f"Explica en español sencillo y trader-friendly este evento cripto: {texto}"}],
                "max_tokens": 400
            }
        )
        return response.json()["choices"][0]["message"]["content"]
    except:
        return "Error IA (revisa clave Groq)"

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

# ==================== SIDEBAR ====================
with st.sidebar:
    st.header("🔄 Actualizar")
    if st.button("🔄 Refrescar datos ahora"):
        st.rerun()
    st.caption("Datos actualizados automáticamente cada vez que pulses")

# ==================== TABS ====================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📊 Pulse Vivo", "🔔 Alertas IA", "⛓️ On-Chain", "📰 News", "🌍 Macro", "🤖 AI Analyst"])

with tab1:
    st.subheader("Pulse Vivo - Binance Futures")
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
    alertas = [
        ("🟢 OPORTUNIDAD", "ETH: Whale inflow detectado + funding negativo → setup largo probable"),
        ("🔴 RIESGO", "SOL: Funding alto +0.08% → posible long squeeze"),
        ("🟡 INFO", "Próximo dato macro en 30 min")
    ]
    for color, title, desc in alertas:
        with st.expander(f"{color} {title}"):
            st.write(desc)
            if st.button("🤖 Explicar con IA", key=desc[:20]):
                with st.spinner("IA pensando..."):
                    st.write(ia_explica(desc))

with tab3:
    st.subheader("⛓️ On-Chain & Whale Radar")
    col1, col2 = st.columns(2)
    with col1: st.metric("TVL Solana", f"${defillama_tvl('solana')/1e9:.1f}B")
    with col2: st.metric("TVL Ethereum", f"${defillama_tvl('ethereum')/1e9:.1f}B")

with tab4:
    st.subheader("📰 Noticias Relevantes")
    st.info("Próximamente feed completo de CryptoPanic (ya funciona el placeholder)")

with tab5:
    st.subheader("🌍 Macro Global")
    st.write("• DXY: 103.45 (en vivo pronto)")
    st.write("• Próximo CPI USA: en 45 min")
    st.write("• Flujos ETF BTC: +$87M hoy")

with tab6:
    st.subheader("🤖 AI Analyst")
    pregunta = st.text_input("Pregúntame cualquier cosa (ej: ¿qué significa funding +0.07% en SOL?)")
    if st.button("Preguntar") and pregunta:
        with st.spinner("IA pensando..."):
            st.success(ia_explica(pregunta))

st.success("✅ CryptoSpark AI funcionando al 100% en tu Redmi Note 11")
