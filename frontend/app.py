import streamlit as st
import api

st.set_page_config(page_title="DocsInsight AI", layout="wide")

if "token" not in st.session_state:
    st.session_state["token"] = None
if "current_session_id" not in st.session_state:
    st.session_state["current_session_id"] = None
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "selected_doc_id" not in st.session_state:
    st.session_state["selected_doc_id"] = None

def logout():
    st.session_state["token"] = None
    st.session_state["current_session_id"] = None
    st.session_state["messages"] = []
    st.session_state["selected_doc_id"] = None

if not st.session_state["token"]:
    st.title("DocsInsight AI")
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login")
        email = st.text_input("Email", key="log_email")
        password = st.text_input("Password", type="password", key="log_pass")
        if st.button("Login"):
            res = api.login(email, password)
            if res.status_code == 200:
                st.session_state["token"] = res.json()["access_token"]
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid credentials")
                
    with tab2:
        st.subheader("Register")
        new_email = st.text_input("Email", key="reg_email")
        new_password = st.text_input("Password", type="password", key="reg_pass")
        if st.button("Register"):
            res = api.register(new_email, new_password)
            if res.status_code == 200:
                st.success("Registered successfully! Please login.")
            else:
                st.error(res.json().get("detail", "Error registering"))

else:
    # Sidebar: Document Management
    with st.sidebar:
        st.title("Dashboard")
        st.button("Logout", on_click=logout)
        st.divider()
        
        st.subheader("Upload PDF")
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
        if uploaded_file is not None:
            if st.button("Upload"):
                with st.spinner("Uploading & processing..."):
                    res = api.upload_document(st.session_state["token"], uploaded_file.getvalue(), uploaded_file.name)
                    if res.status_code == 200:
                        st.success("Document uploaded & processed!")
                    else:
                        st.error("Error uploading document")
        
        st.divider()
        st.subheader("Your Documents")
        docs_res = api.get_documents(st.session_state["token"])
        if docs_res.status_code == 200:
            documents = docs_res.json()
            if not documents:
                st.info("No documents uploaded yet.")
            else:
                doc_options = {"All Documents (Global Search)": None}
                for d in documents:
                    doc_options[f"{d['filename']} ({d['num_pages']} pages)"] = d['id']
                
                selected_doc = st.selectbox("Select document for chat:", options=list(doc_options.keys()))
                st.session_state["selected_doc_id"] = doc_options[selected_doc]
                
                # Delete functionality
                st.write("Manage:")
                for d in documents:
                    col1, col2 = st.columns([3,1])
                    col1.write(f"📄 {d['filename']}")
                    if col2.button("🗑️", key=f"del_{d['id']}"):
                        api.delete_document(st.session_state["token"], d['id'])
                        st.rerun()
    
    # Main Area: Chat Interface
    st.title("Chat with your PDFs")
    
    # Session handling
    if st.session_state["current_session_id"] is None:
        if st.button("Start New Chat Session"):
            res = api.create_chat_session(st.session_state["token"], st.session_state["selected_doc_id"])
            if res.status_code == 200:
                st.session_state["current_session_id"] = res.json()["id"]
                st.session_state["messages"] = []
                st.rerun()
    
    if st.session_state["current_session_id"]:
        st.caption(f"Session ID: {st.session_state['current_session_id']}")
        
        # Display chat history
        for msg in st.session_state["messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
        # Chat input
        if prompt := st.chat_input("Ask a question about your documents..."):
            st.session_state["messages"].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
                
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    res = api.send_message(
                        st.session_state["token"], 
                        st.session_state["current_session_id"], 
                        prompt, 
                        st.session_state["selected_doc_id"]
                    )
                    if res.status_code == 200:
                        answer = res.json()["content"]
                        st.markdown(answer)
                        st.session_state["messages"].append({"role": "assistant", "content": answer})
                    else:
                        st.error("Failed to get response")
    else:
        st.info("Start a new chat session to begin.")
