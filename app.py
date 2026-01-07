import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- SETUP AWAL ---
st.set_page_config(page_title="Sistem Repair Kedai", layout="wide")

# Fail Database Kita (CSV)
DB_FILE = 'data_tickets.csv'

# Fungsi 1: Load Data dari CSV
def load_data():
    if not os.path.exists(DB_FILE):
        # Kalau fail belum wujud, kita create rangka dia
        df = pd.DataFrame(columns=["ID", "Tarikh", "Customer", "Phone", "Model", "Masalah", "Status", "Kos", "Image_Path"])
        df.to_csv(DB_FILE, index=False)
        return df
    else:
        return pd.read_csv(DB_FILE)

# Fungsi 2: Simpan Data Baru
def save_data(data_baru):
    df = load_data()
    # Convert data baru jadi DataFrame dan gabung
    new_entry = pd.DataFrame([data_baru])
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(DB_FILE, index=False)

# --- SIDEBAR MENU ---
st.sidebar.title("🔧 Repair System v1")
menu = st.sidebar.radio("Menu Utama", ["Dashboard", "Daftar Tiket Baru", "Inventory & Stok"])

# --- MODUL 1: DASHBOARD ---
if menu == "Dashboard":
    st.title("📊 Dashboard Status Repair")
    
    # Tarik data terkini
    df = load_data()
    
    # Kira Statistik
    total_pending = len(df[df['Status'] == 'Pending'])
    total_waiting = len(df[df['Status'] == 'Waiting Part'])
    total_done = len(df[df['Status'] == 'Done'])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Pending Check", total_pending, "Perlu tindakan segera")
    col2.metric("Waiting Part", total_waiting, "Tunggu barang")
    col3.metric("Siap (Done)", total_done, "Boleh pickup")

    st.divider()
    st.subheader("Senarai Laptop Ongoing")
    
    # Tunjuk table data sebenar
    if not df.empty:
        # Warnakan status supaya nampak jelas
        def color_status(val):
            color = 'red' if val == 'Pending' else 'orange' if val == 'Waiting Part' else 'green'
            return f'color: {color}'
        
        st.dataframe(df.style.applymap(color_status, subset=['Status']), use_container_width=True)
    else:
        st.info("Belum ada data repair. Sila daftar tiket baru.")

# --- MODUL 2: DAFTAR TIKET ---
elif menu == "Daftar Tiket Baru":
    st.title("📝 Daftar Repair Baru")

    with st.form("repair_form"):
        col_a, col_b = st.columns(2)
        
        with col_a:
            nama = st.text_input("Nama Customer")
            phone = st.text_input("No. Phone")
        
        with col_b:
            model = st.text_input("Model Laptop/PC")
            masalah = st.text_area("Masalah (Complaint)")
        
        st.divider()
        st.subheader("📸 Keadaan Fizikal Device")
        gambar = st.camera_input("Tangkap Gambar")
        
        st.divider()
        st.subheader("Syarat & Peraturan (T&C)")
        tc_agreed = st.checkbox("Saya setuju dengan 5 Terma & Syarat kedai.")
        
        submit = st.form_submit_button("Simpan Tiket")
        
        if submit:
            if not nama or not model:
                st.error("Nama dan Model wajib isi!")
            elif not tc_agreed:
                st.error("Sila tick T&C untuk teruskan.")
            else:
                # Generate ID Unik (Guna Tarikh+Masa)
                ticket_id = f"REP-{datetime.now().strftime('%d%H%M')}"
                
                # Handle Gambar (Simpan dalam folder images)
                img_path = "Tiada Gambar"
                if gambar:
                    img_path = f"images/{ticket_id}.jpg"
                    with open(img_path, "wb") as f:
                        f.write(gambar.getbuffer())
                
                # Data untuk disimpan
                data_entry = {
                    "ID": ticket_id,
                    "Tarikh": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Customer": nama,
                    "Phone": phone,
                    "Model": model,
                    "Masalah": masalah,
                    "Status": "Pending",
                    "Kos": 0.0,
                    "Image_Path": img_path
                }
                
                save_data(data_entry)
                st.success(f"✅ Tiket {ticket_id} Berjaya Disimpan!")
                st.balloons()

# --- MODUL 3: INVENTORY (Placeholder) ---
elif menu == "Inventory & Stok":
    st.title("📦 Inventory")
    st.write("Modul ini akan dibangunkan lepas Modul Tiket stabil.")
