import streamlit as st
import requests
from difflib import SequenceMatcher

st.set_page_config(page_title="Comparador PRO", layout="wide")

# -------- CSS PROFISSIONAL --------
st.markdown("""
<style>
.main {
    max-width: 1200px;
    margin: auto;
}

.card {
    background: #111827;
    padding: 12px;
    border-radius: 12px;
    margin-bottom: 15px;
    color: white;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
}

.card img {
    max-height: 120px;
    object-fit: contain;
}

.price {
    font-size: 18px;
    color: #22c55e;
    font-weight: bold;
}

.title {
    font-size: 13px;
    margin: 8px 0;
}

.button {
    display: inline-block;
    padding: 6px 10px;
    background: #2563eb;
    color: white;
    border-radius: 6px;
    text-decoration: none;
    margin-top: 6px;
}
</style>
""", unsafe_allow_html=True)

st.title("🔎 Comparador de Produtos")

query = st.text_input("Buscar produto")
max_price = st.slider("Preço máximo", 0, 20000, 20000)

# -------- IA --------
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def agrupar(produtos):
    grupos = []
    for p in produtos:
        encontrou = False
        for g in grupos:
            if similar(g[0]["title"], p["title"]) > 0.6:
                g.append(p)
                encontrou = True
                break
        if not encontrou:
            grupos.append([p])

    resultado = []
    for g in grupos:
        melhor = sorted(g, key=lambda x: x["price"])[0]
        resultado.append(melhor)

    return resultado

# -------- MERCADO LIVRE --------
def buscar_ml(q):
    try:
        url = f"https://api.mercadolibre.com/sites/MLB/search?q={q}"
        r = requests.get(url, timeout=5)
        data = r.json()

        if "results" not in data:
            return []

        return [
            {
                "title": i["title"],
                "price": i["price"],
                "link": i["permalink"],
                "image": i["thumbnail"].replace("-I.jpg", "-O.jpg"),
                "source": "Mercado Livre"
            }
            for i in data["results"][:30]
            if i.get("price")
        ]

    except:
        return []

# -------- AMAZON --------
def buscar_amazon(q):
    try:
        from bs4 import BeautifulSoup

        url = f"https://www.amazon.com.br/s?k={q}"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=5)

        soup = BeautifulSoup(r.text, "html.parser")
        items = []

        for el in soup.select(".s-result-item"):
            title = el.select_one("h2 span")
            price = el.select_one(".a-price-whole")

            if title and price:
                p = float(price.text.replace(".", "").replace(",", ""))

                items.append({
                    "title": title.text,
                    "price": p,
                    "source": "Amazon"
                })

        return items[:10]

    except:
        return []

# -------- EXECUÇÃO --------
if st.button("Buscar") and query:

    ml = buscar_ml(query)
    amz = buscar_amazon(query)

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
        - [Facebook](https://www.facebook.com/marketplace/search?query={query})
        """)
        st.stop()

    # -------- MELHOR OFERTA --------
    melhor = todos[0]

    st.markdown("## 🏆 Melhor oferta")
    st.markdown(f"""
    <div class="card">
        <img src="{melhor.get('image','')}" />
        <div class="title">{melhor['title']}</div>
        <div class="price">R$ {melhor['price']}</div>
        <a class="button" href="{melhor.get('link','#')}" target="_blank">Comprar</a>
    </div>
    """, unsafe_allow_html=True)

    # -------- GRID --------
    st.markdown("## 🛍️ Produtos")

    cols = st.columns(4)

    for i, d in enumerate(todos):
        with cols[i % 4]:
            st.markdown(f"""
            <div class="card">
                <img src="{d.get('image','')}" />
                <div class="title">{d['title'][:60]}</div>
                <div class="price">R$ {d['price']}</div>
                <small>{d['source']}</small><br>
                <a class="button" href="{d.get('link','#')}" target="_blank">Ver</a>
            </div>
            """, unsafe_allow_html=True)

    # -------- LINKS EXTRAS --------
    st.markdown("---")
    st.markdown("### 🔎 Buscar em mais lugares")

    st.markdown(f"""
    - [OLX](https://www.olx.com.br/brasil?q={query})
    - [Facebook Marketplace](https://www.facebook.com/marketplace/search?query={query})
    """)
