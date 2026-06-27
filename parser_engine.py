import re

# =============================================================================
# 1. MESIN PENERJEMAH JALUR FAT (LINE DISTRIBUTION)
# =============================================================================
def generate_fat_sequence(command):
    """
    Mengubah perintah ringkas menjadi urutan array.
    Contoh: 'A10' -> ['A01', 'A02', 'A03', ..., 'A10']
    """
    # Mencari kombinasi huruf di awal, diikuti angka di akhir
    match = re.match(r"([a-zA-Z]+)(\d+)", command.strip())
    if not match:
        return []
    
    route = match.group(1).upper() # Mengekstrak huruf rute (A, B, dst)
    count = int(match.group(2))    # Mengekstrak jumlah maksimal
    
    # Menghasilkan list dengan format 2 digit angka (zfill)
    return [f"{route}{str(i).zfill(2)}" for i in range(1, count + 1)]

def parse_all_fat(fat_commands_list):
    """Mengeksekusi seluruh daftar perintah FAT dari Web"""
    result_list = []
    for cmd in fat_commands_list:
        if cmd.strip():
            result_list.extend(generate_fat_sequence(cmd))
    return result_list

# =============================================================================
# 2. MESIN PENERJEMAH TIANG (POLE ERECTION)
# =============================================================================
def parse_pole_command(command):
    """
    Memecah perintah tiang menjadi kamus data terstruktur.
    Contoh: 'Pole 72.5 = 15' -> type: 'NEW POLE', size: '72.5', qty: 15
    """
    # Membelah string berdasarkan tanda "="
    parts = command.split("=")
    if len(parts) != 2:
        return None
    
    left_side = parts[0].strip().lower()
    try:
        qty = int(parts[1].strip())
    except ValueError:
        return None # Mengabaikan jika jumlah bukan angka valid
    
    # Deteksi jenis tiang (Baru vs Eksis)
    if "ext" in left_side:
        pole_type = "EXT POLE"
    elif "pole" in left_side:
        pole_type = "NEW POLE"
    else:
        pole_type = "UNKNOWN"
        
    # Ekstraksi angka ukuran tiang (mendukung desimal seperti 72.5)
    size_match = re.search(r"(\d+(\.\d+)?)", left_side)
    size_str = size_match.group(1) if size_match else "Unknown Size"
    
    return {
        "type": pole_type,
        "size": size_str,
        "qty": qty,
        "raw": command.strip()
    }

def parse_all_poles(pole_commands_list):
    """Mengeksekusi seluruh daftar perintah Tiang dari Web"""
    result_list = []
    for cmd in pole_commands_list:
        if cmd.strip():
            parsed_data = parse_pole_command(cmd)
            if parsed_data:
                result_list.append(parsed_data)
    return result_list
