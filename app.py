import streamlit as st
from services import mercado_livre, amazon
from utils.ai import agrupar

st.set_page_config(layout="wide")

# CSS
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("🔎 Buscador PRO")

query = st.text_input("Buscar produto")
max_price = st.slider("Preço máximo", 0, 20000, 20000)

if st.button("Buscar") and query:

    ml = mercado_livre.buscar(query)
    amz = amazon.buscar(query)

    ml = [i for i in ml if i["price"] <= max_price]
    amz = [i for i in amz if i["price"] <= max_price]

    ml = agrupar(ml)
    amz = agrupar(amz)

    todos = sorted(ml + amz, key=lambda x: x["price"])

    tab1, tab2, tab3 = st.tabs(["🟡 Mercado Livre", "🔵 Amazon", "🔥 Melhor"])

    # -------- MERCADO LIVRE --------
    with tab1:
        cols = st.columns(3)
        for i, d in enumerate(ml):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="card">
                    <img src="{d.get('image','')}" width="120"/>
                    <h4>{d['title'][:60]}</h4>
                    <div class="price">R$ {d['price']}</div>
                    <a class="button" href="{d['link']}" target="_blank">Comprar</a>
                </div>
                """, unsafe_allow_html=True)

    # -------- AMAZON --------
    with tab2:
        cols = st.columns(3)
        for i, d in enumerate(amz):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="card">
                    <h4>{d['title'][:60]}</h4>
                    <div class="price">R$ {d['price']}</div>
                    <span>Amazon</span>
                </div>
                """, unsafe_allow_html=True)

    # -------- MELHOR --------
    with tab3:
        if todos:
            melhor = todos[0]

            st.markdown(f"""
            <div class="card">
                <h2>🔥 Melhor Oferta</h2>
                <h3>{melhor['title']}</h3>
                <div class="price">R$ {melhor['price']}</div>
                <a class="button" href="{melhor.get('link','#')}" target="_blank">Comprar Agora</a>
            </div>
            """, unsafe_allow_html=True)

        cols = st.columns(3)

        for i, d in enumerate(todos):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="card">
                    <h4>{d['title'][:50]}</h4>
                    <div class="price">R$ {d['price']}</div>
                    <span>{d['source']}</span>
                </div>
                """, unsafe_allow_html=True)