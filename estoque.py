"""
Núcleo do sistema de estoque (Villot Imports).
Regras de negócio + persistência em JSON, compartilhado entre
a versão desktop (tkinter) e a versão web (Flask).

Os dados vivem em memória como uma LISTA DE DICIONÁRIOS:
    {"id": 1, "nome": "...", "categoria": "...", "quantidade": 10,
     "minimo": 5, "preco": 19.9, "atualizado": "16/11/2026 10:30"}
"""
import json
import os
from datetime import datetime

ARQUIVO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "estoque.json")


def _agora():
    return datetime.now().strftime("%d/%m/%Y %H:%M")


def _exemplo():
    base = [
        ("Teclado Mecânico", "Periféricos", 24, 10, 249.90),
        ("Mouse Sem Fio", "Periféricos", 8, 12, 89.90),
        ("Monitor 24\"", "Monitores", 5, 5, 899.00),
        ("Cabo HDMI 2m", "Cabos", 0, 15, 29.90),
        ("Webcam Full HD", "Periféricos", 17, 6, 179.00),
        ("SSD 480GB", "Armazenamento", 31, 10, 219.90),
    ]
    return [
        {"id": i, "nome": n, "categoria": c, "quantidade": q,
         "minimo": m, "preco": p, "atualizado": _agora()}
        for i, (n, c, q, m, p) in enumerate(base, start=1)
    ]


# ------------------------------------------------------------------ persistência
def carregar_dados():
    """Lê o JSON. Se não existir (ou estiver corrompido), cria dados de exemplo."""
    try:
        with open(ARQUIVO, "r", encoding="utf-8") as f:
            dados = json.load(f)
        if not isinstance(dados, list):
            raise ValueError("Formato inválido")
        return dados
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        dados = _exemplo()
        salvar_dados(dados)
        return dados


def salvar_dados(produtos):
    """Grava a lista de dicionários no JSON (escrita atômica)."""
    tmp = ARQUIVO + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(produtos, f, ensure_ascii=False, indent=2)
        os.replace(tmp, ARQUIVO)
    except OSError as e:
        raise ValueError(f"Não foi possível salvar o arquivo: {e}")


# ------------------------------------------------------------------ validação
def validar_produto(nome, categoria, quantidade, preco, minimo):
    """Valida e normaliza os campos. Levanta ValueError com mensagem clara."""
    nome = str(nome or "").strip()
    categoria = str(categoria or "").strip() or "Geral"
    if not nome:
        raise ValueError("Informe o nome do produto.")
    try:
        quantidade = int(str(quantidade).strip())
        minimo = int(str(minimo).strip() or 0)
    except ValueError:
        raise ValueError("Quantidade e estoque mínimo devem ser números inteiros.")
    try:
        preco = round(float(str(preco).strip().replace(",", ".")), 2)
    except ValueError:
        raise ValueError("Preço inválido. Exemplo: 49,90")
    if quantidade < 0 or minimo < 0 or preco < 0:
        raise ValueError("Os valores não podem ser negativos.")
    return {"nome": nome, "categoria": categoria, "quantidade": quantidade,
            "minimo": minimo, "preco": preco}


# ------------------------------------------------------------------ operações
def proximo_id(produtos):
    return max((p["id"] for p in produtos), default=0) + 1


def adicionar_produto(produtos, dados):
    produto = {"id": proximo_id(produtos), **dados, "atualizado": _agora()}
    produtos.append(produto)
    return produto


def atualizar_produto(produtos, pid, dados):
    for p in produtos:
        if p["id"] == pid:
            p.update(dados, atualizado=_agora())
            return p
    raise ValueError("Produto não encontrado.")


def remover_produto(produtos, pid):
    antes = len(produtos)
    produtos[:] = [p for p in produtos if p["id"] != pid]
    if len(produtos) == antes:
        raise ValueError("Produto não encontrado.")


def movimentar_estoque(produtos, pid, tipo, qtd):
    """Registra entrada ou saída de estoque."""
    try:
        qtd = int(str(qtd).strip())
    except ValueError:
        raise ValueError("A quantidade da movimentação deve ser um inteiro.")
    if qtd <= 0:
        raise ValueError("A quantidade deve ser maior que zero.")
    for p in produtos:
        if p["id"] == pid:
            if tipo == "saida":
                if qtd > p["quantidade"]:
                    raise ValueError(
                        f"Saída maior que o estoque ({p['quantidade']} un. disponíveis).")
                p["quantidade"] -= qtd
            else:
                p["quantidade"] += qtd
            p["atualizado"] = _agora()
            return p
    raise ValueError("Produto não encontrado.")


# ------------------------------------------------------------------ consulta
def status_produto(p):
    if p["quantidade"] == 0:
        return "zerado"
    if p["quantidade"] <= p["minimo"]:
        return "baixo"
    return "ok"


def buscar_produtos(produtos, termo="", categoria=""):
    termo = (termo or "").strip().lower()
    return [
        p for p in produtos
        if (not termo or termo in p["nome"].lower() or termo in p["categoria"].lower())
        and (not categoria or p["categoria"] == categoria)
    ]


def calcular_resumo(produtos):
    return {
        "produtos": len(produtos),
        "unidades": sum(p["quantidade"] for p in produtos),
        "valor": sum(p["quantidade"] * p["preco"] for p in produtos),
        "alertas": sum(1 for p in produtos if status_produto(p) != "ok"),
    }


def formatar_moeda(valor):
    s = f"{valor:,.2f}"
    return "R$ " + s.replace(",", "X").replace(".", ",").replace("X", ".")