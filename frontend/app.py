import streamlit as st
import requests

import os

API_BASE_URL = os.getenv('API_BASE_URL', 'http://nginx/api')

def register():
    st.title("Регистрация")
    username = st.text_input("Имя пользователя")
    password = st.text_input("Пароль", type="password")
    if st.button("Зарегистрироваться"):
        response = requests.post(f"{API_BASE_URL}/register", json={
            "username": username,
            "password": password
        })
        if response.status_code == 200:
            st.success("Успешная регистрация. Теперь вы можете войти.")
        else:
            st.error("Ошибка регистрации.")

def login():
    st.title("Вход")
    username = st.text_input("Имя пользователя")
    password = st.text_input("Пароль", type="password")
    if st.button("Войти"):
        response = requests.post(f"{API_BASE_URL}/login", json={
            "username": username,
            "password": password
        })
        if response.status_code == 200:
            data = response.json()
            # Store the token in session state
            st.session_state["token"] = data["access_token"]
            st.success("Успешный вход.")
            # Set the authenticated flag
            st.session_state.authenticated = True
            # Force a rerun to update the interface
            st.experimental_rerun()
        else:
            st.error("Неверные учетные данные.")

def ask_question():
    st.title("Задайте вопрос")
    question_text = st.text_input("Ваш вопрос")
    if st.button("Отправить вопрос"):
        # Retrieve the token from session state
        TOKEN = st.session_state.get("token")
        if TOKEN is None:
            st.error("Необходимо войти в систему.")
            return
        headers = {"Authorization": f"Bearer {TOKEN}"}
        response = requests.post(f"{API_BASE_URL}/ask", json={
            "question_text": question_text
        }, headers=headers)
        if response.status_code == 200:
            data = response.json()
            st.success(f"Вопрос отправлен. ID вопроса: {data['question_id']}")
        else:
            st.error("Ошибка отправки вопроса.")

def get_answer():
    st.title("Получить ответ")
    question_id = st.number_input("ID вопроса", min_value=1, step=1)
    if st.button("Получить ответ"):
        # Retrieve the token from session state
        TOKEN = st.session_state.get("token")
        if TOKEN is None:
            st.error("Необходимо войти в систему.")
            return
        headers = {"Authorization": f"Bearer {TOKEN}"}
        response = requests.get(f"{API_BASE_URL}/answer/{question_id}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            st.write(f"Ответ: {data['answer_text']}")
        else:
            st.error("Ошибка получения ответа.")

def main():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        menu = ["Задать вопрос", "Получить ответ"]
    else:
        menu = ["Вход", "Регистрация"]

    choice = st.sidebar.selectbox("Меню", menu)

    if st.session_state.authenticated:
        if choice == "Задать вопрос":
            ask_question()
        elif choice == "Получить ответ":
            get_answer()
    else:
        if choice == "Вход":
            login()
        elif choice == "Регистрация":
            register()

if __name__ == '__main__':
    main()
