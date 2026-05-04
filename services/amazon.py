import requests
from bs4 import BeautifulSoup

def buscar(q):
    try:
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