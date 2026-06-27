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
        
        parsed_fat = parse_all_fat(fat_bersih)
        parsed_poles = parse_all_poles(pole_bersih)
        
        st.session_state.parsed_fat = parsed_fat
        st.session_state.parsed_poles = parsed_poles
        
        st.success("✅ Seluruh perintah struktur Fase 1 berhasil divalidasi dan diterjemahkan oleh sistem.")
        
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.write(f"**Hasil Terjemahan Jalur FAT (Total: {len(parsed_fat)} titik):**")
            st.info(", ".join(parsed_fat) if parsed_fat else "Tidak ada data FAT")
        with col_res2:
            st.write("**Hasil Terjemahan Distribusi Tiang:**")
            if parsed_poles:
                for pole in parsed_poles:
                    st.success(f"Tipe: **{pole['type']}** | Ukuran: **{pole['size']}** | Jumlah: **{pole['qty']}** batang")
            else:
                st.info("Tidak ada data Tiang")
                
        # -----------------------------------------------------------------
        # MODUL LIVE GENERATOR EXCEL DOWNLOAD BUTTON
        # -----------------------------------------------------------------
        st.divider()
        st.subheader("📥 Unduh File Hasil Sinkronisasi Dokumen")
        
        # Menyediakan File Uploader di layar agar DC bisa memasukkan Template Master kapan saja
        uploaded_template = st.file_uploader("Unggah Master Template Excel (Template_Cluster.xlsx)", type=["xlsx"])
        
        if         if uploaded_template is not None:
import streamlit as st
import datetime
import random
import os
import io

# Memanggil otak mesin dari file lain
from parser_engine import parse_all_fat, parse_all_poles
from excel_injector import inject_excel_fase1

# =============================================================================
# KONFIGURASI DAN KAMUS PILIHAN BAWAAN (FALLBACK METADATA)
# =============================================================================
DEFAULT_METADATA = {
    "NAMA_PROYEK": "EMR FTTH PROJECT",
    "REGION": "JAWA TIMUR",
    "NAMA_LOKASI": "DUSUN BOGO RW 08 FDT-2",
    "ID_LOKASI": "NJK000095",
    "ALAMAT": "Nglawak Kecamatan Kertosono",
    "NAMA_OLT": "KERTOSONO",
    "ID_FDT_FROM": "NJK.100.021.DSBG08-FDT2.019.110",
    "ID_FAT_TO": "DSBG08FDT2.019",
    "NAMA_PT_VENDOR": "PT Buana Menara Indonesia",
    "REP_VENDOR": "ERFIN FIRMANSYAH",
    "JABATAN_VENDOR": "BMI FIELD SUPERVISOR",
    "NAMA_PT_CUSTOMER": "PT Ekamas Mora Republik Tbk",
    "REP_CUSTOMER": "M. NUGROHO",
    "JABATAN_CUSTOMER": "EMR FIELD SUPERVISOR",
    "TANGGAL_TEST": "2026-06-27",
    "NO_PO": "PO-EMR-2026-001"
}

st.set_page_config(
    page_title="Universal ATP Document Generator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# INSIALISASI MANAJEMEN SESI (DIUBAH MENJADI KOSONG)
# =============================================================================
if "initialized" not in st.session_state:
    st.initialized = True
    st.session_state.current_theme = "dark"
    st.session_state.current_role = "dc"
    st.session_state.user_name = "Anjas"
    st.session_state.user_suffix = "sayang"
    
    # Dikosongkan total agar tidak perlu menghapus manual di halaman web
    st.session_state.metadata = {key: "" for key in DEFAULT_METADATA.keys()}
    
    st.session_state.fat_commands = [""]
    st.session_state.pole_commands = [""]

# =============================================================================
# LOGIKA MESIN SAPAAN DAN TEMA
# =============================================================================
def load_greetings(filepath="greetings.txt"):
    greetings = {"MINGGU": [], "PAGI": [], "SIANG": [], "SORE": [], "MALAM": []}
    current_section = None
    if not os.path.exists(filepath): return greetings
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            if line.startswith("[") and line.endswith("]"):
                current_section = line[1:-1].upper()
            elif current_section in greetings:
                greetings[current_section].append(line)
    return greetings

def generate_dc_greeting(nama, suffix):
    now = datetime.datetime.now()
    hour = now.hour
    hari_lokal = now.strftime("%A")
    kamus_hari = {"Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu", "Thursday": "Kamis", "Friday": "Jumat", "Saturday": "Sabtu", "Sunday": "Minggu"}
    hari_lokal = kamus_hari.get(hari_lokal, hari_lokal)
    panggilan_lengkap = f"{nama} {suffix}".strip() if suffix else nama
    greetings_db = load_greetings()
    
    if hari_lokal == "Minggu" and greetings_db["MINGGU"]: terpilih = random.choice(greetings_db["MINGGU"])
    elif 0 <= hour < 11 and greetings_db["PAGI"]: terpilih = random.choice(greetings_db["PAGI"])
    elif 11 <= hour < 15 and greetings_db["SIANG"]: terpilih = random.choice(greetings_db["SIANG"])
    elif 15 <= hour < 19 and greetings_db["SORE"]: terpilih = random.choice(greetings_db["SORE"])
    elif greetings_db["MALAM"]: terpilih = random.choice(greetings_db["MALAM"])
    else: terpilih = "Halo {nama_lengkap}! Selamat bekerja di Universal ATP Generator."
    return terpilih.format(nama_lengkap=panggilan_lengkap)

if st.session_state.current_theme == "dark":
    st.markdown("""<style>.stApp { background-color: #0E1117; color: #FFFFFF; } .stButton>button { background-color: #1F2937; color: #10B981; border: 1px solid #10B981; } .stButton>button:hover { background-color: #10B981; color: #FFFFFF; } div[data-testid="stForm"] { background-color: #1E293B; border: 1px solid #334155; border-radius: 10px; padding: 25px; } div[data-testid="stForm"] label p { color: #F3F4F6 !important; font-weight: 600 !important; font-size: 14px !important; } div[data-testid="stForm"] input { color: #FFFFFF !important; background-color: #0F172A !important; border: 1px solid #475569 !important; } div[data-testid="stForm"] .stMarkdown p { color: #CBD5E1 !important; } .permanent-footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #0F172A; color: #10B981; text-align: center; padding: 12px 0; font-size: 14px; font-weight: 700; border-top: 2px solid #10B981; z-index: 999; }</style>""", unsafe_allow_html=True)
else:
    st.markdown("""<style>.stApp { background-color: #F9FAFB; color: #1F2937; } .stButton>button { background-color: #FFFFFF; color: #059669; border: 1px solid #059669; } .stButton>button:hover { background-color: #059669; color: #FFFFFF; } div[data-testid="stForm"] { background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 10px; padding: 25px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); } div[data-testid="stForm"] label p { color: #1F2937 !important; font-weight: 600 !important; font-size: 14px !important; } div[data-testid="stForm"] input { color: #1F2937 !important; background-color: #FFFFFF !important; border: 1px solid #D1D5DB !important; } .permanent-footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #FFFFFF; color: #059669; text-align: center; padding: 12px 0; font-size: 14px; font-weight: 700; border-top: 2px solid #059669; box-shadow: 0 -2px 10px rgba(0,0,0,0.05); z-index: 999; }</style>""", unsafe_allow_html=True)

# =============================================================================
# CONTROL PANEL SIDEBAR
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

# =============================================================================
# FORM INPUT METADATA
# =============================================================================
if st.session_state.current_role == "admin":
    st.header("🛠️ Panel Kendali Administrator")
    st.info("Halaman konfigurasi threshold splitting template.")
else:
    st.info(generate_dc_greeting(st.session_state.user_name, st.session_state.user_suffix))
    st.header("📋 Form Identitas Proyek (Fase 1)")
    
    with st.form("form_metadata_proyek"):
        st.subheader("🏢 Blok A: Informasi Proyek & Lokasi")
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.metadata["NAMA_PROYEK"] = st.text_input("Nama Proyek", value=st.session_state.metadata["NAMA_PROYEK"], placeholder=DEFAULT_METADATA["NAMA_PROYEK"])
            st.session_state.metadata["NO_PO"] = st.text_input("Nomor PO", value=st.session_state.metadata["NO_PO"], placeholder=DEFAULT_METADATA["NO_PO"])
            st.session_state.metadata["TANGGAL_TEST"] = st.text_input("Tanggal Test", value=st.session_state.metadata["TANGGAL_TEST"], placeholder=DEFAULT_METADATA["TANGGAL_TEST"])
        with col2:
            st.session_state.metadata["REGION"] = st.text_input("Region", value=st.session_state.metadata["REGION"], placeholder=DEFAULT_METADATA["REGION"])
            st.session_state.metadata["ALAMAT"] = st.text_input("Alamat Lengkap", value=st.session_state.metadata["ALAMAT"], placeholder=DEFAULT_METADATA["ALAMAT"])
            
        st.divider()
        st.subheader("📡 Blok B: Parameter Jaringan")
        col3, col4 = st.columns(2)
        with col3:
            st.session_state.metadata["NAMA_OLT"] = st.text_input("Nama OLT", value=st.session_state.metadata["NAMA_OLT"], placeholder=DEFAULT_METADATA["NAMA_OLT"])
            st.session_state.metadata["NAMA_LOKASI"] = st.text_input("Nama Cluster / Subfeeder", value=st.session_state.metadata["NAMA_LOKASI"], placeholder=DEFAULT_METADATA["NAMA_LOKASI"])
            st.session_state.metadata["ID_LOKASI"] = st.text_input("ID Cluster / Subfeeder", value=st.session_state.metadata["ID_LOKASI"], placeholder=DEFAULT_METADATA["ID_LOKASI"])
        with col4:
            st.session_state.metadata["ID_FDT_FROM"] = st.text_input("ID FDT (Link From)", value=st.session_state.metadata["ID_FDT_FROM"], placeholder=DEFAULT_METADATA["ID_FDT_FROM"])
            st.session_state.metadata["ID_FAT_TO"] = st.text_input("ID FAT (Link To)", value=st.session_state.metadata["ID_FAT_TO"], placeholder=DEFAULT_METADATA["ID_FAT_TO"])
            
        st.divider()
        st.subheader("🤝 Blok C: Informasi Stakeholder")
        col5, col6 = st.columns(2)
        with col5:
            st.session_state.metadata["NAMA_PT_VENDOR"] = st.text_input("Nama Perusahaan Vendor", value=st.session_state.metadata["NAMA_PT_VENDOR"], placeholder=DEFAULT_METADATA["NAMA_PT_VENDOR"])
            st.session_state.metadata["REP_VENDOR"] = st.text_input("Nama Rep. Vendor", value=st.session_state.metadata["REP_VENDOR"], placeholder=DEFAULT_METADATA["REP_VENDOR"])
            st.session_state.metadata["JABATAN_VENDOR"] = st.text_input("Jabatan Vendor", value=st.session_state.metadata["JABATAN_VENDOR"], placeholder=DEFAULT_METADATA["JABATAN_VENDOR"])
        with col6:
            st.session_state.metadata["NAMA_PT_CUSTOMER"] = st.text_input("Nama Perusahaan Customer", value=st.session_state.metadata["NAMA_PT_CUSTOMER"], placeholder=DEFAULT_METADATA["NAMA_PT_CUSTOMER"])
            st.session_state.metadata["REP_CUSTOMER"] = st.text_input("Nama Rep. Customer", value=st.session_state.metadata["REP_CUSTOMER"], placeholder=DEFAULT_METADATA["REP_CUSTOMER"])
            st.session_state.metadata["JABATAN_CUSTOMER"] = st.text_input("Jabatan Customer", value=st.session_state.metadata["JABATAN_CUSTOMER"], placeholder=DEFAULT_METADATA["JABATAN_CUSTOMER"])
            
        submit_metadata = st.form_submit_button("Simpan Data Proyek")
        if submit_metadata:
            st.success("Data Proyek berhasil disimpan!")

    # =============================================================================
    # SEKTOR 2 - SMART INPUT
    # =============================================================================
    st.divider()
    st.header("⚙️ Sektor 2: Smart Input (FAT & Tiang)")
    
    st.subheader("A. Pembangun Jalur FAT")
    for i in range(len(st.session_state.fat_commands)):
        st.session_state.fat_commands[i] = st.text_input(f"Perintah FAT Baris ke-{i+1}", value=st.session_state.fat_commands[i], key=f"fat_input_{i}")
    if st.button("➕ Tambah Jalur FAT"):
        st.session_state.fat_commands.append("")
        st.rerun()

    st.divider()

    st.subheader("B. Pembangun Tiang")
    for i in range(len(st.session_state.pole_commands)):
        st.session_state.pole_commands[i] = st.text_input(f"Perintah Tiang Baris ke-{i+1}", value=st.session_state.pole_commands[i], key=f"pole_input_{i}")
    if st.button("➕ Tambah Rute Tiang"):
        st.session_state.pole_commands.append("")
        st.rerun()

    st.divider()

    if st.button("💾 Simpan & Validasi Draf Fase 1"):
        fat_bersih = [cmd for cmd in st.session_state.fat_commands if cmd.strip() != ""]
        pole_bersih = [cmd for cmd in st.session_state.pole_commands if cmd.strip() != ""]
        
        st.session_state.fat_commands = fat_bersih if fat_bersih else [""]
        st.session_state.pole_commands = pole_bersih if pole_bersih else [""]
        
        st.session_state.parsed_fat = parse_all_fat(fat_bersih)
        st.session_state.parsed_poles = parse_all_poles(pole_bersih)
        st.session_state.is_validated = True 
        st.success("✅ Seluruh perintah struktur Fase 1 berhasil divalidasi.")

    # =============================================================================
    # AREA GENERATOR EXCEL (FIXED CLOSED FILE IO ERROR)
    # =============================================================================
    if st.session_state.get("is_validated", False):
        st.divider()
        st.subheader("📥 Unduh File Hasil Sinkronisasi Dokumen")
        
        uploaded_template = st.file_uploader("Unggah File Template (.xlsx)", type=["xlsx"])
        
        if uploaded_template is not None:
            if "processed_cluster" not in st.session_state or st.session_state.get("last_template") != uploaded_template.name:
                try:
                    with st.spinner("Merakit struktur dokumen secara aman..."):
                        # SOLUSI: Ekstrak stream berkas menjadi data biner mentah murni sekali saja
                        raw_template_bytes = uploaded_template.read()
                        
                        # Gabungkan input form dengan kamus default jika kosong (Option Fallback)
                        actual_metadata = {}
                        for key, val in st.session_state.metadata.items():
                            actual_metadata[key] = val.strip() if val.strip() else DEFAULT_METADATA[key]
                        
                        # Kirim memori bytes yang segar ke rute kloning Cluster
                        excel_cluster = inject_excel_fase1(
                            io.BytesIO(raw_template_bytes), 
                            actual_metadata, 
                            st.session_state.parsed_fat, 
                            st.session_state.parsed_poles,
                            mode="cluster"
                        )
                        st.session_state.processed_cluster = excel_cluster.getvalue()
                        
                        # Kirim memori bytes yang segar ke rute kloning Subfeeder
                        excel_subfeeder = inject_excel_fase1(
                            io.BytesIO(raw_template_bytes), 
                            actual_metadata, 
                            st.session_state.parsed_fat, 
                            st.session_state.parsed_poles,
                            mode="subfeeder"
                        )
                        st.session_state.processed_subfeeder = excel_subfeeder.getvalue()
                        
                        st.session_state.last_template = uploaded_template.name
                        
                    st.success("✨ Pemrosesan Berkas Selesai! Silakan unduh dokumen di bawah ini.")
                except Exception as e:
                    st.error(f"Terjadi kegagalan pemrosesan struktur file: {str(e)}")
            
            if "processed_cluster" in st.session_state and "processed_subfeeder" in st.session_state:
                # Menggunakan fallback penamaan file jika input kosong
                nama_lokasi = st.session_state.metadata.get('NAMA_LOKASI', '').strip() or DEFAULT_METADATA["NAMA_LOKASI"]
                    
                col_dl1, col_dl2 = st.columns(2)
                with col_dl1:
                    st.download_button(
                        label="🚀 UNDUH DRAF CLUSTER",
                        data=st.session_state.processed_cluster,
                        file_name=f"DOC CW ATP CLUSTER {nama_lokasi}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                with col_dl2:
                    st.download_button(
                        label="🚀 UNDUH DRAF SUBFEEDER",
                        data=st.session_state.processed_subfeeder,
                        file_name=f"DOC CW ATP SUBFEEDER {nama_lokasi}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )

st.markdown('<div class="permanent-footer">Developed by An_</div>', unsafe_allow_html=True)
