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
    Menduplikasi sheet dengan Deep Copy pada objek grafis.
    Mengunci posisi Anchor agar logo perusahaan tidak melenceng.
    """
    if master_name not in wb.sheetnames:
        return None
    master_sheet = wb[master_name]
    try:
        cloned_sheet = wb.copy_worksheet(master_sheet)
        cloned_sheet.title = new_title
        if hasattr(master_sheet, "_images"):
            for img in master_sheet._images:
                try:
                    new_img = copy(img)
                    new_img.anchor = img.anchor
                    cloned_sheet.add_image(new_img)
                except Exception:
                    pass 
        return cloned_sheet
    except Exception:
        return wb.create_sheet(title=new_title)

def inject_excel_fase1(template_stream, metadata, parsed_fat, parsed_poles, mode="cluster"):
    """
    Mesin Utama Penyuntik Dokumen.
    Menghapus lembar kerja tidak relevan secara dinamis berbasis acuan Bogo Reference.
    """
    # keep_links=False memutus tautan eksternal korup penyebab error repair Excel
    wb = openpyxl.load_workbook(template_stream, data_only=False, keep_vba=True, keep_links=False)
    p_map = load_external_placeholders()
    
    # Pengelompokan rute FAT untuk BA Splitter per Line
    fat_by_line = {}
    for fat in parsed_fat:
        line_letter = "".join(filter(str.isalpha, fat)) or "A"
        if line_letter not in fat_by_line:
            fat_by_line[line_letter] = []
        fat_by_line[line_letter].append(fat)

    # [1] PROSES DUPLIKASI INDIVIDU FAT
    if "MASTER_FAT" in wb.sheetnames and parsed_fat:
        for fat_code in parsed_fat:
            sheet_title = f"FAT {fat_code}"
            ws = safe_clone_sheet(wb, "MASTER_FAT", sheet_title)
            if ws:
                for row in ws.iter_rows(min_row=1, max_row=40, min_col=1, max_col=15):
                    for cell in row:
                        if cell.value and isinstance(cell.value, str) and "[INPUT_FAT_NAME]" in cell.value:
                            cell.value = cell.value.replace("[INPUT_FAT_NAME]", f"FAT {fat_code}")

    # [2] PROSES DUPLIKASI BA SPLITTER FAT PER LINE
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

    # [3] PROSES DUPLIKASI POLE ERECTION (P001 SERIAL NUMBER)
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

    # [4] MASSIVE REPLACEMENT VARIABEL ADMINISTRASI (SUPPORT TABLE KEY)
    for sheet in wb.worksheets:
        for row in sheet.iter_rows(min_row=1, max_row=100, min_col=1, max_col=20):
            for cell in row:
                if cell.value and isinstance(cell.value, str):
                    for key, val in metadata.items():
                        token = p_map.get(key, f"[{key}]")
                        if token in cell.value:
                            cell.value = cell.value.replace(token, str(val))

    # =============================================================================
    # [5] DYNAMIC DELETION ENGINE (PATUH PADA BOGO_REFERENCE)
    # =============================================================================
    sheets_to_remove = ["MASTER_FAT", "MASTER_POLE", "BA Splitter FAT"]
    
    # Pemindaian awalan kata kunci (startswith) untuk mengantisipasi suffix dinamis line
    for s_name in wb.sheetnames:
        name_lower = s_name.lower().strip()
        
        if mode == "cluster":
            if name_lower.startswith("e2e opm subfeeder") or \
               name_lower.startswith("otdr summary 1550") or \
               name_lower.startswith("otdr summary 1310"):
                sheets_to_remove.append(s_name)
                
        elif mode == "subfeeder":
            if name_lower.startswith("bast key") or \
               name_lower.startswith("otdr sumary (fdt-fat)") or \
               name_lower.startswith("e2e opm distribution") or \
               name_lower.startswith("e2e opm feeder"):
                sheets_to_remove.append(s_name)
                
    for s_name in set(sheets_to_remove):
        if s_name in wb.sheetnames:
            wb.remove(wb[s_name])

    # =============================================================================
    # [6] BLUEPRINT SORTING (URUTAN KAKU DARI KIRI KE KANAN)
    # =============================================================================
    SORT_ORDER_LOWER = [
        "support table", "atp cw cover", "fat", "fdt", "pole erection",
        "trenching", "road and railway", "bridges crossing", "precast handhole",
        "handhole", "boring rojok manual", "building cable access", "cable installation",
        "cw punchpoint defect list", "ba rectifikasi", "cover cw opm", "e2e opm",
        "otdr sum", "opm punchpoint defect list", "ba rectifikasi opm", "ba splitter fdt",
        "ba splitter fat", "bast key", "ba lapangan"
    ]

    def get_sort_weight(sheet_name):
        name_lower = sheet_name.lower()
        for idx, prefix in enumerate(SORT_ORDER_LOWER):
            if name_lower.startswith(prefix):
                return idx
        return 999 

    wb._sheets.sort(key=lambda s: get_sort_weight(s.title))

    excel_stream = io.BytesIO()
    wb.save(excel_stream)
    excel_stream.seek(0)
    return excel_stream
