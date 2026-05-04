import streamlit as st
from services import mercado_livre, amazon
from utils.ai import agrupar

st.set_page_config(layout="wide")

# CSS MELHORADO
st.markdown("""
<style>
.main {
    max-width: 1200px;
    margin: auto;
}

.card {
    background: #1e293b;
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 15px;
    color: white;
    box-shadow: 0 4px 10px rgba(0,0,0,0.3);
}

.price {
    font-size: 20px;
    color: #22c55e;
    font-weight: bold;
}

.title {
    font-size: 14px;
}

.source {
    font-size: 12px;
    color: #94a3b8;
}

.button {
    display: inline-block;
    padding: 6px 10px;
    background: #3b82f6;
    color: white;
    border-radius: 6px;
    text-decoration: none;
    margin-top: 5px;
}
</style>
""", unsafe_allow_html=True)

st.title("🔎 Comparador de Produtos")

query = st.text_input("Buscar produto")
max_price = st.slider("Preço máximo", 0, 20000, 20000)

if st.button("Buscar") and query:

    ml = mercado_livre.buscar(query)
    amz = amazon.buscar(query)

    # FILTRO
    ml = [i for i in ml if i["price"] <= max_price]
    amz = [i for i in amz if i["price"] <= max_price]

    # IA
    ml = agrupar(ml)
    amz = agrupar(amz)

    # JUNTA TUDO
    todos = ml + amz

    # GARANTE RESULTADO
    if not todos:
        st.warning("Nenhum resultado direto encontrado.")
        st.markdown(f"""
        🔎 Tentar manualmente:
        - [Mercado Livre](https://lista.mercadolivre.com.br/{query})
        - [Amazon](https://www.amazon.com.br/s?k={query})
        - [OLX](https://www.olx.com.br/brasil?q={query})
        - [Facebook Marketplace](https://www.facebook.com/marketplace/search?query={query})
        """)
        st.stop()

    # ORDENA
    todos = sorted(todos, key=lambda x: x["price"])

    # MELHOR PREÇO
    melhor = todos[0]

    st.markdown("## 🏆 Melhor oferta")
    st.markdown(f"""
    <div class="card">
        <h3>{melhor['title']}</h3>
        <div class="price">R$ {melhor['price']}</div>
        <div class="source">{melhor['source']}</div>
        <a class="button" href="{melhor.get('link','#')}" target="_blank">Comprar</a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("## 🛍️ Resultados")

    cols = st.columns(4)

    for i, d in enumerate(todos):
        with cols[i % 4]:
            st.markdown(f"""
            <div class="card">
                <div class="title">{d['title'][:60]}</div>
                <div class="price">R$ {d['price']}</div>
                <div class="source">{d['source']}</div>
                <a class="button" href="{d.get('link','#')}" target="_blank">Ver</a>
            </div>
            """, unsafe_allow_html=True)

    # LINKS EXTRAS (OLX + FACEBOOK)
    st.markdown("---")
    st.markdown("### 🔎 Mais opções")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"[🟠 Buscar na OLX](https://www.olx.com.br/brasil?q={query})")

    with col2:
        st.markdown(f"[🔵 Facebook Marketplace](https://www.facebook.com/marketplace/search?query={query})")
