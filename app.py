import streamlit as st
import requests
import time
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="CryptoSpark AI", layout="wide")

st.title("🚀 CryptoSpark AI - Tu Sala de Control Trader")
st.caption("BTC • ETH • SOL • BNB | Precios en tiempo real cada 15s (solo números cambian)")

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")

# ====================== PESTAÑAS PERSISTENTES ======================
if "current_tab" not in st.session_state:
    st.session_state.current_tab = "📊 Pulse Vivo"

tab_options = ["📊 Pulse Vivo", "🔔 Alertas IA", "⛓️ On-Chain", "📰 News", "🌍 Macro", "🤖 AI Analyst"]
selected_tab = st.radio("", tab_options, index=tab_options.index(st.session_state.current_tab), horizontal=True, label_visibility="collapsed")
st.session_state.current_tab = selected_tab

# ====================== PRECIOS LIVE EN TODAS LAS PESTAÑAS ======================
@st.fragment(run_every=15)
def live_prices():
    prices = get_prices()
    cols = st.columns(4)
    symbols = ["BTC", "ETH", "SOL", "BNB"]
    for i, sym in enumerate(symbols):
        data = prices.get(sym, {"price": 0, "change": 0})
        with cols[i]:
            st.metric(
                label=f"**{sym}**",
                value=f"${data['price']:,.0f}" if data['price'] > 0 else "Cargando...",
                delta=f"{data['change']:+.2f}%"
            )

# ====================== FUNCIONES ======================
@st.cache_data(ttl=15)
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

@st.cache_data(ttl=60)  # bajamos el cache para que los gráficos se actualicen mejor
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
    onchain = get_onchain_metrics()
    return f"""
**📊 SNAPSHOT EN TIEMPO REAL**
• BTC ${prices.get('BTC',{}).get('price',0):,.0f} ({prices.get('BTC',{}).get('change',0):+.2f}%)
• ETH ${prices.get('ETH',{}).get('price',0):,.0f} ({prices.get('ETH',{}).get('change',0):+.2f}%)
• SOL ${prices.get('SOL',{}).get('price',0):,.0f} ({prices.get('SOL',{}).get('change',0):+.2f}%)
• BNB ${prices.get('BNB',{}).get('price',0):,.0f} ({prices.get('BNB',{}).get('change',0):+.2f}%)
"""

# (ia_explica, defillama_tvl, get_onchain_metrics, process_ai_question se mantienen iguales - copia del código anterior si quieres)

def ia_explica(texto):
    # ... (usa el mismo que tenías antes, no lo cambio para no romper nada)

def defillama_tvl(chain="solana"):
    # ... (mismo)

def get_onchain_metrics():
    # ... (mismo)

def process_ai_question(q):
    # ... (mismo)

# ====================== DATOS ======================
prices = get_prices()
onchain = get_onchain_metrics()
symbols = ["BTC", "ETH", "SOL", "BNB"]
mapping = {"BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana", "BNB": "binancecoin"}

# ====================== PRECIOS LIVE (siempre arriba) ======================
live_prices()

# ====================== CONTENIDO POR PESTAÑA (sin duplicados) ======================
if selected_tab == "📊 Pulse Vivo":
    st.subheader("📊 Pulse Vivo - Mercado en Tiempo Real")
    cols = st.columns(4)
    for i, sym in enumerate(symbols):
        data = prices.get(sym, {"price": 0, "change": 0})
        series = get_historical_prices(mapping[sym], days=7)
        with cols[i]:
            st.metric(
                label=f"**{sym}**",
                value=f"${data['price']:,.0f}",
                delta=f"{data['change']:+.2f}%",
                chart_data=series.tolist() if not series.empty else None
            )
            if data['price'] > 0:
                st.caption(f"Alto 24h: **${data['high_24h']:,.0f}**")
                st.caption(f"Bajo 24h: **${data['low_24h']:,.0f}**")
                st.caption(f"Volumen 24h: **${data['volume']/1e9:.1f}B**")

elif selected_tab == "🔔 Alertas IA":
    # (tu código de Alertas completo)

elif selected_tab == "⛓️ On-Chain":
    # (tu código de On-Chain completo)

elif selected_tab == "📰 News":
    # (tu código de News completo)

elif selected_tab == "🌍 Macro":
    # (tu código de Macro completo)

elif selected_tab == "🤖 AI Analyst":
    st.subheader("🤖 AI Analyst")
    st.markdown("### 📈 Evolución 7 días")
    chart_cols = st.columns(4)
    for i, (sym, coin_id) in enumerate(mapping.items()):
        with chart_cols[i]:
            st.caption(sym)
            series = get_historical_prices(coin_id, days=7)
            if not series.empty:
                st.line_chart(series, use_container_width=True, height=140)
            else:
                st.caption("Cargando gráfico...")
    st.markdown("---")
    st.write("**Preguntas rápidas con datos actuales**")
    # (tus botones y chat history completos)

# ====================== FOOTER ======================
st.caption(f"Última actualización de precios: {datetime.now().strftime('%H:%M:%S')}")
st.success("✅ CryptoSpark AI 100% tuya • Precios en tiempo real sin recargar nada")
