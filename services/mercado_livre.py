import requests

def buscar(q):
    try:
        url = f"https://api.mercadolibre.com/sites/MLB/search?q={q}"
        r = requests.get(url, timeout=5)

        if r.status_code != 200:
            return []

        data = r.json()

        if "results" not in data:
            return []

        return [
            {
                "title": i.get("title", ""),
                "price": i.get("price", 0),
                "link": i.get("permalink", "#"),
                "image": i.get("thumbnail", ""),
                "source": "Mercado Livre"
            }
            for i in data["results"][:20]
            if i.get("price")
        ]

    except:
        return []