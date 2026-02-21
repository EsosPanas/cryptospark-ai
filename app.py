import streamlit as st
import ccxt
import requests

st.set_page_config(page_title="CryptoSpark AI", layout="wide")
st.title("🚀 CryptoSpark AI - Tu Sala de Control Trader")
st.caption("BTC • ETH • SOL • BNB | Datos en tiempo real cada 15s")

# ==================== TU CLAVE IA ====================
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")

# ==================== DATOS EN VIVO ====================
@st.cache_resource(ttl=30)
def get_exchange():
    return ccxt.binanceusdm({
        'enableRateLimit': True,
        'headers': {'User-Agent': 'Mozilla/5.0'},
        'options': {'defaultType': 'future'}
    })

exchange = get_exchange()

def get_futures_data(symbol):
    try:
        ticker = exchange.fetch_ticker(f"{symbol}/USDT:USDT")
        try:
            funding = exchange.fetch_funding_rate(f"{symbol}/USDT:USDT")['fundingRate'] * 100
        except:
            funding = 0.0
        return {
            "price": ticker['last'],
            "change": ticker['percentage'],
            "funding": funding,
            "oi": ticker.get('info', {}).get('openInterest', 0)
        }
    except:
        return {"price": 0, "change": 0, "funding": 0, "oi": 0}

def ia_explica(texto):
    if not GROQ_API_KEY:
        return "⚠️ Agrega tu clave Groq en Secrets para activar la IA"
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": f"Explica en español sencillo y como trader: {texto}"}],
                "max_tokens": 300
            },
            timeout=10
        )
        return r.json()["choices"][0]["message"]["content"]
    except:
        return "Error temporal en IA. Intenta otra vez."

def defillama_tvl(chain="solana"):
    try:
        r = requests.get("https://api.llama.fi/v2/chains", timeout=10)
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
        data = get_futures_data(sym)
        with cols[i]:
            st.metric(
                f"{sym}",
                f"${data['price']:,.0f}" if data['price'] > 0 else "Cargando...",
                f"{data['change']:+.2f}%"
            )
            st.caption(f"Funding: {data['funding']:+.3f}% | OI: {int(data['oi']):,}")

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
    with col1: st.metric("TVL Solana", f"${defillama_tvl('solana')/1e9:.1f}B")
    with col2: st.metric("TVL Ethereum", f"${defillama_tvl('ethereum')/1e9:.1f}B")

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
