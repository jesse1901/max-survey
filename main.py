import sqlite3
import streamlit as st
from ldap3 import Server, Connection, ALL
import json
import toml
import pandas as pd
from datetime import datetime
import time

# Load secrets
secrets = toml.load('.streamlit/secrets.toml')

# LDAP Configuration
LDAP_SERVER = secrets['ldap']['server_path']
SEARCH_BASE = secrets['ldap']['search_base']
USE_SSL = secrets['ldap']['use_ssl']

ALLOWED_USERS = secrets['users']['allowed_users']


def authenticate(username, password):
    if not password:
        st.error("Password cannot be empty")
        return False

    try:
        # Create an LDAP server object
        server = Server(LDAP_SERVER, use_ssl=USE_SSL, get_info=ALL)

        # Adjust this user format according to your LDAP server requirements
        user = f"uid={username},ou=people,ou=rgy,o=desy,c=de"  # Change if necessary

        # Establish a connection
        conn = Connection(server, user=user, password=password.strip())  # Ensure no whitespace in password
        
        if conn.bind():
            return True  # Authentication successful
        else:
            st.error("Invalid username or password")  # Provide feedback for failed login
            return False  # Authentication failed
    except Exception as e:
        st.error(f"LDAP connection error: {e}")
        return False

def is_user_allowed(username):
    return username in ALLOWED_USERS

def get_user_response(username):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('SELECT answer FROM survey_data WHERE username = ?', (username,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def save_data(username, answer):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS survey_data (username TEXT UNIQUE, answer TEXT, timestamp TEXT)')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    c.execute('INSERT INTO survey_data (username, answer, timestamp) VALUES (?, ?, ?) ON CONFLICT(username) DO UPDATE SET answer = ?, timestamp = ?', (username, answer,timestamp, answer, timestamp))
    conn.commit()
    conn.close()

def main():
    st.set_page_config(page_title="Max-Survey")
    user_name = st.session_state.get('user', 'Unbekannter Benutzer')
    
    # Check if user is already authenticated/
    if 'user' in st.session_state:
        left, right = st.columns([3,1])
    
        lang = right.selectbox(
            "Language", 
            ["English", "Deutsch"],
            key="language_selector",  # Optional: key to control state
            help="Select your preferred language.",  # Optional: tooltip
                
                )
    
        with open('texts.json', 'r') as t:
            texts = json.load(t)
        
        with open('question.json',  'r') as quest:
            question = json.load(quest)
            options = [message.format(user_name=user_name) for message in question["survey_options"][lang]]

        left.title(f"{texts['title'][lang]}")
    


        st.write('')
        st.write('')
        st.write(f"{question['question'][lang]}")
        st.markdown("""
            <style>
            .stForm {
                max-width: 500px;  /* Adjust the width as per your need */
                margin: 0 auto;  /* Center the form */
                width: 100%;
                background-color: #1e1e1e;  /* Dark mode background color */
                color: white;  /* Set text color to white for contrast */
                border-radius: 10px;  /* Optional: Add border-radius for rounded corners */
                box-shadow: 2px 2px 12px rgba(0, 0, 0, 0.5);  /* Optional: Add a shadow for depth */
            }
            
            /* Add space between radio options */
            .stRadio label {
                margin-bottom: 15px;  /* Adjust the value for more or less space */
            }
            </style>
        """, unsafe_allow_html=True)

        if 'previous_answer' not in st.session_state:
            st.session_state['previous_answer'] = get_user_response(st.session_state['user'])
        
        if 'success_submit' not in st.session_state:
            st.session_state['success_submit'] = False
        

        previous_answer = st.session_state['previous_answer']

        with st.form("BeeGFS-Survey"):
            radio_question = texts['survey_question'][lang]
            
            if previous_answer in options:
                selected_index = options.index(previous_answer)
            else:
                selected_index = None  
            
            selected_option = st.radio(radio_question, options, index=selected_index)
            submit_button = st.form_submit_button(label="Submit")

        if submit_button:
            save_data(st.session_state['user'], selected_option)
            st.session_state['previous_answer'] = selected_option
            st.success(texts['your_response_recorded'][lang])
            st.session_state['success_submit'] = True
            st.rerun()

        if st.session_state['success_submit']:
            success = st.success(texts['your_response_recorded'][lang])
            st.session_state['submit_success'] = False
            time.sleep(3)
            success.empty()
            
    else:
        st.title("Login BeeGFS Survey")
        form = st.form(key="login_form")
        # Show login form if user is not authenticated
        username = form.text_input("Username")
        password = form.text_input("Password", type="password")
        try:
            if form.form_submit_button("Login"):
                if authenticate(username, password):
                    if is_user_allowed(username):        
                        st.session_state['user'] = username
                        st.success('success')
                        st.rerun()
                    
                    else:
                        st.error("you are not authorized to participate in the survey")    
        except Exception as e:
            st.error("")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error("An unexpected error occurred. Please try again later.")
