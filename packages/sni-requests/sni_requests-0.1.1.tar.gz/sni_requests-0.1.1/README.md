# `sni_requests`: A Simple SNI Spoofing Wrapper for `requests`

This module is a **drop-in wrapper around `requests`** that lets you spoof or disable [SNI (Server Name Indication)](https://wikipedia.org/wiki/Server_Name_Indication) during HTTPS connections.

> **Why?** Some servers behave differently based on the SNI hostname. This can be used to **bypass security rules**, **test edge cases**, or **mimic unusual clients**.

---

## 🚀 Installation

Just drop `sni_requests.py` in your project folder. It uses `requests` and `urllib3`, which you probably already have.

```bash
pip install requests urllib3
```

---

## 🧠 Quick Start

### ✅ Normal request (like `requests.get`)
```python
from sni_requests import get

r = get("https://example.com")
print(r.status_code)
```

### 🕵️‍♂️ SNI Spoofing
Send SNI for a different hostname than the URL.
```python
r = get("https://1.2.3.4", sni="example.com")
print(r.text)
```

Send text SNI that are not domains
```python
r = get("https://1.2.3.4", sni="hello world")
print(r.text)
```

### 🚫 Disable SNI
Send no SNI at all (unusual, but possible).
```python
r = get("https://example.com", no_sni=True)
print(r.status_code)
```

---

## 🧰 All Methods Supported

Use any HTTP verb you like:

```python
from sni_requests import post, put, delete, patch, head, options

# spoofed POST
r = post("https://1.2.3.4", sni="api.example.com", json={"hello": "world"})
```

---

## 🧵 Want more control?

Use the `Session` class directly:

```python
from sni_requests import Session

session = Session(sni="example.com")
r = session.get("https://1.2.3.4")
session.close()
```

---

👨‍💻 Built by zen for hackers, testers, and tinkerers.
