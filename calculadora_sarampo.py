#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
from streamlit_calendar import calendar
from datetime import datetime, date, timedelta
import pandas as pd

# CONFIGURAÇÃO
st.set_page_config(layout="wide")

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
                                 "color": "#00ffff",
                                 "textColor": "#000000",
                                 "allDay": True, })

    # Período de exposição: 21 dias antes até 7 dias antes
    for delta in range(-21, -6):
        data_evento = data_inicio + timedelta(days=delta)
        calendar_events.append({ "title": "🫂 Período de exposição",
                                 "start": data_evento.strftime("%Y-%m-%d"),
                                 "end": data_evento.strftime("%Y-%m-%d"),
                                 "color": "#ffff00",
                                 "textColor": "#000000",
                                 "allDay": True, })

    # Relacionado à vacina: 14 dias antes até 7 dias antes
    for delta in range(-14, -6):
        data_evento = data_inicio + timedelta(days=delta)
        calendar_events.append({ "title": "💉 Relacionado à vacina",
                                 "start": data_evento.strftime("%Y-%m-%d"),
                                 "end": data_evento.strftime("%Y-%m-%d"),
                                 "color": "#00b050",
                                 "textColor": "#000000",
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
                                 "color": "#ff0000",
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
        "initialDate": datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d"),
        "height": 800,
    }

    # Incrementa o contador para forçar a atualização do componente com uma nova chave
    st.session_state.calendar_update_counter += 1

    # Usa o contador na chave para garantir que o componente seja recriado com novos eventos
    calendar(events=calendar_events, options=calendar_options, key=f"calendar_{selected_idx}_{st.session_state.calendar_update_counter}")

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["Apresentação", "Entrada de Dados", "Calendário"])

# --- ABA 1: Apresentação ---
with tab1:
    st.title("Calculadora de Casos")
    st.markdown("""
    Bem-vindo à calculadora interativa!
    - Registrar notificações de casos
    - Visualizar dados em um calendário
    - Acompanhar informações detalhadas
    """)
    st.image("https://cdn-icons-png.flaticon.com/512/2910/2910760.png", width=200)

# --- ABA 2: Entrada de Dados ---
with tab2:
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("### Formulário de Notificação")
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

        st.markdown("### Notificações Registradas")
        st.dataframe(st.session_state.df_notificacoes)

        if not st.session_state.df_notificacoes.empty:
            st.markdown("### Gerenciar Notificações")

            df = st.session_state.df_notificacoes.reset_index(drop=True)

            # --- Configuração do Selectbox para Seleção e Edição ---
            # Cria opções para o selectbox, incluindo um placeholder 'None' para início em branco
            options_indices = [None] + df.index.tolist()
            labels_map = {
                idx: f'{df.at[idx, "Número de notificação"]} — {df.at[idx, "Data de início do exantema"]}'
                for idx in df.index.tolist()
            }
            labels_map[None] = "Selecione uma notificação..." # Rótulo para a opção inicial em branco

            selected_idx = st.selectbox(
                "Escolha uma notificação para gerenciar:",
                options=options_indices,
                format_func=lambda i: labels_map.get(i, "Erro ao carregar rótulo")
            )

            # Só mostra as opções de remover/editar se um índice válido for selecionado
            if selected_idx is not None: 
                col_remover, col_editar = st.columns([1, 1])

                # REMOVER
                with col_remover:
                    if st.button("Remover", key=f"remover_{selected_idx}"):
                        st.session_state.df_notificacoes.drop(selected_idx, inplace=True)
                        st.session_state.df_notificacoes.reset_index(drop=True, inplace=True)
                        st.success("Notificação removida!")
                        st.rerun() # Atualiza após remover

                # EDIÇÃO
                with col_editar:
                    # Novo formulário para edição, com chave única para cada linha
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
                                datetime.strptime(data_edit, "%d/%m/%Y") # Validação de formato
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
                                st.rerun() # Atualiza após salvar

# --- ABA 3: Calendário ---
with tab3:
    st.markdown("### Visualizar Calendário")

    if st.session_state.df_notificacoes.empty:
        st.info("Nenhuma notificação registrada ainda.")
    else:
        df = st.session_state.df_notificacoes.reset_index(drop=True)

        # --- Configuração do Selectbox para Visualização do Calendário ---
        options_indices_calendar = df.index.tolist()
        labels_map_calendar = {
            idx: f'{df.at[idx, "Número de notificação"]} — {df.at[idx, "Data de início do exantema"]}'
            for idx in options_indices_calendar
        }

        # Cria as opções para o selectbox do calendário, incluindo o placeholder
        selectbox_options_calendar = [None] + options_indices_calendar
        selectbox_labels_calendar = {idx: labels_map_calendar[idx] for idx in options_indices_calendar}
        selectbox_labels_calendar[None] = "Selecione uma notificação para ver o calendário..."

        # Se um índice já foi selecionado e está armazenado no session_state, use-o como valor inicial
        # Isso ajuda a evitar a renderização desnecessária quando o script roda pela primeira vez
        initial_selection = st.session_state.get("selected_calendar_idx", None)

        selected_idx_for_calendar = st.selectbox(
            "Escolha uma notificação para exibir no calendário:",
            options=selectbox_options_calendar,
            format_func=lambda i: selectbox_labels_calendar.get(i, "Erro ao carregar rótulo"),
            index=selectbox_options_calendar.index(initial_selection) if initial_selection in selectbox_options_calendar else 0 # Define o índice inicial
        )

        # Armazena a seleção atual no session_state
        st.session_state["selected_calendar_idx"] = selected_idx_for_calendar

        # Renderiza o calendário apenas se um índice de notificação válido foi selecionado
        if selected_idx_for_calendar is not None:
            row = df.loc[selected_idx_for_calendar]

            # --- Gerar e Plotar o Calendário ---
            try:
                calendar_events = generate_calendar_events(row["Data de início do exantema"])

                calendar_options = {
                    "editable": False,
                    "selectable": False,
                    "locale": "pt-br",
                    "headerToolbar": {"left": "title"},
                    "initialView": "dayGridMonth",
                    "initialDate": datetime.strptime(row["Data de início do exantema"], "%d/%m/%Y").strftime("%Y-%m-%d"),
                    "height": 800,
                }

                # A chave do calendário agora inclui o índice selecionado E o contador.
                # O contador só muda quando o `selected_idx_for_calendar` muda.
                # Isso garante que o componente só será recriado quando o item selecionado mudar.
                calendar(
                    events=calendar_events,
                    options=calendar_options,
                    key=f"calendar_{selected_idx_for_calendar}_{st.session_state.calendar_update_counter}"
                )

            except Exception as e:
                st.error(f"Erro ao gerar ou exibir o calendário: {e}")
        else:
            st.info("Por favor, selecione uma notificação para visualizar o calendário.")

