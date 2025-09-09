#!/usr/bin/env python
# coding: utf-8

# In[4]:


import streamlit as st
from streamlit_calendar import calendar
from datetime import datetime, date, timedelta
import pandas as pd

# CONFIGURAÇÃO
st.set_page_config(layout="wide")

# Inicializa DataFrame no session_state
if "df_notificacoes" not in st.session_state:
    st.session_state.df_notificacoes = pd.DataFrame(
        columns=["Número de notificação", "Idade", "Data de início do exantema"]
    )

# ---------------- TABS ----------------
tab1, tab2, tab3 = st.tabs(["Apresentação", "Entrada de Dados", "Calendário"])

# ---------------- ABA 1: APRESENTAÇÃO ----------------
with tab1:
    st.title("Calculadora de Casos")
    st.markdown("""
    Bem-vindo à calculadora interativa!  
    Nesta aplicação você poderá:  
    - Registrar notificações de casos  
    - Visualizar dados em um calendário  
    - Acompanhar informações detalhadas
    """)
    st.image("https://cdn-icons-png.flaticon.com/512/2910/2910760.png", width=200)

# ---------------- ABA 2: ENTRADA DE DADOS ----------------
with tab2:
    col1, col2, col3 = st.columns([1, 2, 1])  # centraliza formulário

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
                data_exantema = datetime.strptime(data_exantema_str, "%d/%m/%Y")
            except ValueError:
                erros.append("Data de início do exantema inválida. Use DD/MM/AAAA.")

            if erros:
                for erro in erros:
                    st.error(erro)
            else:
                # adiciona linha ao DataFrame
                st.session_state.df_notificacoes = pd.concat([
                    st.session_state.df_notificacoes,
                    pd.DataFrame([{
                        "Número de notificação": numero_notificacao,
                        "Idade": idade,
                        "Data de início do exantema": data_exantema.strftime("%d/%m/%Y")
                    }])
                ], ignore_index=True)
                st.success("Formulário enviado com sucesso!")

        # -----------------------------------
        # Tabela de notificações e ações
        st.markdown("### Notificações Registradas")
        st.dataframe(st.session_state.df_notificacoes)

        if not st.session_state.df_notificacoes.empty:
            st.markdown("### Gerenciar Notificações")

            # seleciona qual registro quer alterar/remover
            notif_selec = st.selectbox(
                "Escolha o número de notificação para alterar ou remover:",
                st.session_state.df_notificacoes["Número de notificação"].tolist()
            )

            col_remover, col_editar = st.columns([1, 1])

            # ------------------ REMOVER ------------------
            with col_remover:
                if st.button("Remover notificação", key=f"remover_{notif_selec}"):
                    # remove a linha
                    st.session_state.df_notificacoes = st.session_state.df_notificacoes[
                        st.session_state.df_notificacoes["Número de notificação"] != notif_selec
                    ]
                    st.success(f"Notificação {notif_selec} removida!")

            # ------------------ EDITAR ------------------
            with col_editar:
                if st.button("Editar notificação", key=f"editar_{notif_selec}"):
                    # pega a linha selecionada
                    row = st.session_state.df_notificacoes[
                        st.session_state.df_notificacoes["Número de notificação"] == notif_selec
                    ].iloc[0]

                    # inputs pré-preenchidos com os valores atuais
                    numero_edit = st.text_input("Número de notificação", value=row["Número de notificação"], key=f"num_{notif_selec}")
                    idade_edit = st.text_input("Idade", value=row["Idade"], key=f"idade_{notif_selec}")
                    data_edit = st.text_input("Data de início do exantema (DD/MM/AAAA)", value=row["Data de início do exantema"], key=f"data_{notif_selec}")

                    if st.button("Salvar alterações", key=f"salvar_{notif_selec}"):
                        erros = []
                        if not numero_edit.isdigit():
                            erros.append("Número de notificação deve conter apenas números.")
                        if not idade_edit.isdigit():
                            erros.append("Idade deve conter apenas números.")
                        try:
                            datetime.strptime(data_edit, "%d/%m/%Y")
                        except ValueError:
                            erros.append("Data de início do exantema inválida. Use DD/MM/AAAA.")

                        if erros:
                            for erro in erros:
                                st.error(erro)
                        else:
                            # atualiza o DataFrame
                            st.session_state.df_notificacoes.loc[
                                st.session_state.df_notificacoes["Número de notificação"] == notif_selec,
                                ["Número de notificação", "Idade", "Data de início do exantema"]
                            ] = [numero_edit, idade_edit, data_edit]
                            st.success(f"Notificação {notif_selec} atualizada!")

# ---------------- ABA 3: CALENDÁRIO ----------------
with tab3:
    st.markdown("### Filtrar Notificação")
    if st.session_state.df_notificacoes.empty:
        st.info("Nenhuma notificação registrada ainda.")
    else:
        # selectbox para escolher a notificação
        notificacao_selecionada = st.selectbox(
            "Escolha o número de notificação:",
            st.session_state.df_notificacoes["Número de notificação"].tolist()
        )

        # filtra DataFrame para a notificação selecionada
        df_filtrado = st.session_state.df_notificacoes[
            st.session_state.df_notificacoes["Número de notificação"] == notificacao_selecionada
        ]

        # cria eventos principais + período de transmissibilidade
        calendar_events = []
        for _, row in df_filtrado.iterrows():
            data_inicio = datetime.strptime(row["Data de início do exantema"], "%d/%m/%Y")

            # Período de transmissibilidade: 6 dias antes até 4 dias depois
            for delta in range(-6, 5):
                data_evento = data_inicio + timedelta(days=delta)
                calendar_events.append({
                    "title": "🗣️ Período de transmissibilidade",
                    "start": data_evento.strftime("%Y-%m-%d"),
                    "end": data_evento.strftime("%Y-%m-%d"),
                    "color": "#00ffff",
                    "textColor": "#000000",
                    "allDay": True,
                })

            # Período de exposição: 21 dias antes até 7 dias antes do início do exantema
            for delta in range(-21, -6):
                data_evento = data_inicio + timedelta(days=delta)
                calendar_events.append({
                    "title": "🫂 Período de exposição",
                    "start": data_evento.strftime("%Y-%m-%d"),
                    "end": data_evento.strftime("%Y-%m-%d"),
                    "color": "#ffff00",
                    "textColor": "#000000",
                    "allDay": True,
                })

            # Período relacionado a vacina: 14 dias antes até 7 dias antes do início do exantema
            for delta in range(-14, -6):
                data_evento = data_inicio + timedelta(days=delta)
                calendar_events.append({
                    "title": "💉 Relacionado à vacina",
                    "start": data_evento.strftime("%Y-%m-%d"),
                    "end": data_evento.strftime("%Y-%m-%d"),
                    "color": "#00b050",
                    "textColor": "#000000",
                    "allDay": True,
                })

            # Período de presença de casos secundários: até 25 dias depois do início do exantema
            for delta in range(0, 26):
                data_evento = data_inicio + timedelta(days=delta)
                calendar_events.append({
                    "title": "🦠 Presença de casos secundários",
                    "start": data_evento.strftime("%Y-%m-%d"),
                    "end": data_evento.strftime("%Y-%m-%d"),
                    "color": "#ff9900",
                    "allDay": True,
                })

            # Período de coleta ideal amostra de soro: até 31 dias depois do início do exantema
            for delta in range(0, 31):
                data_evento = data_inicio + timedelta(days=delta)
                calendar_events.append({
                    "title": "🩸 Amostral ideal soro",
                    "start": data_evento.strftime("%Y-%m-%d"),
                    "end": data_evento.strftime("%Y-%m-%d"),
                    "color": "#ff0000",
                    "allDay": True,
                })

            # Período de coleta ideal amostra nasal: até 14 dias depois do início do exantema
            for delta in range(0, 15):
                data_evento = data_inicio + timedelta(days=delta)
                calendar_events.append({
                    "title": "👃 Amostral ideal nasal, faríngica ou nasofaríngica",
                    "start": data_evento.strftime("%Y-%m-%d"),
                    "end": data_evento.strftime("%Y-%m-%d"),
                    "color": "#7030a0",
                    "allDay": True,
                })

            # Período de coleta ideal amostra urina: até 10 dias depois do início do exantema
            for delta in range(0, 11):
                data_evento = data_inicio + timedelta(days=delta)
                calendar_events.append({
                    "title": "💧 Amostral ideal urina",
                    "start": data_evento.strftime("%Y-%m-%d"),
                    "end": data_evento.strftime("%Y-%m-%d"),
                    "color": "#ffffcc",
                    "textColor": "#000000",
                    "allDay": True,
                })

            # Evento principal da notificação
            calendar_events.append({
                "title": "🤒 Início do exantema",
                "start": data_inicio.strftime("%Y-%m-%d"),
                "end": data_inicio.strftime("%Y-%m-%d"),
                "color": "#000000",
                "textColor": "#FFFFFF",
                "allDay": True,
            })

        # opções do calendário
        calendar_options = {
            "editable": False,
            "selectable": False,
            "locale": "pt-br",
            "headerToolbar": {"left": "title"},
            "buttonText": {"today": "Hoje", "month": "Mês", "week": "Semana", "day": "Dia"},
            "initialView": "dayGridMonth",
            "initialDate": data_inicio.strftime("%Y-%m-%d"),  # 👈 abre na data do exantema
            "height": 800,
        }

        custom_css = """
            .fc {
                max-width: 100% !important;
                max-height: 100% !important;
                margin: 0 auto;
            }
            .fc-toolbar-title {
                font-size: 2rem;
            }
            .fc-event-title {
                font-weight: 700;
            }
        """

        # renderiza calendário direto na tab
        calendar(
            events=calendar_events,
            options=calendar_options,
            custom_css=custom_css,
            key=f"calendar_{notificacao_selecionada}"
        )

