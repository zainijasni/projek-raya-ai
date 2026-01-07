import streamlit as st

import google.generativeai as genai

from PIL import Image



# --- KONFIGURASI API ---

# Nanti ingatkan saya untuk masukkan API KEY sebenar

GOOGLE_API_KEY = "MASUKKAN_API_KEY_ANDA_DI_SINI"



try:

    genai.configure(api_key=GOOGLE_API_KEY)

    model = genai.GenerativeModel('gemini-1.5-flash')

except Exception as e:

    st.error(f"Ralat Konfigurasi API Key: {e}")



# --- FUNGSI UTAMA ---

def process_images_with_gemini(product_imgs, style_imgs, user_text):

    prompt_structure = [

        "Bertindak sebagai Pengarah Kreatif Pemasaran & Pengiklanan Profesional.", 

        "Tugas: Hasilkan prompt visual untuk kempen pemasaran HARI RAYA AIDILFITRI.",

        "Gabungkan subjek utama (Produk) dengan gaya rujukan (Style/Vibe).",

        "ARAHAN 1: KEKALKAN rupa bentuk produk asal (balang kuih/baju/perabot/dll) dari GAMBAR PRODUK.",

        "ARAHAN 2: AMBIL suasana/lighting dari GAMBAR RUJUKAN GAYA.",

        "ARAHAN 3: Pastikan mood 'Hari Raya' itu terserlah (suasana ceria, mewah, atau kampung).",

        f"ARAHAN KHUSUS USER: {user_text}",

        "OUTPUT: Satu perenggan prompt imej dalam Bahasa Inggeris yang sangat detail.",

        "\n--- GAMBAR PRODUK UTAMA ---"

    ]

    for img in product_imgs: prompt_structure.append(img)



    if style_imgs:

        prompt_structure.append("\n--- GAMBAR RUJUKAN GAYA/VIBE ---")

        for img in style_imgs: prompt_structure.append(img)



    response = model.generate_content(prompt_structure)

    return response.text



# --- FRONTEND ---

st.set_page_config(page_title="Sistem Pemasaran Raya AI", layout="wide")

st.title("🌙 Sistem Ajaib Pemasaran Raya AI")

st.markdown("Bantu peniaga hasilkan gambar promosi Raya yang padu (Baju, Kuih, Hiasan, dll).")



with st.sidebar:

    st.header("Input Peniaga")

    product_files = st.file_uploader("1. Upload Gambar Produk Anda (Wajib)", type=["jpg", "png", "webp"], accept_multiple_files=True)

    style_files = st.file_uploader("2. Upload Gambar Contoh/Vibe (Optional)", type=["jpg", "png", "webp"], accept_multiple_files=True)

    user_desc = st.text_area("3. Apa yang anda nak?", "Contoh: Letak balang kuih tart ni atas meja kayu kampung, ada pelita di belakang, lighting suam (warm).")

    generate_btn = st.button("🚀 Jana Idea & Gambar", type="primary")



if generate_btn and product_files:

    product_images_pil = [Image.open(f) for f in product_files]

    style_images_pil = [Image.open(f) for f in style_files] if style_files else []



    with st.spinner("AI sedang memerah idea Raya..."):

        try:

            final_prompt = process_images_with_gemini(product_images_pil, style_images_pil, user_desc)

            st.success("Prompt Siap! Sedia untuk dijana.")

            with st.expander("Lihat Prompt (Copy ini jika perlu)"):

                st.code(final_prompt)

            

            st.subheader("Simulasi Hasil (Belum sambung Image Generator)")

            cols = st.columns(4)

            for i, col in enumerate(cols):

                col.image(f"https://placehold.co/300x400/png?text=Konsep+Raya+{i+1}", caption=f"Variasi {i+1}")

        except Exception as e:

            st.error(f"Ralat: {e}")