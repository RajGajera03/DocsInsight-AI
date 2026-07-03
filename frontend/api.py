import requests

BASE_URL = "https://docsinsight-ai.onrender.com/api"

def login(email, password):
    # OAuth2 Password Request Form needs x-www-form-urlencoded
    data = {"username": email, "password": password}
    response = requests.post(f"{BASE_URL}/auth/login", data=data)
    return response

def register(email, password):
    data = {"email": email, "password": password}
    response = requests.post(f"{BASE_URL}/auth/register", json=data)
    return response

def get_headers(token):
    return {"Authorization": f"Bearer {token}"}

def upload_document(token, file_bytes, filename):
    files = {"file": (filename, file_bytes, "application/pdf")}
    response = requests.post(f"{BASE_URL}/documents/upload", headers=get_headers(token), files=files)
    return response

def get_documents(token):
    response = requests.get(f"{BASE_URL}/documents/", headers=get_headers(token))
    return response

def delete_document(token, doc_id):
    response = requests.delete(f"{BASE_URL}/documents/{doc_id}", headers=get_headers(token))
    return response

def create_chat_session(token, document_id=None):
    data = {"document_id": document_id}
    response = requests.post(f"{BASE_URL}/chat/sessions", headers=get_headers(token), json=data)
    return response

def get_chat_history(token):
    response = requests.get(f"{BASE_URL}/chat/history", headers=get_headers(token))
    return response

def send_message(token, session_id, question, document_id=None):
    data = {
        "session_id": session_id,
        "question": question,
        "document_id": document_id
    }
    response = requests.post(f"{BASE_URL}/chat/", headers=get_headers(token), json=data)
    return response
