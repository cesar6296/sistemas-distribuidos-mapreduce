import math
import nltk
from nltk.corpus import stopwords

try:
    STOPWORDS = set(stopwords.words("english"))
except LookupError:
    nltk.download("stopwords", quiet=True)
    STOPWORDS = set(stopwords.words("english"))


def tokenizar(texto):
    texto = texto.lower()
    caracteres_validos = "abcdefghijklmnopqrstuvwxyzáéíóúñü' "
    texto_limpio = ""
    for c in texto:
        if c in caracteres_validos:
            texto_limpio += c
        else:
            texto_limpio += " "

    palabras = texto_limpio.split()
    resultado = []
    for p in palabras:
        if p not in STOPWORDS:
            resultado.append(p)
    return resultado


def leer_archivos(lista_archivos):
    textos = []
    for nombre in lista_archivos:
        f = open(nombre, "r", encoding="utf-8")
        contenido = f.read()
        f.close()
        textos.append(contenido)
    return textos


def map1(K, V):
    L = []
    for word in V:
        L.append(((K, word), 1))
    return L


def reduce1(K, V):
    return (K, sum(V))


def map2(K, V):
    return (K[1], 1)


def reduce2(K, V):
    return (K, sum(V))


def shuffle_and_sort(pares):
    agrupados = {}
    for clave, valor in pares:
        if clave not in agrupados:
            agrupados[clave] = []
        agrupados[clave].append(valor)
    return agrupados


def vector_normalizado(tf, idf):
    pesos = {}
    for t in tf:
        if t in idf:
            pesos[t] = tf[t] * idf[t]

    suma_cuadrados = 0
    for w in pesos.values():
        suma_cuadrados += w * w
    norma = math.sqrt(suma_cuadrados)

    if norma == 0:
        return {}

    vector = {}
    for t, w in pesos.items():
        vector[t] = w / norma
    return vector


def similitud_coseno(v1, v2):
    suma = 0
    for palabra, peso in v1.items():
        if palabra in v2:
            suma += peso * v2[palabra]
    return suma


class Indice:
    def __init__(self, lista_archivos):
        self.filenames = lista_archivos
        textos = leer_archivos(self.filenames)
        self.tokens = []
        self.doc_lengths = {}
        for i, t in enumerate(textos):
            toks = tokenizar(t)
            self.tokens.append(toks)
            self.doc_lengths[self.filenames[i]] = len(toks)

        pares_map1 = []
        for i in range(len(self.filenames)):
            pares_map1.extend(map1(self.filenames[i], self.tokens[i]))

        agrupados1 = shuffle_and_sort(pares_map1)
        res_reduce1 = []
        for k, v in agrupados1.items():
            res_reduce1.append(reduce1(k, v))

        self.tf_docs = {}
        for (archivo, palabra), count in res_reduce1:
            if archivo not in self.tf_docs:
                self.tf_docs[archivo] = {}
            # TF relativo segun la formula de la libreta: count / total_palabras_doc
            self.tf_docs[archivo][palabra] = count / self.doc_lengths[archivo]

        pares_map2 = []
        for k, v in res_reduce1:
            pares_map2.append(map2(k, v))

        agrupados2 = shuffle_and_sort(pares_map2)
        res_reduce2 = []
        for k, v in agrupados2.items():
            res_reduce2.append(reduce2(k, v))

        N = len(self.filenames)
        self.idf = {}
        for palabra, df in res_reduce2:
            # Formula de la libreta: log( (1 / DF_relativo) + 1 ) = log( (N / df) + 1 )
            self.idf[palabra] = math.log((N / df) + 1)

        self.vectores = []
        for archivo in self.filenames:
            tf = self.tf_docs.get(archivo, {})
            self.vectores.append(vector_normalizado(tf, self.idf))

    def matriz(self):
        n = len(self.vectores)
        matriz = []
        for i in range(n):
            fila = []
            for j in range(n):
                sim = similitud_coseno(self.vectores[i], self.vectores[j])
                fila.append(sim)
            matriz.append(fila)
        return matriz

    def buscar(self, query):
        tokens_query = tokenizar(query)
        tf_query = {}
        for t in tokens_query:
            if t in tf_query:
                tf_query[t] += 1
            else:
                tf_query[t] = 1

        v_query = vector_normalizado(tf_query, self.idf)
        resultados = []
        for i in range(len(self.filenames)):
            archivo = self.filenames[i]
            vector_doc = self.vectores[i]
            sim = similitud_coseno(v_query, vector_doc)
            resultados.append((archivo, sim))

        resultados.sort(key=lambda x: x[1], reverse=True)
        return resultados


def similitudes(filenames):
    idx = Indice(filenames)
    return idx.matriz()


if __name__ == "__main__":
    archivos = ["Doc1.txt", "Doc2.txt", "Doc3.txt"]
    idx = Indice(archivos)

    print("Tokens sin stopwords:")
    for i in range(len(archivos)):
        print(" ", archivos[i] + ":", idx.tokens[i])

    print("\nIDF:")
    for palabra in sorted(idx.idf.keys()):
        print(f"  {palabra:10s} {idx.idf[palabra]:.4f}")

    print("\nVectores normalizados:")
    for i in range(len(archivos)):
        partes = []
        for p, w in sorted(idx.vectores[i].items()):
            partes.append(f"{p}={w:.4f}")
        print(" ", archivos[i] + ": " + ", ".join(partes))

    print("\nMatriz de similitudes:")
    matriz = similitudes(archivos)
    for fila in matriz:
        linea = "  "
        for valor in fila:
            if round(valor, 4) == 1.0:
                linea += "1       "
            else:
                linea += f"{valor:.4f}  "
        print(linea)

    query = "life learning"
    print(f"\nQuery: '{query}'")
    for archivo, sim in idx.buscar(query):
        print(f"  {archivo}: {sim:.3f}")
        