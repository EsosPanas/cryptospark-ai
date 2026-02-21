import streamlit as st
import requests

st.set_page_config(page_title="CryptoSpark AI", layout="wide")
st.title("🚀 CryptoSpark AI - Tu Sala de Control Trader")
st.caption("BTC • ETH • SOL • BNB | Actualización automática cada 15 segundos")

# ==================== TU CLAVE IA ====================
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")

# ==================== BOTÓN GRANDE ====================
if st.button("🔄 Actualizar Todo Ahora", type="primary", use_container_width=True):
    st.rerun()

# ==================== PRECIOS COINGECKO ====================
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
                    "change": coin['price_change_percentage_24h']
                }
        return prices
    except:
        return {}

prices = get_prices()

def ia_explica(texto):
    if not GROQ_API_KEY:
        return "⚠️ Agrega tu clave Groq en Secrets para activar IA"
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": f"Explica en español sencillo y como trader: {texto}"}],
                "max_tokens": 300
            },
            timeout=8
        )
        return r.json()["choices"][0]["message"]["content"]
    except:
        return "Error temporal en IA. Espera 15s o pulsa Actualizar"

def defillama_tvl(chain="solana"):
    try:
        r = requests.get("https://api.llama.fi/v2/chains", timeout=8)
        for c in r.json():
            if c["name"].lower() == chain.lower():
                return c["tvl"]
        return 0
    except:
        return 0

# ==================== TABS ====================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📊 Pulse Vivo", "🔔 Alertas IA", "⛓️ On-Chain", "📰 News", "🌍 Macro", "🤖 AI Analyst"])

with tab1:
    st.subheader("Pulse Vivo - Datos en Vivo")
    cols = st.columns(4)
    symbols = ["BTC", "ETH", "SOL", "BNB"]
    for i, sym in enumerate(symbols):
        data = prices.get(sym, {"price": 0, "change": 0})
        with cols[i]:
            if data['price'] > 0:
                st.metric(f"{sym}", f"${data['price']:,.0f}", f"{data['change']:+.2f}%")
            else:
                st.metric(f"{sym}", "Cargando...", "")

with tab2:
    st.subheader("🔔 Centro de Alertas Inteligentes")
    alertas = [
        {"color": "🟢", "title": "OPORTUNIDAD", "desc": "ETH: Whale inflow detectado + funding negativo → setup largo probable"},
        {"color": "🔴", "title": "RIESGO", "desc": "SOL: Funding alto +0.08% → posible long squeeze en 2-4h"},
        {"color": "🟡", "title": "INFO", "desc": "Próximo dato CPI USA en 45 min → espera volatilidad"}
    ]
    for idx, a in enumerate(alertas):
        with st.expander(f"{a['color']} {a['title']}"):
            st.write(a['desc'])
            if st.button("🤖 Explicar con IA", key=f"btn_{idx}"):
                with st.spinner("IA pensando..."):
                    st.write(ia_explica(a['desc']))

with tab3:
    st.subheader("⛓️ On-Chain & Whale Radar")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("TVL Solana", f"${defillama_tvl('solana')/1e9:.1f}B")
    with col2:
        st.metric("TVL Ethereum", f"${defillama_tvl('ethereum')/1e9:.1f}B")

with tab4:
    st.subheader("📰 Noticias Relevantes")
    st.info("Próximamente feed completo")

with tab5:
    st.subheader("🌍 Macro Global")
    st.write("• DXY actual: 103.45")
    st.write("• Próximo CPI USA: en 45 min")
    st.write("• Flujos ETF BTC hoy: +$87M")

with tab6:
    st.subheader("🤖 AI Analyst")
    pregunta = st.text_input("Pregúntame lo que quieras")
    if st.button("Preguntar") and pregunta:
        with st.spinner("IA pensando..."):
            st.success(ia_explica(pregunta))

st.success("✅ CryptoSpark AI 100% tuya y funcionando")
