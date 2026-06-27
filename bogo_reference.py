# =============================================================================
# KAMUS REFERENSI PERMANEN (BERDASARKAN SITE BOGO)
# =============================================================================

# 1. ATURAN PENAMAAN SHEET (OUTPUT)
SHEET_NAMING_RULES = {
    "fat": "FAT {kode}",                # Contoh: FAT A01
    "ba_fat": "BA Splitter FAT {line}", # Contoh: BA Splitter FAT A
    "pole": "Pole Erection {ukuran}",   # Contoh: Pole Erection 74
    "opm_dist": "E2E OPM Distribution {line}" # Contoh: E2E OPM Distribution B
}

# 2. DAFTAR PEMUSNAHAN SHEET (MODE CLUSTER VS SUBFEEDER)
# Sheet di bawah ini akan dihancurkan mesin sesuai tombol unduh yang dipilih DC
SHEET_TO_DELETE = {
    "cluster": [
        "E2E OPM Subfeeder",
        "OTDR Summary 1550",
        "OTDR Summary 1310 "
    ],
    "subfeeder": [
        "BAST Key",
        "OTDR Sumary (FDT-FAT) line A",
        "OTDR Sumary (FDT-FAT) line B",
        "OTDR Sumary (FDT-FAT) line C",
        "E2E OPM Distribution",
        "E2E OPM Feeder"
    ]
}

# 3. KAMUS PLACEHOLDER UTAMA (Fase 1 & Fase 2)
PLACEHOLDERS = {
    "support_table": [
        "[NAMA_PROYEK]", "[REGION]", "[NAMA_LOKASI]", "[ID_LOKASI]", 
        "[ALAMAT]", "[NAMA_OLT]", "[ID_FDT_FROM]", "[ID_FAT_TO]", 
        "[NAMA_PT_VENDOR]", "[REP_VENDOR]", "[JABATAN_VENDOR]", 
        "[NAMA_PT_CUSTOMER]", "[REP_CUSTOMER]", "[JABATAN_CUSTOMER]", 
        "[TANGGAL_TEST]", "[NO_PO]"
    ],
    "tiang": {
        "deskripsi": "[INPUT_POLE_DESC]", # Akan diinjeksi: NEW POLE P001, dst
        "ukuran": "[INPUT_POLE_SIZE]"     # Akan diinjeksi: 7 MTR 3 INCH
    },
    "opm_otdr": {
        "fat_name_format": "Line {line} No {no}", # Konversi FAT A01 -> Line A No 01
        "splitter_id": "[SPL_ID]",
        "splitter_sn": "[SPL_SN]",
        "opm_before": "[OPM_BEFORE]",
        "opm_after": "[OPM_AFTER]"
    }
}
