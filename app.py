import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests # Kita guna requests balik sebab senang nak debug
import io
import time

# --- KONFIGURASI API ---
try:
    # 1. Setup Gemini (Otak)
    if "GOOGLE_API_KEY" in st.secrets:
        GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-flash-latest') 
    else:
        st.error("Google API Key tiada dalam Secrets!")

    # 2. Setup HuggingFace (Pelukis)
    if "HF_API_KEY" in st.secrets:
        HF_API_KEY = st.secrets["HF_API_KEY"]
    else:
        st.error("HuggingFace API Key tiada dalam Secrets!")

except Exception as e:
    st.error(f"Ralat Setup: {e}")

# --- FUNGSI 1: GEMINI (BUAT TEXT PROMPT) ---
def process_text_with_gemini(product_imgs, style_imgs, user_text):
    prompt_structure = [
        "Role: Professional Commercial Photographer.",
        "Task: Create a highly detailed image generation prompt.",
        "INSTRUCTION: Describe the product in a festive Hari Raya setting.",
        f"USER REQUEST: {user_text}",
        "OUTPUT: A single paragraph of English text.",
        "\n--- PRODUCT IMAGES ---"
    ]
    for img in product_imgs: prompt_structure.append(img)
    if style_imgs:
        for img in style_imgs: prompt_structure.append(img)

    try:
        response = model.generate_content(prompt_structure)
        return response.text
    except Exception as e:
        return f"Error Gemini: {e}"

# --- FUNGSI 2: HUGGINGFACE (LUKIS GAMBAR - DEBUG MODE) ---
def generate_image_with_hf(prompt_text):
    # Guna model public (RunwayML)
    API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {"inputs": prompt_text}

    st.write("📡 Menghubungi Server Pelukis...")
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        
        # JIKA BERJAYA (Kod 200)
        if response.status_code == 200:
            return response.content
        
        # JIKA ERROR, KITa BACA MESEJ DIA
        else:
            st.error(f"❌ Error Code: {response.status_code}")
            st.json(response.json()) # Paparkan raw message dari server
            return None
            
    except Exception as e:
        st.error(f"❌ Connection Error: {e}")
        return None

# --- FRONTEND ---
st.set_page_config(page_title="AI Raya Generator", layout="wide")
st.title("🌙 AI Raya Marketing Generator")
st.caption("Debug Mode Active")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Masukkan Bahan")
    product_files = st.file_uploader("Upload Produk", type=["jpg", "png", "webp"], accept_multiple_files=True)
    style_files = st.file_uploader("Upload Style (Optional)", type=["jpg", "png", "webp"], accept_multiple_files=True)
    user_desc = st.text_area("Arahan", "Contoh: Suasana raya kampung.")
    generate_btn = st.button("🚀 Jana Gambar", type="primary")

with col2:
    st.subheader("2. Hasil AI")
    if generate_btn and product_files:
        product_images_pil = [Image.open(f) for f in product_files]
        style_images_pil = [Image.open(f) for f in style_files] if style_files else []

        with st.status("Sedang memproses...", expanded=True) as status:
            status.write("🧠 Gemini sedang berfikir prompt...")
            final_prompt = process_text_with_gemini(product_images_pil, style_images_pil, user_desc)
            
            if "Error" in final_prompt:
                st.error(final_prompt)
            else:
                status.write("✅ Idea siap! Menghantar ke pelukis...")
                st.code(final_prompt, language="text")
                
                # Panggil fungsi debug
                image_bytes = generate_image_with_hf(final_prompt)
                
                if image_bytes:
                    try:
                        generated_image = Image.open(io.BytesIO(image_bytes))
                        st.image(generated_image, caption="Hasil AI")
                        status.update(label="Siap!", state="complete", expanded=False)
                        st.balloons()
                    except Exception as e:
                        st.error(f"Gagal buka gambar: {e}")
                        st.write(image_bytes) # Tunjuk kalau server hantar sampah
