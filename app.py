from flask import Flask, request, render_template_string

from similitudes import Indice

ARCHIVOS = ["Doc1.txt", "Doc2.txt", "Doc3.txt"]
indice = Indice(ARCHIVOS)

app = Flask(__name__)

PAGINA = """
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Buscador de documentos</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 640px; margin: 48px auto; padding: 0 16px; }
    form { display: flex; gap: 8px; }
    input[type=text] { flex: 1; padding: 10px 12px; font-size: 1rem; }
    button { padding: 10px 16px; font-size: 1rem; cursor: pointer; }
    .res { margin-top: 24px; }
    .fila { padding: 10px 0; border-bottom: 1px solid #ddd; }
    .barra { height: 6px; background: #4a7bd0; border-radius: 3px; margin-top: 6px; }
    small { color: #666; }
  </style>
</head>
<body>
  <h1>Buscador</h1>
  <form method="get">
    <input type="text" name="q" value="{{ q }}" placeholder="Escribe aqui tu query brotherrrrrrr" autofocus>
    <button>Buscar</button>
  </form>

  {% if q %}
  <div class="res">
    <h2>Resultados para “{{ q }}”</h2>
    {% for archivo, sim, texto in resultados %}
      <div class="fila">
        <strong>{{ archivo }}</strong> - similitud {{ "%.3f"|format(sim) }}<br>
        <small>{{ texto }}</small>
        <div class="barra" style="width: {{ (sim * 100)|round(1) }}%"></div>
      </div>
    {% endfor %}
  </div>
  {% endif %}
</body>
</html>
"""


@app.route("/")
def inicio():
    q = request.args.get("q", "").strip()
    resultados = []
    if q:
        for archivo, sim in indice.buscar(q):
            with open(archivo, encoding="utf-8") as f:
                resultados.append((archivo, sim, f.read()))
    return render_template_string(PAGINA, q=q, resultados=resultados)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
