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
    st.session_state.current_theme = "light"
    st.session_state.current_role = "dc"  # Default role: Document Control
    st.session_state.user_name = "An_"
    st.session_state.user_suffix = ""  # Suffix spesial kustom
    
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
    
    if not os.path.exists(filepath):
        return greetings
        
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
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
    hari_lokal = kamus_hari.get(hari_inggris, grid_day:=hari_inggris)
    hari_lokal = kamus_hari.get(hari_inggris, hari_inggris)
    
    panggilan_lengkap = f"{nama} {suffix}".strip() if suffix else nama
    greetings_db = load_greetings()
    
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
        terpilih = "Halo {nama_lengkap}! Selamat bekerja di Universal ATP Generator. Pastikan data terekam dengan baik."
        
    return terpilih.format(nama_lengkap=panggilan_lengkap)

# =============================================================================
# 4. IMPLEMENTASI INTEGRASI TEMA & PERBAIKAN KONTRAS FONT (CSS INJECTION)
# =============================================================================
def apply_theme_style():
    """Menginjeksi CSS kuat untuk menjamin keterbacaan teks di semua mode perangkat"""
    if st.session_state.current_theme == "dark":
        st.markdown("""
            <style>
            .stApp { background-color: #0E1117; color: #FFFFFF; }
            .stButton>button { background-color: #1F2937; color: #10B981; border: 1px solid #10B981; }
            .stButton>button:hover { background-color: #10B981; color: #FFFFFF; }
            
            /* Perbaikan Kontras Komponen Form Mode Gelap */
            div[data-testid="stForm"] { background-color: #1E293B; border: 1px solid #334155; border-radius: 10px; padding: 25px; }
            div[data-testid="stForm"] label p { color: #F3F4F6 !important; font-weight: 600 !important; font-size: 14px !important; }
            div[data-testid="stForm"] input { color: #FFFFFF !important; background-color: #0F172A !important; border: 1px solid #475569 !important; }
            div[data-testid="stForm"] .stMarkdown p { color: #CBD5E1 !important; }
            
            /* Footer Khusus Mode Gelap PC & Mobile */
            .permanent-footer {
                position: fixed; left: 0; bottom: 0; width: 100%;
                background-color: #0F172A; color: #10B981;
                text-align: center; padding: 12px 0; font-size: 14px;
                font-weight: 700; border-top: 2px solid #10B981; z-index: 999;
            }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
            .stApp { background-color: #F9FAFB; color: #1F2937; }
            .stButton>button { background-color: #FFFFFF; color: #059669; border: 1px solid #059669; }
            .stButton>button:hover { background-color: #059669; color: #FFFFFF; }
            
            /* Desain Komponen Form Mode Terang */
            div[data-testid="stForm"] { background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 10px; padding: 25px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
            div[data-testid="stForm"] label p { color: #1F2937 !important; font-weight: 600 !important; font-size: 14px !important; }
            div[data-testid="stForm"] input { color: #1F2937 !important; background-color: #FFFFFF !important; border: 1px solid #D1D5DB !important; }
            
            /* Footer Khusus Mode Terang PC & Mobile */
            .permanent-footer {
                position: fixed; left: 0; bottom: 0; width: 100%;
                background-color: #FFFFFF; color: #059669;
                text-align: center; padding: 12px 0; font-size: 14px;
                font-weight: 700; border-top: 2px solid #059669;
                box-shadow: 0 -2px 10px rgba(0,0,0,0.05); z-index: 999;
            }
            </style>
        """, unsafe_allow_html=True)

apply_theme_style()

# =============================================================================
# 5. STRUKTUR NAVIGASI UTAMA (SIDEBAR CONTROLS)
# =============================================================================
with st.sidebar:
    st.subheader("👤 Kendali Akses & Profil")
    st.session_state.user_name = st.text_input("Nama Pengguna:", value=st.session_state.user_name)
    st.session_state.user_suffix = st.text_input("Suffix Spesial:", value=st.session_state.user_suffix)
    
    st.divider()
    
    st.subheader("⚙️ Ruang Lingkup Kerja")
    role_choice = st.radio("Pilih Hak Akses Halaman:", ["Document Control (DC)", "Administrator System"])
    st.session_state.current_role = "dc" if "DC" in role_choice else "admin"
    
    st.divider()
    
    st.subheader("🎨 Visual Tema")
    theme_toggle = st.toggle("Aktifkan Mode Terang", value=(st.session_state.current_theme == "light"))
    st.session_state.current_theme = "light" if theme_toggle else "dark"
    
    st.divider()
    
    if st.sidebar.button("🔒 Logout Akun"):
        st.toast("Sesi Anda telah diakhiri secara aman.")

# =============================================================================
# 6. PEMBAGIAN BLOK RUANG KERJA & FORM DENGAN PETUNJUK LENGKAP
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
    st.markdown("Silakan lengkapi 16 parameter di bawah ini untuk mengunci data pada lembar `support table` secara otomatis.")
    
    with st.form("form_metadata_proyek"):
        
        # --- BLOK A ---
        st.subheader("🏢 Blok A: Informasi Proyek & Lokasi")
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.metadata["NAMA_PROYEK"] = st.text_input(
                "Nama Proyek", placeholder="Contoh: EMR FTTH PROJECT", 
                help="Masukkan nama proyek utama sesuai kontrak kerja spek pelanggan."
            )
            st.session_state.metadata["NO_PO"] = st.text_input(
                "Nomor Purchase Order (PO)", placeholder="Contoh: PO-2026/06/EMR-01",
                help="Nomor PO resmi sebagai validasi penagihan dokumen."
            )
            st.session_state.metadata["TANGGAL_TEST"] = st.text_input(
                "Tanggal Pelaksanaan Test", placeholder="Contoh: 27 Juni 2026",
                help="Tanggal aktual tim lapangan melakukan pengukuran OPM/OTDR."
            )
        with col2:
            st.session_state.metadata["REGION"] = st.text_input(
                "Region Wilayah", placeholder="Contoh: JAWA TIMUR",
                help="Lokasi provinsi atau cakupan area kerja proyek."
            )
            st.session_state.metadata["ALAMAT"] = st.text_input(
                "Alamat Lengkap Site", placeholder="Contoh: Nglawak Kecamatan Kertosono, Kediri",
                help="Alamat geografi spesifik tempat infrastruktur dipasang."
            )
            
        st.divider()
        
        # --- BLOK B ---
        st.subheader("📡 Blok B: Parameter Jaringan (Network Identifiers)")
        col3, col4 = st.columns(2)
        with col3:
            st.session_state.metadata["NAMA_OLT"] = st.text_input(
                "Nama OLT Host", placeholder="Contoh: KERTOSONO",
                help="Identitas perangkat pusat OLT penyuplai sinyal optik."
            )
            st.session_state.metadata["NAMA_LOKASI"] = st.text_input(
                "Nama Cluster / Subfeeder", placeholder="Contoh: DUSUN BOGO RW 08 FDT-2",
                help="Nama segmen jaringan atau area cakupan cluster distribusi."
            )
            st.session_state.metadata["ID_LOKASI"] = st.text_input(
                "ID Cluster / Subfeeder", placeholder="Contoh: NJK000095",
                help="ID kode unik ekosistem lokasi cluster jaringan."
            )
        with col4:
            st.session_state.metadata["ID_FDT_FROM"] = st.text_input(
                "ID FDT (Link From)", placeholder="Contoh: NJK.100.021.DSBG08-FDT2.019.110",
                help="Kode identitas koneksi hulu (awal penarikan kabel feeder/distribusi)."
            )
            st.session_state.metadata["ID_FAT_TO"] = st.text_input(
                "ID FAT (Link To)", placeholder="Contoh: DSBG08FDT2.019",
                help="Kode identitas kotak terminal distribusi akhir arah pelanggan."
            )
            
        st.divider()
        
        # --- BLOK C ---
        st.subheader("🤝 Blok C: Informasi Stakeholder (Customer & Vendor)")
        col5, col6 = st.columns(2)
        with col5:
            st.session_state.metadata["NAMA_PT_VENDOR"] = st.text_input(
                "Nama Perusahaan Vendor", placeholder="Contoh: PT Buana Menara Indonesia",
                help="Nama resmi perusahaan pelaksana pembangunan infrastruktur."
            )
            st.session_state.metadata["REP_VENDOR"] = st.text_input(
                "Nama Representatif Vendor", placeholder="Contoh: VIFIN ARI P.",
                help="Nama lengkap penanggung jawab dari vendor untuk tanda tangan dokumen."
            )
            st.session_state.metadata["JABATAN_VENDOR"] = st.text_input(
                "Jabatan Pelaksana Vendor", placeholder="Contoh: BMI FIELD SUPERVISOR",
                help="Posisi struktural dari penanggung jawab pihak mitra/vendor."
            )
        with col6:
            st.session_state.metadata["NAMA_PT_CUSTOMER"] = st.text_input(
                "Nama Perusahaan Customer", placeholder="Contoh: PT Ekamas Mora Republik Tbk",
                help="Nama perusahaan pemilik jaringan/pemilik proyek utama."
            )
            st.session_state.metadata["REP_CUSTOMER"] = st.text_input(
                "Nama Representatif Customer", placeholder="Contoh: SUPARMANTO",
                help="Nama pengawas atau direksi resmi dari pihak customer."
            )
            st.session_state.metadata["JABATAN_CUSTOMER"] = st.text_input(
                "Jabatan Pengawas Customer", placeholder="Contoh: EMR FIELD SUPERVISOR",
                help="Posisi struktural dari penanggung jawab pihak customer."
            )
            
        submit_metadata = st.form_submit_button("🔒 Simpan Data Proyek")
        
    if submit_metadata:
        st.success("✅ Data Proyek berhasil diamankan ke dalam memori sistem murni!")

    # =============================================================================
    # SEKTOR 2 - SMART INPUT SEKUENSIAL VERTIKAL WITH GUIDE EXAMPLES
    # =============================================================================
    st.divider()
    st.header("⚙️ Sektor 2: Smart Input (FAT & Tiang)")
    st.info("Gunakan tombol 'Tambah Baris' di bawah masing-masing kategori untuk menambahkan input sekuensial secara bertingkat.")
    
    # --- JALUR FAT ---
    st.subheader("A. Pembangun Jalur FAT (Line Distribution)")
    st.markdown("> 💡 **Panduan & Contoh:** Masukkan kode huruf jalur diikuti total unit. Teks `A10` akan diterjemahkan sistem menjadi urutan **FAT A01 sampai FAT A10** secara murni.")
    
    for i in range(len(st.session_state.fat_commands)):
        st.session_state.fat_commands[i] = st.text_input(
            f"Perintah FAT Jalur ke-{i+1}", 
            value=st.session_state.fat_commands[i], 
            placeholder="Misal: A10 atau B08",
            key=f"fat_input_{i}"
        )
        
    if st.button("➕ Tambah Jalur FAT"):
        st.session_state.fat_commands.append("")
        st.rerun()

    st.write("") 
    st.divider()

        # --- JALUR TIANG ---
    st.subheader("B. Pembangun Tiang (Pole Erection)")
    st.markdown("> 💡 **Panduan & Contoh:** Gunakan awalan kata kunci yang ketat. \n> * `Pole 74 = 10` ➔ Memicu lembar **Pole Erection 74** (10 baris data NEW POLE).\n> * `Ext 74 = 12` ➔ Memicu lembar **Pole Erection Ext 74** (12 baris data EXT POLE).")

    for i in range(len(st.session_state.pole_commands)):
        st.session_state.pole_commands[i] = st.text_input(
            f"Perintah Volume Tiang ke-{i+1}", 
            value=st.session_state.pole_commands[i], 
            placeholder="Misal: Pole 72.5 = 35 atau Ext 74 = 28",
            key=f"pole_input_{i}"
        )

    if st.button("➕ Tambah Rute Tiang"):
        st.session_state.pole_commands.append("")
        st.rerun()

    st.divider()

    # --- PENGUNCI DATA AKHIR ---
    if st.button("💾 Simpan & Validasi Draf Fase 1"):
        fat_bersih = [cmd for cmd in st.session_state.fat_commands if cmd.strip() != ""]
        pole_bersih = [cmd for cmd in st.session_state.pole_commands if cmd.strip() != ""]
        
        st.session_state.fat_commands = fat_bersih if fat_bersih else [""]
        st.session_state.pole_commands = pole_bersih if pole_bersih else [""]
        
        st.success("✅ Seluruh perintah struktur Fase 1 berhasil divalidasi dan dikunci dalam sistem.")
        st.write("**Daftar Jalur FAT Terdaftar:**", fat_bersih)
        st.write("**Daftar Distribusi Tiang Terdaftar:**", pole_bersih)

# =============================================================================
# 7. SUNTIKAN KOMPONEN FOOTER STATIS (HIGH VISIBILITY FOR PC & MOBILE)
# =============================================================================
st.markdown('<div class="permanent-footer">Developed by An_</div>', unsafe_allow_html=True)
