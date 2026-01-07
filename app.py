import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests
import io
# --- TAMBAH BARIS INI UNTUK CHECK VERSION ---
st.warning(f"Versi Google AI yang diinstall: {genai.__version__}") 
# --------------------------------------------
# ... sambung kod lain di bawah ...
# --- DEBUGGING: Tunjukkan Senarai Model ---
try:
    st.subheader("🔍 Diagnostik Model")
    if st.button("Check Model Availability"):
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        st.write("Model yang ditemui:", available_models)
except Exception as e:
    st.error(f"Error Checking Models: {e}")
# ------------------------------------------
# --- KONFIGURASI API (RAHSIA) ---
try:
    # 1. Setup Gemini (Otak)
    if "GOOGLE_API_KEY" in st.secrets:
        GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
    else:
        st.error("Google API Key tiada dalam Secrets!")

    # 2. Setup HuggingFace (Pelukis)
    if "HF_API_KEY" in st.secrets:
        HF_API_KEY = st.secrets["HF_API_KEY"]
        # Kita guna model 'Stable Diffusion XL' (Percuma & Cantik)
        HF_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
        headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    else:
        st.error("HuggingFace API Key tiada dalam Secrets!")

except Exception as e:
    st.error(f"Ralat Setup: {e}")

# --- FUNGSI 1: GEMINI (BUAT TEXT PROMPT) ---
def process_text_with_gemini(product_imgs, style_imgs, user_text):
    prompt_structure = [
        "Role: Professional Commercial Photographer & Art Director.",
        "Task: Create a highly detailed image generation prompt for an AI image generator (Stable Diffusion).",
        "Context: Hari Raya Aidilfitri Marketing Campaign.",
        "INSTRUCTION 1: Describe the MAIN PRODUCT based on the uploaded product image. Focus on its shape, color, and texture.",
        "INSTRUCTION 2: Apply the VIBE/STYLE from the style reference image (lighting, mood, background).",
        "INSTRUCTION 3: Ensure a festive 'Hari Raya' atmosphere (ketupat, pelita, warm lighting, kampung house, or modern luxury).",
        f"USER REQUEST: {user_text}",
        "OUTPUT FORMAT: A single paragraph of English text describing the visual scene. Start with 'A professional product photography of...'",
        "\n--- PRODUCT IMAGES ---"
    ]
    for img in product_imgs: prompt_structure.append(img)
    if style_imgs:
        prompt_structure.append("\n--- STYLE IMAGES ---")
        for img in style_imgs: prompt_structure.append(img)

    response = model.generate_content(prompt_structure)
    return response.text

# --- FUNGSI 2: HUGGINGFACE (LUKIS GAMBAR) ---
def generate_image_with_hf(prompt_text):
    payload = {"inputs": prompt_text}
    response = requests.post(HF_API_URL, headers=headers, json=payload)
    return response.content

# --- FRONTEND (MUKA DEPAN) ---
st.set_page_config(page_title="AI Raya Generator", layout="wide")
st.title("🌙 AI Raya Marketing Generator")
st.markdown("Upload produk anda, AI akan fikirkan idea & lukiskan poster Raya!")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Masukkan Bahan")
    product_files = st.file_uploader("Upload Produk (Wajib)", type=["jpg", "png", "webp"], accept_multiple_files=True)
    style_files = st.file_uploader("Upload Contoh Style (Optional)", type=["jpg", "png", "webp"], accept_multiple_files=True)
    user_desc = st.text_area("Arahan Tambahan", "Contoh: Suasana pagi raya yang ceria, atas meja kayu.")
    generate_btn = st.button("🚀 Jana Gambar Raya", type="primary")

with col2:
    st.subheader("2. Hasil AI")
    if generate_btn and product_files:
        product_images_pil = [Image.open(f) for f in product_files]
        style_images_pil = [Image.open(f) for f in style_files] if style_files else []

        with st.status("Sedang memproses...", expanded=True) as status:
            # Step 1: Gemini fikir prompt
            status.write("🧠 Gemini sedang berfikir idea...")
            try:
                final_prompt = process_text_with_gemini(product_images_pil, style_images_pil, user_desc)
                status.write("✅ Idea siap! Menghantar ke pelukis...")
                st.info(f"Prompt AI: {final_prompt}") # Tunjuk prompt pada user
                
                # Step 2: HuggingFace lukis gambar
                status.write("🎨 Sedang melukis gambar (Mungkin ambil masa 30s)...")
                image_bytes = generate_image_with_hf(final_prompt)
                
                # Step 3: Papar gambar
                try:
                    generated_image = Image.open(io.BytesIO(image_bytes))
                    st.image(generated_image, caption="Hasil Generasi AI Raya")
                    status.update(label="Siap!", state="complete", expanded=False)
                    st.success("Gambar berjaya dihasilkan!")
                except Exception as img_error:
                    st.warning("Gambar gagal dibuka. HuggingFace mungkin sedang 'Loading Model'. Sila tekan butang Jana sekali lagi dalam 20 saat.")
                    st.error(f"Error detail: {image_bytes}")

            except Exception as e:
                st.error(f"Ralat Sistem: {e}")






