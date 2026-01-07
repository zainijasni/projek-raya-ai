import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests
import io
import time  # Library untuk fungsi menunggu

# --- KONFIGURASI API ---
try:
    # 1. Setup Gemini (Otak)
    if "GOOGLE_API_KEY" in st.secrets:
        GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=GOOGLE_API_KEY)
        # Guna nama model yang ada dalam akaun awak
        model = genai.GenerativeModel('gemini-flash-latest') 
    else:
        st.error("Google API Key tiada dalam Secrets!")

    # 2. Setup HuggingFace (Pelukis)
    if "HF_API_KEY" in st.secrets:
        HF_API_KEY = st.secrets["HF_API_KEY"]
        # Kita guna model v1-5 yang paling stabil
        HF_API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
        headers = {"Authorization": f"Bearer {HF_API_KEY}"}
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

    response = model.generate_content(prompt_structure)
    return response.text

# --- FUNGSI 2: HUGGINGFACE (LUKIS GAMBAR - VERSI DEGIL) ---
def generate_image_with_hf(prompt_text):
    payload = {"inputs": prompt_text}
    
    # Kita akan cuba 5 KALI secara automatik
    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = requests.post(HF_API_URL, headers=headers, json=payload)
            
            # Kalau berjaya (Status 200)
            if response.status_code == 200:
                return response.content
            
            # Kalau server kata "Loading" (Biasanya ada 'estimated_time')
            elif "estimated_time" in response.text:
                data = response.json()
                wait_time = data.get("estimated_time", 20)
                st.warning(f"Percubaan {attempt+1}/{max_retries}: Server sedang 'warm up'. Menunggu {wait_time:.1f} saat...")
                time.sleep(wait_time) # Kod akan berhenti rehat sekejap di sini
            
            else:
                st.error(f"Error HuggingFace: {response.text}")
                return None
                
        except Exception as e:
            st.error(f"Connection Error: {e}")
            time.sleep(5)
            
    st.error("Maaf, server terlalu sibuk. Sila cuba sebentar lagi.")
    return None

# --- FRONTEND ---
st.set_page_config(page_title="AI Raya Generator", layout="wide")
st.title("🌙 AI Raya Marketing Generator")
st.caption("Powered by Gemini Flash & Stable Diffusion v1.5")

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
            try:
                final_prompt = process_text_with_gemini(product_images_pil, style_images_pil, user_desc)
                status.write("✅ Idea siap! Menghantar ke pelukis...")
                st.code(final_prompt, language="text")
                
                # Panggil fungsi yang dah ada auto-retry
                status.write("🎨 Sedang melukis (Mungkin ambil masa)...")
                image_bytes = generate_image_with_hf(final_prompt)
                
                if image_bytes:
                    generated_image = Image.open(io.BytesIO(image_bytes))
                    st.image(generated_image, caption="Hasil AI")
                    status.update(label="Siap!", state="complete", expanded=False)
                    st.balloons()
                
            except Exception as e:
                st.error(f"Ralat: {e}")
