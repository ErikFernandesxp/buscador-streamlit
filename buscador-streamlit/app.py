import streamlit as st
import requests
from difflib import SequenceMatcher

st.set_page_config(page_title="Buscador Pro", layout="wide")

st.title("🔎 Buscador de Produtos")

query = st.text_input("Buscar produto")
max_price = st.slider("Preço máximo", 0, 20000, 20000)

# ---------------- IA ----------------
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

# ---------------- BUSCAS ----------------
def buscar_ml(q):
    url = f"https://api.mercadolibre.com/sites/MLB/search?q={q}"
    res = requests.get(url).json()

    return [
        {
            "title": i["title"],
            "price": i["price"],
            "link": i["permalink"],
            "image": i["thumbnail"],
            "source": "Mercado Livre"
        }
        for i in res["results"][:15]
    ]

def buscar_amazon(q):
    try:
        from bs4 import BeautifulSoup

        url = f"https://www.amazon.com.br/s?k={q}"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=5)

        soup = BeautifulSoup(res.text, "html.parser")

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

# ---------------- EXECUÇÃO ----------------
if st.button("Buscar") and query:

    with st.spinner("Buscando produtos..."):

        ml = buscar_ml(query)
        amz = buscar_amazon(query)

        # FILTRO
        ml = [i for i in ml if i["price"] <= max_price]
        amz = [i for i in amz if i["price"] <= max_price]

        # IA
        ml = agrupar(ml)
        amz = agrupar(amz)

        ml = sorted(ml, key=lambda x: x["price"])
        amz = sorted(amz, key=lambda x: x["price"])

    st.success("Resultados encontrados")

    # ---------------- ABAS ----------------
    tab1, tab2, tab3 = st.tabs(["🟡 Mercado Livre", "🔵 Amazon", "🌐 Todos"])

    # -------- Mercado Livre --------
    with tab1:
        cols = st.columns(3)
        for i, d in enumerate(ml):
            with cols[i % 3]:
                st.image(d.get("image", ""), width=150)
                st.markdown(f"**{d['title'][:60]}...**")
                st.write(f"💰 R$ {d['price']}")
                st.markdown(f"[Comprar]({d['link']})")
                st.divider()

    # -------- Amazon --------
    with tab2:
        cols = st.columns(3)
        for i, d in enumerate(amz):
            with cols[i % 3]:
                st.markdown(f"**{d['title'][:60]}...**")
                st.write(f"💰 R$ {d['price']}")
                st.write("Amazon")
                st.divider()

    # -------- Todos (Comparador) --------
    with tab3:
        todos = ml + amz
        todos = sorted(todos, key=lambda x: x["price"])

        cols = st.columns(3)

        for i, d in enumerate(todos):
            with cols[i % 3]:
                st.markdown(f"### {d['title'][:50]}...")
                st.write(f"🔥 R$ {d['price']}")
                st.write(f"🏪 {d['source']}")
                if "link" in d:
                    st.markdown(f"[Ver produto]({d['link']})")
                st.divider()

# Facebook
if query:
    st.markdown("---")
    st.markdown(f"[🔎 Buscar no Facebook Marketplace](https://www.facebook.com/marketplace/search?query={query})")
