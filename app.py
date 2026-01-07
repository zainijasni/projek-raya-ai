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
        
        # GUNA NAMA SPESIFIK DARI LIST AWAK
        model = genai.GenerativeModel('gemini-flash-latest') 
    
    if "HF_API_KEY" in st.secrets:
        HF_API_KEY = st.secrets["HF_API_KEY"]
    else:
        st.error("HuggingFace API Key tiada dalam Secrets!")

except Exception as e:
    st.error(f"Ralat Setup: {e}")

# --- FUNGSI GEMINI (TENGOK GAMBAR + TEXT) ---
def process_multimodal_gemini(product_imgs, user_text):
    prompt_structure = [
        "Role: Professional Commercial Photographer.",
        "Task: Create a vivid image generation prompt based on this product.",
        "Context: Hari Raya Aidilfitri Marketing Campaign.",
        "INSTRUCTION 1: Analyze the product image (shape, color, label). Keep the product identity clear.",
        "INSTRUCTION 2: Place the product in a beautiful Hari Raya setting (Example: Wooden kampung table, pelita lights, ketupat, warm warm lighting).",
        f"USER REQUEST: {user_text}",
        "OUTPUT: A single paragraph of English text describing the scene for Stable Diffusion.",
        "\n--- PRODUCT IMAGES ---"
    ]
    for img in product_imgs: prompt_structure.append(img)

    try:
        response = model.generate_content(prompt_structure)
        return response.text
    except Exception as e:
        if "429" in str(e):
            return "QUOTA_LIMIT"
        return f"Error Gemini: {e}"

# --- FUNGSI HUGGINGFACE (MODEL OPENJOURNEY) ---
def generate_image_with_hf(prompt_text):
    # Model: OpenJourney (Midjourney Style)
    API_URL = "https://api-inference.huggingface.co/models/prompthero/openjourney"
    
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {"inputs": f"mdjrny-v4 style, {prompt_text}"} 
    
    for attempt in range(3):
        try:
            response = requests.post(API_URL, headers=headers, json=payload)
            
            if response.status_code == 200:
                return response.content
            
            elif response.status_code == 503:
                wait_time = response.json().get("estimated_time", 15)
                st.warning(f"Server tengah loading... tunggu {wait_time:.0f} saat.")
                time.sleep(wait_time)
                continue
            
            else:
                st.error(f"❌ Error Code: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            st.error(f"Connection Error: {e}")
            return None
    return None

# --- FRONTEND ---
st.set_page_config(page_title="AI Raya Generator", layout="wide")
st.title("🌙 AI Raya Marketing Generator")
st.caption("Upload Gambar Produk -> AI Buat Latar Belakang Raya")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Masukkan Bahan")
    product_files = st.file_uploader("Upload Gambar Produk (Wajib)", type=["jpg", "png", "webp"], accept_multiple_files=True)
    user_desc = st.text_area("Arahan Tambahan", "Contoh: Letak atas meja kayu, suasana malam raya, ada lampu pelita.")
    generate_btn = st.button("🚀 Jana Gambar", type="primary")

with col2:
    st.subheader("2. Hasil AI")
    if generate_btn and product_files:
        product_images_pil = [Image.open(f) for f in product_files]

        with st.status("Sedang memproses...", expanded=True) as status:
            status.write("🧠 Gemini (Flash Latest) sedang menganalisa produk...")
            final_prompt = process_multimodal_gemini(product_images_pil, user_desc)
            
            if final_prompt == "QUOTA_LIMIT":
                status.update(label="Kuota Gemini Habis!", state="error")
                st.error("⚠️ Kuota Google Gemini anda dah limit. Sila cuba esok atau guna API Key baru.")
            
            elif "Error" in final_prompt:
                st.error(final_prompt)
                status.update(label="Ralat Gemini", state="error")
            
            else:
                status.write("✅ Analisa siap! Menghantar ke pelukis...")
                with st.expander("Tengok Prompt AI"):
                    st.write(final_prompt)
                
                status.write("🎨 Sedang melukis (OpenJourney)...")
                image_bytes = generate_image_with_hf(final_prompt)
                
                if image_bytes:
                    try:
                        generated_image = Image.open(io.BytesIO(image_bytes))
                        st.image(generated_image, caption="Hasil AI")
                        status.update(label="Siap!", state="complete", expanded=False)
                        st.balloons()
                    except:
                        st.error("Gagal memproses gambar.")
                else:
                    status.update(label="Gagal", state="error")
