import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests
import io
import time

# --- KONFIGURASI ---
try:
    if "GOOGLE_API_KEY" in st.secrets:
        GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-flash-latest')
    
    if "HF_API_KEY" in st.secrets:
        HF_API_KEY = st.secrets["HF_API_KEY"]
    else:
        st.error("TIADA HF KEY!")

except Exception as e:
    st.error(f"Setup Error: {e}")

# --- FUNGSI GEMINI ---
def get_gemini_prompt(user_text):
    try:
        # Prompt simple je untuk test
        response = model.generate_content(f"Create a short image prompt for: {user_text}")
        return response.text
    except Exception as e:
        return f"Gemini Error: {e}"

# --- FUNGSI HUGGINGFACE (FORENSIK MODE) ---
def debug_hf_image(prompt_text):
    # Kita guna URL 'Router' yang dia minta tadi
    # Kita guna model SDXL (Paling standard untuk free tier)
    API_URL = "https://router.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {"inputs": prompt_text}
    
    st.write(f"📡 Menghubungi: {API_URL}")
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        
        # CETAK SEMUA INFO UNTUK KITA BACA
        st.write(f"Status Code: {response.status_code}") # 200 = Berjaya, 401 = Token Salah, 503 = Loading
        
        if response.status_code == 200:
            return response.content
        else:
            # Ini yang kita nak baca! Apa server cakap!
            st.error("MESEJ DARI SERVER:")
            st.code(response.text) 
            return None
            
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return None

# --- FRONTEND ---
st.title("🕵️ Mod Forensik AI")
user_input = st.text_input("Taip apa-apa (contoh: Kucing pakai songkok)")
btn = st.button("Test System")

if btn and user_input:
    # 1. Test Gemini
    st.info("1. Testing Gemini...")
    prompt = get_gemini_prompt(user_input)
    st.success(f"Gemini OK: {prompt}")
    
    # 2. Test HuggingFace
    st.info("2. Testing HuggingFace...")
    image_bytes = debug_hf_image(prompt)
    
    if image_bytes:
        try:
            img = Image.open(io.BytesIO(image_bytes))
            st.image(img, caption="BERJAYA!")
            st.balloons()
        except:
            st.error("Dapat data, tapi bukan gambar. (Mungkin error text)")
