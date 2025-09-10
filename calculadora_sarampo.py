#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
from streamlit_calendar import calendar
from datetime import datetime, date, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# CONFIGURAÇÃO
st.set_page_config(layout="wide")


# --- INSERÇÃO DA LOGO ---
logo_url = "https://fns2.saude.gov.br/proconvenio/imagens/subtopodireita.png" # Substitua pelo nome do seu arquivo de logo local, se aplicável

try:
    st.image(logo_url, width=150) # Ajuste a largura conforme necessário
except Exception as e:
    st.warning(f"Não foi possível carregar a logo. Verifique o caminho do arquivo ou URL. Erro: {e}")
# --- FIM DA INSERÇÃO DA LOGO ---


# --- Inicialização do Session State ---
if "df_notificacoes" not in st.session_state:
    st.session_state.df_notificacoes = pd.DataFrame(
        columns=["Número de notificação", "Idade", "Data de início do exantema"]
    )
# Contador para forçar a atualização do componente calendário quando seus eventos mudam.
if "calendar_update_counter" not in st.session_state:
    st.session_state.calendar_update_counter = 0

# --- Funções Auxiliares ---

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
    # Período de transmissibilidade: 6 dias antes até 4 dias depois
    for delta in range(-6, 5):
        data_evento = data_inicio + timedelta(days=delta)
        calendar_events.append({ "title": "🗣️ Período de transmissibilidade",
                                 "start": data_evento.strftime("%Y-%m-%d"),
                                 "end": data_evento.strftime("%Y-%m-%d"),
                                 "color": "#AAFFFF",
                                 "textColor": "#000000",
                                 "allDay": True, })

    # Período de exposição: 21 dias antes até 7 dias antes
    for delta in range(-21, -6):
        data_evento = data_inicio + timedelta(days=delta)
        calendar_events.append({ "title": "🫂 Período de exposição",
                                 "start": data_evento.strftime("%Y-%m-%d"),
                                 "end": data_evento.strftime("%Y-%m-%d"),
                                 "color": "#FFFF59",
                                 "textColor": "#000000",
                                 "allDay": True, })

    # Relacionado à vacina: 14 dias antes até 7 dias antes
    for delta in range(-14, -6):
        data_evento = data_inicio + timedelta(days=delta)
        calendar_events.append({ "title": "💉 Relacionado à vacina",
                                 "start": data_evento.strftime("%Y-%m-%d"),
                                 "end": data_evento.strftime("%Y-%m-%d"),
                                 "color": "#00b050",
                                 "textColor": "#FFFFFF",
                                 "allDay": True, })

    # Presença de casos secundários: 0 a 25 dias depois
    for delta in range(0, 26):
        data_evento = data_inicio + timedelta(days=delta)
        calendar_events.append({ "title": "🦠 Presença de casos secundários",
                                 "start": data_evento.strftime("%Y-%m-%d"),
                                 "end": data_evento.strftime("%Y-%m-%d"),
                                 "color": "#ff9900",
                                 "textColor": "#000000",
                                 "allDay": True, })

    # Amostra soro ideal: 0 a 31 dias depois
    for delta in range(0, 31):
        data_evento = data_inicio + timedelta(days=delta)
        calendar_events.append({ "title": "🩸 Amostral ideal soro",
                                 "start": data_evento.strftime("%Y-%m-%d"),
                                 "end": data_evento.strftime("%Y-%m-%d"),
                                 "color": "#D10000",
                                 "textColor": "#FFFFFF",
                                 "allDay": True, })

    # Amostra nasal ideal: 0 a 14 dias depois
    for delta in range(0, 15):
        data_evento = data_inicio + timedelta(days=delta)
        calendar_events.append({ "title": "👃 Amostral ideal nasal, faríngica ou nasofaríngica",
                                 "start": data_evento.strftime("%Y-%m-%d"),
                                 "end": data_evento.strftime("%Y-%m-%d"),
                                 "color": "#7030a0",
                                 "textColor": "#FFFFFF",
                                 "allDay": True, })

    # Amostra urina ideal: 0 a 10 dias depois
    for delta in range(0, 11):
        data_evento = data_inicio + timedelta(days=delta)
        calendar_events.append({ "title": "💧 Amostral ideal urina",
                                 "start": data_evento.strftime("%Y-%m-%d"),
                                 "end": data_evento.strftime("%Y-%m-%d"),
                                 "color": "#ffffcc",
                                 "textColor": "#000000",
                                 "allDay": True, })

    # Evento principal da notificação
    calendar_events.append({ "title": "🤒 Início do exantema",
                             "start": data_inicio.strftime("%Y-%m-%d"),
                             "end": data_inicio.strftime("%Y-%m-%d"),
                             "color": "#000000",
                             "textColor": "#FFFFFF",
                             "allDay": True, })
    return calendar_events

def get_period_details(data_inicio_exantema_str):
    """Retorna uma lista de dicionários com os detalhes de cada período."""
    if not data_inicio_exantema_str:
        return []

    try:
        data_inicio = datetime.strptime(data_inicio_exantema_str, "%d/%m/%Y")
    except ValueError:
        st.error("Erro ao interpretar a data no registro selecionado.")
        return []

    period_data = []
    period_colors = {
        "🗣️ Período de transmissibilidade": {"color": "#AAFFFF", "days": (-6, 4)},
        "🫂 Período de exposição": {"color": "#FFFF59", "days": (-21, -7)},
        "💉 Relacionado à vacina": {"color": "#00b050", "days": (-14, -7)},
        "🦠 Presença de casos secundários": {"color": "#ff9900", "days": (0, 25)},
        "🩸 Amostral ideal soro": {"color": "#D10000", "days": (0, 30)},
        "👃 Amostral ideal nasal, faríngica ou nasofaríngica": {"color": "#7030a0", "days": (0, 14)},
        "💧 Amostral ideal urina": {"color": "#ffffcc", "days": (0, 10)},
        "🤒 Início do exantema": {"color": "#000000", "days": (0, 0)}
    }

    for period_name, config in period_colors.items():
        start_day, end_day = config["days"]

        # Lida com o caso específico de "Início do exantema" que é um único dia
        if period_name == "🤒 Início do exantema":
            start_date = data_inicio
            end_date = data_inicio
        else:
            start_date = data_inicio + timedelta(days=start_day)
            end_date = data_inicio + timedelta(days=end_day)

        period_data.append({
            "nome": period_name,
            "data_inicio": start_date.strftime("%d/%m/%Y"),
            "data_fim": end_date.strftime("%d/%m/%Y"),
            "cor": config["color"]
        })

    return period_data

def render_calendar(selected_idx, df):
    """Renderiza o componente de calendário se um índice válido for selecionado."""
    if selected_idx is None or df.empty:
        st.info("Por favor, selecione uma notificação para visualizar o calendário.")
        return

    row = df.loc[selected_idx]
    date_str = row.get("Data de início do exantema")

    if not date_str:
        st.error("Data de início do exantema não encontrada para este registro.")
        return

    calendar_events = generate_calendar_events(date_str)

    if not calendar_events: # Se generate_calendar_events retornou lista vazia (erro de data)
        return

    calendar_options = {
        "editable": False,
        "selectable": False,
        "locale": "pt-br",
        "headerToolbar": {"left": "title"},
        "initialView": "dayGridMonth",
        "buttonText": {"today": "Hoje", "month": "Mês", "week": "Semana", "day": "Dia"},
        "initialDate": datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d"),
        "height": 800,
    }

    st.session_state.calendar_update_counter += 1

    calendar(events=calendar_events, options=calendar_options, key=f"calendar_{selected_idx}_{st.session_state.calendar_update_counter}")

# --- Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Apresentação", "Notificações", "Períodos de investigação", "Calendário", "Linha do tempo"])

# --- ABA 1: Apresentação ---
with tab1:
    st.title("Ferramenta para investigação de sarampo")
    st.markdown("""
    A ferramenta foi desenvolvida para apoiar a vigilância do sarampo, integrando registros de casos suspeitos com recursos visuais que facilitam a análise e acompanhamento da investigação epidemiológica.
    - Aba "Notificações": onde você registra os casos suspeitos de sarampo.
    - Aba "Períodos de investigação": exibe os detalhes de cada período de forma organizada.
    - Aba "Calendário": mostra os períodos de investigação a partir da data de início do exantema.
    - Aba "Linha do tempo": ajuda a entender a corrente de transmissão do sarampo, mostrando como os casos estão ligados entre si.
    """)

    # --- INSERÇÃO DO RODAPÉ DA ABA 1 ---
    st.markdown("---") # Adiciona uma linha divisória
    try:
        st.image(logo_url, width=100) # Insere a imagem do rodapé
    except Exception as e:
        st.warning(f"Não foi possível carregar a logo de rodapé na Aba Apresentação. Erro: {e}")
    # --- FIM DA INSERÇÃO DO RODAPÉ DA ABA 1 ---


# --- ABA 2: Entrada de Dados ---
with tab2:
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("### Formulário de notificação")
        with st.form("form_notificacao"):
            numero_notificacao = st.text_input("Número de notificação")
            idade = st.text_input("Idade")
            data_exantema_str = st.text_input(
                "Data de início do exantema (DD/MM/AAAA)",
                value=date.today().strftime("%d/%m/%Y")
            )
            submit = st.form_submit_button("Enviar")

        if submit:
            erros = []
            if not numero_notificacao.isdigit():
                erros.append("Número de notificação deve conter apenas números.")
            if not idade.isdigit():
                erros.append("Idade deve conter apenas números.")
            try:
                datetime.strptime(data_exantema_str, "%d/%m/%Y") # Validação de formato
            except ValueError:
                erros.append("Data inválida. Use DD/MM/AAAA.")

            if erros:
                for erro in erros:
                    st.error(erro)
            else:
                st.session_state.df_notificacoes = pd.concat([
                    st.session_state.df_notificacoes,
                    pd.DataFrame([{
                        "Número de notificação": numero_notificacao,
                        "Idade": idade,
                        "Data de início do exantema": data_exantema_str
                    }])
                ], ignore_index=True)
                st.success("Notificação adicionada!")
                st.rerun() # Atualiza a página após adicionar

        st.markdown("### Notificações registradas")
        st.dataframe(st.session_state.df_notificacoes)

        if not st.session_state.df_notificacoes.empty:
            st.markdown("### Gerenciar notificações")

            df = st.session_state.df_notificacoes.reset_index(drop=True)

            options_indices = [None] + df.index.tolist()
            labels_map = {
                idx: f'{df.at[idx, "Número de notificação"]} — {df.at[idx, "Data de início do exantema"]}'
                for idx in df.index.tolist()
            }
            labels_map[None] = "Selecione uma notificação..." 

            selected_idx = st.selectbox(
                "Escolha uma notificação para gerenciar:",
                options=options_indices,
                format_func=lambda i: labels_map.get(i, "Erro ao carregar rótulo")
            )

            if selected_idx is not None: 
                col_remover, col_editar = st.columns([1, 1])

                with col_remover:
                    if st.button("Remover", key=f"remover_{selected_idx}"):
                        st.session_state.df_notificacoes.drop(selected_idx, inplace=True)
                        st.session_state.df_notificacoes.reset_index(drop=True, inplace=True)
                        st.success("Notificação removida!")
                        st.rerun() 

                with col_editar:
                    with st.form(f"form_edicao_{selected_idx}"):
                        row = df.loc[selected_idx]
                        numero_edit = st.text_input("Número de notificação", value=row["Número de notificação"], key=f"num_{selected_idx}")
                        idade_edit = st.text_input("Idade", value=row["Idade"], key=f"idade_{selected_idx}")
                        data_edit = st.text_input("Data (DD/MM/AAAA)", value=row["Data de início do exantema"], key=f"data_{selected_idx}")

                        if st.form_submit_button("Salvar alterações"):
                            erros = []
                            if not numero_edit.isdigit():
                                erros.append("Número inválido.")
                            if not idade_edit.isdigit():
                                erros.append("Idade inválida.")
                            try:
                                datetime.strptime(data_edit, "%d/%m/%Y") 
                            except ValueError:
                                erros.append("Data inválida.")

                            if erros:
                                for erro in erros:
                                    st.error(erro)
                            else:
                                st.session_state.df_notificacoes.loc[selected_idx] = [
                                    numero_edit, idade_edit, data_edit
                                ]
                                st.success("Notificação atualizada!")
                                st.rerun() 

    # --- INSERÇÃO DO RODAPÉ DA ABA 2 ---
    st.markdown("---")
    try:
        st.image(logo_url, width=100)
    except Exception as e:
        st.warning(f"Não foi possível carregar a logo de rodapé na Aba Notificações. Erro: {e}")
    # --- FIM DA INSERÇÃO DO RODAPÉ DA ABA 2 ---


# --- ABA 4: Calendário ---
with tab4:
    st.markdown("### Calendário")

    if st.session_state.df_notificacoes.empty:
        st.info("Nenhuma notificação registrada ainda.")
    else:
        df = st.session_state.df_notificacoes.reset_index(drop=True)

        options_indices_calendar = df.index.tolist()
        labels_map_calendar = {
            idx: f'{df.at[idx, "Número de notificação"]} — {df.at[idx, "Data de início do exantema"]}'
            for idx in options_indices_calendar
        }

        selectbox_options_calendar = [None] + options_indices_calendar
        selectbox_labels_calendar = {idx: labels_map_calendar[idx] for idx in options_indices_calendar}
        selectbox_labels_calendar[None] = "Selecione uma notificação para ver o calendário..."

        initial_selection = st.session_state.get("selected_calendar_idx", None)

        selected_idx_for_calendar = st.selectbox(
            "Escolha uma notificação para exibir no calendário:",
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

    # --- INSERÇÃO DO RODAPÉ DA ABA 3 ---
    st.markdown("---")
    try:
        st.image(logo_url, width=100)
    except Exception as e:
        st.warning(f"Não foi possível carregar a logo de rodapé na Aba Calendário. Erro: {e}")
    # --- FIM DA INSERÇÃO DO RODAPÉ DA ABA 3 ---


# ---------------- ABA 5: Linha do tempo ----------------
with tab5:
    st.markdown("### Linha do tempo")

    if st.session_state.df_notificacoes.empty:
        st.info("Nenhuma notificação registrada ainda.")
    else:
        df_plot_base = st.session_state.df_notificacoes.copy()
        df_plot_base['Data de início do exantema'] = pd.to_datetime(df_plot_base['Data de início do exantema'], format='%d/%m/%Y', errors='coerce')

        df_plot_base['ID Genérico'] = range(1, len(df_plot_base) + 1)

        period_colors = {
            "🗣️ Período de transmissibilidade": "#00ffff", # Ciano
            "🫂 Período de exposição": "#ffff00",          # Amarelo
            "💉 Relacionado à vacina": "#00b050",          # Verde
            "🦠 Presença de casos secundários": "#ff9900", # Laranja
            "🩸 Amostral ideal soro": "#ff0000",           # Vermelho
            "👃 Amostral ideal nasal, faríngica ou nasofaríngica": "#7030a0", # Roxo
            "💧 Amostral ideal urina": "#ffffcc",          # Amarelo claro
            "🤒 Início do exantema": "#000000"           # Preto
        }

        plot_data = []

        for index, row in df_plot_base.iterrows():
            data_inicio_exantema_str = row["Data de início do exantema"].strftime("%d/%m/%Y")
            id_generico = row['ID Genérico']
            notificacao_num = row["Número de notificação"]

            events_for_notification = generate_calendar_events(data_inicio_exantema_str)

            for event in events_for_notification:
                start_date = datetime.strptime(event['start'], "%Y-%m-%d")

                plot_data.append({
                    "ID Genérico": id_generico,
                    "Data": start_date,
                    "Período": event['title'],
                    "Cor": period_colors.get(event['title'], '#cccccc'),
                    "Notificação": notificacao_num,
                    "Opacidade": 0.7 
                })

        if plot_data:
            df_plot_events = pd.DataFrame(plot_data)

            notification_options_dict = {
                row['ID Genérico']: f'{row["Número de notificação"]} ({row["Data de início do exantema"].strftime("%d/%m/%Y")})'
                for index, row in df_plot_base.iterrows()
            }

            selected_notification_ids = st.multiselect(
                "Selecione as notificações para visualizar os períodos:",
                options=list(notification_options_dict.keys()),
                format_func=lambda i: notification_options_dict[i],
                default=list(notification_options_dict.keys())
            )

            if selected_notification_ids:
                df_filtered_plot = df_plot_events[
                    df_plot_events['ID Genérico'].isin(selected_notification_ids)
                ]

                fig = go.Figure()

                default_visible_periods = [
                    "🗣️ Período de transmissibilidade",
                    "🫂 Período de exposição",
                    "🦠 Presença de casos secundários",
                    "🤒 Início do exantema"
                ]

                for period in period_colors.keys():
                    df_period = df_filtered_plot[df_filtered_plot['Período'] == period]

                    if not df_period.empty:
                        fig.add_trace(go.Scatter(
                            x=df_period['Data'],
                            y=df_period['ID Genérico'],
                            mode='markers',
                            marker=dict(
                                color=period_colors[period],
                                size=12,
                                opacity=0.7,
                                symbol='circle'
                            ),
                            name=period,
                            hoverinfo='text',
                            hovertext=df_period.apply(
                                lambda row: f"Notificação: {row['Notificação']}<br>Período: {row['Período']}<br>Data: {row['Data'].strftime('%d/%m/%Y')}",
                                axis=1
                            ),
                            visible=True if period in default_visible_periods else 'legendonly'
                        ))

                fig.update_layout(
                    title='Períodos de Eventos por Notificação',
                    xaxis_title='Data',
                    yaxis_title='Número de notificação',
                    yaxis=dict(
                        tickmode='array',
                        tickvals=list(range(1, len(df_plot_base) + 1)),
                        ticktext=[f'{row["Número de notificação"]}' for _, row in df_plot_base.iterrows()],
                        autorange='reversed'
                    ),
                    xaxis=dict(
                        rangeslider_visible=False
                    ),
                    hovermode='closest',
                    legend=dict(title='Períodos'),
                    margin=dict(l=50, r=50, t=100, b=100),
                    height=550,
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Selecione uma ou mais notificações para visualizar os períodos no gráfico.")
        else:
            st.info("Nenhuma notificação registrada para gerar o gráfico.")

    # --- INSERÇÃO DO RODAPÉ DA ABA 4 ---
    st.markdown("---")
    try:
        st.image(logo_url, width=100)
    except Exception as e:
        st.warning(f"Não foi possível carregar a logo de rodapé na Aba Linha do tempo. Erro: {e}")
    # --- FIM DA INSERÇÃO DO RODAPÉ DA ABA 4 ---


# --- NOVA ABA 3: Períodos de investigação ---
with tab3:
    st.markdown("### Períodos de investigação")

    if st.session_state.df_notificacoes.empty:
        st.info("Nenhuma notificação registrada ainda.")
    else:
        df_details = st.session_state.df_notificacoes.reset_index(drop=True)

        # --- Seletor para escolher a notificação ---
        options_indices_details = df_details.index.tolist()
        labels_map_details = {
            idx: f'{df_details.at[idx, "Número de notificação"]} — {df_details.at[idx, "Data de início do exantema"]}'
            for idx in options_indices_details
        }

        selectbox_options_details = [None] + options_indices_details
        selectbox_labels_details = {idx: labels_map_details[idx] for idx in options_indices_details}
        selectbox_labels_details[None] = "Selecione uma notificação para ver os detalhes dos períodos..."

        selected_idx_for_details = st.selectbox(
            "Escolha uma notificação:",
            options=selectbox_options_details,
            format_func=lambda i: selectbox_labels_details.get(i, "Erro ao carregar rótulo")
        )

        # --- Exibição dos Cards dos Períodos ---
        if selected_idx_for_details is not None:
            row = df_details.loc[selected_idx_for_details]
            data_inicio_exantema_str = row["Data de início do exantema"]

            period_details_list = get_period_details(data_inicio_exantema_str)

            if period_details_list:
                # Cria colunas para organizar os cards. Ajuste o número de colunas conforme necessário.
                # Por exemplo, 2 colunas para telas mais largas, 1 para mais estreitas.
                num_cols = 2
                cols = st.columns(num_cols)

                for i, period_info in enumerate(period_details_list):
                    with cols[i % num_cols]: # Distribui os cards pelas colunas
                        st.markdown(f"""
                        <div style="
                            background-color: {period_info['cor']};
                            color: {'#000000' if period_info['cor'] in ['#AAFFFF', '#FFFF59', '#ff9900', '#ffffcc'] else '#FFFFFF'};
                            padding: 15px;
                            border-radius: 10px;
                            margin-bottom: 10px;
                            box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
                        ">
                            <h5 style="margin-top: 0;">{period_info['nome']}</h5>
                            <p style="margin-bottom: 5px;"><strong>Início:</strong> {period_info['data_inicio']}</p>
                            <p><strong>Fim:</strong> {period_info['data_fim']}</p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("Não foi possível obter os detalhes dos períodos para esta notificação.")
        else:
            st.info("Por favor, selecione uma notificação para visualizar os detalhes dos períodos.")

    # --- INSERÇÃO DO RODAPÉ DA ABA 5 ---
    st.markdown("---")
    try:
        st.image(logo_url, width=100)
    except Exception as e:
        st.warning(f"Não foi possível carregar a logo de rodapé na Aba Detalhes dos Períodos. Erro: {e}")
    # --- FIM DA INSERÇÃO DO RODAPÉ DA ABA 5 ---


# In[ ]:




