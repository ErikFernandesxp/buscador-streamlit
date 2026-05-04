import streamlit as st
from services import mercado_livre, amazon
from utils.ai import agrupar

st.set_page_config(page_title="Comparador PRO", layout="wide")

# CSS PROFISSIONAL
st.markdown("""
<style>
.main {
    max-width: 1200px;
    margin: auto;
}

.card {
    background: #111827;
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 15px;
    color: white;
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
}

.price {
    font-size: 18px;
    color: #22c55e;
    font-weight: bold;
}

.title {
    font-size: 14px;
    margin-bottom: 8px;
}

.source {
    font-size: 12px;
    color: #9ca3af;
}
</style>
""", unsafe_allow_html=True)

st.title("🔎 Comparador de Produtos")

query = st.text_input("Buscar produto")
max_price = st.slider("Preço máximo", 0, 20000, 20000)

if st.button("Buscar") and query:

    with st.spinner("Buscando melhores preços..."):

        ml = mercado_livre.buscar(query)
        amz = amazon.buscar(query)

        ml = [i for i in ml if i["price"] <= max_price]
        amz = [i for i in amz if i["price"] <= max_price]

        ml = agrupar(ml)
        amz = agrupar(amz)

        todos = sorted(ml + amz, key=lambda x: x["price"])

    if not todos:
        st.warning("Nenhum resultado encontrado.")
        st.markdown(f"""
        - [Mercado Livre](https://lista.mercadolivre.com.br/{query})
        - [Amazon](https://www.amazon.com.br/s?k={query})
        - [OLX](https://www.olx.com.br/brasil?q={query})
        - [Facebook Marketplace](https://www.facebook.com/marketplace/search?query={query})
        """)
        st.stop()

    # MELHOR OFERTA
    melhor = todos[0]

    st.markdown("## 🏆 Melhor oferta")
    st.markdown(f"""
    <div class="card">
        <h3>{melhor['title']}</h3>
        <div class="price">R$ {melhor['price']}</div>
        <div class="source">{melhor['source']}</div>
    </div>
    """, unsafe_allow_html=True)

    st.link_button("🔥 Comprar melhor oferta", melhor.get("link", "#"))

    st.markdown("## 🛍️ Todos os resultados")

    cols = st.columns(4)

    for i, d in enumerate(todos):
        with cols[i % 4]:
            if d.get("image"):
                st.image(d["image"], width=120)

            st.markdown(f"""
            <div class="card">
                <div class="title">{d['title'][:60]}</div>
                <div class="price">R$ {d['price']}</div>
                <div class="source">{d['source']}</div>
            </div>
            """, unsafe_allow_html=True)

            st.link_button("Ver produto", d.get("link", "#"))

    # LINKS EXTRAS
    st.markdown("---")
    st.markdown("### 🔎 Mais opções")

    col1, col2 = st.columns(2)

    with col1:
        st.link_button("🟠 Buscar na OLX", f"https://www.olx.com.br/brasil?q={query}")

    with col2:
        st.link_button("🔵 Facebook Marketplace", f"https://www.facebook.com/marketplace/search?query={query}")
