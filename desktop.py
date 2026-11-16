"""Villot Imports — versão desktop (tkinter). Execute: python desktop.py"""
import tkinter as tk
from tkinter import ttk, messagebox

import estoque as eq

COR = {
    "bg": "#eef2f6", "card": "#ffffff", "campo": "#f1f5f9", "tinta": "#12263a",
    "sub": "#64748b", "borda": "#d9e1ea", "laranja": "#f26a1b",
    "verde": "#17a673", "verm": "#d64545", "amar": "#e8a317", "azul": "#2f6fdb",
}
FONTE = "Segoe UI"


def clarear(hexcor, f=0.15):
    r, g, b = (int(hexcor[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % tuple(int(c + (255 - c) * f) for c in (r, g, b))


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Villot Imports — Gestão de Estoque")
        self.geometry("1200x740")
        self.minsize(780, 660)
        self.configure(bg=COR["bg"])
        self.produtos = eq.carregar_dados()
        self.selecionado = None
        self._estreito = None

        self.v_busca = tk.StringVar()
        self.v_cat = tk.StringVar(value="Todas")
        self.v_nome, self.v_cat_f = tk.StringVar(), tk.StringVar()
        self.v_qtd, self.v_preco, self.v_min = tk.StringVar(), tk.StringVar(), tk.StringVar()
        self.v_mov = tk.StringVar(value="1")

        self._estilos()
        self._montar()
        self.v_busca.trace_add("write", lambda *_: self.atualizar())
        self.v_cat.trace_add("write", lambda *_: self.atualizar())
        self.bind("<Configure>", self._responsivo)
        self.atualizar()

    # ------------------------------------------------------------ estilos / widgets
    def _estilos(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("Treeview", background=COR["card"], fieldbackground=COR["card"],
                    foreground=COR["tinta"], rowheight=34, borderwidth=0, font=(FONTE, 10))
        s.configure("Treeview.Heading", background=COR["tinta"], foreground="white",
                    font=(FONTE, 10, "bold"), relief="flat", padding=8)
        s.map("Treeview", background=[("selected", "#ffe2d1")],
              foreground=[("selected", COR["tinta"])])
        s.map("Treeview.Heading", background=[("active", COR["tinta"])])
        s.configure("Vertical.TScrollbar", background=COR["borda"], troughcolor=COR["card"],
                    bordercolor=COR["card"], arrowcolor=COR["sub"], relief="flat")
        s.configure("TCombobox", fieldbackground=COR["campo"], background=COR["campo"],
                    foreground=COR["tinta"], bordercolor=COR["borda"], padding=6)

    def _botao(self, pai, texto, cmd, cor):
        b = tk.Button(pai, text=texto, command=cmd, bg=cor, fg="white",
                      activebackground=clarear(cor), activeforeground="white",
                      relief="flat", bd=0, cursor="hand2", padx=14, pady=8,
                      font=(FONTE, 10, "bold"))
        b.bind("<Enter>", lambda e: b.config(bg=clarear(cor)))
        b.bind("<Leave>", lambda e: b.config(bg=cor))
        return b

    def _entrada(self, pai, var):
        return tk.Entry(pai, textvariable=var, bg=COR["campo"], fg=COR["tinta"],
                        insertbackground=COR["tinta"], relief="flat", font=(FONTE, 11),
                        highlightthickness=1, highlightbackground=COR["borda"],
                        highlightcolor=COR["laranja"])

    def _kpi(self, pai, titulo, cor):
        f = tk.Frame(pai, bg=COR["card"], highlightthickness=1, highlightbackground=COR["borda"])
        tk.Frame(f, bg=cor, width=6).pack(side="left", fill="y")
        corpo = tk.Frame(f, bg=COR["card"])
        corpo.pack(side="left", fill="both", expand=True, padx=14, pady=10)
        tk.Label(corpo, text=titulo, bg=COR["card"], fg=COR["sub"],
                 font=(FONTE, 9)).pack(anchor="w")
        val = tk.Label(corpo, text="0", bg=COR["card"], fg=COR["tinta"],
                       font=(FONTE, 20, "bold"))
        val.pack(anchor="w")
        return f, val

    # ------------------------------------------------------------ layout
    def _montar(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        topo = tk.Frame(self, bg=COR["tinta"])
        topo.grid(row=0, column=0, sticky="ew")
        tk.Label(topo, text="Villot Imports", bg=COR["tinta"], fg="white",
                 font=(FONTE, 18, "bold")).pack(side="left", padx=(24, 8), pady=14)
        tk.Label(topo, text="controle de estoque", bg=COR["tinta"], fg="#9fb3c8",
                 font=(FONTE, 10)).pack(side="left", pady=(8, 0))
        tk.Frame(self, bg=COR["laranja"], height=4).grid(row=0, column=0, sticky="sew")

        self.kpis = tk.Frame(self, bg=COR["bg"])
        self.kpis.grid(row=1, column=0, sticky="ew", padx=24, pady=(20, 12))
        self.cards = []
        for titulo, cor in [("Produtos cadastrados", COR["azul"]),
                            ("Unidades em estoque", COR["verde"]),
                            ("Valor em estoque", COR["laranja"]),
                            ("Alertas de reposição", COR["verm"])]:
            card, lbl = self._kpi(self.kpis, titulo, cor)
            self.cards.append((card, lbl))

        self.corpo = tk.Frame(self, bg=COR["bg"])
        self.corpo.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 20))

        # --- painel da tabela
        self.tabela_box = tk.Frame(self.corpo, bg=COR["card"], highlightthickness=1,
                                   highlightbackground=COR["borda"])
        self.tabela_box.rowconfigure(1, weight=1)
        self.tabela_box.columnconfigure(0, weight=1)

        barra = tk.Frame(self.tabela_box, bg=COR["card"])
        barra.grid(row=0, column=0, columnspan=2, sticky="ew", padx=14, pady=12)
        barra.columnconfigure(0, weight=1)
        busca = self._entrada(barra, self.v_busca)
        busca.grid(row=0, column=0, sticky="ew", ipady=6)
        self.combo_filtro = ttk.Combobox(barra, textvariable=self.v_cat, state="readonly",
                                         width=16, font=(FONTE, 10))
        self.combo_filtro.grid(row=0, column=1, padx=(10, 0), ipady=3)
        tk.Label(barra, text="Busque por nome ou categoria", bg=COR["card"], fg=COR["sub"],
                 font=(FONTE, 8)).grid(row=1, column=0, sticky="w", pady=(2, 0))

        cols = ("id", "nome", "cat", "qtd", "min", "preco", "total")
        self.tree = ttk.Treeview(self.tabela_box, columns=cols, show="headings",
                                 selectmode="browse")
        for c, t, w, anc in [("id", "#", 44, "center"), ("nome", "Produto", 220, "w"),
                             ("cat", "Categoria", 130, "w"), ("qtd", "Qtd.", 70, "center"),
                             ("min", "Mín.", 60, "center"), ("preco", "Preço", 100, "e"),
                             ("total", "Total", 110, "e")]:
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w, anchor=anc, stretch=(c == "nome"))
        self.tree.tag_configure("baixo", foreground="#a86a00", background="#fff6e0")
        self.tree.tag_configure("zerado", foreground="#b42a2a", background="#fde8e8")
        self.tree.grid(row=1, column=0, sticky="nsew", padx=(14, 0), pady=(0, 14))
        sb = ttk.Scrollbar(self.tabela_box, orient="vertical", command=self.tree.yview)
        sb.grid(row=1, column=1, sticky="ns", padx=(0, 14), pady=(0, 14))
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.bind("<<TreeviewSelect>>", self._ao_selecionar)

        # --- painel do formulário
        self.form_box = tk.Frame(self.corpo, bg=COR["card"], highlightthickness=1,
                                 highlightbackground=COR["borda"])
        f = self.form_box
        f.columnconfigure((0, 1), weight=1, uniform="c")
        self.lbl_form = tk.Label(f, text="Novo produto", bg=COR["card"], fg=COR["tinta"],
                                 font=(FONTE, 14, "bold"))
        self.lbl_form.grid(row=0, column=0, columnspan=2, sticky="w", padx=16, pady=(14, 8))

        def campo(r, c, rotulo, var, span=1):
            tk.Label(f, text=rotulo, bg=COR["card"], fg=COR["sub"],
                     font=(FONTE, 9)).grid(row=r, column=c, columnspan=span, sticky="w",
                                           padx=16, pady=(6, 0))
            self._entrada(f, var).grid(row=r + 1, column=c, columnspan=span, sticky="ew",
                                       padx=16, ipady=5)

        campo(1, 0, "Nome do produto", self.v_nome, 2)
        tk.Label(f, text="Categoria", bg=COR["card"], fg=COR["sub"],
                 font=(FONTE, 9)).grid(row=3, column=0, columnspan=2, sticky="w", padx=16, pady=(6, 0))
        self.combo_cat = ttk.Combobox(f, textvariable=self.v_cat_f, font=(FONTE, 11))
        self.combo_cat.grid(row=4, column=0, columnspan=2, sticky="ew", padx=16, ipady=3)
        campo(5, 0, "Quantidade", self.v_qtd)
        campo(5, 1, "Estoque mínimo", self.v_min)
        campo(7, 0, "Preço unitário (R$)", self.v_preco, 2)

        acoes = tk.Frame(f, bg=COR["card"])
        acoes.grid(row=9, column=0, columnspan=2, sticky="ew", padx=16, pady=14)
        acoes.columnconfigure((0, 1, 2), weight=1)
        self.btn_salvar = self._botao(acoes, "Adicionar", self.salvar, COR["laranja"])
        self.btn_salvar.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        self._botao(acoes, "Limpar", self.limpar, COR["sub"]).grid(row=0, column=1, sticky="ew", padx=4)
        self._botao(acoes, "Excluir", self.excluir, COR["verm"]).grid(row=0, column=2, sticky="ew", padx=(4, 0))

        tk.Frame(f, bg=COR["borda"], height=1).grid(row=10, column=0, columnspan=2,
                                                     sticky="ew", padx=16)
        tk.Label(f, text="Movimentar estoque", bg=COR["card"], fg=COR["tinta"],
                 font=(FONTE, 11, "bold")).grid(row=11, column=0, columnspan=2, sticky="w",
                                                padx=16, pady=(12, 4))
        mov = tk.Frame(f, bg=COR["card"])
        mov.grid(row=12, column=0, columnspan=2, sticky="ew", padx=16, pady=(0, 16))
        mov.columnconfigure((1, 2), weight=1)
        e = self._entrada(mov, self.v_mov)
        e.config(width=6, justify="center")
        e.grid(row=0, column=0, ipady=5, padx=(0, 8))
        self._botao(mov, "+ Entrada", lambda: self.movimentar("entrada"),
                    COR["verde"]).grid(row=0, column=1, sticky="ew", padx=4)
        self._botao(mov, "− Saída", lambda: self.movimentar("saida"),
                    COR["azul"]).grid(row=0, column=2, sticky="ew", padx=(4, 0))

    # ------------------------------------------------------------ responsividade
    def _responsivo(self, ev):
        if ev.widget is not self:
            return
        estreito = ev.width < 980
        if estreito != self._estreito:
            self._estreito = estreito
            self._posicionar()

    def _posicionar(self):
        for w in (*[c for c, _ in self.cards], self.tabela_box, self.form_box):
            w.grid_forget()
        for i in range(4):
            self.kpis.columnconfigure(i, weight=0, uniform="")
        for i in range(2):
            self.corpo.columnconfigure(i, weight=0)
            self.corpo.rowconfigure(i, weight=0)

        if self._estreito:
            for i, (c, _) in enumerate(self.cards):
                c.grid(row=i // 2, column=i % 2, sticky="ew", padx=4, pady=4)
            self.kpis.columnconfigure((0, 1), weight=1, uniform="k")
            self.tabela_box.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
            self.form_box.grid(row=1, column=0, sticky="nsew")
            self.corpo.columnconfigure(0, weight=1)
            self.corpo.rowconfigure(0, weight=1)
        else:
            for i, (c, _) in enumerate(self.cards):
                c.grid(row=0, column=i, sticky="ew", padx=6)
            self.kpis.columnconfigure((0, 1, 2, 3), weight=1, uniform="k")
            self.tabela_box.grid(row=0, column=0, sticky="nsew")
            self.form_box.grid(row=0, column=1, sticky="ns", padx=(14, 0))
            self.corpo.columnconfigure(0, weight=1)
            self.corpo.rowconfigure(0, weight=1)

    # ------------------------------------------------------------ dados na tela
    def atualizar(self):
        cat = "" if self.v_cat.get() == "Todas" else self.v_cat.get()
        lista = eq.buscar_produtos(self.produtos, self.v_busca.get(), cat)
        self.tree.delete(*self.tree.get_children())
        for p in lista:
            st = eq.status_produto(p)
            self.tree.insert("", "end", iid=str(p["id"]),
                             values=(p["id"], p["nome"], p["categoria"], p["quantidade"],
                                     p["minimo"], eq.formatar_moeda(p["preco"]),
                                     eq.formatar_moeda(p["preco"] * p["quantidade"])),
                             tags=(st,) if st != "ok" else ())
        r = eq.calcular_resumo(self.produtos)
        for (_, lbl), txt in zip(self.cards, [r["produtos"], r["unidades"],
                                              eq.formatar_moeda(r["valor"]), r["alertas"]]):
            lbl.config(text=str(txt))
        cats = sorted({p["categoria"] for p in self.produtos})
        self.combo_filtro["values"] = ["Todas"] + cats
        self.combo_cat["values"] = cats

    def _ao_selecionar(self, _):
        sel = self.tree.selection()
        if not sel:
            return
        pid = int(sel[0])
        p = next((x for x in self.produtos if x["id"] == pid), None)
        if p:
            self.selecionado = pid
            self.v_nome.set(p["nome"]); self.v_cat_f.set(p["categoria"])
            self.v_qtd.set(p["quantidade"]); self.v_min.set(p["minimo"])
            self.v_preco.set(f"{p['preco']:.2f}".replace(".", ","))
            self.lbl_form.config(text=f"Editando #{pid}")
            self.btn_salvar.config(text="Salvar")

    # ------------------------------------------------------------ ações
    def _persistir(self):
        try:
            eq.salvar_dados(self.produtos)
        except ValueError as e:
            messagebox.showerror("Erro ao salvar", str(e))
        self.atualizar()

    def salvar(self):
        try:
            dados = eq.validar_produto(self.v_nome.get(), self.v_cat_f.get(), self.v_qtd.get(),
                                       self.v_preco.get(), self.v_min.get())
            if self.selecionado:
                eq.atualizar_produto(self.produtos, self.selecionado, dados)
            else:
                eq.adicionar_produto(self.produtos, dados)
        except ValueError as e:
            messagebox.showwarning("Verifique os dados", str(e))
            return
        self._persistir()
        self.limpar()

    def excluir(self):
        if not self.selecionado:
            messagebox.showinfo("Excluir", "Selecione um produto na tabela.")
            return
        if messagebox.askyesno("Excluir produto", "Deseja excluir este produto?"):
            try:
                eq.remover_produto(self.produtos, self.selecionado)
            except ValueError as e:
                messagebox.showwarning("Erro", str(e))
                return
            self._persistir()
            self.limpar()

    def movimentar(self, tipo):
        if not self.selecionado:
            messagebox.showinfo("Movimentar", "Selecione um produto na tabela.")
            return
        try:
            eq.movimentar_estoque(self.produtos, self.selecionado, tipo, self.v_mov.get())
        except ValueError as e:
            messagebox.showwarning("Movimentação inválida", str(e))
            return
        pid = self.selecionado
        self._persistir()
        self.tree.selection_set(str(pid))

    def limpar(self):
        self.selecionado = None
        for v in (self.v_nome, self.v_cat_f, self.v_qtd, self.v_min, self.v_preco):
            v.set("")
        self.v_mov.set("1")
        self.lbl_form.config(text="Novo produto")
        self.btn_salvar.config(text="Adicionar")
        self.tree.selection_remove(self.tree.selection())


if __name__ == "__main__":
    App().mainloop()