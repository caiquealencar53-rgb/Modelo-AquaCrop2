# -*- coding: utf-8 -*-
"""
SertãoCrop Simulador
Interface gráfica em português para simulação de produtividade agrícola
com o modelo AquaCrop-OSPy, voltada para culturas do Semiárido brasileiro.
"""

import io
import datetime as dt

import pandas as pd
import streamlit as st

from aquacrop import AquaCropModel, Soil, Crop, InitialWaterContent, IrrigationManagement
from aquacrop.utils import prepare_weather, get_filepath

# --------------------------------------------------------------------------------------
# CONFIGURAÇÃO GERAL DA PÁGINA
# --------------------------------------------------------------------------------------
st.set_page_config(
    page_title="SertãoCrop Simulador",
    page_icon="🌾",
    layout="wide",
)

# --------------------------------------------------------------------------------------
# DICIONÁRIOS DE TRADUÇÃO / OPÇÕES (tudo em português para o usuário)
# --------------------------------------------------------------------------------------

CULTURAS = {
    "Sorgo": "Sorghum",
    "Milho": "Maize",
    "Trigo": "Wheat",
    "Feijão (Dry Bean)": "DryBean",
    "Arroz (sequeiro/inundado)": "PaddyRice",
    "Batata": "Potato",
    "Soja": "Soybean",
    "Algodão": "Cotton",
    "Girassol": "Sunflower",
    "Tomate": "Tomato",
    "Quinoa": "Quinoa",
    "Cevada": "Barley",
    "Cana-de-açúcar": "SugarCane",
    "Beterraba açucareira": "SugarBeet",
    "Mandioca": "Cassava",
    "Alfafa": "AlfalfaGDD",
}

SOLOS = {
    "Argila (Clay)": "Clay",
    "Franco-argiloso (ClayLoam)": "ClayLoam",
    "Padrão (Default)": "Default",
    "Franco (Loam)": "Loam",
    "Areia-franca (LoamySand)": "LoamySand",
    "Arenoso (Sand)": "Sand",
    "Areia-argilosa (SandyClay)": "SandyClay",
    "Franco-argilo-arenoso (SandyClayLoam)": "SandyClayLoam",
    "Franco-arenoso (SandyLoam)": "SandyLoam",
    "Silte (Silt)": "Silt",
    "Silte-argilo-franco (SiltClayLoam)": "SiltClayLoam",
    "Silte-franco (SiltLoam)": "SiltLoam",
    "Silte-argiloso (SiltClay)": "SiltClay",
    "Várzea / arroz inundado (Paddy)": "Paddy",
}

UMIDADE_INICIAL = {
    "Capacidade de campo (solo úmido, recomendado)": "FC",
    "Ponto de murcha permanente (solo bem seco)": "WP",
    "Saturação (solo encharcado)": "SAT",
}

MODO_IRRIGACAO = {
    "Sequeiro (sem irrigação, depende só da chuva)": 0,
    "Irrigação automática por limite de umidade do solo": 1,
}

MESES_PT = {
    1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril", 5: "maio", 6: "junho",
    7: "julho", 8: "agosto", 9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro",
}

COLUNAS_RESULTADO_PT = {
    "Season": "Safra (nº)",
    "crop Type": "Cultura",
    "Harvest Date (YYYY/MM/DD)": "Data da colheita",
    "Harvest Date (Step)": "Dia da colheita (nº de dias)",
    "Dry yield (tonne/ha)": "Produtividade em grão seco (t/ha)",
    "Fresh yield (tonne/ha)": "Produtividade em massa fresca (t/ha)",
    "Yield potential (tonne/ha)": "Produtividade potencial, sem estresse (t/ha)",
    "Seasonal irrigation (mm)": "Irrigação total na safra (mm)",
}

COLUNAS_CRESCIMENTO_PT = {
    "dap": "Dias após plantio",
    "canopy_cover": "Cobertura do dossel (%)",
    "biomass": "Biomassa acumulada (ton/ha)",
    "z_root": "Profundidade das raízes (m)",
    "DryYield": "Produtividade em grão seco acumulada (t/ha)",
}

# --------------------------------------------------------------------------------------
# FUNÇÕES AUXILIARES
# --------------------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def carregar_clima_exemplo():
    """Carrega o arquivo climático de exemplo (Tunis) que acompanha o AquaCrop."""
    caminho = get_filepath("tunis_climate.txt")
    return prepare_weather(caminho)


def validar_arquivo_clima(df: pd.DataFrame) -> list:
    """Confere se o arquivo enviado pelo usuário tem as colunas exigidas."""
    colunas_esperadas = {"Day", "Month", "Year", "Tmin(C)", "Tmax(C)", "Prcp(mm)", "Et0(mm)"}
    faltando = colunas_esperadas - set(df.columns)
    return sorted(faltando)


def rodar_simulacao(weather_df, nome_cultura_en, data_plantio, data_colheita,
                     nome_solo_en, umidade_inicial_cod, data_inicio, data_fim,
                     modo_irrigacao_cod, lamina_irrigacao_mm, intervalo_dias,
                     limite_umidade_pct):
    """Monta e executa o modelo AquaCrop com os parâmetros escolhidos na interface."""

    cultura = Crop(nome_cultura_en, planting_date=data_plantio,
                    harvest_date=data_colheita if data_colheita else None)
    solo = Soil(nome_solo_en)
    agua_inicial = InitialWaterContent(value=[umidade_inicial_cod])

    if modo_irrigacao_cod == 0:
        # Sequeiro: sem irrigação, depende só da chuva
        manejo_irrigacao = IrrigationManagement(irrigation_method=0)
    else:
        # Irrigação automática: aplica água sempre que a umidade do solo
        # cair abaixo do limite escolhido pelo usuário (em % da água disponível)
        manejo_irrigacao = IrrigationManagement(
            irrigation_method=1,
            SMT=[limite_umidade_pct] * 4,
        )

    modelo = AquaCropModel(
        sim_start_time=data_inicio,
        sim_end_time=data_fim,
        weather_df=weather_df,
        soil=solo,
        crop=cultura,
        initial_water_content=agua_inicial,
        irrigation_management=manejo_irrigacao,
    )
    modelo.run_model(till_termination=True)
    return modelo


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    return buffer.getvalue().encode("utf-8")


# --------------------------------------------------------------------------------------
# CABEÇALHO
# --------------------------------------------------------------------------------------

st.title("🌾 SertãoCrop Simulador")
st.markdown(
    "Ferramenta de apoio à decisão para **simulação de produtividade agrícola**, "
    "baseada no modelo científico **AquaCrop-OSPy** (FAO). "
    "Ajuste os parâmetros no menu à esquerda e clique em **Rodar simulação**."
)

with st.expander("ℹ️ Como funciona esta ferramenta (clique para abrir)"):
    st.markdown(
        """
O **AquaCrop** é um modelo desenvolvido pela FAO que estima a produtividade de uma
cultura agrícola a partir de três grupos de informação:

1. **Clima** — chuva, temperatura e evapotranspiração ao longo do período simulado;
2. **Solo** — capacidade do solo de reter e disponibilizar água para as plantas;
3. **Cultura e manejo** — espécie plantada, data de plantio, umidade inicial do solo
   e se haverá ou não irrigação.

Com esses dados, o modelo simula **dia a dia** o balanço de água no solo e o
crescimento da planta, estimando ao final a **produtividade esperada (toneladas por
hectare)**.

Esta interface foi criada para facilitar o uso do AquaCrop por quem não é
programador — todos os termos técnicos aparecem traduzidos e explicados.
        """
    )

st.divider()

# --------------------------------------------------------------------------------------
# BARRA LATERAL — ENTRADA DE DADOS
# --------------------------------------------------------------------------------------

st.sidebar.header("⚙️ 1. Dados climáticos")

fonte_clima = st.sidebar.radio(
    "De onde vêm os dados de clima?",
    ["Usar dados de exemplo (Tunísia)", "Enviar meu próprio arquivo"],
    help="Os dados de exemplo servem para testar a ferramenta. Para resultados "
         "reais do Semiárido, envie um arquivo com o clima da sua região.",
)

weather_df = None
erro_clima = None

if fonte_clima == "Usar dados de exemplo (Tunísia)":
    weather_df = carregar_clima_exemplo()
    st.sidebar.success("Dados de exemplo carregados (1979–1985).")
else:
    st.sidebar.markdown(
        "Envie um arquivo **.txt** ou **.csv** separado por tabulação, com as colunas:\n"
        "`Day  Month  Year  Tmin(C)  Tmax(C)  Prcp(mm)  Et0(mm)`"
    )
    arquivo = st.sidebar.file_uploader("Arquivo climático", type=["txt", "csv"])
    if arquivo is not None:
        try:
            bruto = pd.read_csv(arquivo, sep=r"\s+|\t", engine="python")
            faltando = validar_arquivo_clima(bruto)
            if faltando:
                erro_clima = f"Faltam colunas no arquivo: {', '.join(faltando)}"
            else:
                arquivo.seek(0)
                weather_df = prepare_weather(arquivo)
                st.sidebar.success("Arquivo climático carregado com sucesso.")
        except Exception as e:
            erro_clima = f"Não foi possível ler o arquivo: {e}"

    if erro_clima:
        st.sidebar.error(erro_clima)

st.sidebar.divider()
st.sidebar.header("🌱 2. Cultura e plantio")

nome_cultura_pt = st.sidebar.selectbox("Cultura", list(CULTURAS.keys()), index=0)
nome_cultura_en = CULTURAS[nome_cultura_pt]

if nome_cultura_pt in ("Sorgo",):
    st.sidebar.caption(
        "⚠️ O milheto ainda não tem parâmetros próprios no AquaCrop-OSPy. "
        "Use o Sorgo como aproximação, ou ajuste parâmetros customizados em versões futuras."
    )

col_data1, col_data2 = st.sidebar.columns(2)
mes_plantio = col_data1.selectbox("Mês de plantio", list(range(1, 13)),
                                   format_func=lambda m: MESES_PT[m], index=5)
dia_plantio = col_data2.selectbox("Dia de plantio", list(range(1, 29)), index=0)
data_plantio_str = f"{mes_plantio:02d}/{dia_plantio:02d}"  # AquaCrop espera o formato MM/DD

st.sidebar.divider()
st.sidebar.header("🟤 3. Solo e água inicial")

nome_solo_pt = st.sidebar.selectbox("Tipo de solo", list(SOLOS.keys()), index=8)
nome_solo_en = SOLOS[nome_solo_pt]

umidade_pt = st.sidebar.selectbox("Umidade inicial do solo", list(UMIDADE_INICIAL.keys()), index=0)
umidade_cod = UMIDADE_INICIAL[umidade_pt]

st.sidebar.divider()
st.sidebar.header("💧 4. Irrigação")

irrigacao_pt = st.sidebar.selectbox("Modo de irrigação", list(MODO_IRRIGACAO.keys()), index=0)
irrigacao_cod = MODO_IRRIGACAO[irrigacao_pt]

limite_umidade_pct = 70
if irrigacao_cod != 0:
    limite_umidade_pct = st.sidebar.slider(
        "Irrigar quando a água disponível no solo cair abaixo de (%)",
        min_value=10, max_value=100, value=70, step=5,
        help="Quanto menor o valor, mais seco o solo fica antes de irrigar "
             "(economiza água, mas aumenta o risco de estresse hídrico).",
    )

st.sidebar.divider()
st.sidebar.header("📅 5. Período da simulação")

ano_inicio = st.sidebar.number_input("Ano de início", min_value=1901, max_value=2100, value=1979)
ano_fim = st.sidebar.number_input("Ano de término", min_value=1901, max_value=2100, value=1979)

data_inicio_str = f"{ano_inicio}/{mes_plantio:02d}/{dia_plantio:02d}"
data_fim_str = f"{ano_fim}/12/31"

st.sidebar.divider()
rodar = st.sidebar.button("▶️ Rodar simulação", type="primary", use_container_width=True)

# --------------------------------------------------------------------------------------
# ÁREA PRINCIPAL — RESULTADOS
# --------------------------------------------------------------------------------------

if rodar:
    if weather_df is None:
        st.error("⚠️ Não há dados climáticos válidos. Verifique o arquivo enviado na barra lateral.")
    else:
        with st.spinner("Rodando a simulação AquaCrop... isso pode levar alguns segundos."):
            try:
                modelo = rodar_simulacao(
                    weather_df=weather_df,
                    nome_cultura_en=nome_cultura_en,
                    data_plantio=data_plantio_str,
                    data_colheita=None,
                    nome_solo_en=nome_solo_en,
                    umidade_inicial_cod=umidade_cod,
                    data_inicio=data_inicio_str,
                    data_fim=data_fim_str,
                    modo_irrigacao_cod=irrigacao_cod,
                    lamina_irrigacao_mm=None,
                    intervalo_dias=None,
                    limite_umidade_pct=limite_umidade_pct,
                )
                resultados = modelo.get_simulation_results()
                crescimento = modelo.get_crop_growth()
            except Exception as e:
                st.error(
                    "❌ Ocorreu um erro ao rodar a simulação. Verifique se as datas e o "
                    f"período escolhido são compatíveis com os dados climáticos.\n\nDetalhe técnico: {e}"
                )
                resultados = None
                crescimento = None

        if resultados is not None and len(resultados) > 0:
            st.success("✅ Simulação concluída com sucesso!")

            linha = resultados.iloc[-1]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Produtividade (grão seco)", f"{linha['Dry yield (tonne/ha)']:.2f} t/ha")
            c2.metric("Produtividade potencial (sem estresse)", f"{linha['Yield potential (tonne/ha)']:.2f} t/ha")
            perda_pct = 0.0
            if linha["Yield potential (tonne/ha)"] > 0:
                perda_pct = 100 * (1 - linha["Dry yield (tonne/ha)"] / linha["Yield potential (tonne/ha)"])
            c3.metric("Perda por estresse hídrico", f"{perda_pct:.1f} %")
            c4.metric("Irrigação total aplicada", f"{linha['Seasonal irrigation (mm)']:.0f} mm")

            st.divider()

            aba1, aba2, aba3 = st.tabs([
                "📋 Resumo da(s) safra(s)", "📈 Evolução ao longo do ciclo", "⬇️ Baixar dados"
            ])

            with aba1:
                tabela_pt = resultados.rename(columns=COLUNAS_RESULTADO_PT)
                st.dataframe(tabela_pt, use_container_width=True)

            with aba2:
                if crescimento is not None and len(crescimento) > 0:
                    ultima_safra = crescimento[crescimento["dap"] >= 0].copy()

                    st.markdown("**Cobertura do dossel (%) ao longo do ciclo**")
                    st.line_chart(ultima_safra.set_index("dap")[["canopy_cover"]]
                                  .rename(columns={"canopy_cover": "Cobertura do dossel (%)"}))

                    st.markdown("**Biomassa acumulada (ton/ha) ao longo do ciclo**")
                    st.line_chart(ultima_safra.set_index("dap")[["biomass"]]
                                  .rename(columns={"biomass": "Biomassa (ton/ha)"}))

                    st.markdown("**Profundidade das raízes (m) ao longo do ciclo**")
                    st.line_chart(ultima_safra.set_index("dap")[["z_root"]]
                                  .rename(columns={"z_root": "Profundidade das raízes (m)"}))
                else:
                    st.info("Sem dados diários de crescimento para exibir.")

            with aba3:
                st.markdown("Baixe os resultados para usar em relatórios, planilhas ou no artigo.")
                st.download_button(
                    "⬇️ Baixar resumo da safra (CSV)",
                    data=to_csv_bytes(resultados.rename(columns=COLUNAS_RESULTADO_PT)),
                    file_name="sertaocrop_resumo_safra.csv",
                    mime="text/csv",
                )
                if crescimento is not None:
                    st.download_button(
                        "⬇️ Baixar evolução diária (CSV)",
                        data=to_csv_bytes(crescimento),
                        file_name="sertaocrop_evolucao_diaria.csv",
                        mime="text/csv",
                    )
else:
    st.info(
        "👈 Preencha os parâmetros na barra lateral e clique em **Rodar simulação** "
        "para ver os resultados aqui."
    )
    st.markdown("### Pré-visualização dos dados climáticos")
    if weather_df is not None:
        st.dataframe(weather_df.head(10), use_container_width=True)
    else:
        st.warning("Nenhum dado climático carregado ainda.")

st.divider()
st.caption(
    "SertãoCrop Simulador · Interface construída sobre o AquaCrop-OSPy "
    "(github.com/aquacropos/aquacrop) · Uso acadêmico/educacional."
)
