import openpyxl
from openpyxl.styles import Font
from copy import copy
import io
import os

def load_external_placeholders(filepath="placeholders.txt"):
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
    if master_name not in wb.sheetnames:
        return None
    master_sheet = wb[master_name]
    new_title = new_title[:31] # Batas aman Excel
    
    try:
        cloned_sheet = wb.copy_worksheet(master_sheet)
        cloned_sheet.title = new_title
        if hasattr(master_sheet, "_images"):
            for img in master_sheet._images:
                try:
                    new_img = copy(img)
                    cloned_sheet.add_image(new_img, img.anchor)
                except Exception:
                    pass 
        return cloned_sheet
    except Exception:
        return wb.create_sheet(title=new_title)

def inject_excel_fase1(template_stream, metadata, parsed_fat, parsed_poles, mode="cluster"):
    wb = openpyxl.load_workbook(template_stream, keep_vba=True)
    p_map = load_external_placeholders()
    black_font = Font(color="000000") 
    
    fat_by_line = {}
    for fat in parsed_fat:
        line_letter = "".join(filter(str.isalpha, fat)) or "A"
        if line_letter not in fat_by_line:
            fat_by_line[line_letter] = []
        fat_by_line[line_letter].append(fat)

    if "MASTER_FAT" in wb.sheetnames and parsed_fat:
        for fat_code in parsed_fat:
            sheet_title = f"FAT {fat_code}"
            ws = safe_clone_sheet(wb, "MASTER_FAT", sheet_title)
            if ws:
                for row in ws.iter_rows(min_row=1, max_row=40, min_col=1, max_col=15):
                    for cell in row:
                        if cell.value and isinstance(cell.value, str) and "[INPUT_FAT_NAME]" in cell.value:
                            cell.value = cell.value.replace("[INPUT_FAT_NAME]", f"FAT {fat_code}")
                            cell.font = black_font

    for line in fat_by_line.keys():
        if "MASTER OTDR Sumary (FDT-FAT)" in wb.sheetnames:
            safe_clone_sheet(wb, "MASTER OTDR Sumary (FDT-FAT)", f"OTDR Sumary (FDT-FAT) line {line}")
        if "MASTER_OPM_DISTRIBUTION" in wb.sheetnames:
            safe_clone_sheet(wb, "MASTER_OPM_DISTRIBUTION", f"E2E OPM Distribution line {line}")

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
                    ws.cell(row=current_row, column=2, value=f"Splitter {idx + 1}").font = black_font
                    ws.cell(row=current_row, column=3, value=1).font = black_font
                    ws.cell(row=current_row, column=4, value="MICRO").font = black_font
                    ws.cell(row=current_row, column=5, value="NO SN").font = black_font
                    ws.cell(row=current_row, column=7, value="Good").font = black_font
                    ws.cell(row=current_row, column=8, value=f"FAT {fat_code}").font = black_font

    if "MASTER_POLE" in wb.sheetnames and parsed_poles:
        for pole in parsed_poles:
            sheet_title = pole["title"] 
            ws = safe_clone_sheet(wb, "MASTER_POLE", sheet_title)
            if ws:
                start_row = 12
                for r in range(1, 30):
                    if ws.cell(row=r, column=1).value == "[INPUT_POLE_DESC]":
                        start_row = r
                        break
                        
                prefix = "P" if "NEW" in pole["type"] else "E"
                size_clean = sheet_title.replace("Pole Erection", "").replace("ext", "").strip()
                
                for idx in range(pole["qty"]):
                    current_row = start_row + idx
                    serial_num = f"{prefix}{str(idx + 1).zfill(3)}"
                    
                    ws.cell(row=current_row, column=1, value=f"{pole['type']} {serial_num}").font = black_font
                    ws.cell(row=current_row, column=4, value=size_clean).font = black_font
                    ws.cell(row=current_row, column=11, value="☑pass  □fail □Need Repair").font = black_font

    for sheet in wb.worksheets:
        for row in sheet.iter_rows(min_row=1, max_row=100, min_col=1, max_col=20):
            for cell in row:
                if cell.value and isinstance(cell.value, str):
                    original_val = cell.value
                    changed = False
                    for key, val in metadata.items():
                        token = p_map.get(key, f"[{key}]")
                        if token in original_val:
                            original_val = original_val.replace(token, str(val))
                            changed = True
                    if changed:
                        cell.value = original_val
                        cell.font = black_font

    sheets_to_remove = ["MASTER_FAT", "MASTER_POLE", "BA Splitter FAT", "MASTER OTDR Sumary (FDT-FAT)", "MASTER_OPM_DISTRIBUTION", "MASTER_OPM"]
    
    for s_name in wb.sheetnames:
        name_lower = s_name.lower().strip()
        if mode == "cluster":
            if "opm subfeeder" in name_lower or "otdr summary 1550" in name_lower or "otdr summary 1310" in name_lower or "bast key" in name_lower:
                sheets_to_remove.append(s_name)
        elif mode == "subfeeder":
            if "otdr sumary (fdt-fat)" in name_lower or "opm distribution" in name_lower or "ba splitter fat" in name_lower or "opm feeder" in name_lower:
                sheets_to_remove.append(s_name)
                
    for s_name in set(sheets_to_remove):
        if s_name in wb.sheetnames:
            wb.remove(wb[s_name])

    # =========================================================================
    # CETAK BIRU URUTAN SHEET (SANGAT SPESIFIK & AKURAT)
    # =========================================================================
    SORT_ORDER_LOWER = [
        "support table",
        "atp cw cover",
        "fdt",
        "fat",
        "ba splitter fdt",
        "ba splitter fat",
        "pole erection",
        "trenching",
        "road",
        "bridge",
        "precast",
        "handhole",
        "boring",
        "building",
        "cable",
        "cw punchpoint",
        "ba rectifikasi cw",
        "cover cw opm",
        "e2e opm",
        "otdr",
        "opm punchpoint",
        "ba rectifikasi opm",
        "bast",
        "ba lapangan"
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
