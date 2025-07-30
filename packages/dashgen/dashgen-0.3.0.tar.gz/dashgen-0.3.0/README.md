
# Dashgen

📊 Gere **dashboards visuais como imagens (PNG)** diretamente do Python com HTML, Tailwind CSS e Chart.js.

---

## ✨ O que é?

`dashgen` é um micro-framework que permite criar dashboards dinâmicos e exportá-los como imagens de alta qualidade.

Ideal para gerar relatórios diários, KPIs, resumos visuais e compartilhar automaticamente via e-mail, WhatsApp, sistemas internos etc.

---

## 🛠 Instalação

```bash
pip install dashgen
playwright install
```

---

## 🚀 Exemplo Completo

```python
from dashgen import (
    Dashboard,
    Row,
    Column,
    Text,
    Image,
    ProgressBar,
    Chart,
    Table,
)

# Criar o dashboard com altura automática, título estilizado e tema
db = Dashboard(
    title="📊 Relatório de Desempenho Comercial",
    title_style="text-3xl font-bold text-emerald-700",
    logo_path="logo.png",
    size=(1080, None),
    auto_size=True,
    theme={
        "primary": "#0f766e",
        "accent": "#22d3ee",
        "bg": "#f0fdfa",
        "text": "#082f49"
    }
)

# Linha com dois cards
db.add(Row(
    Column(6).add_card("Receita Acumulada", 9000000, 10000000),
    Column(6).add_card("Unidades Vendidas", 430, 500)
))

# Linha com tabela e gráfico de barras
dados = [
    {"Nome": "Projeto A", "Meta": "R$ 3M", "Realizado": "R$ 2.4M", "Variação": "-20%"},
    {"Nome": "Projeto B", "Meta": "R$ 5M", "Realizado": "R$ 5.2M", "Variação": "+4%"}
]

db.add(Row(
    Column(6).add_table("Desempenho por Projeto", dados, ["Nome", "Meta", "Realizado", "Variação"]),
    Column(6).add_chart(
        "bar",
        "Vendas por Mês",
        [
            {"label": "Jan", "value": 120},
            {"label": "Fev", "value": 135},
            {"label": "Mar", "value": 160},
            {"label": "Abr", "value": 110},
            {"label": "Mai", "value": 190}
        ],
        options={
            "height": 300,
            "show_data_labels": True,
            "data_label_color": "#ef4444",
            "data_label_format": "value + ' unidades'",
            "show_legend": False,
            "show_x_axis": True,
            "show_y_axis": True,
            "autosize_x": True,
            "bar_color": "#0f766e"
        }
    )
))

# Linha com gráfico de linha (largura total)
db.add(Row(
    Column(12).add_chart(
        "line",
        "Receita Total (R$)",
        [
            {"label": "Jan", "value": 1200000},
            {"label": "Fev", "value": 1450000},
            {"label": "Mar", "value": 1600000},
            {"label": "Abr", "value": 1800000},
            {"label": "Mai", "value": 2100000}
        ],
        options={
            "height": 460,
            "show_legend": False,
            "show_x_axis": True,
            "show_y_axis": True,
            "autosize_x": True,
            "tension": 0.4,
            "fill": False,
            "border_color": "#22d3ee"
        }
    )
))

# Gerar imagem
db.generate("output_dashboard.png")
print("✅ Dashboard gerado com sucesso!")

```
Mais scripts de exemplo podem ser encontrados em `examples/`.

---

## 🧱 Componentes Disponíveis

### 📐 Layout

* `Row(..., align={...}, margin="...", padding="...")`
* `Column(width=..., order=..., breakpoints={...}, align={...})`

### 🌿 Elementos Declarativos

* `Box(content, style={...})`
* `Text(text, style={...})`
* `Image(path, style={...})`
* `ProgressBar(percent, style={...})`
* `Chart(type, title, data, options={...})`
* `Table(title, data, headers, progress_columns=None)`

Exemplo com breakpoints e ordem customizada:

```python
Row(
    Column(6, breakpoints={"md": 4}, order=2).add_text("A"),
    Column(6, breakpoints={"md": 8}, order=1).add_text("B"),
    align={"horizontal": "center"},
    margin="my-4"
)
```

### 📦 Card (KPI)

```python
Column(6).add_card("Título", valor, meta, style={ ... })
```

Suporta personalização com:

* `title_color`, `title_size`, `text_size`
* `bar_color`, `card_class`

### 📊 Tabela

```python
Column(6).add_table("Título", data, headers)
```

* `data`: lista de dicionários
* `headers`: nomes das colunas a exibir

### 📈 Gráfico (Chart.js)

```python
Column(6).add_chart("bar" ou "line" ou "pie" ou "scatter", "Título", data, options={...})
```

* `data`: lista com `label` e `value` (ou `x`/`y` para `scatter`)
* `options`:

  * `height`: altura do canvas
  * `fill`: preencher área sob a linha
  * `tension`: suavidade das curvas
  * `autosize_x` / `autosize_y`: expandir horizontal/vertical
  * `show_legend`: mostrar legenda
  * `show_x_axis` / `show_y_axis`: mostrar eixos
  * `show_data_labels`: mostrar valores sobre as barras
  * `data_label_color`: cor dos rótulos
  * `data_label_font`: fonte dos rótulos (dict Chart.js)
  * `data_label_anchor`: posição do rótulo
  * `data_label_format`: função/expressão para formatar o valor

Exemplos rápidos:

```python
Column(6).add_chart("bar", "Vendas", [{"label": "A", "value": 10}])
Column(6).add_chart("line", "Tendência", [{"label": "A", "value": 5}])
Column(6).add_chart("pie", "Participação", [
    {"label": "A", "value": 30, "color": "#ff0000"},
    {"label": "B", "value": 70, "color": "#00ff00"}
])
Column(6).add_chart("scatter", "Correlação", [
    {"x": 1, "y": 2},
    {"x": 2, "y": 3}
])
```

#### 🎯 Data Labels Personalizados

O template base já carrega automaticamente o plugin `chartjs-plugin-datalabels`,
permitindo exibir e estilizar rótulos sobre as barras ou pontos.

* `data_label_color` – cor do texto
* `data_label_font` – fonte dos rótulos (dict Chart.js)
* `data_label_anchor` – posição do rótulo (`start`, `center`, `end`)
* `data_label_format` – expressão ou função para formatar o valor

Exemplo rápido de formatação customizada:

```python
from dashgen import Dashboard, Row, Column

db = Dashboard(title="Labels", size=(600, 300))

dados = [
    {"label": "Jan", "value": 15000},
    {"label": "Fev", "value": 22000},
]

db.add(
    Row(
        Column(12).add_chart(
            "bar",
            "Receita",
            dados,
            options={
                "show_data_labels": True,
                "data_label_color": "#16a34a",
                "data_label_anchor": "end",
                "data_label_font": {"size": 12, "weight": "bold"},
                "data_label_format": "'R$ ' + value.toFixed(2)",
            },
        )
    )
)

db.generate("custom_label_format.png")
```

Veja o script completo em `examples/custom_label_format.py`.


## 🌱 API Declarativa

Componha diretamente elementos de forma simples:

```python
from dashgen import Dashboard, Row, Column, Text, Image, ProgressBar

db = Dashboard(title="Demo")
db.add(
    Row(
        Column(6, Text("Progresso"), ProgressBar(75)),
        Column(6, Image("logo.png", style={"width": "80px"})),
    )
)
db.generate("demo.png")
```

---

## 🎨 Tema Personalizado

```python
theme = {
    "primary": "#005f73",  # Barras e títulos
    "accent": "#94d2bd",   # Detalhes
    "bg": "#fefae0",       # Fundo da imagem
    "text": "#001219"      # Cor do texto
}
```

### ♻️ Temas Reutilizáveis

```python
db.save_theme("tema.json")
novo = Dashboard()
novo.load_theme("tema.json")
```

## 📄 Múltiplas Páginas

Finalize uma página com `generate_page()` e depois informe uma lista de
caminhos para `generate`:

```python
db.generate_page()
db.add(Row(Column(12).add_text("Segunda página")))
db.generate(["pagina1.png", "pagina2.png"])
```

---

## 🧠 Funcionalidades Especiais

* `auto_size=True`: ajusta altura da imagem com base no conteúdo
* Layout com alinhamento e breakpoints
* Componentes `Box`, `Text`, `Image` e `ProgressBar`
* Gráficos `bar`, `line`, `pie` e `scatter` via Chart.js
* Responsivo com Tailwind e rótulos (`chartjs-plugin-datalabels`)
* Estilização por componente (`style`, `options`)

---

## 📚 API Referência

### 📘 `Dashboard(...)`

| Parâmetro   | Tipo             | Descrição                   |
| ----------- | ---------------- | --------------------------- |
| `title`     | `str`            | Título do dashboard         |
| `logo_path` | `str` (opcional) | Caminho da logo             |
| `size`      | `(int, int)`     | Tamanho fixo da imagem      |
| `auto_size` | `bool`           | Ajuste automático de altura |
| `theme`     | `dict`           | Cores do tema               |

---

## ✅ Requisitos

* Python 3.7+
* `playwright`
* `jinja2`

```bash
pip install dashgen
playwright install
```

---

## 🖼 Gere imagens de dashboards com visual moderno, responsivo e exportável – em uma linha de código.

