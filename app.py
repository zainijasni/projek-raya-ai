import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests
import io
import time

# --- KONFIGURASI API ---
try:
    if "GOOGLE_API_KEY" in st.secrets:
        GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=GOOGLE_API_KEY)
        
        # --- TUKAR MODEL KE PRO (KUOTA LAIN) ---
        model = genai.GenerativeModel('gemini-1.5-pro') 
        # ---------------------------------------
    
    if "HF_API_KEY" in st.secrets:
        HF_API_KEY = st.secrets["HF_API_KEY"]
    else:
        st.error("HuggingFace API Key tiada dalam Secrets!")

except Exception as e:
    st.error(f"Ralat Setup: {e}")

# --- FUNGSI GEMINI (VERSI TEXT ONLY - JIMAT KUOTA) ---
def process_text_with_gemini(user_text):
    # Kita tak hantar gambar, kita hantar text je supaya tak kena block
    prompt_structure = [
        "Role: Professional AI Art Prompter.",
        "Task: Create a detailed image generation prompt for Midjourney/Stable Diffusion.",
        "Context: Hari Raya Aidilfitri Marketing.",
        f"USER DESCRIPTION OF PRODUCT & SCENE: {user_text}",
        "INSTRUCTION: Describe the visual scene vividly. Mention lighting, mood, and festive elements.",
        "OUTPUT: A single paragraph of English text."
    ]

    try:
        response = model.generate_content(prompt_structure)
        return response.text
    except Exception as e:
        return f"Error Gemini: {e}"

# --- FUNGSI HUGGINGFACE (MODEL OPENJOURNEY) ---
def generate_image_with_hf(prompt_text):
    # Model: OpenJourney (Gaya Midjourney)
    API_URL = "https://api-inference.huggingface.co/models/prompthero/openjourney"
    
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {"inputs": f"mdjrny-v4 style, {prompt_text}"} 
    
    # Auto-Retry 3 kali
    for attempt in range(3):
        try:
            response = requests.post(API_URL, headers=headers, json=payload)
            
            if response.status_code == 200:
                return response.content
            
            elif response.status_code == 503:
                wait_time = response.json().get("estimated_time", 20)
                st.warning(f"Server tengah loading... tunggu {wait_time:.0f} saat.")
                time.sleep(wait_time)
                continue
            
            else:
                st.error(f"❌ Error Code: {response.status_code}")
                # Kalau 401, maksudnya Token HF salah
                if response.status_code == 401:
                    st.error("TOKEN SALAH: Sila check Secrets HF_API_KEY anda.")
                return None
                
        except Exception as e:
            st.error(f"Connection Error: {e}")
            return None
            
    return None

# --- FRONTEND ---
st.set_page_config(page_title="AI Raya Generator", layout="wide")
st.title("🌙 AI Raya Marketing Generator")
st.caption("Mode: Text-Only Input (Jimat Kuota) + OpenJourney")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Masukkan Bahan")
    # Kita tutup upload gambar untuk prompt (tapi user masih boleh upload utk hiasan)
    st.info("💡 Tips: Tulis deskripsi produk anda dengan jelas di bawah.")
    
    user_desc = st.text_area("Deskripsi Produk & Suasana (Wajib)", 
                             "Contoh: Botol minyak wangi warna emas, atas meja kayu, ada pelita dan ketupat, suasana malam raya yang warm.")
    
    generate_btn = st.button("🚀 Jana Gambar", type="primary")

with col2:
    st.subheader("2. Hasil AI")
    if generate_btn and user_desc:
        
        with st.status("Sedang memproses...", expanded=True) as status:
            # Step 1: Gemini (Text Only)
            status.write("🧠 Gemini Pro sedang menulis prompt...")
            final_prompt = process_text_with_gemini(user_desc)
            
            if "Error" in final_prompt:
                st.error(final_prompt)
                status.update(label="Gemini Gagal (Kuota Habis)", state="error")
            else:
                status.write("✅ Idea siap! Menghantar ke pelukis...")
                st.code(final_prompt, language="text")
                
                # Step 2: HuggingFace
                status.write("🎨 Sedang melukis (OpenJourney)...")
                image_bytes = generate_image_with_hf(final_prompt)
                
                if image_bytes:
                    try:
                        generated_image = Image.open(io.BytesIO(image_bytes))
                        st.image(generated_image, caption="Hasil AI")
                        status.update(label="Siap!", state="complete", expanded=False)
                        st.balloons()
                    except:
                        st.error("Data rosak diterima.")
                else:
                    status.update(label="Gagal", state="error")
