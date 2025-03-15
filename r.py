import streamlit as st
import subprocess
import time

st.title("Convert URL ke Ngrok dengan Streamlit")

# Input untuk memasukkan URL server
server_url = st.text_input("Masukkan URL Server:", "http://52.65.152.167:8000/")

if st.button("Convert ke Ngrok"):
    st.write("Menjalankan Ngrok...")

    # Menjalankan Ngrok untuk port 8000
    ngrok_process = subprocess.Popen(["ngrok", "http", "8000"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Tunggu beberapa detik agar Ngrok bisa menghasilkan URL
    time.sleep(3)

    # Ambil URL publik dari Ngrok
    ngrok_url = subprocess.check_output(["curl", "-s", "http://127.0.0.1:4040/api/tunnels"])
    ngrok_url = eval(ngrok_url.decode("utf-8"))["tunnels"][0]["public_url"]

    # Tampilkan hasilnya
    st.success(f"Ngrok URL: {ngrok_url}")
    st.write(f"Akses server AWS dengan Ngrok di sini: [🔗 {ngrok_url}]({ngrok_url})")
