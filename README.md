
# Streamlit Survey-Tool with LDAP-login

create .streamlit/secrets


```
[ldap]
server_path = "ldap_url"
domain = "your_domain"
search_base = "search_base"
attributes = ["attributes"]
use_ssl = true

[session_state_names]
user = "login_user"
remember_me = "login_remember_me"
```

Start Survey-Tool


```
streamlit run main.py
```
