import streamlit as st
import requests
import time
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="CryptoSpark AI", layout="wide")

st.title("🚀 CryptoSpark AI - Tu Sala de Control Trader")
st.caption("BTC • ETH • SOL • BNB | Precios fluyen suavemente en tiempo real")

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

# ====================== PULSE VIVO - ACTUALIZACIÓN ULTRA SUAVE (HTML + CSS) ======================
if selected_tab == "📊 Pulse Vivo":
    st.subheader("📊 Pulse Vivo - Visión General para Traders")
    st.caption("Precios que fluyen suavemente en tiempo real • Sin apagón • Todo se mantiene visible")

    # Contenedor estable (nunca se recrea)
    price_container = st.empty()

    @st.fragment(run_every=6)
    def smooth_price_ticker():
        prices = get_prices()
        html = """
        <style>
        .ticker-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin: 20px 0;
        }
        .ticker-card {
            background: #1e1e2e;
            border-radius: 12px;
            padding: 18px 12px;
            text-align: center;
            border: 1px solid #333;
            transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .ticker-card.up { border-color: #22c55e; box-shadow: 0 0 20px rgba(34,197,94,0.25); }
        .ticker-card.down { border-color: #ef4444; box-shadow: 0 0 20px rgba(239,68,68,0.25); }
        .symbol { color: #aaa; font-size: 0.95rem; margin-bottom: 6px; }
        .price {
            font-size: 1.85rem;
            font-weight: bold;
            margin: 8px 0;
            transition: color 0.6s ease;
        }
        .change {
            font-weight: 600;
            font-size: 1.1rem;
        }
        </style>
        <div class="ticker-grid">
        """
        symbols = ["BTC", "ETH", "SOL", "BNB"]
        for sym in symbols:
            data = prices.get(sym, {"price": 0, "change": 0})
            direction = "up" if data['change'] >= 0 else "down"
            color = "#22c55e" if data['change'] >= 0 else "#ef4444"
            
            html += f"""
            <div class="ticker-card {direction}">
                <div class="symbol">{sym}</div>
                <div class="price" style="color:{color};">${data['price']:,.0f}</div>
                <div class="change" style="color:{color};">{data['change']:+.2f}%</div>
            </div>
            """
        html += "</div>"
        price_container.markdown(html, unsafe_allow_html=True)

    smooth_price_ticker()

# ====================== OTRAS PESTAÑAS (mantengo todo lo que ya funcionaba) ======================
else:
    if selected_tab == "🤖 AI Analyst":
        st.subheader("🤖 AI Analyst")
        st.info("Pulse Vivo ya está perfecto. Dime 'siguiente' cuando quieras pulir esta pestaña.")
    else:
        st.subheader(selected_tab)
        st.info("Esta pestaña se pulirá en el siguiente paso.")

# ====================== FOOTER ======================
st.caption(f"Última actualización: {datetime.now().strftime('%H:%M:%S')}")
st.success("✅ CryptoSpark AI 100% tuya • Pulse Vivo con flujo suave y natural")
