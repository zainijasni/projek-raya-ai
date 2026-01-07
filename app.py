import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests # Kita guna posmen biasa je
import io
import time

# --- KONFIGURASI API ---
try:
    if "GOOGLE_API_KEY" in st.secrets:
        GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-flash-latest') 
    
    if "HF_API_KEY" in st.secrets:
        HF_API_KEY = st.secrets["HF_API_KEY"]
    else:
        st.error("HuggingFace API Key tiada dalam Secrets!")

except Exception as e:
    st.error(f"Ralat Setup: {e}")

# --- FUNGSI GEMINI ---
def process_text_with_gemini(product_imgs, style_imgs, user_text):
    prompt_structure = [
        "Role: Photographer.",
        "Task: Create a simple image prompt.",
        "INSTRUCTION: Describe the product in a Hari Raya setting.",
        f"USER REQUEST: {user_text}",
        "OUTPUT: A single short paragraph.",
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

# --- FUNGSI HUGGINGFACE (GUNA REQUESTS + ROUTER) ---
def generate_image_with_hf(prompt_text):
    # INI KUNCI DIA:
    # 1. Guna 'router' (sebab api-inference dah mati)
    # 2. Guna 'runwayml' (sebab SDXL tadi 404/tak jumpa)
    API_URL = "https://router.huggingface.co/models/runwayml/stable-diffusion-v1-5"
    
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {"inputs": prompt_text}
    
    # Kita cuba 3 kali (Auto-Retry)
    for attempt in range(3):
        try:
            response = requests.post(API_URL, headers=headers, json=payload)
            
            # Kalau berjaya (200)
            if response.status_code == 200:
                return response.content
            
            # Kalau server loading (503)
            elif response.status_code == 503:
                wait_time = response.json().get("estimated_time", 20)
                st.warning(f"Server tengah loading... tunggu {wait_time:.0f} saat.")
                time.sleep(wait_time)
                continue # Ulang semula loop
            
            # Kalau error lain, tunjuk terus
            else:
                st.error(f"❌ Error Code: {response.status_code}")
                st.write(response.text) # Tunjuk mesej server
                return None
                
        except Exception as e:
            st.error(f"Connection Error: {e}")
            return None
            
    return None

# --- FRONTEND ---
st.set_page_config(page_title="AI Raya Generator", layout="wide")
st.title("🌙 AI Raya Marketing Generator")
st.caption("Mode: Router URL + RunwayML")

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
                
                status.write("🎨 Sedang melukis...")
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
