import streamlit as st
import sqlite3
import os
import base64

# Helper functions
def create_connection():
    conn = sqlite3.connect('school_portal.db')
    return conn

def create_user(username, password, role):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (username, password, role)
        VALUES (?, ?, ?)
    ''', (username, password, role))
    conn.commit()
    conn.close()

def authenticate_user(username, password, role):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username=? AND password=? AND role=?', (username, password, role))
    user = cursor.fetchone()
    conn.close()
    return user

def upload_file(file, title, username):
    if not os.path.exists("uploaded_files"):
        os.makedirs("uploaded_files")
    
    file_path = os.path.join("uploaded_files", file.name)
    with open(file_path, "wb") as f:
        f.write(file.getbuffer())
    
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO documents (title, file_path, uploaded_by)
        VALUES (?, ?, ?)
    ''', (title, file_path, username))
    conn.commit()
    conn.close()

def get_documents():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM documents')
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_document(doc_id, file_path):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM documents WHERE id=?', (doc_id,))
    conn.commit()
    conn.close()
    
    # Remove the file from the file system
    if os.path.exists(file_path):
        os.remove(file_path)

# Streamlit App Configuration
st.set_page_config(page_title="School Portal", layout="centered", initial_sidebar_state="collapsed")

def add_favicon(icon_file):
    with open(icon_file, "rb") as icon_file:
        encoded_icon = base64.b64encode(icon_file.read()).decode()
    
    st.markdown(
        f"""
        <style>
        link[rel="icon"] {{
            content: url(data:image/x-icon;base64,{encoded_icon});
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"jpg"};base64,{encoded_string.decode()});
        background-size: cover;
        background-opacity: 0.5;
    }}
    </style>
    """,
    unsafe_allow_html=True
    )

add_bg_from_local('background.jpg')
add_favicon('favicon.ico')

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['role'] = None
    st.session_state['username'] = None
    st.session_state['current_page'] = 'Login'

def reset_session():
    st.session_state['logged_in'] = False
    st.session_state['role'] = None
    st.session_state['username'] = None
    st.session_state['current_page'] = 'Login'

def show_login_page():
    st.title("Welcome to the School Portal")
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select a page", ["Login", "Register"], key="landing_page")
    
    if page == "Login":
        st.header("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        role = st.selectbox("Role", ["Student", "Admin"], key="login_role")
        
        if st.button("Login", key="login_button"):
            user = authenticate_user(username, password, role)
            if user:
                st.session_state['logged_in'] = True
                st.session_state['role'] = role
                st.session_state['username'] = username
                st.session_state['current_page'] = 'Student' if role == 'Student' else 'Admin'
            else:
                st.error("Invalid credentials")

    elif page == "Register":
        st.header("Register")
        username = st.text_input("Username", key="register_username")
        password = st.text_input("Password", type="password", key="register_password")
        role = st.selectbox("Role", ["Student", "Admin"], key="register_role")
        
        if st.button("Register", key="register_button"):
            if username and password:
                conn = create_connection()
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE username=?', (username,))
                existing_user = cursor.fetchone()
                conn.close()
                
                if existing_user:
                    st.error("Username already exists")
                else:
                    create_user(username, password, role)
                    st.success("User registered successfully")
                    st.session_state['current_page'] = 'Login'
            else:
                st.error("Please fill in all fields")

def show_student_portal():
    st.title("Student Portal")
    st.sidebar.title("Student Menu")
    student_menu = st.sidebar.radio("Select a page", ["View Documents", "Logout"], key="student_menu")

    if student_menu == "View Documents":
        st.subheader("Available Documents")
        documents = get_documents()
        
        if documents:
            cols = st.columns(4)  # Adjust the number of columns as needed
            for i, doc in enumerate(documents):
                with cols[i % 4]:
                    st.image("document.png", use_column_width=True)  # Replace with your preview image or icon
                    st.write(doc[1])
                    with open(doc[2], "rb") as file:
                        st.download_button(
                            label="Download",
                            data=file,
                            file_name=os.path.basename(doc[2]),
                            key=f"download_button_{i}"
                        )
        else:
            st.write("No documents available.")
    
    elif student_menu == "Logout":
        reset_session()

def show_admin_portal():
    st.title("Admin Portal")
    st.sidebar.title("Admin Menu")
    admin_menu = st.sidebar.radio("Select a page", ["Upload Documents", "Manage Documents", "Logout"], key="admin_menu")

    if admin_menu == "Upload Documents":
        st.subheader("Upload Document")
        uploaded_file = st.file_uploader("Choose a file", key="upload_file")
        title = st.text_input("Title of the document", key="upload_title")
        
        if st.button("Upload Document", key="upload_button"):
            if uploaded_file and title:
                upload_file(uploaded_file, title, st.session_state['username'])
                st.success("File uploaded successfully")
            else:
                st.error("Please upload a file and provide a title")
    
    elif admin_menu == "Manage Documents":
        st.subheader("Manage Documents")
        documents = get_documents()
        
        if documents:
            for doc in documents:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(doc[1])
                with col2:
                    if st.button("Delete", key=f"delete_{doc[0]}"):
                        delete_document(doc[0], doc[2])
                        st.success(f"Document '{doc[1]}' deleted successfully")
        else:
            st.write("No documents available.")
    
    elif admin_menu == "Logout":
        reset_session()

# Main logic
if st.session_state['current_page'] == 'Student':
    show_student_portal()
elif st.session_state['current_page'] == 'Admin':
    show_admin_portal()
else:
    show_login_page()
