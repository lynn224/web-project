import streamlit as st
import datetime
import random
import os
import io
import json
import re
import pandas as pd
import traceback

from excel_injector import inject_excel_final
from module_fase2_otdr import render_otdr_ui
from module_fase2_opm_dist import render_opm_dist_ui
from module_fase2_opm_feeder import render_opm_feeder_ui

TEMPLATE_PATH = "Template.xlsx"
DB_DIR = "history_database"
GREETINGS_PATH = "greetings.txt"
os.makedirs(DB_DIR, exist_ok=True)

# =====================================================================
# BLOK RUANG LOGIN & MANAJEMEN ADMIN 
# =====================================================================
# Area ini disiapkan untuk diintegrasikan dengan database kredensial.
# Admin memiliki panel eksklusif untuk 'Create/Edit/Delete User'.
# =====================================================================

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
    st.session_state.user_name = "An_"        
    st.session_state.user_suffix = ""         
    st.session_state.metadata = {key: "" for key in DEFAULT_METADATA.keys()}
    st.session_state.fat_commands = [""]
    st.session_state.pole_commands = [""]

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
        else: res.append(cmd)
    return res

def format_pole_size_dynamic(raw_size):
    clean_str = str(raw_size).strip().lower().replace("m", "").replace("meter", "").replace("inch", "").strip()
    match = re.match(r'^(\d)[\.\s]*([\d\.]+)$', clean_str)
    if match: return f"{match.group(1)} METER {match.group(2)} INCH"
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
        if lower_left.startswith("pole "): val = left[5:].strip(); p_type = "NEW POLE"
        elif lower_left.startswith("ext "): val = left[4:].strip(); p_type = "EXT POLE"
        else: val = left; p_type = "NEW POLE"
            
        res.append({"title": f"Pole Erection {val}", "type": p_type, "size_clean": format_pole_size_dynamic(val), "qty": qty})
    return res

def load_greetings_from_file():
    db = {"MINGGU": [], "PAGI": [], "SIANG": [], "SORE": [], "MALAM": []}
    if not os.path.exists(GREETINGS_PATH): return db
    current_section = None
    with open(GREETINGS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("[") and line.endswith("]"): current_section = line[1:-1].upper()
            elif line and current_section in db: db[current_section].append(line)
    return db

def generate_dc_greeting(nama, suffix):
    now = datetime.datetime.now()
    hour = now.hour
    hari = now.strftime("%A")
    panggilan = f"{nama} {suffix}".strip() if suffix else nama
    db = load_greetings_from_file()
    fallback = f"Halo {panggilan}! Selamat bekerja."
    
    if hari == "Sunday" and db.get("MINGGU"): terpilih = random.choice(db["MINGGU"])
    elif 0 <= hour < 11 and db.get("PAGI"): terpilih = random.choice(db["PAGI"])
    elif 11 <= hour < 15 and db.get("SIANG"): terpilih = random.choice(db["SIANG"])
    elif 15 <= hour < 19 and db.get("SORE"): terpilih = random.choice(db["SORE"])
    elif db.get("MALAM"): terpilih = random.choice(db["MALAM"])
    else: terpilih = fallback
    return terpilih.format(nama_lengkap=panggilan)

if st.session_state.current_theme == "dark":
    st.markdown("""<style>.stApp { background-color: #0E1117; color: #FFFFFF; }</style>""", unsafe_allow_html=True)
else:
    st.markdown("""<style>.stApp { background-color: #F9FAFB; color: #1F2937; }</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.subheader("👤 Profil Pengguna")
    st.session_state.user_name = st.text_input("Nama Pengguna:", value=st.session_state.user_name)
    st.session_state.user_suffix = st.text_input("Suffix Spesial:", value=st.session_state.user_suffix)
    st.session_state.current_theme = "light" if st.toggle("Aktifkan Mode Terang", value=(st.session_state.current_theme == "light")) else "dark"
    st.divider()
    st.markdown("**(Admin Panel Placeholder)**\n*Akan diaktifkan untuk manajemen akun.*")

st.info(generate_dc_greeting(st.session_state.user_name, st.session_state.user_suffix))

tab1, tab2, tab3 = st.tabs(["📋 FASE 1: Struktur Administrasi", "📊 FASE 2: Data Teknis Final", "🗄️ PUSAT ARSIP DIGITAL"])

with tab1:
    st.header("1. Form Identitas Proyek")
    with st.form("form_metadata_proyek"):
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.metadata["NAMA_PROYEK"] = st.text_input("Nama Proyek", value=st.session_state.metadata["NAMA_PROYEK"], placeholder="Contoh: EMR FTTH PROJECT")
            st.session_state.metadata["NO_PO"] = st.text_input("Nomor PO", value=st.session_state.metadata["NO_PO"], placeholder="Contoh: PO-EMR-2026-001")
            st.session_state.metadata["TANGGAL_TEST"] = st.text_input("Tanggal Test", value=st.session_state.metadata["TANGGAL_TEST"], placeholder="Contoh: 2026-06-27")
        with col2:
            st.session_state.metadata["REGION"] = st.text_input("Region", value=st.session_state.metadata["REGION"], placeholder="Contoh: JAWA TIMUR")
            st.session_state.metadata["ALAMAT"] = st.text_input("Alamat Lengkap", value=st.session_state.metadata["ALAMAT"], placeholder="Contoh: Nglawak Kecamatan Kertosono")
            
        st.divider()
        col3, col4 = st.columns(2)
        with col3:
            st.session_state.metadata["NAMA_OLT"] = st.text_input("Nama OLT", value=st.session_state.metadata["NAMA_OLT"], placeholder="Contoh: KERTOSONO")
            st.session_state.metadata["NAMA_LOKASI"] = st.text_input("Nama Cluster/Subfeeder", value=st.session_state.metadata["NAMA_LOKASI"], placeholder="Contoh: DUSUN BOGO RW 08 FDT-2")
            st.session_state.metadata["ID_LOKASI"] = st.text_input("ID Cluster/Subfeeder", value=st.session_state.metadata["ID_LOKASI"], placeholder="Contoh: NJK000095")
        with col4:
            st.session_state.metadata["ID_FDT_FROM"] = st.text_input("ID FDT (Link From)", value=st.session_state.metadata["ID_FDT_FROM"], placeholder="Contoh: NJK.100.021.DSBG08-FDT2.019.110")
            st.session_state.metadata["ID_FAT_TO"] = st.text_input("ID FAT (Link To)", value=st.session_state.metadata["ID_FAT_TO"], placeholder="Contoh: DSBG08FDT2.019")
            with st.expander("Detail Representatif (Opsional)"):
                st.session_state.metadata["NAMA_PT_VENDOR"] = st.text_input("PT Vendor", value=st.session_state.metadata["NAMA_PT_VENDOR"], placeholder="PT Buana Menara Indonesia")
                st.session_state.metadata["REP_VENDOR"] = st.text_input("Nama Rep Vendor", value=st.session_state.metadata["REP_VENDOR"], placeholder="ERFIN FIRMANSYAH")
                st.session_state.metadata["JABATAN_VENDOR"] = st.text_input("Jabatan Vendor", value=st.session_state.metadata["JABATAN_VENDOR"], placeholder="BMI FIELD SUPERVISOR")
                st.session_state.metadata["NAMA_PT_CUSTOMER"] = st.text_input("PT Customer", value=st.session_state.metadata["NAMA_PT_CUSTOMER"], placeholder="PT Ekamas Mora Republik Tbk")
                st.session_state.metadata["REP_CUSTOMER"] = st.text_input("Nama Rep Customer", value=st.session_state.metadata["REP_CUSTOMER"], placeholder="M. NUGROHO")
                st.session_state.metadata["JABATAN_CUSTOMER"] = st.text_input("Jabatan Customer", value=st.session_state.metadata["JABATAN_CUSTOMER"], placeholder="EMR FIELD SUPERVISOR")
        st.form_submit_button("🔒 Kunci Identitas")

    st.divider()
    st.header("2. Sektor Teknis")
    col_sect1, col_sect2 = st.columns(2)
    with col_sect1:
        for i in range(len(st.session_state.fat_commands)): st.session_state.fat_commands[i] = st.text_input(f"Baris FAT-{i+1} (Cth: A10)", value=st.session_state.fat_commands[i], key=f"fat_{i}")
        if st.button("➕ Tambah FAT"): st.session_state.fat_commands.append(""); st.rerun()
    with col_sect2:
        for i in range(len(st.session_state.pole_commands)): st.session_state.pole_commands[i] = st.text_input(f"Baris Tiang-{i+1} (Cth: pole 73 = 10)", value=st.session_state.pole_commands[i], key=f"pole_{i}")
        if st.button("➕ Tambah Tiang"): st.session_state.pole_commands.append(""); st.rerun()

    if st.button("🔄 Ekstrak Struktur"):
        st.session_state.parsed_fat = parse_fat_inline([c for c in st.session_state.fat_commands if c.strip()])
        st.session_state.parsed_poles = parse_pole_inline([c for c in st.session_state.pole_commands if c.strip()])
        st.session_state.fase1_extracted = True

    if st.session_state.get("fase1_extracted"):
        st.success(f"Terekstrak: {len(st.session_state.parsed_fat)} FAT, {len(st.session_state.parsed_poles)} Baris Tiang")

with tab2:
    st.header("Input Data Teknis (Angka Moduler)")
    if st.session_state.get("fase1_extracted"):
        # Memanggil modul terpisah untuk UI Fase 2
        otdr_data = render_otdr_ui(st.session_state.parsed_fat)
        st.divider()
        opm_dist_data = render_opm_dist_ui(st.session_state.parsed_fat)
        st.divider()
        feeder_data = render_opm_feeder_ui()
        st.divider()

        st.subheader("📥 Generator Excel FINAL (Integrasi Fase 1 + Fase 2)")
        
        # Variabel global Wavelength, Distance SF, OTDR SF yang berlaku umum
        wave_length = st.text_input("Wavelength (nm) Umum:", "1310 / 1550")
        distance_sf = st.text_input("Distance SF (Km) Umum:", "0.5")
        otdr_sf = st.text_input("OTDR SF Loss Umum:", "0.05")
        
        if st.button("💾 GENERATE DOKUMEN FINAL"):
            try:
                with open(TEMPLATE_PATH, "rb") as f: raw_bytes = f.read()
                actual_meta = {key: (val.strip() if val.strip() else DEFAULT_METADATA[key]) for key, val in st.session_state.metadata.items()}
                actual_meta.update({"WAVE_LENGHT": wave_length, "DISTANCE_SF": distance_sf, "OTDR_SF": otdr_sf})
                
                with st.spinner("Memproses Integrasi Cluster..."):
                    st.session_state.dl_final_c = inject_excel_final(io.BytesIO(raw_bytes), actual_meta, st.session_state.parsed_fat, st.session_state.parsed_poles, otdr_data, opm_dist_data, feeder_data, mode="cluster").getvalue()
                with st.spinner("Memproses Integrasi Subfeeder..."):
                    st.session_state.dl_final_s = inject_excel_final(io.BytesIO(raw_bytes), actual_meta, st.session_state.parsed_fat, st.session_state.parsed_poles, otdr_data, opm_dist_data, feeder_data, mode="subfeeder").getvalue()
                
                st.session_state.final_ready = True
                st.success("Dokumen Final berhasil dirakit tanpa Corrupt!")
            except Exception as e:
                st.error(f"Gagal memproses dokumen. Error:\n{traceback.format_exc()}")

        if st.session_state.get("final_ready"):
            col_dl1, col_dl2 = st.columns(2)
            with col_dl1: st.download_button("🚀 UNDUH FINAL CLUSTER", data=st.session_state.dl_final_c, file_name=f"FINAL CLUSTER.xlsx", use_container_width=True)
            with col_dl2: st.download_button("🚀 UNDUH FINAL SUBFEEDER", data=st.session_state.dl_final_s, file_name=f"FINAL SUBFEEDER.xlsx", use_container_width=True)
    else:
        st.warning("⚠️ Selesaikan ekstraksi data di Tab Fase 1 terlebih dahulu.")

with tab3:
    st.header("🗄️ Pusat Arsip")
    if st.button("💾 AMANKAN PROJECT"):
        loc_name = st.session_state.metadata.get("NAMA_LOKASI", "BARU").strip()
        archive_data = {
            "metadata": st.session_state.metadata,
            "fat_commands": st.session_state.fat_commands,
            "pole_commands": st.session_state.pole_commands
        }
        with open(f"{DB_DIR}/{loc_name}.json", "w", encoding="utf-8") as jf: json.dump(archive_data, jf, indent=4)
        st.success("Tersimpan!")

    files = [f for f in os.listdir(DB_DIR) if f.endswith(".json")]
    for file in files:
        col1, col2 = st.columns([3, 1])
        with col1: st.markdown(f"📁 `{file}`")
        with col2:
            if st.button("📥 Muat", key=f"load_{file}"):
                with open(f"{DB_DIR}/{file}", "r", encoding="utf-8") as jf: loaded = json.load(jf)
                st.session_state.metadata = loaded.get("metadata", {})
                st.session_state.fat_commands = loaded.get("fat_commands", [""])
                st.session_state.pole_commands = loaded.get("pole_commands", [""])
                st.rerun()
