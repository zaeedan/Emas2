import re

# Daftar data yang perlu diproses
data_list = [
    "Soal-Latihan-UTS-2024 closes activity in Arsitektur Komputer Moderen 2024 is due on 23 October 2024, 1:00 PM",
    "Tugas-Proyek-Akhir-2024 closes activity in Pemrograman Berbasis Objek 2024 is due on 25 October 2024, 3:30 PM",
    "Ujian-Praktikum-2024 closes activity in Jaringan Komputer 2024 is due on 30 October 2024, 10:00 AM"
]

# Fungsi untuk memproses satu entri data
def proses_data(data):
    # Pisahkan berdasarkan "activity in"
    parts = data.split(" activity in ")

    # Bagian judul (sebelum "activity in")
    judul = parts[0].strip()

    # Bagian setelah "activity in" yang berisi nama matkul dan tanggal
    matkul_tanggal = parts[1]

    # Cari nama matkul (hingga "is due on")
    matkul, tanggal_waktu = re.split(r" is due on ", matkul_tanggal)

    # Bersihkan spasi tambahan
    matkul = matkul.strip()
    tanggal_waktu = tanggal_waktu.strip()

    return judul, matkul, tanggal_waktu

# Loop melalui semua data
for data in data_list:
    judul, matkul, tanggal_waktu = proses_data(data)
    print(f"Judul: {judul}")
    print(f"Nama Matkul: {matkul}")
    print(f"Tanggal dan Waktu: {tanggal_waktu}")
    print("-" * 40)  # Pembatas antar data

