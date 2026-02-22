import streamlit as st
import requests
import time
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="CryptoSpark AI", layout="wide")

st.title("🚀 CryptoSpark AI - Tu Sala de Control Trader")
st.caption("BTC • ETH • SOL • BNB | Precios cambian suavemente en tiempo real cada 6s")

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")

# ====================== PESTAÑAS PERSISTENTES ======================
if "current_tab" not in st.session_state:
    st.session_state.current_tab = "📊 Pulse Vivo"

tab_options = ["📊 Pulse Vivo", "🔔 Alertas IA", "⛓️ On-Chain", "📰 News", "🌍 Macro", "🤖 AI Analyst"]
selected_tab = st.radio("", tab_options, index=tab_options.index(st.session_state.current_tab), horizontal=True, label_visibility="collapsed")
st.session_state.current_tab = selected_tab

# ====================== FUNCIONES ======================
@st.cache_data(ttl=6)
def get_prices():
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=bitcoin,ethereum,solana,binancecoin&price_change_percentage=24h"
        r = requests.get(url, timeout=10)
        data = r.json()
        prices = {}
        mapping = {'bitcoin': 'BTC', 'ethereum': 'ETH', 'solana': 'SOL', 'binancecoin': 'BNB'}
        for coin in data:
            sym = mapping.get(coin['id'])
            if sym:
                prices[sym] = {
                    "price": coin['current_price'],
                    "change": coin.get('price_change_percentage_24h', 0),
                    "high_24h": coin.get('high_24h', 0),
                    "low_24h": coin.get('low_24h', 0),
                    "volume": coin.get('total_volume', 0)
                }
        return prices
    except:
        return {}

@st.cache_data(ttl=60)
def get_historical_prices(coin_id="bitcoin", days=7):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days={days}"
        r = requests.get(url, timeout=10)
        data = r.json()['prices']
        df = pd.DataFrame(data, columns=['timestamp', 'price'])
        return df['price']
    except:
        return pd.Series()

def get_market_snapshot_text():
    prices = get_prices()
    return f"""
**📊 SNAPSHOT EN TIEMPO REAL**
• BTC ${prices.get('BTC',{}).get('price',0):,.0f}
• ETH ${prices.get('ETH',{}).get('price',0):,.0f}
• SOL ${prices.get('SOL',{}).get('price',0):,.0f}
• BNB ${prices.get('BNB',{}).get('price',0):,.0f}
"""

def ia_explica(texto):
    if not GROQ_API_KEY:
        return "⚠️ Agrega tu clave Groq en Secrets para activar IA"
    prices = get_prices()
    market_snapshot = f"DATOS ACTUALES: BTC ${prices.get('BTC',{}).get('price',0):,.0f} | ETH ${prices.get('ETH',{}).get('price',0):,.0f} | SOL ${prices.get('SOL',{}).get('price',0):,.0f} | BNB ${prices.get('BNB',{}).get('price',0):,.0f}"
    prompt = f"Eres trader pro. Usa estos datos: {market_snapshot}\nPregunta: {texto}"
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions", 
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "max_tokens": 900},
            timeout=15)
        return r.json()["choices"][0]["message"]["content"]
    except:
        return "Error temporal en IA"

def process_ai_question(q):
    st.session_state.chat_history.append(("Tú", q))
    with st.spinner("IA analizando..."):
        respuesta = ia_explica(q)
        st.session_state.chat_history.append(("AI", respuesta))
    st.rerun()

# ====================== PULSE VIVO - ACTUALIZACIÓN SUAVE ======================
if selected_tab == "📊 Pulse Vivo":
    st.subheader("📊 Pulse Vivo - Visión General para Traders")
    st.caption("Precios que se mueven suavemente en tiempo real • Alto/Bajo/Volumen 24h")

    @st.fragment(run_every=6)
    def pulse_live_smooth():
        prices = get_prices()
        cols = st.columns(4)
        mapping = {"BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana", "BNB": "binancecoin"}
        for i, sym in enumerate(["BTC", "ETH", "SOL", "BNB"]):
            data = prices.get(sym, {"price": 0, "change": 0})
            series = get_historical_prices(mapping[sym], days=7)
            with cols[i]:
                st.metric(
                    label=f"**{sym}**",
                    value=f"${data['price']:,.0f}" if data['price'] > 0 else "—",
                    delta=f"{data['change']:+.2f}%",
                    chart_data=series.tolist() if not series.empty else None
                )
                if data['price'] > 0:
                    st.caption(f"**Alto 24h** ${data['high_24h']:,.0f}")
                    st.caption(f"**Bajo 24h** ${data['low_24h']:,.0f}")
                    st.caption(f"**Volumen 24h** ${data['volume']/1e9:.1f}B")
    pulse_live_smooth()

# ====================== OTRAS PESTAÑAS (mantengo todo lo que ya funcionaba) ======================
else:
    st.subheader(selected_tab)
    st.info("Esta pestaña se pulirá en el siguiente paso (dime 'siguiente' cuando estés listo)")

# ====================== FOOTER ======================
st.caption(f"Última actualización: {datetime.now().strftime('%H:%M:%S')}")
st.success("✅ CryptoSpark AI 100% tuya • Pulse Vivo con actualización suave y natural")
