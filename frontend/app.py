# frontend/app.py

import streamlit as st
import requests

import os

API_BASE_URL = os.getenv('API_BASE_URL', 'http://nginx/api')
TOKEN = None

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
            global TOKEN
            TOKEN = data["access_token"]
            st.success("Успешный вход.")
            st.session_state.authenticated = True
        else:
            st.error("Неверные учетные данные.")

def ask_question():
    st.title("Задайте вопрос")
    question_text = st.text_input("Ваш вопрос")
    if st.button("Отправить вопрос"):
        headers = {"Authorization": f"Bearer {TOKEN}"}
        response = requests.post(f"{API_BASE_URL}/ask", json={
            "question_text": question_text
        }, headers=headers)
        if response.status_code == 200:
            data = response.json()
            st.success("Вопрос отправлен. ID вопроса: {}".format(data["question_id"]))
        else:
            st.error("Ошибка отправки вопроса.")

def get_answer():
    st.title("Получить ответ")
    question_id = st.number_input("ID вопроса", min_value=1, step=1)
    if st.button("Получить ответ"):
        headers = {"Authorization": f"Bearer {TOKEN}"}
        response = requests.get(f"{API_BASE_URL}/answer/{question_id}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            st.write("Ответ: {}".format(data["answer_text"]))
        else:
            st.error("Ошибка получения ответа.")

def main():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    menu = ["Вход", "Регистрация", "Задать вопрос", "Получить ответ"]

    if st.session_state.authenticated:
        choice = st.sidebar.selectbox("Меню", menu[2:])
        if choice == "Задать вопрос":
            ask_question()
        elif choice == "Получить ответ":
            get_answer()
    else:
        choice = st.sidebar.selectbox("Меню", menu[:2])
        if choice == "Вход":
            login()
        elif choice == "Регистрация":
            register()

if __name__ == '__main__':
    main()
