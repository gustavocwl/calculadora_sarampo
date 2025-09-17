#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
from streamlit_calendar import calendar
from datetime import datetime, date, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
    "Período de transmissibilidade": {"short_name": "Transmissão", "color": "#ff8a70", "days": (-6, 4)},
    "Período de exposição": {"short_name": "Exposição", "color": "#f8cbad", "days": (-21, -7)},
    "Relacionado à vacina": {"short_name": "Vacina", "color": "#9dc3e6", "days": (-14, -6)},
    "Presença de casos secundários": {"short_name": "Casos Sec.", "color": "#ffe699", "days": (0, 25)},
    "Amostral ideal soro": {"short_name": "Amostra (Soro)", "color": "#c5e0b4", "days": (0, 30)},
    "Amostral ideal nasal, faríngica ou nasofaríngica": {"short_name": "Amostra (Nasal)", "color": "#deebf7", "days": (0, 14)},
    "Amostral ideal urina": {"short_name": "Amostra (Urina)", "color": "#fff2cc", "days": (0, 10)},
}

special_day_color = "#ec3e32"
special_day_name = "Início do exantema"

periods_to_show = [
    "Período de transmissibilidade",
    "Período de exposição",
    "Presença de casos secundários",
    "Início do exantema"
]

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
                                 "color": "#ff8a70",
                                 "textColor": "#000000",
                                 "allDay": True, })

    # Período de exposição: 21 dias antes até 7 dias antes
    for delta in range(-21, -6):
        data_evento = data_inicio + timedelta(days=delta)
        calendar_events.append({ "title": "Período de exposição",
                                 "start": data_evento.strftime("%Y-%m-%d"),
                                 "end": data_evento.strftime("%Y-%m-%d"),
                                 "color": "#f8cbad",
                                 "textColor": "#000000",
                                 "allDay": True, })

    # Relacionado à vacina: 14 dias antes até 7 dias antes
    for delta in range(-14, -6):
        data_evento = data_inicio + timedelta(days=delta)
        calendar_events.append({ "title": "Relacionado à vacina",
                                 "start": data_evento.strftime("%Y-%m-%d"),
                                 "end": data_evento.strftime("%Y-%m-%d"),
                                 "color": "#9dc3e6",
                                 "textColor": "#000000",
                                 "allDay": True, })

    # Presença de casos secundários: 0 a 25 dias depois
    for delta in range(0, 26):
        data_evento = data_inicio + timedelta(days=delta)
        calendar_events.append({ "title": "Presença de casos secundários",
                                 "start": data_evento.strftime("%Y-%m-%d"),
                                 "end": data_evento.strftime("%Y-%m-%d"),
                                 "color": "#ffe699",
                                 "textColor": "#000000",
                                 "allDay": True, })

    # Amostra soro ideal: 0 a 31 dias depois
    for delta in range(0, 31):
        data_evento = data_inicio + timedelta(days=delta)
        calendar_events.append({ "title": "Amostral ideal soro",
                                 "start": data_evento.strftime("%Y-%m-%d"),
                                 "end": data_evento.strftime("%Y-%m-%d"),
                                 "color": "#c5e0b4",
                                 "textColor": "#000000",
                                 "allDay": True, })

    # Amostra nasal ideal: 0 a 14 dias depois
    for delta in range(0, 15):
        data_evento = data_inicio + timedelta(days=delta)
        calendar_events.append({ "title": "Amostral ideal nasal, faríngica ou nasofaríngica",
                                 "start": data_evento.strftime("%Y-%m-%d"),
                                 "end": data_evento.strftime("%Y-%m-%d"),
                                 "color": "#deebf7",
                                 "textColor": "#000000",
                                 "allDay": True, })

    # Amostra urina ideal: 0 a 10 dias depois
    for delta in range(0, 11):
        data_evento = data_inicio + timedelta(days=delta)
        calendar_events.append({ "title": "Amostral ideal urina",
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
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import timedelta
import locale
locale.setlocale(locale.LC_TIME, "pt_BR.utf8")

def create_single_case_timeline(case_row):
    period_data = get_period_details(case_row["Data de início do exantema"])
    if not period_data:
        return px.scatter()

    # Expande cada período para cada dia
    expanded_rows = []
    for period in period_data:
        start = pd.to_datetime(period["Data Início"])
        end = pd.to_datetime(period["Data Fim"])
        for d in pd.date_range(start, end):
            expanded_rows.append({
                "Tipo": period["Tipo"],
                "Data Início": d,
                "Data Fim": d + timedelta(days=1),
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

    fig.update_traces(textposition="inside", insidetextanchor="start", textfont=dict(size=16))

    # Limita o eixo X apenas ao intervalo necessário
    min_date = df_expanded["Data Início"].min()
    max_date = df_expanded["Data Fim"].max()

    # Layout
    fig.update_layout(
        yaxis=dict(visible=False, title_font=dict(size=16), tickfont=dict(size=14)),
        xaxis=dict(tickformat="%d", tickangle=0, range=[min_date, max_date], title_font=dict(size=16), tickfont=dict(size=14)),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5, font=dict(size=14), title=None),
        margin=dict(l=0, r=0, t=70, b=70),
        height=400
    )

    # Linhas verticais e nomes dos meses centralizados
    months = pd.date_range(min_date.replace(day=1), max_date, freq="MS")
    for m in months:
        end_of_month = m + pd.offsets.MonthEnd(0)
        days_in_month = (end_of_month - m).days + 1
        mid_month = m + timedelta(days=days_in_month // 2)

        # Linha vertical no início do mês
        fig.add_vline(x=m, line_width=1, line_dash="dash", line_color="gray")

        # Nome do mês logo abaixo do eixo X
        fig.add_annotation(
            x=mid_month,
            y=-0.25,  # posição abaixo do eixo X
            xref="x",
            yref="paper",
            text=m.strftime("%B/%Y"),  # ex: janeiro/2025
            showarrow=False,
            align="center",
            font=dict(size=14),
        )

    return fig



# --- FUNÇÃO PARA CRIAR O GRÁFICO CADEIA DE TRANSMISSÃO ---
# --- FUNÇÃO PARA CRIAR O GRÁFICO CADEIA DE TRANSMISSÃO ---
import pandas as pd
import plotly.express as px
from datetime import timedelta
import locale

# 🔹 Configura locale para português (Linux/macOS/Windows)
try:
    locale.setlocale(locale.LC_TIME, "pt_BR.utf8")
except:
    try:
        locale.setlocale(locale.LC_TIME, "Portuguese_Brazil.1252")
    except:
        pass

def create_timeline_figure(df_notifications, selected_ids=None, show_labels=True):
    """Gera a figura da linha do tempo com hachura e rótulos opcionais independentes da opacidade."""

    plot_data = []
    periods_to_show = [
        "Período de transmissibilidade",
        "Período de exposição",
        "Presença de casos secundários",
    ]

    df_copy = df_notifications.copy()
    df_copy['Data de início do exantema'] = pd.to_datetime(
        df_copy['Data de início do exantema'], format='%d/%m/%Y', errors='coerce'
    )

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
                            "Cor": period_configs["Presença de casos secundários"]["color"],
                            "Período": "Presença de casos secundários",
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
    ticktext = [mes.strftime("%B/%Y").capitalize() for mes in meses]

    fig.update_xaxes(tickvals=tickvals, ticktext=ticktext, tickangle=0, gridcolor="lightgrey")
    for mes in meses:
        fig.add_vline(x=mes, line_width=1, line_dash="dot", line_color="gray")

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

    with col1:
        st.markdown("### Formulário de notificação")
        with st.form("form_notificacao", clear_on_submit=True):
            # CSS para reduzir padding do input
            st.markdown("""
            <style>
                div.stTextInput > label {
                    display:none;
                }
                div.stTextInput > div > input {
                    padding: 4px 6px;  /* Ajuste conforme necessário */
                    font-size: 16px;   /* Tamanho da fonte dentro do input */
                }
            </style>
            """, unsafe_allow_html=True)

            st.markdown('<div style="font-size:18px; margin-bottom:2px;">Identificação do caso</div>', unsafe_allow_html=True)
            identificacao = st.text_input("", key="identificacao")

            st.markdown('<div style="font-size:18px; margin-bottom:2px;">Idade</div>', unsafe_allow_html=True)
            idade = st.text_input("", key="Idade")

            st.markdown('<div style="font-size:18px; margin-bottom:2px;">Data de início do exantema (DD/MM/AAAA)</div>', unsafe_allow_html=True)
            data_exantema_str = st.text_input("", key="Data de início do exantema (DD/MM/AAAA)", value=date.today().strftime("%d/%m/%Y"))

            submit = st.form_submit_button("Salvar")

        if submit:
            erros = []
            if not idade.isdigit():
                erros.append("Idade deve conter apenas números.")
            try:
                datetime.strptime(data_exantema_str, "%d/%m/%Y")
            except ValueError:
                erros.append("Data inválida. Use o formato DD/MM/AAAA.")

            if erros:
                for erro in erros:
                    st.error(erro)
            else:
                # Adiciona nova notificação
                nova_notificacao = pd.DataFrame([{
                    "Identificação": identificacao,
                    "Idade": idade,
                    "Data de início do exantema": data_exantema_str
                }])
                st.session_state.df_notificacoes = pd.concat(
                    [st.session_state.df_notificacoes, nova_notificacao],
                    ignore_index=True
                )

                # 🔹 Incrementa o contador para atualizar o calendário
                if "calendar_update_counter" not in st.session_state:
                    st.session_state.calendar_update_counter = 0
                st.session_state.calendar_update_counter += 1

                st.success("Notificação adicionada!")
                st.rerun()


    with col2:
        st.markdown("### Lista de notificações")
        if not st.session_state.df_notificacoes.empty:
            for index in reversed(st.session_state.df_notificacoes.index):
                row = st.session_state.df_notificacoes.loc[index]
                with st.container(border=True):
                    info_col, button_col1 = st.columns([0.95, 0.05])
                    with info_col:
                        st.markdown(f"**Identificação:** {row['Identificação']} | **Idade:** {row['Idade']} | **Data:** {row['Data de início do exantema']}")
                    with button_col1:
                        if st.button("🗑️", key=f"delete_{index}", help="Remover"):
                            st.session_state.df_notificacoes.drop(index, inplace=True)
                            st.rerun()
                    #with button_col2:
                    #    if st.button("✏️", key=f"edit_{index}", help="Editar (a implementar)"):
                    #        st.info(f"Funcionalidade de edição para '{row['Identificação']}'.")

                    with st.expander("Visualizar linha do tempo"):
                        fig = create_single_case_timeline(row)
                        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key=f"chart_{index}")
        else:
            st.info("Nenhuma notificação registrada ainda.")

    # --- INSERÇÃO DO RODAPÉ DA ABA 2 ---
    st.markdown("---")
    try:
        st.markdown(f'<img src="{logo_url_rodape}" style="max-width:20%; height:auto; margin-bottom:20px; display:block; margin-left:auto; margin-right:0;"/>',
                    unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Não foi possível carregar a logo de rodapé na Aba Detalhes dos Períodos. Erro: {e}")
    # --- FIM DA INSERÇÃO DO RODAPÉ DA ABA 2 ---





# --- ABA 3: Períodos de investigação ---
with tab3:
    st.markdown("### Períodos de investigação")

    # Dicionário de descrições para os cards
    period_descriptions = {
        "Início do exantema": "Data em que a erupção cutânea (exantema) apareceu no paciente.",
        "Período de transmissibilidade": "Investigue: (1) locais visitados, (2) visitas recebidas, (3) rotas e tipo de transporte utilizado, (4) localize as pessoas com quem você esteve em contato, (5) vacinar contatos em risco de contágio.",
        "Período de exposição": "Investigue: (1) contato com pessoas com febre ou erupção cutânea, (2) lugares visitados, (3) visitas recebidas, (4) rotas e tipo de transporte utilizado, e (5) história e data da vacinação contra o sarampo.",
        "Relacionado à vacina": "Critérios de classificação: (1) paciente com erupção cutânea, com ou sem febre, sem tosse ou outros sintomas respiratórios relacionados à erupção cutânea; (2) a erupção começou 7 a 14 dias após a vacinação contendo o vírus do sarampo; (3) a amostra de sangue contendo anticorpos IgM específicos foi obtida entre 8 e 56 dias após a vacinação; (4) após investigação exaustiva, nenhum caso secundário foi identificado; (5) a investigação de campo e laboratório não pôde estabelecer outras causas, ou o genótipo A foi isolado do caso suspeito, sendo este o único relacionado à vacina.",
        "Presença de casos secundários": "Investigue de 7 dias após o primeiro dia de transferibilidade até 21 dias após o último dia de transferibilidade: (1) vigilância e monitoramento completo dos contatos diretos até o final deste período; e (2) identifique todos os contatos que começam com: febre, irritação na pele, adenopatia, tosse, coriza ou conjuntivite.",
        "Amostral ideal soro": "Amostras de soro devem ser obtidas no primeiro contato com o caso, preferencialmente no período que vai do início do exantema até 30 dias depois.",
        "Amostral ideal nasal, faríngica ou nasofaríngica": "O momento ideal para obtenção de amostras nasais, faríngeas ou nasofaríngeas é em até 7 dias após o aparecimento do rash, mas podem ser obtidas em até 14 dias após o aparecimento do rash.",
        "Amostral ideal urina": "O intervalo de tempo recomendado para a obtenção das amostras de urina é de 7 dias após o aparecimento da erupção, mas podem ser obtidas em até 10 dias após o aparecimento da erupção.",
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

            period_details_list = get_period_details(data_inicio_exantema_str) # Certifique-se que esta função está definida e retorna os dados corretamente

            if period_details_list:
                # Cria um container para garantir que todos os cards tenham a mesma altura
                with st.container():
                    # Cria colunas para organizar os cards.
                    num_cols = 2
                    cols = st.columns(num_cols)

                    for i, period_info in enumerate(period_details_list):
                        with cols[i % num_cols]: # Distribui os cards pelas colunas
                            text_color = "#FFFFFF" if period_info['Tipo'] == "Início do exantema" else "#000000"
                            st.markdown(f"""
                            <div style="
                                background-color: {period_info['Cor']};
                                color: {text_color};
                                padding: 15px;
                                border-radius: 10px;
                                margin-bottom: 10px;
                                box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
                                height: 200px; /* Define uma altura fixa para todos os cards */
                                display: flex;
                                flex-direction: column;
                                justify-content: space-between; /* Distribui o conteúdo verticalmente */
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

        show_labels = st.checkbox("Exibir rótulos", value=True)

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



# In[ ]:




