import csv
import re
import json

base = '/Users/roishadiprayitno/.gemini/antigravity-ide/brain/0fb33612-5894-45b0-9b24-d92640e4073a/.system_generated/steps'

files = {
    'RT 01': f'{base}/482/content.md',  # gid=0
    'RT 02': f'{base}/494/content.md',  # sheet RT 02
    'RT 03': f'{base}/498/content.md',  # sheet RT 03
    'RT 04': f'{base}/452/content.md',  # gid=1302691228
}

current_year = 2026

def parse_birth_year(nik, ttl):
    birth_year = None
    nik = str(nik).strip()
    ttl = str(ttl).strip()
    
    if len(nik) == 16 and nik.isdigit():
        yy = int(nik[10:12])
        birth_year = 1900 + yy if yy > 26 else 2000 + yy
    elif ttl:
        match = re.search(r'\d{4}', ttl)
        if match:
            birth_year = int(match.group(0))
    return birth_year

def get_gender(nik):
    nik = str(nik).strip()
    if len(nik) == 16 and nik.isdigit():
        day = int(nik[6:8])
        return 'P' if day > 40 else 'L'
    return None

all_stats = {}
grand_total = 0
grand_kk = 0
grand_male = 0
grand_female = 0
grand_ages = []

for rt_name, filepath in files.items():
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Find start of CSV data
    lines = content.split('\n')
    start_idx = 0
    for i, line in enumerate(lines):
        if 'RT' in line and ('No' in line or 'Nama' in line) and ('NIK' in line or 'Keluarga' in line):
            start_idx = i
            break
    
    csv_text = '\n'.join(lines[start_idx:])
    reader = list(csv.reader(csv_text.splitlines()))
    
    if len(reader) < 2:
        continue
    
    header = reader[0]
    rows = reader[1:]
    
    # Find column indices
    nik_col = -1
    ttl_col = -1
    kk_col = -1
    hub_col = -1
    ket_col = -1
    nama_col = -1
    nama_kk_col = -1
    catatan_col = -1
    
    for i, h in enumerate(header):
        h_lower = h.strip().lower()
        if 'nik' in h_lower:
            nik_col = i
        elif h_lower == 'ttl':
            ttl_col = i
        elif 'nomer kk' in h_lower:
            kk_col = i
        elif 'hubungan' in h_lower:
            hub_col = i
        elif 'keterangan' in h_lower:
            ket_col = i
        elif 'nama anggota' in h_lower:
            nama_col = i
        elif 'nama kk' in h_lower:
            nama_kk_col = i
        elif 'catatan' in h_lower:
            catatan_col = i
    
    kk_set = set()
    total_jiwa = 0
    males = 0
    females = 0
    ages = []
    ketua_rt = ''
    
    for r in rows:
        if not r or len(r) < max(nik_col, ttl_col, kk_col, ket_col, hub_col, nama_col) + 1:
            continue
        
        nama = r[nama_col].strip() if nama_col >= 0 and nama_col < len(r) else ''
        if not nama and nama_kk_col >= 0 and nama_kk_col < len(r):
            nama = r[nama_kk_col].strip()
        if not nama:
            continue
        
        ket = ''
        if ket_col >= 0 and ket_col < len(r):
            ket = r[ket_col].strip().lower()
        if catatan_col >= 0 and catatan_col < len(r):
            ket += ' ' + r[catatan_col].strip().lower()
        
        if 'meninggal' in ket or 'keluar dari gaten' in ket or 'mati' in ket.split(',')[0] if ',' in ket else 'mati' == ket:
            continue
        
        nik = r[nik_col].strip() if nik_col >= 0 and nik_col < len(r) else ''
        ttl = r[ttl_col].strip() if ttl_col >= 0 and ttl_col < len(r) else ''
        kk_no = r[kk_col].strip() if kk_col >= 0 and kk_col < len(r) else ''
        hubungan = r[hub_col].strip().lower() if hub_col >= 0 and hub_col < len(r) else ''
        
        # Skip deceased
        if hubungan and ('meninggal' in hubungan or 'mati' in hubungan):
            continue
        if 'sudah meninggal' in ket:
            continue
            
        total_jiwa += 1
        
        if kk_no and len(kk_no) > 5:
            kk_set.add(kk_no)
        
        gender = get_gender(nik)
        if gender == 'L':
            males += 1
        elif gender == 'P':
            females += 1
        
        birth_year = parse_birth_year(nik, ttl)
        if birth_year and birth_year < current_year:
            ages.append(current_year - birth_year)
        
        # Find ketua RT (first Kepala Keluarga named Wajidi/Wahyudianto etc)
        if 'kepala keluarga' in hubungan and not ketua_rt:
            ketua_rt = nama
    
    all_stats[rt_name] = {
        'total': total_jiwa,
        'kk': len(kk_set),
        'L': males,
        'P': females,
        'ketua': ketua_rt,
        'ages': ages
    }
    
    grand_total += total_jiwa
    grand_kk += len(kk_set)
    grand_male += males
    grand_female += females
    grand_ages.extend(ages)

print("=" * 60)
print("REKAPITULASI DATA PENDUDUK PADUKUHAN GATEN")
print("=" * 60)
print(f"\nTotal Penduduk: {grand_total} Jiwa")
print(f"Total KK: {grand_kk}")
print(f"Laki-laki: {grand_male}")
print(f"Perempuan: {grand_female}")

print("\n--- PER RT ---")
for rt_name in sorted(all_stats.keys()):
    d = all_stats[rt_name]
    print(f"{rt_name}: Jiwa={d['total']}, KK={d['kk']}, L={d['L']}, P={d['P']}, Ketua={d['ketua']}")

if grand_ages:
    tot = len(grand_ages)
    balita = sum(1 for a in grand_ages if a < 5)
    anak = sum(1 for a in grand_ages if 5 <= a <= 14)
    produktif = sum(1 for a in grand_ages if 15 <= a <= 64)
    lansia = sum(1 for a in grand_ages if a >= 65)
    
    print(f"\n--- DISTRIBUSI USIA (dari {tot} jiwa teridentifikasi) ---")
    print(f"Balita (<5): {balita} ({balita/tot*100:.1f}%)")
    print(f"Anak-anak (5-14): {anak} ({anak/tot*100:.1f}%)")
    print(f"Produktif (15-64): {produktif} ({produktif/tot*100:.1f}%)")
    print(f"Lansia (65+): {lansia} ({lansia/tot*100:.1f}%)")
    
    pct_produktif = produktif/tot*100
    print(f"\nPersentase Usia Produktif: {pct_produktif:.0f}%")
