import streamlit as st
import datetime
import random
import os
import io
import json
import pandas as pd

from parser_engine import parse_all_fat, parse_all_poles
from excel_injector import inject_excel_fase1

# =============================================================================
# KONFIGURASI SISTEM
# =============================================================================
TEMPLATE_PATH = "Template.xlsx"
DB_DIR = "history_database"
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
    st.session_state.df_pole_editor = pd.DataFrame(columns=["Tipe Tiang", "Ukuran", "Jumlah"])

def generate_dc_greeting(nama, suffix):
    now = datetime.datetime.now()
    hour = now.hour
    panggilan = f"{nama} {suffix}".strip() if suffix else nama
    if 0 <= hour < 11: return f"Selamat Pagi, {panggilan}! Mari fokus selesaikan Fase 1."
    elif 11 <= hour < 15: return f"Selamat Siang, {panggilan}! Tetap teliti pada struktur data."
    elif 15 <= hour < 19: return f"Selamat Sore, {panggilan}! Fase 1 hampir matang."
    else: return f"Selamat Malam, {panggilan}! Sistem siap merakit dokumen Anda."

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

# =============================================================================
# UI UTAMA
# =============================================================================
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
            st.info("Database server dalam keadaan bersih.")
    else:
        st.info("Folder database belum terbentuk.")

else:
    st.info(generate_dc_greeting(st.session_state.user_name, st.session_state.user_suffix))
    
    if not os.path.exists(TEMPLATE_PATH):
        st.error(f"⚠️ KRITIS: File {TEMPLATE_PATH} tidak ditemukan di root server GitHub!")
        st.stop()

    tab1, tab2 = st.tabs([
        "📋 FASE 1: Struktur Identitas & Eksekusi Draf", 
        "🗄️ PUSAT ARSIP DIGITAL"
    ])

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
                st.session_state.pole_commands[i] = st.text_input(f"Baris Tiang-{i+1} (Cth: Pole 74 = 10)", value=st.session_state.pole_commands[i], key=f"pole_cmd_{i}")
            if st.button("➕ Tambah Baris Tiang"):
                st.session_state.pole_commands.append("")
                st.rerun()

        if st.button("🔄 Ekstrak Data Struktur"):
            fat_bersih = [cmd for cmd in st.session_state.fat_commands if cmd.strip() != ""]
            pole_bersih = [cmd for cmd in st.session_state.pole_commands if cmd.strip() != ""]
            
            st.session_state.df_fat_editor = pd.DataFrame({"Jalur FAT": parse_all_fat(fat_bersih)})
            st.session_state.df_pole_editor = pd.DataFrame([[p["type"], p["size"], p["qty"]] for p in parse_all_poles(pole_bersih)], columns=["Tipe Tiang", "Ukuran", "Jumlah"])
            st.session_state.fase1_extracted = True

        if st.session_state.get("fase1_extracted", False):
            st.divider()
            st.subheader("📥 Generator Excel Draf Fase 1")
            if st.button("💾 LIVE SINKRONISASI FILE DRAF FASE 1"):
                try:
                    with open(TEMPLATE_PATH, "rb") as f: raw_bytes = f.read()
                    
                    final_fats = st.session_state.df_fat_editor["Jalur FAT"].tolist()
                    final_poles = [{"type": r["Tipe Tiang"], "size": r["Ukuran"], "qty": int(r["Jumlah"])} for _, r in st.session_state.df_pole_editor.iterrows()]
                    actual_meta = {key: (val.strip() if val.strip() else DEFAULT_METADATA[key]) for key, val in st.session_state.metadata.items()}
                    
                    with st.spinner("Memisahkan sheet Cluster & Subfeeder..."):
                        c_out = inject_excel_fase1(io.BytesIO(raw_bytes), actual_meta, final_fats, final_poles, mode="cluster")
                        s_out = inject_excel_fase1(io.BytesIO(raw_bytes), actual_meta, final_fats, final_poles, mode="subfeeder")
                        
                        st.session_state.dl_fase1_c = c_out.getvalue()
                        st.session_state.dl_fase1_s = s_out.getvalue()
                        st.session_state.sfx_name = actual_meta["NAMA_LOKASI"] or "BARU"
                        st.session_state.fase1_ready = True
                    st.success("File Draf Fase 1 berhasil dirakit!")
                except Exception as e:
                    st.error(f"Gagal memproses file: {str(e)}")

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
                            st.session_state.fase1_extracted = False 
                            st.rerun()

st.markdown('<div class="permanent-footer">Developed by An_</div>', unsafe_allow_html=True)
