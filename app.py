import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Debug Mode", layout="wide")

st.title("🛠️ Mode Test Kerosakan")
st.info("Kita test fungsi simpan data dulu.")

# 1. Setup Fail & Folder
DB_FILE = 'data_tickets.csv'

# Check Folder Images
if not os.path.exists("images"):
    try:
        os.makedirs("images")
        st.success("✅ Folder 'images' berjaya dicipta automatik.")
    except Exception as e:
        st.error(f"❌ Gagal buat folder images: {e}")

# 2. Input Simple
col1, col2 = st.columns(2)
nama = col1.text_input("Test Nama", "Ali Test")
model = col2.text_input("Test Model", "Dell Test")

# 3. Butang Test
if st.button("TEKAN SINI UNTUK SIMPAN"):
    st.write("...Sedang memproses...")
    
    try:
        # Cuba baca/buat database
        if not os.path.exists(DB_FILE):
            df = pd.DataFrame(columns=["ID", "Nama", "Model", "Tarikh"])
            df.to_csv(DB_FILE, index=False)
            st.write("📂 Database baru dicipta.")
        else:
            df = pd.read_csv(DB_FILE)
            st.write("📂 Database lama ditemui.")

        # Data Baru
        new_data = {
            "ID": f"TEST-{datetime.now().strftime('%M%S')}",
            "Nama": nama,
            "Model": model,
            "Tarikh": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
        # Cuba Simpan
        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        df.to_csv(DB_FILE, index=False)
        
        st.success("✅ BERJAYA! Data dah masuk CSV.")
        st.dataframe(df.tail(3)) # Tunjuk 3 baris terakhir

    except Exception as e:
        # INI YANG KITA NAK TENGOK (Kalau ada error)
        st.error(f"❌ ERROR DITEMUI: {e}")
        st.write("Sila copy error merah di atas dan bagi pada saya.")
