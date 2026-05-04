from difflib import SequenceMatcher

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