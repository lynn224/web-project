import openpyxl
import io

def inject_excel_fase1(template_file, metadata, parsed_fat, parsed_poles):
    """
    Mesin Inti Penyuntik Data Administrasi & Pengganda Sheet Sekuensial.
    Menggunakan objek file-like (BytesIO) agar kompatibel dengan serverless cloud.
    """
    # Memuat workbook master dari memori atau jalur file
    wb = openpyxl.load_workbook(template_file)
    
    # =============================================================================
    # 1. LOGIKA INJEKSI METADATA KE LEMBAR SUPPORT TABLE
    # =============================================================================
    support_sheet = None
    # Deteksi dinamis mencari sheet support table milik DC
    for name in wb.sheetnames:
        if "support" in name.lower() or "table" in name.lower():
            support_sheet = wb[name]
            break
            
    if support_sheet:
        # Melakukan pemindaian sel untuk mencari placeholder kaku [NAMA_VARIABEL]
        for row in support_sheet.iter_rows(min_row=1, max_row=100, min_col=1, max_col=20):
            for cell in row:
                if cell.value and isinstance(cell.value, str):
                    for key, val in metadata.items():
                        placeholder = f"[{key}]"
                        if placeholder in cell.value:
                            # Menyuntikkan nilai teks murni dari Form Web
                            cell.value = cell.value.replace(placeholder, str(val))

    # =============================================================================
    # 2. LOGIKA CLONING & SEKUENSIONAL SHEET JALUR FAT
    # =============================================================================
    # Sistem mencari template sheet bernama 'MASTER_FAT' untuk diduplikasi
    if "MASTER_FAT" in wb.sheetnames and parsed_fat:
        master_fat_sheet = wb["MASTER_FAT"]
        for fat_code in parsed_fat:
            # Lewati proses jika sheet dengan nama tersebut sudah ada akibat double klik
            if fat_code in wb.sheetnames:
                continue
            # Proses duplikasi sheet beserta seluruh style, font, dan rumus bawaannya
            cloned_fat = wb.copy_worksheet(master_fat_sheet)
            cloned_fat.title = fat_code
            
            # Cari placeholder internal [ID_FAT] di dalam sheet yang baru dikloning
            for row in cloned_fat.iter_rows(min_row=1, max_row=50, min_col=1, max_col=15):
                for cell in row:
                    if cell.value and isinstance(cell.value, str):
                        if "[ID_FAT]" in cell.value:
                            cell.value = cell.value.replace("[ID_FAT]", str(fat_code))

    # =============================================================================
    # 3. LOGIKA CLONING & PENULISAN BARIS DATA TABEL TIANG (POLE)
    # =============================================================================
    if "MASTER_POLE" in wb.sheetnames and parsed_poles:
        master_pole_sheet = wb["MASTER_POLE"]
        for pole in parsed_poles:
            # Merakit nama sheet berdasarkan Tipe dan Ukuran, misal: NEW_POLE_72.5 atau EXT_POLE_74
            raw_title = f"{pole['type'].replace(' ', '_')}_{pole['size']}"
            sheet_title = raw_title[:31] # Batasan kaku panjang nama sheet Excel
            
            if sheet_title in wb.sheetnames:
                cloned_pole = wb[sheet_title]
            else:
                cloned_pole = wb.copy_worksheet(master_pole_sheet)
                cloned_pole.title = sheet_title
            
            # Cari baris jangkar/start row tempat data fisik tiang harus ditulis
            start_row = 10  # Batas aman default jika jangkar tidak ditemukan
            for r in range(1, 40):
                found = False
                for c in range(1, 10):
                    if cloned_pole.cell(row=r, column=c).value == "[DATA_TIANG]":
                        start_row = r
                        cloned_pole.cell(row=r, column=c).value = "" # Hapus tanda pembatas
                        found = True
                        break
                if found:
                    break
            
            # Menyuntikkan baris data fisik tiang secara berulang sesuai nilai qty perintah
            for idx in range(pole["qty"]):
                target_row = start_row + idx
                # Mengisi kolom nomor urut, tipe tiang, dan dimensi ukuran ke lembar kerja
                cloned_pole.cell(row=target_row, column=1).value = idx + 1
                cloned_pole.cell(row=target_row, column=2).value = str(pole["type"])
                cloned_pole.cell(row=target_row, column=3).value = f"{pole['size']} MTR"

    # =============================================================================
    # 4. PROSES CLEANING SHEET MASTER & PACKING BUFFER
    # =============================================================================
    # Menghapus sheet master induk agar dokumen final bersih dan siap diserahkan ke customer
    if "MASTER_FAT" in wb.sheetnames:
        wb.remove(wb["MASTER_FAT"])
    if "MASTER_POLE" in wb.sheetnames:
        wb.remove(wb["MASTER_POLE"])
        
    # Memasukkan seluruh struktur binary Excel ke dalam memory stream buffer
    excel_stream = io.BytesIO()
    wb.save(excel_stream)
    excel_stream.seek(0) # Mengembalikan posisi pointer ke nol siap unduh
    
    return excel_stream
