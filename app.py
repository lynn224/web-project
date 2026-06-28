import streamlit as st
import datetime
import random
import os
import io
import json
import re
import traceback
import pandas as pd

from excel_injector import inject_excel_fase1

TEMPLATE_PATH = "Template.xlsx"
DB_DIR = "history_database"
GREETINGS_PATH = "greetings.txt"
os.makedirs(DB_DIR, exist_ok=True)

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

st.set_page_config(page_title="Universal ATP Generator", page_icon="⚡", layout="wide")

if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.current_theme = "light" 
    st.session_state.current_role = "dc"
    st.session_state.user_name = "An_"        
    st.session_state.user_suffix = ""         
    
    st.session_state.metadata = {key: "" for key in DEFAULT_METADATA.keys()}
    st.session_state.fat_commands = [""]
    st.session_state.pole_commands = [""]
    
    st.session_state.df_fat_editor = pd.DataFrame(columns=["Jalur FAT"])
    st.session_state.df_pole_editor = pd.DataFrame(columns=["Tipe Tiang", "Nama Sheet Target", "Ukuran Detail", "Jumlah"])

def parse_fat_inline(commands):
    res = []
    for cmd in commands:
        cmd = cmd.strip()
        if not cmd: continue
        match = re.match(r"([A-Za-z]+)(\d+)", cmd)
        if match:
            line = match.group(1).upper()
            count = int(match.group(2))
            for i in range(1, count + 1):
                res.append(f"{line}{i:02d}")
        else:
            res.append(cmd)
    return res

def format_pole_size_dynamic(raw_size):
    clean_str = str(raw_size).strip().lower().replace("m", "").replace("meter", "").replace("inch", "").strip()
    match = re.match(r'^(\d)[\.\s]*([\d\.]+)$', clean_str)
    if match:
        meter = match.group(1)
        inch = match.group(2)
        return f"{meter} METER {inch} INCH"
    return str(raw_size).strip() 

def parse_pole_inline(commands):
    res = []
    for cmd in commands:
        cmd = cmd.strip()
        if not cmd or "=" not in cmd: continue
        left, right = cmd.split("=", 1)
        left = left.strip()
        
        try: qty = int(right.strip())
        except: qty = 0
        
        lower_left = left.lower()
        if lower_left.startswith("pole "):
            val = left[5:].strip() 
            size_clean = format_pole_size_dynamic(val) 
            sheet_title = f"Pole Erection {val}"       # Imbuhan kode langsung (Cth: Pole Erection 73)
            p_type = "NEW POLE"
        elif lower_left.startswith("ext "):
            val = left[4:].strip()
            size_clean = format_pole_size_dynamic(val) 
            sheet_title = f"Pole Erection EXT {val}"   # Imbuhan kode langsung (Cth: Pole Erection EXT 74)
            p_type = "EXT POLE"
        else:
            val = left
            size_clean = format_pole_size_dynamic(val) 
            sheet_title = f"Pole Erection {val}"
            p_type = "NEW POLE"
            
        res.append({
            "title": sheet_title, 
            "type": p_type, 
            "size_clean": size_clean, 
            "qty": qty
        })
    return res

def load_greetings_from_file():
    db = {"MINGGU": [], "PAGI": [], "SIANG": [], "SORE": [], "MALAM": []}
    if not os.path.exists(GREETINGS_PATH): return db
    
    current_section = None
    with open(GREETINGS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            if line.startswith("[") and line.endswith("]"):
                current_section = line[1:-1].upper()
            elif current_section in db:
                db[current_section].append(line)
    return db

def generate_dc_greeting(nama, suffix):
    now = datetime.datetime.now()
    hour = now.hour
    hari = now.strftime("%A")
    panggilan = f"{nama} {suffix}".strip() if suffix else nama
    
    db = load_greetings_from_file()
    fallback = f"Halo {panggilan}! Selamat datang kembali di Universal ATP Generator."
    
    if hari == "Sunday" and db.get("MINGGU"):
        terpilih = random.choice(db["MINGGU"])
    elif 0 <= hour < 11 and db.get("PAGI"):
        terpilih = random.choice(db["PAGI"])
    elif 11 <= hour < 15 and db.get("SIANG"):
        terpilih = random.choice(db["SIANG"])
    elif 15 <= hour < 19 and db.get("SORE"):
        terpilih = random.choice(db["SORE"])
    elif db.get("MALAM"):
        terpilih = random.choice(db["MALAM"])
    else:
        terpilih = fallback
        
    return terpilih.format(nama_lengkap=panggilan)

if st.session_state.current_theme == "dark":
    st.markdown("""<style>.stApp { background-color: #0E1117; color: #FFFFFF; } .stButton>button { border: 1px solid #10B981; } .permanent-footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #0F172A; color: #10B981; text-align: center; padding: 12px 0; z-index: 999; }</style>""", unsafe_allow_html=True)
else:
    st.markdown("""<style>.stApp { background-color: #F9FAFB; color: #1F2937; } .stButton>button { border: 1px solid #059669; } .permanent-footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #FFFFFF; color: #059669; text-align: center; padding: 12px 0; z-index: 999; }</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.subheader("👤 Kendali Akses & Profil")
    st.session_state.user_name = st.text_input("Nama Pengguna:", value=st.session_state.user_name)
    st.session_state.user_suffix = st.text_input("Suffix Spesial:", value=st.session_state.user_suffix)
    role_choice = st.radio("Hak Akses:", ["Document Control (DC)", "Administrator System"])
    st.session_state.current_role = "dc" if "DC" in role_choice else "admin"
    st.session_state.current_theme = "light" if st.toggle("Aktifkan Mode Terang", value=(st.session_state.current_theme == "light")) else "dark"

if st.session_state.current_role == "admin":
    st.header("🛠️ Panel Kendali Administrator")
    st.divider()
    st.subheader("🗑️ Manajemen Penghapusan Arsip Digital")
    if os.path.exists(DB_DIR):
        files = [f for f in os.listdir(DB_DIR) if f.endswith(".json")]
        if files:
            search_admin = st.text_input("🔍 Cari Arsip untuk Dihapus:", "", key="search_admin")
            for file in files:
                if search_admin.lower() in file.lower():
                    col_file, col_btn_del = st.columns([3, 1])
                    with col_file: st.markdown(f"📁 `{file}`")
                    with col_btn_del:
                        if st.button("🗑️ Hapus", key=f"admin_del_{file}", use_container_width=True):
                            os.remove(f"{DB_DIR}/{file}")
                            st.rerun()
        else:
            st.info("Database server bersih.")

else:
    st.info(generate_dc_greeting(st.session_state.user_name, st.session_state.user_suffix))
    if not os.path.exists(TEMPLATE_PATH):
        st.error(f"⚠️ KRITIS: File {TEMPLATE_PATH} tidak ditemukan!")
        st.stop()

    tab1, tab2 = st.tabs(["📋 FASE 1: Struktur Identitas & Eksekusi Draf", "🗄️ PUSAT ARSIP DIGITAL"])

    with tab1:
        st.header("1. Form Identitas Proyek")
        with st.form("form_metadata_proyek"):
            col1, col2 = st.columns(2)
            with col1:
                st.session_state.metadata["NAMA_PROYEK"] = st.text_input("Nama Proyek", value=st.session_state.metadata["NAMA_PROYEK"], placeholder=DEFAULT_METADATA["NAMA_PROYEK"])
                st.session_state.metadata["NO_PO"] = st.text_input("Nomor PO", value=st.session_state.metadata["NO_PO"], placeholder=DEFAULT_METADATA["NO_PO"])
                st.session_state.metadata["TANGGAL_TEST"] = st.text_input("Tanggal Test", value=st.session_state.metadata["TANGGAL_TEST"], placeholder=DEFAULT_METADATA["TANGGAL_TEST"])
            with col2:
                st.session_state.metadata["REGION"] = st.text_input("Region", value=st.session_state.metadata["REGION"], placeholder=DEFAULT_METADATA["REGION"])
                st.session_state.metadata["ALAMAT"] = st.text_input("Alamat Lengkap", value=st.session_state.metadata["ALAMAT"], placeholder=DEFAULT_METADATA["ALAMAT"])
                
            st.divider()
            col3, col4 = st.columns(2)
            with col3:
                st.session_state.metadata["NAMA_OLT"] = st.text_input("Nama OLT", value=st.session_state.metadata["NAMA_OLT"], placeholder=DEFAULT_METADATA["NAMA_OLT"])
                st.session_state.metadata["NAMA_LOKASI"] = st.text_input("Nama Cluster/Subfeeder", value=st.session_state.metadata["NAMA_LOKASI"], placeholder=DEFAULT_METADATA["NAMA_LOKASI"])
                st.session_state.metadata["ID_LOKASI"] = st.text_input("ID Cluster/Subfeeder", value=st.session_state.metadata["ID_LOKASI"], placeholder=DEFAULT_METADATA["ID_LOKASI"])
            with col4:
                st.session_state.metadata["ID_FDT_FROM"] = st.text_input("ID FDT (Link From)", value=st.session_state.metadata["ID_FDT_FROM"], placeholder=DEFAULT_METADATA["ID_FDT_FROM"])
                st.session_state.metadata["ID_FAT_TO"] = st.text_input("ID FAT (Link To)", value=st.session_state.metadata["ID_FAT_TO"], placeholder=DEFAULT_METADATA["ID_FAT_TO"])
            st.form_submit_button("🔒 Kunci Identitas Proyek")

        st.divider()
        st.header("2. Sektor Teknis (Suntikan Struktur)")
        col_sect1, col_sect2 = st.columns(2)
        with col_sect1:
            st.subheader("A. Pembangun Jalur FAT")
            for i in range(len(st.session_state.fat_commands)):
                st.session_state.fat_commands[i] = st.text_input(f"Baris FAT-{i+1} (Cth: A10)", value=st.session_state.fat_commands[i], key=f"fat_cmd_{i}")
            if st.button("➕ Tambah Baris FAT"):
                st.session_state.fat_commands.append("")
                st.rerun()
                
        with col_sect2:
            st.subheader("B. Pembangun Tiang")
            for i in range(len(st.session_state.pole_commands)):
                st.session_state.pole_commands[i] = st.text_input(f"Baris Tiang-{i+1} (Cth: pole 73 = 10, ext 74 = 5)", value=st.session_state.pole_commands[i], key=f"pole_cmd_{i}")
            if st.button("➕ Tambah Baris Tiang"):
                st.session_state.pole_commands.append("")
                st.rerun()

        if st.button("🔄 Ekstrak Data Struktur"):
            fat_bersih = [cmd for cmd in st.session_state.fat_commands if cmd.strip() != ""]
            pole_bersih = [cmd for cmd in st.session_state.pole_commands if cmd.strip() != ""]
            
            st.session_state.df_fat_editor = pd.DataFrame({"Jalur FAT": parse_fat_inline(fat_bersih)})
            
            p_list = parse_pole_inline(pole_bersih)
            st.session_state.df_pole_editor = pd.DataFrame([[p["type"], p["title"], p["size_clean"], p["qty"]] for p in p_list], columns=["Tipe Tiang", "Nama Sheet Target", "Ukuran Detail", "Jumlah"])
            st.session_state.fase1_extracted = True

        if st.session_state.get("fase1_extracted", False):
            st.markdown("### ✏️ Editor & Validasi Data Fase 1")
            col_ed1, col_ed2 = st.columns(2)
            with col_ed1:
                st.write("**Tabel Jalur FAT:**")
                st.session_state.df_fat_editor = st.data_editor(st.session_state.df_fat_editor, num_rows="dynamic", use_container_width=True)
            with col_ed2:
                st.write("**Tabel Distribusi Tiang:**")
                st.session_state.df_pole_editor = st.data_editor(st.session_state.df_pole_editor, num_rows="dynamic", use_container_width=True)

            st.divider()
            st.subheader("📥 Generator Excel Draf Fase 1")
            if st.button("💾 LIVE SINKRONISASI FILE DRAF"):
                try:
                    with open(TEMPLATE_PATH, "rb") as f: raw_bytes = f.read()
                    
                    final_fats = st.session_state.df_fat_editor["Jalur FAT"].tolist()
                    final_poles = []
                    for _, r in st.session_state.df_pole_editor.iterrows():
                        final_poles.append({"type": r["Tipe Tiang"], "title": r["Nama Sheet Target"], "size_clean": r["Ukuran Detail"], "qty": int(r["Jumlah"])})
                        
                    actual_meta = {key: (val.strip() if val.strip() else DEFAULT_METADATA[key]) for key, val in st.session_state.metadata.items()}
                    
                    with st.spinner("Memproses struktur Cluster..."):
                        c_out = inject_excel_fase1(io.BytesIO(raw_bytes), actual_meta, final_fats, final_poles, mode="cluster")
                        st.session_state.dl_fase1_c = c_out.getvalue()
                        
                    with st.spinner("Memproses struktur Subfeeder..."):
                        s_out = inject_excel_fase1(io.BytesIO(raw_bytes), actual_meta, final_fats, final_poles, mode="subfeeder")
                        st.session_state.dl_fase1_s = s_out.getvalue()
                        
                    st.session_state.sfx_name = actual_meta["NAMA_LOKASI"] or "BARU"
                    st.session_state.fase1_ready = True
                    st.success("File Draf Fase 1 berhasil dirakit secara berurutan!")
                except Exception as e:
                    error_detail = traceback.format_exc()
                    st.error(f"Gagal memproses file. Detail Error:\n\n{error_detail}")

            if st.session_state.get("fase1_ready", False):
                col_dl1, col_dl2 = st.columns(2)
                with col_dl1: st.download_button("🚀 UNDUH DRAF CLUSTER", data=st.session_state.dl_fase1_c, file_name=f"DRAF CLUSTER {st.session_state.sfx_name}.xlsx", use_container_width=True)
                with col_dl2: st.download_button("🚀 UNDUH DRAF SUBFEEDER", data=st.session_state.dl_fase1_s, file_name=f"DRAF SUBFEEDER {st.session_state.sfx_name}.xlsx", use_container_width=True)

    with tab2:
        st.header("🗄️ Pusat Database JSON Murni")
        if st.button("💾 AMANKAN FORM FASE 1 SEBAGAI ARSIP"):
            loc_name = st.session_state.metadata.get("NAMA_LOKASI", "").strip() or DEFAULT_METADATA["NAMA_LOKASI"]
            clean_filename = loc_name.replace(" ", "_").replace("-", "_")
            archive_data = {
                "saved_at": str(datetime.datetime.now()),
                "metadata": st.session_state.metadata,
                "fat_commands": st.session_state.fat_commands,
                "pole_commands": st.session_state.pole_commands,
                "table_fat": st.session_state.df_fat_editor.to_dict(orient="list"),
                "table_pole": st.session_state.df_pole_editor.to_dict(orient="list")
            }
            with open(f"{DB_DIR}/{clean_filename}.json", "w", encoding="utf-8") as json_file:
                json.dump(archive_data, json_file, indent=4)
            st.success(f"✅ Data `{loc_name}` di-arsip!")

        st.divider()
        files = [f for f in os.listdir(DB_DIR) if f.endswith(".json")]
        if files:
            search_db = st.text_input("🔍 Cari Arsip:")
            for file in files:
                if search_db.lower() in file.lower():
                    col_file, col_btn_load = st.columns([3, 1])
                    with col_file: st.markdown(f"📁 `{file}`")
                    with col_btn_load:
                        if st.button("📥 Muat", key=f"load_{file}", use_container_width=True):
                            with open(f"{DB_DIR}/{file}", "r", encoding="utf-8") as json_file:
                                loaded = json.load(json_file)
                            st.session_state.metadata = loaded["metadata"]
                            st.session_state.fat_commands = loaded["fat_commands"]
                            st.session_state.pole_commands = loaded["pole_commands"]
                            st.session_state.df_fat_editor = pd.DataFrame(loaded["table_fat"])
                            st.session_state.df_pole_editor = pd.DataFrame(loaded["table_pole"])
                            st.session_state.fase1_extracted = True 
                            st.rerun()

st.markdown('<div class="permanent-footer">Developed by An_</div>', unsafe_allow_html=True)
