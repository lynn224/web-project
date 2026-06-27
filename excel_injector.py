import openpyxl
from copy import copy
import io
import os

def load_external_placeholders(filepath="placeholders.txt"):
    """Membaca pemetaan placeholder dari file teks eksternal secara aman."""
    mapping = {}
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    mapping[key.strip()] = val.strip()
    return mapping

def safe_clone_sheet(wb, master_name, new_title):
    """
    Menduplikasi sheet sekaligus menyalin objek gambar secara deep copy.
    Mengunci Anchor posisi agar logo tidak melenceng dan bebas error XML.
    """
    if master_name not in wb.sheetnames:
        return None
    
    master_sheet = wb[master_name]
    cloned_sheet = wb.copy_worksheet(master_sheet)
    cloned_sheet.title = new_title
    
    if hasattr(master_sheet, "_images"):
        for img in master_sheet._images:
            new_img = copy(img)
            new_img.anchor = img.anchor
            cloned_sheet.add_image(new_img)
            
    return cloned_sheet

def inject_excel_fase1(template_file, metadata, parsed_fat, parsed_poles, mode="cluster"):
    """
    Mesin Inti Penyuntik Komponen ATP.
    Memisahkan BA per Line, menata urutan sheet secara absolut, dan menghapus lembar residu.
    """
    wb = openpyxl.load_workbook(template_file)
    p_map = load_external_placeholders()
    
    # Kelompokkan FAT berdasarkan Huruf Jalur (Line) untuk pembentukan BA
    fat_by_line = {}
    for fat in parsed_fat:
        line_letter = "".join(filter(str.isalpha, fat)) or "A"
        if line_letter not in fat_by_line:
            fat_by_line[line_letter] = []
        fat_by_line[line_letter].append(fat)

    # =============================================================================
    # 1. PROSES DUPLIKASI SHEET INDIVIDU FAT
    # =============================================================================
    if "MASTER_FAT" in wb.sheetnames and parsed_fat:
        for fat_code in parsed_fat:
            sheet_title = f"FAT {fat_code}"
            ws = safe_clone_sheet(wb, "MASTER_FAT", sheet_title)
            if ws:
                for row in ws.iter_rows(min_row=1, max_row=40, min_col=1, max_col=15):
                    for cell in row:
                        if cell.value and isinstance(cell.value, str) and "[INPUT_FAT_NAME]" in cell.value:
                            cell.value = cell.value.replace("[INPUT_FAT_NAME]", f"FAT {fat_code}")

    # =============================================================================
    # 2. PROSES PEMBENTUKAN BA SPLITTER FAT (Dipisah Mutlak Per Line)
    # =============================================================================
    if "BA Splitter FAT" in wb.sheetnames and fat_by_line:
        for line, fats in fat_by_line.items():
            sheet_title = f"BA Splitter FAT {line}"
            ws = safe_clone_sheet(wb, "BA Splitter FAT", sheet_title)
            if ws:
                start_row = 19
                for r in range(1, 40):
                    for c in range(1, 15):
                        if ws.cell(row=r, column=c).value == "[INPUT_FAT_NAME]":
                            start_row = r
                            break
                
                for idx, fat_code in enumerate(fats):
                    current_row = start_row + idx
                    ws.cell(row=current_row, column=2).value = f"Splitter {idx + 1}"
                    ws.cell(row=current_row, column=3).value = 1
                    ws.cell(row=current_row, column=4).value = "MICRO"
                    ws.cell(row=current_row, column=8).value = f"FAT {fat_code}"

    # =============================================================================
    # 3. PROSES PEMBENTUKAN SHEET POLE ERECTION (Auto-Increment P001)
    # =============================================================================
    if "MASTER_POLE" in wb.sheetnames and parsed_poles:
        for pole in parsed_poles:
            sheet_title = f"Pole Erection {pole['size']}"
            ws = safe_clone_sheet(wb, "MASTER_POLE", sheet_title)
            if ws:
                start_row = 12
                for r in range(1, 30):
                    for c in range(1, 10):
                        if ws.cell(row=r, column=c).value == "[INPUT_POLE_DESC]":
                            start_row = r
                            break
                
                prefix = "P" if "NEW" in pole["type"] else "E"
                for idx in range(pole["qty"]):
                    current_row = start_row + idx
                    serial_num = f"{prefix}{str(idx + 1).zfill(3)}"
                    ws.cell(row=current_row, column=1).value = f"{pole['type']} {serial_num}"
                    ws.cell(row=current_row, column=4).value = f"{pole['size']} MTR"

    # =============================================================================
    # 4. GLOBAL REPLACEMENT UNTUK VARIABEL ADMINISTRASI
    # =============================================================================
    for sheet in wb.worksheets:
        for row in sheet.iter_rows(min_row=1, max_row=100, min_col=1, max_col=20):
            for cell in row:
                if cell.value and isinstance(cell.value, str):
                    for key, val in metadata.items():
                        token = p_map.get(key, f"[{key}]")
                        if token in cell.value:
                            cell.value = cell.value.replace(token, str(val))

    # =============================================================================
    # 5. MANAJEMEN DELETION (Pembersihan Lembar Kerja)
    # =============================================================================
    sheets_to_remove = ["MASTER_FAT", "MASTER_POLE", "BA Splitter FAT"]
    
    if mode == "cluster":
        sheets_to_remove.extend(["E2E OPM Subfeeder", "OTDR Summary 1550", "OTDR Summary 1310 "])
    else:
        sheets_to_remove.extend(["BAST Key", "E2E OPM Distribution", "E2E OPM Feeder"])
        
    for s_name in sheets_to_remove:
        if s_name in wb.sheetnames:
            wb.remove(wb[s_name])

    # =============================================================================
    # 6. ABSOLUTE BLUEPRINT SORTING (Urutan Eksekusi dari Kiri ke Kanan)
    # =============================================================================
    SORT_ORDER_LOWER = [
        "support table",
        "atp cw cover",
        "fat",
        "fdt",
        "pole erection",
        "trenching",
        "road and railway",
        "bridges crossing",
        "precast handhole",
        "handhole",
        "boring rojok manual",
        "building cable access",
        "cable installation",
        "cw punchpoint defect list",
        "ba rectifikasi",    
        "cover cw opm",
        "e2e opm",
        "otdr sum",          
        "opm punchpoint defect list",
        "ba rectifikasi opm",
        "ba splitter fdt",
        "ba splitter fat",
        "bast key",
        "ba lapangan"
    ]

    def get_sort_weight(sheet_name):
        name_lower = sheet_name.lower()
        for idx, prefix in enumerate(SORT_ORDER_LOWER):
            if name_lower.startswith(prefix):
                return idx
        return 999 

    wb._sheets.sort(key=lambda s: get_sort_weight(s.title))

    # Kompres berkas menjadi bentuk binary stream buffer RAM
    excel_stream = io.BytesIO()
    wb.save(excel_stream)
    excel_stream.seek(0)
    return excel_stream

