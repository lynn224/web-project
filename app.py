import streamlit as st
import datetime
import random
import os

# =============================================================================
# 1. KONFIGURASI HALAMAN UTAMA (UNIVERSAL)
# =============================================================================
st.set_page_config(
    page_title="Universal ATP Document Generator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# 2. INSIALISASI MANAJEMEN SESI (SESSION STATE) - MENJAGA DATA MURNI AMAN
# =============================================================================
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.current_theme = "dark"
    st.session_state.current_role = "dc"  # Default role: Document Control
    st.session_state.user_name = "Anjas"
    st.session_state.user_suffix = "sayang"  # Suffix spesial kustom
    
    # Inisialisasi 16 Variabel Penting Support Table (Fase 1)
    st.session_state.metadata = {
        "NAMA_PROYEK": "",
        "REGION": "",
        "NAMA_LOKASI": "",
        "ID_LOKASI": "",
        "ALAMAT": "",
        "NAMA_OLT": "",
        "ID_FDT_FROM": "",
        "ID_FAT_TO": "",
        "NAMA_PT_VENDOR": "",
        "REP_VENDOR": "",
        "JABATAN_VENDOR": "",
        "NAMA_PT_CUSTOMER": "",
        "REP_CUSTOMER": "",
        "JABATAN_CUSTOMER": "",
        "TANGGAL_TEST": "",
        "NO_PO": ""
    }
    
    # Inisialisasi Kontainer untuk Smart Input Sekuensial Vertikal
    st.session_state.fat_commands = [""]
    st.session_state.pole_commands = [""]

# =============================================================================
# 3. LOGIKA MESIN SAPAAN DINAMIS UNTUK DOCUMENT CONTROL (DC)
# =============================================================================
def load_greetings(filepath="greetings.txt"):
    """Membaca file eksternal database sapaan agar mudah ditambahkan tanpa ubah kode"""
    greetings = {"MINGGU": [], "PAGI": [], "SIANG": [], "SORE": [], "MALAM": []}
    current_section = None
    
    # Jika file tidak ditemukan, kembalikan wadah kosong
    if not os.path.exists(filepath):
        return greetings
        
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Deteksi kategori jam/hari
            if line.startswith("[") and line.endswith("]"):
                current_section = line[1:-1].upper()
            elif current_section in greetings:
                greetings[current_section].append(line)
    return greetings

def generate_dc_greeting(nama, suffix):
    """Membangun kalimat sapaan berdasarkan waktu lokal dan suffix kustom"""
    now = datetime.datetime.now()
    hour = now.hour
    
    hari_inggris = now.strftime("%A")
    kamus_hari = {
        "Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu",
        "Thursday": "Kamis", "Friday": "Jumat", "Saturday": "Sabtu", "Sunday": "Minggu"
    }
    hari_lokal = kamus_hari.get(hari_inggris, hari_inggris)
    
    # Merakit nama lengkap + suffix
    panggilan_lengkap = f"{nama} {suffix}".strip() if suffix else nama
    
    # Panggil database dari TXT
    greetings_db = load_greetings()
    
    # Logika Penentuan Sapaan (Prioritas: Hari Minggu -> Jam Kerja)
    if hari_lokal == "Minggu" and greetings_db["MINGGU"]:
        terpilih = random.choice(greetings_db["MINGGU"])
    elif 0 <= hour < 11 and greetings_db["PAGI"]:
        terpilih = random.choice(greetings_db["PAGI"])
    elif 11 <= hour < 15 and greetings_db["SIANG"]:
        terpilih = random.choice(greetings_db["SIANG"])
    elif 15 <= hour < 19 and greetings_db["SORE"]:
        terpilih = random.choice(greetings_db["SORE"])
    elif greetings_db["MALAM"]:
        terpilih = random.choice(greetings_db["MALAM"])
    else:
        # Teks Cadangan Darurat Jika File Txt Rusak / Kosong
        terpilih = "Halo {nama_lengkap}! Selamat bekerja di Universal ATP Generator. Pastikan data terekam dengan baik."
        
    # Menyuntikkan variabel {nama_lengkap} ke dalam string yang ditarik dari database
    return terpilih.format(nama_lengkap=panggilan_lengkap)

# =============================================================================
# 4. IMPLEMENTASI INTEGRASI TEMA (DARK / LIGHT MODE CSS INJECTION)
# =============================================================================
def apply_theme_style():
    """Menginjeksi CSS untuk mengubah tema antarmuka secara presisi"""
    if st.session_state.current_theme == "dark":
        st.markdown("""
            <style>
            .stApp { background-color: #0E1117; color: #FFFFFF; }
            .stButton>button { background-color: #1F2937; color: #10B981; border: 1px solid #10B981; }
            .stButton>button:hover { background-color: #10B981; color: #FFFFFF; }
            div[data-testid="stForm"] { background-color: #1E293B; border: 1px solid #334155; border-radius: 10px; }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
            .stApp { background-color: #F9FAFB; color: #1F2937; }
            .stButton>button { background-color: #FFFFFF; color: #059669; border: 1px solid #059669; }
            .stButton>button:hover { background-color: #059669; color: #FFFFFF; }
            div[data-testid="stForm"] { background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 10px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
            </style>
        """, unsafe_allow_html=True)

apply_theme_style()

# =============================================================================
# 5. STRUKTUR NAVIGASI UTAMA & FOOTER PERMANEN (STRICT)
# =============================================================================
with st.sidebar:
    st.subheader("👤 Kendali Akses & Profil")
    st.session_state.user_name = st.text_input("Nama Pengguna:", value=st.session_state.user_name)
    st.session_state.user_suffix = st.text_input("Suffix Spesial:", value=st.session_state.user_suffix)
    
    st.divider()
    
    # Pengatur Akun & Role (Admin vs DC)
    st.subheader("⚙️ Ruang Lingkup Kerja")
    role_choice = st.radio("Pilih Hak Akses Halaman:", ["Document Control (DC)", "Administrator System"])
    st.session_state.current_role = "dc" if "DC" in role_choice else "admin"
    
    st.divider()
    
    # Sakelar Toggle Dark / Light Mode
    st.subheader("🎨 Estetika Visual")
    theme_toggle = st.toggle("Aktifkan Light Mode", value=(st.session_state.current_theme == "light"))
    st.session_state.current_theme = "light" if theme_toggle else "dark"
    
    st.divider()
    
    # Simulasi Logout Akun
    if st.sidebar.button("🔒 Logout Akun"):
        st.toast("Sesi Anda telah diakhiri secara aman.")

# =============================================================================
# 6. PEMBAGIAN BLOK RUANG KERJA (BERDASARKAN ROLE)
# =============================================================================
st.title("⚡ Universal ATP Document Generator")

if st.session_state.current_role == "admin":
    st.header("🛠️ Panel Kendali Administrator")
    st.info("Halaman konfigurasi threshold splitting template dan batas kapasitas sel akan diletakkan di modul ini pada tahap selanjutnya.")
else:
    # --- TAMPILAN KHUSUS DOCUMENT CONTROL (DC) ---
    current_greeting = generate_dc_greeting(st.session_state.user_name, st.session_state.user_suffix)
    st.info(current_greeting)
    
    st.header("📋 Form Identitas Proyek (Fase 1)")
    
    # Membungkus form agar halaman tidak me-refresh setiap kali DC mengetik
    with st.form("form_metadata_proyek"):
        
        st.subheader("🏢 Blok A: Informasi Proyek & Lokasi")
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.metadata["NAMA_PROYEK"] = st.text_input("Nama Proyek", value="EMR FTTH PROJECT")
            st.session_state.metadata["NO_PO"] = st.text_input("Nomor PO")
            st.session_state.metadata["TANGGAL_TEST"] = st.text_input("Tanggal Test")
        with col2:
            st.session_state.metadata["REGION"] = st.text_input("Region", value="JAWA TIMUR")
            st.session_state.metadata["ALAMAT"] = st.text_input("Alamat Lengkap", value="Pare, Jawa Timur")
            
        st.divider()
        
        st.subheader("📡 Blok B: Parameter Jaringan")
        col3, col4 = st.columns(2)
        with col3:
            st.session_state.metadata["NAMA_OLT"] = st.text_input("Nama OLT")
            st.session_state.metadata["NAMA_LOKASI"] = st.text_input("Nama Cluster / Subfeeder")
            st.session_state.metadata["ID_LOKASI"] = st.text_input("ID Cluster / Subfeeder")
        with col4:
            st.session_state.metadata["ID_FDT_FROM"] = st.text_input("ID FDT (Link From)")
            st.session_state.metadata["ID_FAT_TO"] = st.text_input("ID FAT (Link To)")
            
        st.divider()
        
        st.subheader("🤝 Blok C: Informasi Stakeholder")
        col5, col6 = st.columns(2)
        with col5:
            st.session_state.metadata["NAMA_PT_VENDOR"] = st.text_input("Nama Perusahaan Vendor", value="PT Buana Menara Indonesia")
            st.session_state.metadata["REP_VENDOR"] = st.text_input("Nama Rep. Vendor")
            st.session_state.metadata["JABATAN_VENDOR"] = st.text_input("Jabatan Vendor", value="BMI FIELD SUPERVISOR")
        with col6:
            st.session_state.metadata["NAMA_PT_CUSTOMER"] = st.text_input("Nama Perusahaan Customer", value="PT Ekamas Mora Republik Tbk")
            st.session_state.metadata["REP_CUSTOMER"] = st.text_input("Nama Rep. Customer", value="Suparmanto")
            st.session_state.metadata["JABATAN_CUSTOMER"] = st.text_input("Jabatan Customer", value="EMR FIELD SUPERVISOR")
            
        # Tombol Eksekusi
        submit_metadata = st.form_submit_button("Simpan Data Proyek")
        
    if submit_metadata:
        st.success("Data Proyek berhasil diamankan ke dalam memori sistem murni!")

# =============================================================================
# 7. SUNTIKAN KOMPONEN FOOTER STATIS (STRICT LAYOUT)
# =============================================================================
st.markdown("""
    <style>
    .permanent-footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: transparent;
        color: #6B7280;
        text-align: center;
        padding: 10px 0;
        font-size: 13px;
        font-weight: 500;
        z-index: 999;
        pointer-events: none;
    }
    </style>
    <div class="permanent-footer">Developed by An_</div>
""", unsafe_allow_html=True)
