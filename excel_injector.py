import openpyxl
from openpyxl.styles import Font
import io
import os

from config_referensi import BLACKLIST_CLUSTER, BLACKLIST_SUBFEEDER, SORT_ORDER_LOWER

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

def fill_sequential_placeholders(ws, placeholder, values_list, clear_unused=True):
    cells = []
    for row in ws.iter_rows():
        for cell in row:
            if cell.value and isinstance(cell.value, str) and placeholder in cell.value:
                cells.append(cell)
                
    cells.sort(key=lambda c: c.row) 
    
    for i, cell in enumerate(cells):
        if i < len(values_list):
            cell.value = cell.value.replace(placeholder, values_list[i])
            cell.font = Font(color="000000")
        elif clear_unused:
            cell.value = "" 

def inject_excel_fase1(template_stream, metadata, parsed_fat, parsed_poles, mode="cluster"):
    wb = openpyxl.load_workbook(template_stream)
    p_map = load_external_placeholders()
    black_font = Font(color="000000") 
    
    fat_by_line = {}
    for fat in parsed_fat:
        line_letter = "".join(filter(str.isalpha, fat)) or "A"
        if line_letter not in fat_by_line:
            fat_by_line[line_letter] = []
        fat_by_line[line_letter].append(fat)

    # 1. RENAME & ISI FAT INDIVIDU (Dari FAT_)
    template_fats = sorted([s for s in wb.sheetnames if s.startswith("FAT_")])
    for i, fat_code in enumerate(parsed_fat):
        if i < len(template_fats):
            ws = wb[template_fats[i]]
            ws.title = f"FAT {fat_code}"
            for row in ws.iter_rows(min_row=1, max_row=40, min_col=1, max_col=15):
                for cell in row:
                    if cell.value and isinstance(cell.value, str) and "[INPUT_FAT_NAME]" in cell.value:
                        cell.value = cell.value.replace("[INPUT_FAT_NAME]", f"FAT {fat_code}")
                        cell.font = black_font
                        
    for s_name in template_fats[len(parsed_fat):]:
        if s_name in wb.sheetnames: wb.remove(wb[s_name])

    # 2. RENAME & ISI BA SPLITTER FAT
    template_splitters = sorted([s for s in wb.sheetnames if s.startswith("BA Spitter FAT_") or s.startswith("BA Splitter FAT_")])
    line_keys = list(fat_by_line.keys())
    
    for i, line in enumerate(line_keys):
        if i < len(template_splitters):
            ws = wb[template_splitters[i]]
            ws.title = f"BA Splitter FAT {line}"
            fats = [f"FAT {f}" for f in fat_by_line[line]]
            fill_sequential_placeholders(ws, "[INPUT_FAT_NAME]", fats)

    for s_name in template_splitters[len(line_keys):]:
        if s_name in wb.sheetnames: wb.remove(wb[s_name])

    # 3. RENAME & ISI OTDR SUMMARY FDT-FAT
    template_otdr_fdt = sorted([s for s in wb.sheetnames if s.startswith("OTDR Summary (FDT-FAT)_") or s.startswith("master otdr summary")])
    for i, line in enumerate(line_keys):
        if i < len(template_otdr_fdt):
            ws = wb[template_otdr_fdt[i]]
            ws.title = f"OTDR Sumary (FDT-FAT) line {line}"
            fats = [f"FAT {f}" for f in fat_by_line[line]]
            fill_sequential_placeholders(ws, "[INPUT_FAT_NAME]", fats)

    for s_name in template_otdr_fdt[len(line_keys):]:
        if s_name in wb.sheetnames: wb.remove(wb[s_name])

    # 4. RENAME & ISI OPM DISTRIBUTION
    template_opm_dist = sorted([s for s in wb.sheetnames if s.startswith("OPM_DISTRIBUTION_")])
    for i, line in enumerate(line_keys):
        if i < len(template_opm_dist):
            ws = wb[template_opm_dist[i]]
            ws.title = f"E2E OPM Distribution line {line}"
            fats = [f"FAT {f}" for f in fat_by_line[line]]
            fill_sequential_placeholders(ws, "[INPUT_FAT_NAME]", fats)

    for s_name in template_opm_dist[len(line_keys):]:
        if s_name in wb.sheetnames: wb.remove(wb[s_name])

    # 5. RENAME E2E OPM FEEDER / SUBFEEDER (Dari OPM_)
    template_opm = sorted([s for s in wb.sheetnames if s.startswith("OPM_") and "DIST" not in s.upper()])
    if len(template_opm) > 0:
        if mode == "cluster":
            wb[template_opm[0]].title = "E2E OPM Feeder"
        else:
            wb[template_opm[0]].title = "E2E OPM Subfeeder"
    for s_name in template_opm[1:]:
        if s_name in wb.sheetnames: wb.remove(wb[s_name])

    # 6. RENAME OTDR SUMMARY WAVE (Dari OTDR Summary (WAVE)_)
    template_otdr_wave = [s for s in wb.sheetnames if s.startswith("OTDR Summary (WAVE)_")]
    for i, s_name in enumerate(template_otdr_wave):
        if i == 0: wb[s_name].title = "OTDR Summary 1550"
        elif i == 1: wb[s_name].title = "OTDR Summary 1310"

    # 7. RENAME & ISI POLE ERECTION (NEW VS EXT TETAP TERPISAH)
    template_poles = sorted([s for s in wb.sheetnames if s.startswith("POLE_")])
    for i, pole in enumerate(parsed_poles):
        if i < len(template_poles):
            ws = wb[template_poles[i]]
            ws.title = pole["title"][:31] # Menggunakan judul bersih tanpa suffix mtr/inch
            
            cells = []
            for row in ws.iter_rows():
                for cell in row:
                    if cell.value == "[INPUT_POLE_DESC]":
                        cells.append(cell)
            cells.sort(key=lambda c: c.row)
            
            prefix = "P" if "NEW" in pole["type"] else "E"
            
            for idx, cell in enumerate(cells):
                r = cell.row
                if idx < pole["qty"]:
                    serial = f"{prefix}{str(idx+1).zfill(3)}"
                    ws.cell(row=r, column=1, value=f"{pole['type']} {serial}").font = black_font
                    ws.cell(row=r, column=4, value=pole["size_clean"]).font = black_font # Isi tabel detail METER INCH
                    ws.cell(row=r, column=11, value="□pass  □fail □Need Repair").font = black_font # Kotak kosong manual
                else:
                    ws.cell(row=r, column=1, value="")
                    ws.cell(row=r, column=4, value="")
                    ws.cell(row=r, column=11, value="")

    for s_name in template_poles[len(parsed_poles):]:
        if s_name in wb.sheetnames: wb.remove(wb[s_name])

    # 8. PENGGANTIAN METADATA MASIF (WARNA HITAM)
    for sheet in wb.worksheets:
        for row in sheet.iter_rows():
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

    # 9. PEMBUNUH SHEET AGRESIF
    sheets_to_remove = []
    for s_name in wb.sheetnames:
        name_lower = s_name.lower().strip()
        if mode == "cluster":
            for blacklist in BLACKLIST_CLUSTER:
                if blacklist in name_lower:
                    sheets_to_remove.append(s_name)
                    break
        elif mode == "subfeeder":
            for blacklist in BLACKLIST_SUBFEEDER:
                if blacklist in name_lower:
                    sheets_to_remove.append(s_name)
                    break
                
    for s_name in set(sheets_to_remove):
        if s_name in wb.sheetnames: wb.remove(wb[s_name])

    def get_sort_weight(sheet_name):
        name_lower = sheet_name.lower()
        for idx, prefix in enumerate(SORT_ORDER_LOWER):
            if name_lower.startswith(prefix): return idx
        return 999 
        
    wb._sheets.sort(key=lambda s: get_sort_weight(s.title))

    excel_stream = io.BytesIO()
    wb.save(excel_stream)
    excel_stream.seek(0)
    return excel_stream
