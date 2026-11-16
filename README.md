# Villot Imports — Sistema de Gestão de Estoque

Sistema de controle de estoque em Python com **duas interfaces** que compartilham o mesmo núcleo e os mesmos dados:

- **Desktop** (`desktop.py`) — tkinter, com layout responsivo.
- **Web** (`app.py`) — Flask, responsiva (funciona em celular, tablet e desktop).

Os dados ficam em um arquivo `estoque.json`, então as duas versões enxergam sempre as mesmas informações.

## Funcionalidades

- Cadastro, edição e exclusão de produtos
- Entrada e saída de estoque (com bloqueio de saída maior que o saldo)
- Busca por nome/categoria e filtro por categoria
- Indicadores: produtos cadastrados, unidades em estoque, valor total e alertas de reposição
- Destaque visual para produtos com estoque baixo (amarelo) e esgotados (vermelho)
- Persistência em JSON com escrita atômica (evita arquivo corrompido)
- Endpoint de API: `GET /api/produtos`

## Estrutura do projeto

```
villot-imports/
├── estoque.py          # núcleo: regras de negócio + persistência JSON
├── desktop.py          # interface desktop (tkinter)
├── app.py              # interface web (Flask)
├── requirements.txt    # dependências
├── .gitignore
└── estoque.json        # criado automaticamente na primeira execução
```

## Requisitos

- Python 3.9 ou superior
- tkinter (já incluído no instalador oficial do Python para Windows e macOS; no Linux: `sudo apt install python3-tk`)
- Flask (apenas para a versão web)

## Instalação

```bash
git clone https://github.com/SEU_USUARIO/villot-imports.git
cd villot-imports

# opcional: ambiente virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/macOS

pip install -r requirements.txt
```

## Como executar

**Versão desktop**

```bash
python desktop.py
```

**Versão web**

```bash
python app.py
```

Depois acesse <http://127.0.0.1:5000>.

> Na primeira execução, o sistema cria o `estoque.json` com produtos de exemplo.

## Modelo de dados

Os produtos são mantidos como uma **lista de dicionários**:

```json
{
  "id": 1,
  "nome": "Teclado Mecânico",
  "categoria": "Periféricos",
  "quantidade": 24,
  "minimo": 10,
  "preco": 249.9,
  "atualizado": "16/11/2026 10:30"
}
```

Situação do produto:

| Situação | Regra |
|----------|-------|
| `ok` | quantidade acima do mínimo |
| `baixo` | quantidade maior que 0 e menor ou igual ao mínimo |
| `zerado` | quantidade igual a 0 |

## Funções do núcleo (`estoque.py`)

| Função | Descrição |
|--------|-----------|
| `carregar_dados()` | Lê o JSON; se não existir ou estiver inválido, cria dados de exemplo |
| `salvar_dados(produtos)` | Grava a lista no JSON (escrita atômica) |
| `validar_produto(...)` | Valida e normaliza os campos; levanta `ValueError` com mensagem clara |
| `proximo_id(produtos)` | Calcula o próximo ID disponível |
| `adicionar_produto(produtos, dados)` | Insere um novo produto |
| `atualizar_produto(produtos, pid, dados)` | Altera um produto existente |
| `remover_produto(produtos, pid)` | Remove um produto |
| `movimentar_estoque(produtos, pid, tipo, qtd)` | Registra entrada (`entrada`) ou saída (`saida`) |
| `status_produto(p)` | Retorna `ok`, `baixo` ou `zerado` |
| `buscar_produtos(produtos, termo, categoria)` | Filtra por texto e categoria |
| `calcular_resumo(produtos)` | Calcula os indicadores do painel |
| `formatar_moeda(valor)` | Formata em reais (R$ 1.234,56) |

## Validação de entrada

A validação usa `try/except` e é feita em `validar_produto` e `movimentar_estoque`:

- Nome é obrigatório
- Quantidade e estoque mínimo devem ser inteiros
- Preço aceita vírgula ou ponto (ex.: `49,90`)
- Valores negativos são recusados
- Saída maior que o saldo disponível é bloqueada

Na versão desktop, os erros aparecem em caixas de diálogo; na web, como mensagens no topo da página.

## Rotas da versão web

| Método | Rota | Ação |
|--------|------|------|
| GET | `/` | Painel com indicadores, busca e tabela |
| POST | `/salvar` | Cria ou atualiza um produto |
| POST | `/mov/<id>` | Registra entrada ou saída |
| POST | `/excluir/<id>` | Exclui um produto |
| GET | `/api/produtos` | Lista os produtos em JSON |

## Configuração para produção

- Defina a chave secreta por variável de ambiente: `SECRET_KEY`.
- Em `app.py`, troque `app.run(debug=True)` por `app.run(debug=False)` ou use um servidor WSGI como o Gunicorn.
- O `estoque.json` está no `.gitignore` para não publicar dados reais do estoque.

## Publicando no GitHub

```bash
git init                      # pule se a pasta já for um repositório
git add .
git commit -m "Villot Imports: sistema de gestão de estoque"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/villot-imports.git
git push -u origin main
```

Antes, crie um repositório vazio em <https://github.com/new> com o nome `villot-imports`.

## Licença

Defina a licença do projeto (por exemplo, MIT) adicionando um arquivo `LICENSE`.
