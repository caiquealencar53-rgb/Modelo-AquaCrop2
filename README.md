# 🌾 SertãoCrop Simulador

Interface gráfica **inteiramente em português**, autoexplicativa, para simular a
produtividade de culturas agrícolas usando o modelo científico **AquaCrop-OSPy**
(a implementação em Python do modelo AquaCrop da FAO — a mesma base usada no
projeto SertãoCrop).

## O que a ferramenta faz

- Simula, dia a dia, o crescimento de uma cultura e o balanço de água no solo.
- Estima a **produtividade final (t/ha)**, a **produtividade potencial sem
  estresse hídrico** e a **perda de produtividade causada pela falta de água**.
- Permite comparar cenários de **sequeiro** (só chuva) e **irrigado**.
- Mostra gráficos da evolução da cobertura do dossel, biomassa e raízes ao
  longo do ciclo.
- Exporta os resultados em **CSV** para uso em relatórios, planilhas ou artigos.

Toda a interface — rótulos, opções de menu, mensagens e resultados — está
traduzida para o português, para que qualquer pessoa consiga usar sem precisar
programar ou entender inglês técnico.

## Como instalar e rodar

### 1. Pré-requisitos
- Python 3.10 ou superior instalado no computador.

### 2. Instalar as dependências

Abra um terminal na pasta do projeto e rode:

```bash
pip install -r requirements.txt
```

### 3. Rodar o aplicativo

```bash
streamlit run app.py
```

O navegador abrirá automaticamente em `http://localhost:8501` com a interface
gráfica. Se não abrir sozinho, copie esse endereço e cole no navegador.

## Como usar a interface

A barra lateral (à esquerda) tem 5 blocos de configuração, na ordem em que
devem ser preenchidos:

1. **Dados climáticos** — use os dados de exemplo para testar, ou envie um
   arquivo próprio (veja o modelo em `dados_exemplo/modelo_clima.txt`).
2. **Cultura e plantio** — escolha a cultura (sorgo, milho, feijão etc.) e a
   data de plantio.
3. **Solo e água inicial** — tipo de solo e quão úmido ele está no início.
4. **Irrigação** — sequeiro (só chuva) ou irrigação automática por limite de
   umidade do solo.
5. **Período da simulação** — ano de início e término.

Depois é só clicar em **▶️ Rodar simulação**. Os resultados aparecem na área
principal, em três abas: resumo da safra, gráficos de evolução do ciclo, e
download dos dados.

## Formato do arquivo climático próprio

Arquivo `.txt` ou `.csv` separado por tabulação/espaço, com estas colunas
exatas (veja `dados_exemplo/modelo_clima.txt`):

```
Day  Month  Year  Tmin(C)  Tmax(C)  Prcp(mm)  Et0(mm)
```

- `Tmin(C)` / `Tmax(C)`: temperaturas mínima e máxima do dia, em °C.
- `Prcp(mm)`: precipitação (chuva) do dia, em mm.
- `Et0(mm)`: evapotranspiração de referência do dia, em mm (pode ser obtida
  de estações meteorológicas do INMET ou calculada pelo método de
  Penman-Monteith/Hargreaves).

## Observação sobre o milheto

O AquaCrop-OSPy, na versão usada aqui, ainda não traz parâmetros próprios
para o **milheto**. Por enquanto a interface usa o **sorgo** como cultura
equivalente mais próxima para o Semiárido. Para uma futura versão do
SertãoCrop, é possível cadastrar parâmetros de cultura customizados
(`Crop("custom", ...)`) com os coeficientes específicos do milheto.

## Estrutura do projeto

```
sertaocrop_app/
├── app.py                       # aplicativo principal (interface + lógica)
├── requirements.txt             # dependências Python
├── dados_exemplo/
│   └── modelo_clima.txt         # modelo de arquivo climático para preencher
└── README.md
```

## Créditos

Construído sobre o **AquaCrop-OSPy**
(https://github.com/aquacropos/aquacrop), desenvolvido pela Universidade de
Manchester em colaboração com a FAO, licenciado sob Apache 2.0.
# Modelo-AquaCrop
