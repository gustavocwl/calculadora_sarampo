#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
from streamlit_calendar import calendar
from datetime import datetime, date, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
#import locale ; locale.setlocale(locale.LC_TIME, "pt_BR.utf8")

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(layout="wide")
st.session_state["language"] = "pt"

# Estilo para aumentar o texto das abas
st.markdown("""
<style>
    .stTabs [role="tab"] p {
        font-size: 18px;
    }
</style>
""", unsafe_allow_html=True)

# --- CONFIGURAÇÃO GLOBAL DOS PERÍODOS ---
period_configs = {
    "Início do exantema": {"short_name": "Início Exantema", "color": "#ec3e32", "days": (0, 0)},
    "Período de transmissibilidade": {"short_name": "Transmissão", "color": "#ffe699", "days": (-6, 4)},
    "Período de incubação": {"short_name": "Incubação", "color": "#e7e6e6", "days": (-21, 0)},
    "Período de exposição": {"short_name": "Exposição", "color": "#e2f0d9", "days": (-21, -7)},
    "Período de investigação da fonte de infecção": {"short_name": "Investigação", "color": "#deebf7", "days": (-21, -7)},
    #"Relacionado à vacina": {"short_name": "Vacina", "color": "#9dc3e6", "days": (-14, -6)},
    "Investigar": {"short_name": "Investigar", "color": "#ffd966", "days": (0, 2)},
    "Bloqueio vacinal": {"short_name": "Bloqueio vacinal", "color": "#deebf7", "days": (0, 3)},
    "Isolamento": {"short_name": "Isolamento", "color": "#ffe699", "days": (0, 4)},
    "Período de aparecimento de casos secundários": {"short_name": "Casos Sec.", "color": "#f8cbad", "days": (1, 25)},
    "Período ideal para coleta de amostras de sangue": {"short_name": "Amostra (Sangue)", "color": "#c5e0b4", "days": (0, 30)},
    "Período ideal para coleta de swab combinado de secreções naso/orofaríngea": {"short_name": "Amostra (Nasal)", "color": "#deebf7", "days": (0, 14)},
    "Período ideal para coleta de urina": {"short_name": "Amostra (Urina)", "color": "#fff2cc", "days": (0, 10)},
}

special_day_color = "#ec3e32"
special_day_name = "Início do exantema"



# --- MESES EM PORTUGUÊS ---
MESES_PT = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]



# --- FUNÇÃO PARA CALENDÁRIO ---
def generate_calendar_events(data_inicio_exantema_str):
    """Gera os eventos para o componente de calendário."""
    if not data_inicio_exantema_str: # Validação para caso de data inválida ou ausente
        return []
    try:
        data_inicio = datetime.strptime(data_inicio_exantema_str, "%d/%m/%Y")
    except ValueError:
        st.error("Erro ao interpretar a data no registro selecionado.")
        return []

    calendar_events = []

    # Evento principal da notificação
    calendar_events.append({ "title": "Início do exantema",
                             "start": data_inicio.strftime("%Y-%m-%d"),
                             "end": data_inicio.strftime("%Y-%m-%d"),
                             "color": "#ec3e32",
                             "textColor": "#FFFFFF",
                             "allDay": True, })

    # Período de transmissibilidade: 6 dias antes até 4 dias depois
    for delta in range(-6, 5):
        data_evento = data_inicio + timedelta(days=delta)
        calendar_events.append({ "title": "Período de transmissibilidade",
                                 "start": data_evento.strftime("%Y-%m-%d"),
                                 "end": data_evento.strftime("%Y-%m-%d"),
                                 "color": "#ffe699",
                                 "textColor": "#000000",
                                 "allDay": True, })

    # Período de incubação: 21 dias antes
    for delta in range(-21, 0):
        data_evento = data_inicio + timedelta(days=delta)
        calendar_events.append({ "title": "Período de incubação",
                                 "start": data_evento.strftime("%Y-%m-%d"),
                                 "end": data_evento.strftime("%Y-%m-%d"),
                                 "color": "#e7e6e6",
                                 "textColor": "#000000",
                                 "allDay": True, })

    # Período de exposição: 21 dias antes até 7 dias antes
    for delta in range(-21, -6):
        data_evento = data_inicio + timedelta(days=delta)
        calendar_events.append({ "title": "Período de exposição",
                                 "start": data_evento.strftime("%Y-%m-%d"),
                                 "end": data_evento.strftime("%Y-%m-%d"),
                                 "color": "#e2f0d9",
                                 "textColor": "#000000",
                                 "allDay": True, })

    # Período de investigação: 21 dias antes até 7 dias antes
    for delta in range(-21, -6):
        data_evento = data_inicio + timedelta(days=delta)
        calendar_events.append({ "title": "Período de investigação",
                                 "start": data_evento.strftime("%Y-%m-%d"),
                                 "end": data_evento.strftime("%Y-%m-%d"),
                                 "color": "#deebf7",
                                 "textColor": "#000000",
                                 "allDay": True, })

    # Relacionado à vacina: 14 dias antes até 7 dias antes
    #for delta in range(-14, -6):
    #    data_evento = data_inicio + timedelta(days=delta)
    #    calendar_events.append({ "title": "Relacionado à vacina",
    #                             "start": data_evento.strftime("%Y-%m-%d"),
    #                             "end": data_evento.strftime("%Y-%m-%d"),
    #                             "color": "#9dc3e6",
    #                             "textColor": "#000000",
    #                             "allDay": True, })

    # Investigação: 2 dias depois
    #for delta in range(0, 3):
    #    data_evento = data_inicio + timedelta(days=delta)
    #    calendar_events.append({ "title": "Investigar",
    #                             "start": data_evento.strftime("%Y-%m-%d"),
    #                             "end": data_evento.strftime("%Y-%m-%d"),
    #                             "color": "#ffd966",
    #                             "textColor": "#000000",
    #                             "allDay": True, })

    # Bloqueio vacinal: 3 dias depois
    for delta in range(0, 4):
        data_evento = data_inicio + timedelta(days=delta)
        calendar_events.append({ "title": "Bloqueio vacinal",
                                 "start": data_evento.strftime("%Y-%m-%d"),
                                 "end": data_evento.strftime("%Y-%m-%d"),
                                 "color": "#deebf7",
                                 "textColor": "#000000",
                                 "allDay": True, })

    # Isolamento: 4 dias depois
    #for delta in range(0, 5):
    #    data_evento = data_inicio + timedelta(days=delta)
    #    calendar_events.append({ "title": "Isolamento",
    #                             "start": data_evento.strftime("%Y-%m-%d"),
    #                             "end": data_evento.strftime("%Y-%m-%d"),
    #                             "color": "#ffe699",
    #                             "textColor": "#000000",
    #                             "allDay": True, })

    # Período de aparecimento de casos secundários: 0 a 25 dias depois
    for delta in range(0, 26):
        data_evento = data_inicio + timedelta(days=delta)
        calendar_events.append({ "title": "Período de aparecimento de casos secundários",
                                 "start": data_evento.strftime("%Y-%m-%d"),
                                 "end": data_evento.strftime("%Y-%m-%d"),
                                 "color": "#f8cbad",
                                 "textColor": "#000000",
                                 "allDay": True, })

    # Amostra sangue: 0 a 31 dias depois
    for delta in range(0, 31):
        data_evento = data_inicio + timedelta(days=delta)
        calendar_events.append({ "title": "Período ideal para coleta de amostras de sangue",
                                 "start": data_evento.strftime("%Y-%m-%d"),
                                 "end": data_evento.strftime("%Y-%m-%d"),
                                 "color": "#c5e0b4",
                                 "textColor": "#000000",
                                 "allDay": True, })

    # Amostra nasal: 0 a 14 dias depois
    for delta in range(0, 15):
        data_evento = data_inicio + timedelta(days=delta)
        calendar_events.append({ "title": "Período ideal para coleta de swab combinado de secreções naso/orofaríngea",
                                 "start": data_evento.strftime("%Y-%m-%d"),
                                 "end": data_evento.strftime("%Y-%m-%d"),
                                 "color": "#deebf7",
                                 "textColor": "#000000",
                                 "allDay": True, })

    # Amostra urina: 0 a 10 dias depois
    for delta in range(0, 11):
        data_evento = data_inicio + timedelta(days=delta)
        calendar_events.append({ "title": "Período ideal para coleta de urina",
                                 "start": data_evento.strftime("%Y-%m-%d"),
                                 "end": data_evento.strftime("%Y-%m-%d"),
                                 "color": "#fff2cc",
                                 "textColor": "#000000",
                                 "allDay": True, })

    return calendar_events



# --- FUNÇÃO PARA DETALHAR OS PERÍODOS ---
def get_period_details(data_inicio_exantema_str, identificacao=None, idade=None):
    """Retorna períodos como intervalos contínuos."""
    if not data_inicio_exantema_str:
        return []

    try:
        data_inicio = datetime.strptime(data_inicio_exantema_str, "%d/%m/%Y")
    except ValueError:
        return []

    period_data = []
    for period_name, config in period_configs.items():
        start_day, end_day = config["days"]
        start_date = data_inicio + timedelta(days=start_day)
        end_date = data_inicio + timedelta(days=end_day)

        period_data.append({
            "Tipo": period_name,
            "Data Início": start_date,
            "Data Fim": end_date,
            "Cor": config["color"]
        })
    return period_data




# --- FUNÇÃO PARA CRIAR O GRÁFICO LINHA DO TEMPO ---
def create_single_case_timeline(case_row):
    period_data = get_period_details(case_row["Data de início do exantema"])
    if not period_data:
        return px.scatter()

    # Expande cada período para cada dia
    expanded_rows = []
    for period in period_data:
        if period["Tipo"] in ["Relacionado à vacina",
                              "Período ideal para coleta de amostras de sangue",
                              "Período ideal para coleta de swab combinado de secreções naso/orofaríngea",
                              "Período ideal para coleta de urina"]:
            continue
        start = pd.to_datetime(period["Data Início"])
        end = pd.to_datetime(period["Data Fim"])
        for d in pd.date_range(start, end):
            expanded_rows.append({
                "Tipo": period["Tipo"],
                #"Data Início": d,
                #"Data Fim": d + timedelta(days=1),
                "Data Início": d - timedelta(hours=12),  # desloca meio dia para trás
                "Data Fim": d + timedelta(hours=12),     # fecha meio dia depois
                "Data Label": d.strftime("%d"),
                "Cor": period["Cor"]
            })

    df_expanded = pd.DataFrame(expanded_rows)
    color_map = {nome: config["color"] for nome, config in period_configs.items()}

    # Cria gráfico
    fig = px.timeline(
        df_expanded,
        x_start="Data Início",
        x_end="Data Fim",
        y="Tipo",
        color="Tipo",
        color_discrete_map=color_map,
        text="Data Label",
        hover_name="Tipo"
    )

    fig.update_traces(textposition="inside", insidetextanchor="start", textfont=dict(size=16), textangle=0, hoverinfo="skip", hovertemplate=None)

    # Limita o eixo X apenas ao intervalo necessário
    min_date = df_expanded["Data Início"].min()
    max_date = df_expanded["Data Fim"].max()

    # Layout
    fig.update_layout(
        yaxis=dict(visible=False, title_font=dict(size=16), tickfont=dict(size=14)),
        xaxis=dict(tickformat="%d", tickangle=0, range=[min_date + timedelta(hours=0), max_date + timedelta(hours=0)],
                   title_font=dict(size=16), tickfont=dict(size=14)),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5, font=dict(size=14), title=None),
        margin=dict(l=0, r=0, t=70, b=70),
        height=400,
        dragmode=False,
        hovermode=False
    )

    # --- Linhas verticais e nomes dos meses centralizados ---
    months = pd.date_range(min_date.replace(day=1), max_date, freq="MS")
    for m in months:
        # Desloca 12h para alinhar com os dados
        m_adjusted = m - timedelta(hours=24)

        # Linha vertical no início do mês
        fig.add_vline(
            x=m_adjusted,
            line_width=1,
            line_dash="dash",
            line_color="#404040"
        )

        # Nome do mês logo abaixo do eixo X
        end_of_month = m + pd.offsets.MonthEnd(0)
        days_in_month = (end_of_month - m).days + 1
        mid_month = m + timedelta(days=days_in_month // 2) - timedelta(hours=12)  # também desloca 12h

        fig.add_annotation(
            x=mid_month,
            y=-0.25,  # posição abaixo do eixo X
            xref="x",
            yref="paper",
            text=f"{MESES_PT[m.month-1]}/{m.year}",
            showarrow=False,
            align="center",
            font=dict(size=14),
        )

    return fig



# --- FUNÇÃO PARA CRIAR O GRÁFICO CADEIA DE TRANSMISSÃO ---
periods_to_show = ["Período de transmissibilidade",
                   "Período de exposição",
                   "Período de aparecimento de casos secundários",
                   "Início do exantema"]

def create_timeline_figure(df_notifications, selected_ids=None, show_labels=True):
    """Gera a figura da linha do tempo com hachura e rótulos opcionais independentes da opacidade."""

    plot_data = []
    df_copy = df_notifications.copy()
    df_copy['Data de início do exantema'] = pd.to_datetime(df_copy['Data de início do exantema'], format='%d/%m/%Y', errors='coerce')

    for _, case in df_copy.iterrows():
        case_name = case["Identificação"]
        case_id = case["ID Genérico"]
        start_date = case["Data de início do exantema"]
        if pd.isna(start_date):
            continue

        for period_name, config in period_configs.items():
            if period_name in periods_to_show:
                period_start = start_date + timedelta(days=config["days"][0])
                period_end = start_date + timedelta(days=config["days"][1])
                current_date = period_start
                while current_date <= period_end:
                    plot_data.append({
                        "ID Genérico": case_id,
                        "Identificação": case_name,
                        "Início": current_date,
                        "Fim": current_date + timedelta(days=1),
                        "Label": current_date.strftime("%d"),
                        "Cor": config["color"],
                        "Período": period_name,
                    })

                    if period_name == "Período de transmissibilidade" and 1 <= (current_date - start_date).days <= 4:
                        plot_data.append({
                            "ID Genérico": case_id,
                            "Identificação": case_name,
                            "Início": current_date,
                            "Fim": current_date + timedelta(days=1),
                            "Label": current_date.strftime("%d"),
                            "Cor": period_configs["Período de aparecimento de casos secundários"]["color"],
                            "Período": "Período de aparecimento de casos secundários",
                        })

                    current_date += timedelta(days=1)

        plot_data.append({
            "ID Genérico": case_id,
            "Identificação": case_name,
            "Início": start_date,
            "Fim": start_date + timedelta(days=1),
            "Label": start_date.strftime("%d"),
            "Cor": special_day_color,
            "Período": special_day_name,
        })

    if not plot_data:
        return None 

    df = pd.DataFrame(plot_data)
    df = df.drop_duplicates(subset=["ID Genérico", "Identificação", "Início", "Período"], keep="last")

    if selected_ids is not None:
        df = df[df["ID Genérico"].isin(selected_ids)]
        if df.empty:
            return None

    color_map = {p: c["color"] for p, c in period_configs.items()}
    color_map[special_day_name] = special_day_color

    fig = px.timeline(
        df, x_start="Início", x_end="Fim", y="Identificação",
        color="Período",
        hover_name="Período",
        color_discrete_map=color_map
    )
    fig.update_yaxes(autorange="reversed")

    # Hachura e opacidade
    for trace in fig.data:
        if trace.name == "Período de transmissibilidade":
            trace.update(marker_pattern_shape="/", marker_pattern_fgcolor="#ff6d4b", marker_pattern_size=5, opacity=0.7)
        else:
            trace.update(opacity=0.65)

    fig.update_layout(
        yaxis=dict(title=None, tickfont=dict(size=16)),
        xaxis=dict(title=None, tickfont=dict(size=16)),
        margin=dict(l=10, r=10, t=40, b=10),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5, font=dict(size=14), title=None),
        dragmode=False,
        hovermode=False,
    )

    # Rótulos como anotações opcionais
    if show_labels:
        for i, row in df.iterrows():
            fig.add_annotation(
                x=row["Início"] + (row["Fim"] - row["Início"]) / 2,
                y=row["Identificação"],
                text=row["Label"],
                showarrow=False,
                font=dict(size=14, color="#000000", family="Arial", weight=600),
                align="center",
                valign="middle",
                bgcolor="white",
                borderwidth=1,
                borderpad=3
            )

    # Linhas verticais + meses
    data_min = df["Início"].min().replace(day=1)
    data_max = df["Fim"].max()
    meses = pd.date_range(data_min, data_max, freq="MS")
    tickvals = meses
    ticktext = [f"{MESES_PT[mes.month-1]}/{mes.year}" for mes in meses]

    fig.update_xaxes(tickvals=tickvals, ticktext=ticktext, tickangle=0, gridcolor="lightgrey")
    for mes in meses:
        fig.add_vline(x=mes, line_width=1, line_dash="dash", line_color="#404040")

    return fig
















# --- INICIALIZAÇÃO DO SESSION STATE ---
if "df_notificacoes" not in st.session_state:
    st.session_state.df_notificacoes = pd.DataFrame(columns=["Identificação", "Idade", "Data de início do exantema"])

if "calendar_update_counter" not in st.session_state:
    st.session_state.calendar_update_counter = 0



# --- CABEÇALHO ---
logo_url_rodape = "https://raw.githubusercontent.com/gustavocwl/calculadora_sarampo/refs/heads/main/src/barra%20neutra%20(1).png"
st.markdown("<h1 style='font-size: 26px; margin-bottom: 20px; margin-top: 0px; font-weight: normal;'> <span style='font-weight: bold;'>Ministério da Saúde</span> — Ferramenta para investigação de sarampo</h1>", unsafe_allow_html=True)

# --- CRIAÇÃO DAS ABAS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Início", "Linha do tempo", "Períodos de investigação", "Calendário", "Cadeia de transmissão"])






# --- CONTEÚDO DA ABA 1 ---
with tab1:
    st.markdown("<h1 style='font-weight: bold; font-size: 22px; margin-top: 20px'>Apresentação</h1>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size: 18px;'>
    A ferramenta para investigação de sarampo foi desenvolvida para apoiar as ações de vigilância em saúde, integrando registros de casos suspeitos com recursos visuais que facilitam a análise e acompanhamento da investigação epidemiológica.
    <ul>
        <li><b>Aba "Linha do tempo":</b> onde você registra os casos suspeitos de sarampo e visualiza suas linhas do tempo individuais.</li>
        <li><b>Aba "Períodos de investigação":</b> exibe os detalhes de cada período de forma organizada.</li>
        <li><b>Aba "Calendário":</b> mostra os períodos de investigação a partir da data de início do exantema.</li>
        <li><b>Aba "Cadeia de transmissão":</b> ajuda a entender a corrente de transmissão, mostrando como os casos estão ligados entre si.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    # --- INSERÇÃO DO RODAPÉ DA ABA 1 ---
    st.markdown("---")
    try:
        st.markdown(f'<img src="{logo_url_rodape}" style="max-width:20%; height:auto; margin-bottom:20px; display:block; margin-left:auto; margin-right:0;"/>',
                    unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Não foi possível carregar a logo de rodapé na Aba Detalhes dos Períodos. Erro: {e}")
    # --- FIM DA INSERÇÃO DO RODAPÉ DA ABA 1 ---






# --- CONTEÚDO DA ABA 2: Linha do tempo ---
with tab2:
    col1, col2 = st.columns([1, 3])

    # Garante que o DataFrame exista na sessão
    if "df_notificacoes" not in st.session_state:
        st.session_state.df_notificacoes = pd.DataFrame(
            columns=["Identificação", "Data de nascimento", "Data de início do exantema"]
        )

    with col1:
        st.markdown("### Formulário de notificação")
        with st.form("form_notificacao", clear_on_submit=True):
            # CSS para reduzir padding do input
            st.markdown(""" <style> div.stTextInput > label { display:none; } div.stTextInput > div > input { padding: 4px 6px; /* Ajuste conforme necessário */ font-size: 16px; /* Tamanho da fonte dentro do input */ } </style> """, unsafe_allow_html=True)

            st.markdown('<div style="font-size:18px; margin-bottom:2px;">Identificação do caso</div>', unsafe_allow_html=True)
            identificacao = st.text_input("", key="identificacao_form")

            st.markdown('<div style="font-size:18px; margin-bottom:2px;">Data de nascimento (DD/MM/AAAA)</div>', unsafe_allow_html=True)
            data_nascimento_str = st.text_input("", key="nascimento_form")

            st.markdown('<div style="font-size:18px; margin-bottom:2px;">Data de início do exantema (DD/MM/AAAA)</div>', unsafe_allow_html=True)
            data_exantema_str = st.text_input("", key="exantema_form", value=date.today().strftime("%d/%m/%Y"))

            submit = st.form_submit_button("Salvar")

        if submit:
            erros = []
            if not identificacao.strip():
                erros.append("Por favor, insira um identificador.")
            elif identificacao.lower() in st.session_state.df_notificacoes["Identificação"].str.lower().values:
                erros.append("Este identificador já existe! Escolha outro.")

            try:
                data_nascimento = datetime.strptime(data_nascimento_str, "%d/%m/%Y")
            except ValueError:
                erros.append("Data de nascimento inválida. Use o formato DD/MM/AAAA.")
            try:
                data_exantema = datetime.strptime(data_exantema_str, "%d/%m/%Y")
            except ValueError:
                erros.append("Data de início do exantema inválida. Use o formato DD/MM/AAAA.")

            if erros:
                for erro in erros:
                    st.error(erro)
            else:
                nova_notificacao = pd.DataFrame([{
                    "Identificação": identificacao,
                    "Data de nascimento": data_nascimento_str,
                    "Data de início do exantema": data_exantema_str
                }])
                st.session_state.df_notificacoes = pd.concat(
                    [st.session_state.df_notificacoes, nova_notificacao],
                    ignore_index=True
                )
                st.session_state.calendar_update_counter += 1
                st.success("Notificação adicionada!")
                st.rerun()

    with col2:
        st.markdown("### Lista de notificações")
        if not st.session_state.df_notificacoes.empty:
            for index in reversed(st.session_state.df_notificacoes.index):
                row = st.session_state.df_notificacoes.loc[index]

                # Calcula idade
                nascimento = datetime.strptime(row["Data de nascimento"], "%d/%m/%Y")
                inicio_exantema = datetime.strptime(row["Data de início do exantema"], "%d/%m/%Y")

                delta = inicio_exantema - nascimento
                anos = delta.days // 365
                meses = (delta.days % 365) // 30
                dias = (delta.days % 365) % 30
                idade_formatada = f"{anos} anos, {meses} meses, {dias} dias"

                with st.container(border=True):
                    info_col, button_col1 = st.columns([0.95, 0.05])
                    with info_col:
                        st.markdown(f"**Identificação:** {row['Identificação']} | **Idade:** {idade_formatada} | **Data de início do exantema:** {row['Data de início do exantema']}")
                    with button_col1:
                        if st.button("🗑️", key=f"delete_{index}", help="Remover"):
                            st.session_state.df_notificacoes.drop(index, inplace=True)
                            st.rerun()
                    with st.expander("Visualizar linha do tempo"):
                        fig = create_single_case_timeline(row)
                        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key=f"chart_{index}")
        else:
            st.info("Nenhuma notificação registrada ainda.")

    # --- RODAPÉ ---
    st.markdown("---")
    try:
        st.markdown(
            f'<img src="{logo_url_rodape}" style="max-width:20%; height:auto; margin-bottom:20px; display:block; margin-left:auto; margin-right:0;"/>',
            unsafe_allow_html=True
        )
    except Exception as e:
        st.warning(f"Não foi possível carregar a logo de rodapé na Aba Detalhes dos Períodos. Erro: {e}")











# --- ABA 3: Períodos de investigação ---
with tab3:
    st.markdown("### Períodos de investigação")

    # Dicionário de descrições para os cards
    period_descriptions = {
        "Início do exantema": "Data em que a erupção cutânea (exantema) apareceu no paciente.",
        "Período de transmissibilidade": "O período de transmissibilidade do sarampo é o intervalo de tempo durante o qual uma pessoa infectada pode transmitir o vírus para outras pessoas. Esse período inicia 6 dias antes e se estende até 4 dias após o início do exantema.<br>Investigue: (1) locais visitados, (2) visitas recebidas, (3) rotas e tipo de transporte utilizado, (4) localize as que o caso esteve em contato, (5) vacinar contatos.<br>Ações que devem ser realizadas referente a esse período: (1) orientar o caso a ficar em isolamento social (ele pode transmitir a doença), (2) rastrear todos os contatos do caso suspeito, (3) monitorar todos os contatos por 30 dias da data da exposição, e (4) realizar o bloqueio vacinal seletivo em todos os contatos.",
        "Período de exposição": "Investigue: (1) contato com pessoas com febre e exantema, acompanhados de tosse e/ou coriza e/ou conjutivite, (2) lugares visitados, (3) visitas recebidas, e (4) história e data da vacinação contra o sarampo. O período de exposição do sarampo é o intervalo em que provavelmente o caso foi exposto ao vírus do sarampo. Ocorre de 7 a 21 dias anteriores a data de início do exantema e indica o período que o paciente provavelmente contraiu a infecção. Ações que devem ser realizadas nesse período: • Rastrear os contatos do caso suspeito para identificar a fonte de infecção. • Coletar amostras da fonte de infecção se ainda for possível",
        "Período de incubação":"É o intervalo entre a data da exposição e o início do exantema. Para o sarampo, o período de incubação varia de 7 a 21 dias.<br>Ações que devem ser realizadas nesse período: (1) rastrear os contatos do caso suspeito para identificar a fonte de infecção, e (2) coletar amostras da fonte de infecção se ainda for possível.",
        #"Relacionado à vacina": "Critérios de classificação: (1) paciente com erupção cutânea, com ou sem febre, sem tosse ou outros sintomas respiratórios relacionados à erupção cutânea; (2) a erupção começou 7 a 14 dias após a vacinação contendo o vírus do sarampo; (3) a amostra de sangue contendo anticorpos IgM específicos foi obtida entre 8 e 56 dias após a vacinação; (4) após investigação exaustiva, nenhum caso secundário foi identificado; (5) a investigação de campo e laboratório não pôde estabelecer outras causas, ou o genótipo A foi isolado do caso suspeito, sendo este o único relacionado à vacina.",
        "Período de aparecimento de casos secundários": "Investigue: (1) vigilância e monitoramento completo dos contatos até o final deste período; e (2) identifique todos os contatos que apresentarem febre e exantema, acompanhados de tosse e/ou coriza e/ou conjuntivite. O período aparecimento de casos secundários é o intervalo em que provavelmente os contatos do caso que foram expostos ao vírus do sarampo podem desenvolver sinais e sintomas. Esse período ocorre a partir de 7 dias após o primeiro dia de transmissão até 21 dias após o último dia de transmissão. Ações que devem ser realizadas nesse período: • Monitorar os contatos do caso por 30 dias • Verificar aparecimento de sinais e sintomas • Se apresentar a tríade do sarampo, notificar e realizar as demais ações oportunas de vigilância do sarampo",
        "Período ideal para coleta de amostras de sangue": "A coleta de amostras biológicas deve ser realizada em todos os casos suspeitos de sarampo e/ou rubéola no primeiro atendimento ao paciente. Para o diagnóstico sorológico, coleta-se sangue total sem anticoagulante, para obtenção de soro destinado à detecção de anticorpos das classes IgM e IgG. Em casos onde não seja possível a coleta no primeiro contato com o paciente, conduta considerada ideal, as amostras de sangue devem ser coletadas entre o 1º e 30º dia a partir do início do exantema. Observação: • Para casos com resultado IgM reagente ou inconclusivo, deve-se coletar uma segunda amostra (S2) entre 15 e 25 dias após a primeira (S1). • Falso Negativo: as amostras coletadas precocemente (coleta menor que 5 dias a partir da data de início do exantema) podem apresentar resultados de sorologia IgM e IgG não reagente. Nesse caso, aconselha-se avaliar o quadro clínico do paciente, relatar a situação à Vigilância Epidemiológica (VE) do estado, para solicitação de nova coleta (S2) entre 15 a 25 dias após a coleta da primeira (S1), com posterior testagem pareada.",
        "Período ideal para coleta de swab combinado de secreções naso/orofaríngea": "Para o diagnóstico molecular e determinar se a infecção é autóctone, importada, de fonte desconhecida ou um evento adverso possivelmente atribuível a vacinação, é necessária a coleta de amostras de swab combinado da secreção naso/orofaringe e de urina, ambas destinadas à detecção viral. A coleta de swab combinado naso/orofaríngeo deve ocorrer preferencialmente entre o 1º e 7º dia após o início do exantema, e no máximo até o 14º dia.",
        "Período ideal para coleta de urina": "Para o diagnóstico molecular e determinar se a infecção é autóctone, importada, de fonte desconhecida ou um evento adverso possivelmente atribuível a vacinação, é necessária a coleta de amostras de swab combinado da secreção naso/orofaringe e de urina, ambas destinadas à detecção viral. As amostras de urina destinadas à identificação e caracterização viral devem ser coletadas preferencialmente entre o 1º e o 7º dia após o início do exantema e no máximo até o 10º dia.",
    }

    if st.session_state.df_notificacoes.empty:
        st.info("Nenhuma notificação registrada ainda.")
    else:
        df_details = st.session_state.df_notificacoes.reset_index(drop=True)

        # --- Seletor para escolher a notificação ---
        options_indices_details = df_details.index.tolist()
        labels_map_details = {
            idx: f'{df_details.at[idx, "Identificação"]} — {df_details.at[idx, "Data de início do exantema"]}'
            for idx in options_indices_details
        }

        selectbox_options_details = [None] + options_indices_details
        selectbox_labels_details = {idx: labels_map_details[idx] for idx in options_indices_details}
        selectbox_labels_details[None] = "Selecione uma notificação para ver os detalhes dos períodos..."

        #st.markdown('<span style="font-size:18px; margin-bottom:2px;">Escolha uma notificação:</span>', unsafe_allow_html=True)
        selected_idx_for_details = st.selectbox(
            "",
            options=selectbox_options_details,
            format_func=lambda i: selectbox_labels_details.get(i, "Erro ao carregar rótulo")
        )

        # --- Exibição dos Cards dos Períodos ---
        if selected_idx_for_details is not None:
            row = df_details.loc[selected_idx_for_details]
            data_inicio_exantema_str = row["Data de início do exantema"]

            period_details_list = get_period_details(data_inicio_exantema_str)  # função já definida

            if period_details_list:
                # --- Remover os períodos indesejados ---
                excluir_periodos = ["Investigar", "Bloqueio vacinal", "Isolamento", "Período de investigação da fonte de infecção"]
                period_details_list = [
                    p for p in period_details_list if p['Tipo'] not in excluir_periodos
                ]

                if not period_details_list:
                    st.info("Não há períodos disponíveis após aplicar os filtros.")
                else:
                    # Cria um container para garantir que todos os cards tenham a mesma altura
                    with st.container():
                        # Cria colunas para organizar os cards
                        num_cols = 2
                        cols = st.columns(num_cols)

                        for i, period_info in enumerate(period_details_list):
                            with cols[i % num_cols]:
                                text_color = "#FFFFFF" if period_info['Tipo'] == "Início do exantema" else "#000000"

                                # --- regra para exibir só "Início" em "Início do exantema" ---
                                if period_info['Tipo'] == "Início do exantema":
                                    st.markdown(f"""
                                    <div style="
                                        background-color: {period_info['Cor']};
                                        color: {text_color};
                                        padding: 15px;
                                        border-radius: 10px;
                                        margin-bottom: 10px;
                                        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
                                        height: 250px;
                                        display: flex;
                                        flex-direction: column;
                                        justify-content: space-between;
                                    ">
                                        <h5 style="margin-top: 0;">{period_info['Tipo']}</h5>
                                        <div style="display: flex; justify-content: space-between; gap: 5px;">
                                            <p style="margin-bottom: 5px; flex: 1;"><strong>Início:</strong> {pd.to_datetime(period_info['Data Início']).strftime("%d/%m/%Y")}</p>
                                        </div>
                                        <p style="font-size: 0.8rem; margin-top: 6px; font-style: italic; flex-grow: 1;">{period_descriptions.get(period_info['Tipo'], '')}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                else:
                                    st.markdown(f"""
                                    <div style="
                                        background-color: {period_info['Cor']};
                                        color: {text_color};
                                        padding: 15px;
                                        border-radius: 10px;
                                        margin-bottom: 10px;
                                        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
                                        height: 250px;
                                        display: flex;
                                        flex-direction: column;
                                        justify-content: space-between;
                                    ">
                                        <h5 style="margin-top: 0;">{period_info['Tipo']}</h5>
                                        <div style="display: flex; justify-content: space-between; gap: 5px;">
                                            <p style="margin-bottom: 5px; flex: 1;"><strong>Início:</strong> {pd.to_datetime(period_info['Data Início']).strftime("%d/%m/%Y")}</p>
                                            <p style="margin-bottom: 5px; flex: 1;"><strong>Fim:</strong> {pd.to_datetime(period_info['Data Fim']).strftime("%d/%m/%Y")}</p>
                                        </div>
                                        <p style="font-size: 0.8rem; margin-top: 6px; font-style: italic; flex-grow: 1;">{period_descriptions.get(period_info['Tipo'], '')}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
            else:
                st.info("Não foi possível obter os detalhes dos períodos para esta notificação.")

        else:
            st.info("Por favor, selecione uma notificação para visualizar os detalhes dos períodos.")

    # --- INSERÇÃO DO RODAPÉ DA ABA 3 ---
    st.markdown("---")
    try:
        st.markdown(f'<img src="{logo_url_rodape}" style="max-width:20%; height:auto; margin-bottom:20px; display:block; margin-left:auto; margin-right:0;"/>',
                    unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Não foi possível carregar a logo de rodapé na Aba Detalhes dos Períodos. Erro: {e}")
    # --- FIM DA INSERÇÃO DO RODAPÉ DA ABA 3 ---







# --- ABA 4: Calendário ---
with tab4:
    st.markdown("### Calendário")

    if st.session_state.df_notificacoes.empty:
        st.info("Nenhuma notificação registrada ainda.")
    else:
        df = st.session_state.df_notificacoes.reset_index(drop=True)

        options_indices_calendar = df.index.tolist()
        labels_map_calendar = {
            idx: f'{df.at[idx, "Identificação"]} — {df.at[idx, "Data de início do exantema"]}'
            for idx in options_indices_calendar
        }

        selectbox_options_calendar = [None] + options_indices_calendar
        selectbox_labels_calendar = {idx: labels_map_calendar[idx] for idx in options_indices_calendar}
        selectbox_labels_calendar[None] = "Selecione uma notificação para ver o calendário..."

        initial_selection = st.session_state.get("selected_calendar_idx", None)

        selected_idx_for_calendar = st.selectbox(
            "",
            options=selectbox_options_calendar,
            format_func=lambda i: selectbox_labels_calendar.get(i, "Erro ao carregar rótulo"),
            index=selectbox_options_calendar.index(initial_selection) if initial_selection in selectbox_options_calendar else 0 
        )

        st.session_state["selected_calendar_idx"] = selected_idx_for_calendar

        if selected_idx_for_calendar is not None:
            row = df.loc[selected_idx_for_calendar]

            try:
                calendar_events = generate_calendar_events(row["Data de início do exantema"])

                calendar_options = {
                    "editable": False,
                    "selectable": False,
                    "locale": "pt-br",
                    "headerToolbar": {"left": "title"},
                    "initialView": "dayGridMonth",
                    "buttonText": {"today": "Hoje", "month": "Mês", "week": "Semana", "day": "Dia"},
                    "initialDate": datetime.strptime(row["Data de início do exantema"], "%d/%m/%Y").strftime("%Y-%m-%d"),
                    "height": 800,
                }

                calendar(
                    events=calendar_events,
                    options=calendar_options,
                    key=f"calendar_{selected_idx_for_calendar}_{st.session_state.calendar_update_counter}"
                )

            except Exception as e:
                st.error(f"Erro ao gerar ou exibir o calendário: {e}")
        else:
            st.info("Por favor, selecione uma notificação para visualizar o calendário.")

    # --- INSERÇÃO DO RODAPÉ DA ABA 4 ---
    st.markdown("---")
    try:
        st.markdown(f'<img src="{logo_url_rodape}" style="max-width:20%; height:auto; margin-bottom:20px; display:block; margin-left:auto; margin-right:0;"/>',
                    unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Não foi possível carregar a logo de rodapé na Aba Calendário. Erro: {e}")
    # --- FIM DA INSERÇÃO DO RODAPÉ DA ABA 4 ---







# ---------------- ABA 5: Cadeia de transmissão ----------------
with tab5:
    st.markdown("### Cadeia de Transmissão")

    if st.session_state.df_notificacoes.empty:
        st.info("Nenhuma notificação registrada ainda.")
    else:
        df_plot_base = st.session_state.df_notificacoes.copy()

        # 🔹 Converte a coluna de datas para datetime
        df_plot_base["Data de início do exantema"] = pd.to_datetime(
            df_plot_base["Data de início do exantema"], format="%d/%m/%Y", errors="coerce"
        )

        # 🔹 Garante coluna ID Genérico usando a identificação do caso
        df_plot_base["ID Genérico"] = df_plot_base["Identificação"]

        # 🔹 Cria dicionário para o multiselect usando ID Genérico + data
        notification_options_dict = {
            row["ID Genérico"]: f'{row["ID Genérico"]} ({row["Data de início do exantema"].strftime("%d/%m/%Y")})'
            for _, row in df_plot_base.iterrows()
        }

        # 🔹 Multiselect para filtrar notificações (todos selecionados por padrão)
        selected_notification_ids = st.multiselect(
            "Selecione as notificações para visualizar os períodos:",
            options=list(notification_options_dict.keys()),
            format_func=lambda i: notification_options_dict[i],
            default=list(notification_options_dict.keys())
        )

        show_labels = st.checkbox("Exibir rótulos", value=False)

        # 🔹 Filtra o DataFrame
        df_filtered_plot = df_plot_base[df_plot_base["ID Genérico"].isin(selected_notification_ids)]

        # 🔹 Gera o gráfico
        timeline_fig = create_timeline_figure(df_filtered_plot, show_labels=show_labels)

        if timeline_fig:
            st.plotly_chart(timeline_fig, use_container_width=True, config={'displayModeBar': False})
        else:
            st.warning("Não foi possível gerar o gráfico. Verifique as datas das notificações.")

    # --- INSERÇÃO DO RODAPÉ DA ABA 5 ---
    st.markdown("---")
    try:
        st.markdown(
            f'<img src="{logo_url_rodape}" style="max-width:20%; height:auto; margin-bottom:20px; display:block; margin-left:auto; margin-right:0;"/>',
            unsafe_allow_html=True
        )
    except Exception as e:
        st.warning(f"Não foi possível carregar a logo de rodapé na Aba Linha do tempo. Erro: {e}")
    # --- FIM DA INSERÇÃO DO RODAPÉ DA ABA 5 ---


