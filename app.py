"""StockFlow — versão web (Flask). Execute: python app_web.py  →  http://127.0.0.1:5000"""
from flask import (Flask, render_template_string, request, redirect,
                   url_for, flash, jsonify)

import estoque_core as eq

app = Flask(__name__)
app.secret_key = "stockflow-dev-key"
app.jinja_env.globals.update(moeda=eq.formatar_moeda, status=eq.status_produto)


@app.route("/")
def index():
    produtos = eq.carregar_dados()
    q, cat = request.args.get("q", ""), request.args.get("cat", "")
    return render_template_string(
        TEMPLATE,
        produtos=eq.buscar_produtos(produtos, q, cat),
        resumo=eq.calcular_resumo(produtos),
        categorias=sorted({p["categoria"] for p in produtos}),
        q=q, cat=cat)


@app.post("/salvar")
def salvar():
    produtos = eq.carregar_dados()
    try:
        dados = eq.validar_produto(request.form.get("nome"), request.form.get("categoria"),
                                   request.form.get("quantidade"), request.form.get("preco"),
                                   request.form.get("minimo"))
        pid = request.form.get("id")
        if pid:
            eq.atualizar_produto(produtos, int(pid), dados)
            msg = "Produto atualizado."
        else:
            eq.adicionar_produto(produtos, dados)
            msg = "Produto adicionado."
        eq.salvar_dados(produtos)
        flash(msg, "ok")
    except ValueError as e:
        flash(str(e), "erro")
    return redirect(url_for("index"))


@app.post("/mov/<int:pid>")
def mov(pid):
    produtos = eq.carregar_dados()
    try:
        eq.movimentar_estoque(produtos, pid, request.form.get("tipo"), request.form.get("qtd"))
        eq.salvar_dados(produtos)
        flash("Movimentação registrada.", "ok")
    except ValueError as e:
        flash(str(e), "erro")
    return redirect(request.referrer or url_for("index"))


@app.post("/excluir/<int:pid>")
def excluir(pid):
    produtos = eq.carregar_dados()
    try:
        eq.remover_produto(produtos, pid)
        eq.salvar_dados(produtos)
        flash("Produto excluído.", "ok")
    except ValueError as e:
        flash(str(e), "erro")
    return redirect(url_for("index"))


@app.get("/api/produtos")
def api_produtos():
    return jsonify(eq.carregar_dados())


TEMPLATE = r"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>StockFlow — Gestão de Estoque</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@400;600;800&display=swap" rel="stylesheet">
<style>
:root{--bg:#eef2f6;--card:#fff;--tinta:#12263a;--sub:#64748b;--borda:#d9e1ea;--laranja:#f26a1b;
--verde:#17a673;--verm:#d64545;--amar:#e8a317;--azul:#2f6fdb;--campo:#f1f5f9}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--tinta);font-family:'Bricolage Grotesque',system-ui,sans-serif;line-height:1.45}
header{background:var(--tinta);color:#fff;position:relative}
header::after{content:"";position:absolute;left:0;right:0;bottom:0;height:5px;
background:repeating-linear-gradient(-45deg,var(--laranja) 0 14px,var(--tinta) 14px 28px)}
.topo{max-width:1180px;margin:auto;padding:22px 20px 26px;display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap}
h1{margin:0;font-size:1.7rem;font-weight:800;letter-spacing:-.02em}
h1 small{display:block;font-size:.85rem;font-weight:400;color:#9fb3c8;letter-spacing:0}
main{max-width:1180px;margin:auto;padding:22px 20px 60px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px;margin-bottom:20px}
.kpi{background:var(--card);border:1px solid var(--borda);border-left:6px solid var(--c);padding:14px 18px}
.kpi span{color:var(--sub);font-size:.85rem}
.kpi b{display:block;font-size:1.8rem;font-weight:800;letter-spacing:-.02em}
.painel{background:var(--card);border:1px solid var(--borda)}
.barra{display:flex;gap:10px;padding:14px;flex-wrap:wrap;border-bottom:1px solid var(--borda)}
.barra form{display:flex;gap:10px;flex:1;min-width:260px;flex-wrap:wrap}
input,select{font:inherit;color:var(--tinta);background:var(--campo);border:1px solid var(--borda);padding:10px 12px;border-radius:4px;width:100%}
input:focus,select:focus,button:focus-visible{outline:2px solid var(--laranja);outline-offset:1px}
.barra input[type=search]{flex:1;min-width:160px;width:auto}
.barra select{width:auto;min-width:150px}
button{font:inherit;font-weight:600;border:0;border-radius:4px;padding:10px 16px;cursor:pointer;color:#fff;background:var(--tinta);transition:filter .15s}
button:hover{filter:brightness(1.15)}
.b-novo{background:var(--laranja)}
table{width:100%;border-collapse:collapse}
th{background:var(--tinta);color:#fff;text-align:left;font-weight:600;font-size:.85rem;padding:11px 14px}
td{padding:11px 14px;border-bottom:1px solid var(--borda);vertical-align:middle}
td.n,th.n{text-align:right}
tr.baixo td{background:#fff6e0}tr.zerado td{background:#fde8e8}
.tag{display:inline-block;font-size:.78rem;font-weight:600;padding:2px 9px;border-radius:99px}
.tag.ok{background:#dcf5ea;color:#0d7a55}.tag.baixo{background:#fde9b8;color:#8a5a00}.tag.zerado{background:#f9c9c9;color:#9b2323}
.nome small{display:block;color:var(--sub);font-size:.8rem}
.mov{display:flex;gap:4px}
.mov input{width:64px;padding:6px 8px;text-align:center}
.mov button{padding:6px 11px}
.acoes{display:flex;gap:6px;justify-content:flex-end}
.ic{background:var(--campo);color:var(--tinta);border:1px solid var(--borda);padding:6px 11px}
.ic.x{color:var(--verm)}
.vazio{padding:40px;text-align:center;color:var(--sub)}
.flash{max-width:1180px;margin:16px auto 0;padding:0 20px}
.flash div{padding:11px 16px;border-left:5px solid;background:#fff;margin-bottom:8px;animation:sai .4s 4s forwards}
.flash .ok{border-color:var(--verde)}.flash .erro{border-color:var(--verm);background:#fde8e8}
@keyframes sai{to{opacity:0;height:0;padding:0;margin:0;overflow:hidden}}
dialog{border:0;border-top:6px solid var(--laranja);padding:0;width:min(440px,94vw);background:var(--card);color:var(--tinta)}
dialog::backdrop{background:rgba(18,38,58,.6)}
dialog form{padding:22px;display:grid;grid-template-columns:1fr 1fr;gap:12px}
dialog h2{grid-column:1/-1;margin:0;font-size:1.3rem}
dialog label{font-size:.85rem;color:var(--sub);display:grid;gap:4px}
dialog .full{grid-column:1/-1}
dialog .rodape{grid-column:1/-1;display:flex;gap:10px;justify-content:flex-end}
.cancelar{background:var(--campo);color:var(--tinta)}
@media(max-width:820px){
 thead{display:none}
 table,tbody,tr,td{display:block;width:100%}
 tr{border-bottom:6px solid var(--bg);padding:8px 0}
 td{border:0;display:flex;justify-content:space-between;align-items:center;gap:12px;padding:6px 14px;text-align:right}
 td::before{content:attr(data-l);color:var(--sub);font-size:.82rem;text-align:left}
 td.nome{display:block;text-align:left;font-weight:600;font-size:1.05rem}td.nome::before{display:none}
 .acoes{justify-content:flex-end}
}
@media(prefers-reduced-motion:reduce){.flash div{animation:none}}
</style>
</head>
<body>
<header><div class="topo">
  <h1>StockFlow<small>controle de estoque</small></h1>
  <button class="b-novo" onclick="novo()">+ Novo produto</button>
</div></header>

<div class="flash">{% for cat_, msg in get_flashed_messages(with_categories=true) %}<div class="{{ cat_ }}">{{ msg }}</div>{% endfor %}</div>

<main>
  <section class="kpis">
    <div class="kpi" style="--c:var(--azul)"><span>Produtos cadastrados</span><b>{{ resumo.produtos }}</b></div>
    <div class="kpi" style="--c:var(--verde)"><span>Unidades em estoque</span><b>{{ resumo.unidades }}</b></div>
    <div class="kpi" style="--c:var(--laranja)"><span>Valor em estoque</span><b>{{ moeda(resumo.valor) }}</b></div>
    <div class="kpi" style="--c:var(--verm)"><span>Alertas de reposição</span><b>{{ resumo.alertas }}</b></div>
  </section>

  <section class="painel">
    <div class="barra">
      <form method="get">
        <input type="search" name="q" value="{{ q }}" placeholder="Buscar por nome ou categoria">
        <select name="cat" onchange="this.form.submit()">
          <option value="">Todas as categorias</option>
          {% for c in categorias %}<option {{ 'selected' if c == cat }}>{{ c }}</option>{% endfor %}
        </select>
        <button>Buscar</button>
      </form>
    </div>
    {% if produtos %}
    <table>
      <thead><tr><th>Produto</th><th>Situação</th><th class="n">Qtd.</th><th class="n">Preço</th><th class="n">Total</th><th>Movimentar</th><th></th></tr></thead>
      <tbody>
      {% for p in produtos %}{% set s = status(p) %}
      <tr class="{{ s if s != 'ok' }}">
        <td class="nome" data-l="Produto">{{ p.nome }}<small>{{ p.categoria }} · #{{ p.id }}</small></td>
        <td data-l="Situação"><span class="tag {{ s }}">{{ {'ok':'Em dia','baixo':'Repor','zerado':'Esgotado'}[s] }}</span></td>
        <td class="n" data-l="Quantidade (mín. {{ p.minimo }})"><b>{{ p.quantidade }}</b></td>
        <td class="n" data-l="Preço">{{ moeda(p.preco) }}</td>
        <td class="n" data-l="Total">{{ moeda(p.preco * p.quantidade) }}</td>
        <td data-l="Movimentar">
          <form class="mov" method="post" action="{{ url_for('mov', pid=p.id) }}">
            <input type="number" name="qtd" min="1" value="1" aria-label="Quantidade">
            <button name="tipo" value="entrada" style="background:var(--verde)" title="Entrada">+</button>
            <button name="tipo" value="saida" style="background:var(--azul)" title="Saída">−</button>
          </form>
        </td>
        <td data-l="Ações"><div class="acoes">
          <button class="ic" onclick='editar({{ p|tojson }})'>Editar</button>
          <form method="post" action="{{ url_for('excluir', pid=p.id) }}" onsubmit="return confirm('Excluir este produto?')">
            <button class="ic x">Excluir</button></form>
        </div></td>
      </tr>{% endfor %}
      </tbody>
    </table>
    {% else %}<div class="vazio">Nenhum produto encontrado. Clique em “Novo produto” para cadastrar.</div>{% endif %}
  </section>
</main>

<dialog id="dlg">
  <form method="post" action="{{ url_for('salvar') }}">
    <h2 id="tit">Novo produto</h2>
    <input type="hidden" name="id" id="f-id">
    <label class="full">Nome do produto<input name="nome" id="f-nome" required></label>
    <label class="full">Categoria<input name="categoria" id="f-categoria" list="cats"></label>
    <datalist id="cats">{% for c in categorias %}<option value="{{ c }}">{% endfor %}</datalist>
    <label>Quantidade<input name="quantidade" id="f-quantidade" type="number" min="0" value="0" required></label>
    <label>Estoque mínimo<input name="minimo" id="f-minimo" type="number" min="0" value="0"></label>
    <label class="full">Preço unitário (R$)<input name="preco" id="f-preco" inputmode="decimal" placeholder="49,90" required></label>
    <div class="rodape">
      <button type="button" class="cancelar" onclick="dlg.close()">Cancelar</button>
      <button class="b-novo">Salvar produto</button>
    </div>
  </form>
</dialog>

<script>
const dlg = document.getElementById('dlg');
function preencher(p){
  for (const k of ['id','nome','categoria','quantidade','minimo','preco'])
    document.getElementById('f-'+k).value = p[k] ?? '';
}
function novo(){ preencher({quantidade:0, minimo:0}); document.getElementById('tit').textContent='Novo produto'; dlg.showModal(); }
function editar(p){
  p.preco = String(p.preco).replace('.', ',');
  preencher(p); document.getElementById('tit').textContent='Editar produto #'+p.id; dlg.showModal();
}
</script>
</body>
</html>"""


if __name__ == "__main__":
    app.run(debug=True)