import streamlit as st
import requests
from difflib import SequenceMatcher

st.set_page_config(page_title="Buscador Inteligente", layout="wide")

st.title("🔎 Buscador Inteligente de Produtos")

# INPUT
query = st.text_input("Digite o produto")
max_price = st.slider("Preço máximo", 0, 20000, 20000)

# SIMILARIDADE (IA leve)
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

# AGRUPAMENTO
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

        resultado.append({
            "title": melhor["title"],
            "price": melhor["price"],
            "link": melhor.get("link", "#"),
            "source": melhor["source"]
        })

    return resultado

# MERCADO LIVRE
def buscar_ml(q):
    try:
        url = f"https://api.mercadolibre.com/sites/MLB/search?q={q}"
        res = requests.get(url)
        data = res.json()

        return [
            {
                "title": i["title"],
                "price": i["price"],
                "link": i["permalink"],
                "source": "Mercado Livre"
            }
            for i in data["results"][:15]
        ]
    except:
        return []

# AMAZON (simples)
def buscar_amazon(q):
    try:
        url = f"https://www.amazon.com.br/s?k={q}"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers)

        from bs4 import BeautifulSoup
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

# EXECUÇÃO
if st.button("Buscar") and query:

    with st.spinner("Buscando produtos..."):

        dados = []
        dados += buscar_ml(query)
        dados += buscar_amazon(query)

        # FILTRO DE PREÇO
        dados = [d for d in dados if d["price"] <= max_price]

        # IA AGRUPAMENTO
        dados = agrupar(dados)

        # ORDENAR
        dados = sorted(dados, key=lambda x: x["price"])

    st.success(f"{len(dados)} produtos encontrados")

    # RESULTADOS
    cols = st.columns(3)

    for i, d in enumerate(dados):
        with cols[i % 3]:
            st.markdown(f"### {d['title'][:60]}...")
            st.write(f"💰 R$ {d['price']}")
            st.write(f"🏪 {d['source']}")
            st.markdown(f"[🔗 Ver produto]({d['link']})")
            st.divider()

# FACEBOOK (BOTÃO)
if query:
    st.markdown("### 🔎 Buscar também em outras plataformas")
    st.markdown(
        f"[Facebook Marketplace](https://www.facebook.com/marketplace/search?query={query})",
        unsafe_allow_html=True
    )