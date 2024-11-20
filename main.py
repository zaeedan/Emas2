from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from datetime import datetime
import re

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path
import pickle
import datetime 

import maskpass

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def connectCalendar(SCOPES):
    """Menambahkan tugas baru ke Google Calendar dengan warna tertentu."""
    creds = None
    # File token.pickle menyimpan token akses dan refresh pengguna.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # Jika tidak ada kredensial (valid), biarkan pengguna login.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Simpan kredensial untuk run berikutnya
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service

# Menambahkan tugas ke Google Calendar
def insertCalendar(service, task_summary, task_description, due_date, due_time):

    task = {
        'summary': task_summary,
        'description': task_description,
        'start': {
            'date': due_date,  # Hanya tanggal, bukan waktu
            'time': due_time,  # Waktu tugas
        },
        'end': {
            'date': due_date,
            'time': due_time,
        },
        'status': 'confirmed',
        'colorId': '8',  # Ganti dengan ID warna yang diinginkan
    }

    # Memasukkan tugas ke kalender
    service.events().insert(calendarId='primary', body=task).execute()
    # print('Tugas berhasil ditambahkan!')
    return

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

def main():

    print("Masukkan username dan password Emas2 Anda!")
    username = input("Username: ")
    password = maskpass.askpass(prompt="Password: ", mask="*")
    
    print("\nOpening browser...\n(Do not close it)\n")

    # URL halaman login
    url = 'https://emas2.ui.ac.id/my/'

    # Inisialisasi Selenium
    options = webdriver.FirefoxOptions()
    options.add_argument('--start-maximized')
    driver = webdriver.Firefox(options=options)
    driver.get(url)

    # Tunggu halaman login muncul
    time.sleep(3)


    print("\nLogging in...")
    # Cari elemen input username dan password, dan masukkan nilai
    driver.find_element(By.ID, 'username').send_keys(username)
    driver.find_element(By.ID, 'password').send_keys(password)

    # Klik tombol login (ganti selector sesuai dengan halaman web)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    
    time.sleep(10)
    # Mengecek jika login gagal
    if driver.current_url == "https://emas2.ui.ac.id/login/index.php":
        print("Login failed!\n")
        print("Closing browser...")
        driver.quit()
        print("Browser closed!\n")
        print("All done!")
        return
    
    print("Login successful!\n")

    print("Collecting data...")

    # Tunggu sampai login berhasil dan halaman berikutnya dimuat
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'text-truncate')))

    # Sekarang mulai scraping halaman setelah login berhasil
    soup = BeautifulSoup(driver.page_source, "html.parser")
    containers = soup.findAll('ul', attrs={'class': 'media-list'})

    data = []

    # Ambil data yang diinginkan
    for container in containers:
        try:
            anchors = container.findAll('a', title=True)

            for anchor in anchors:
                if anchor :
                    # judul_tugas = anchor.get('title', '').strip()
                    deskripsi = anchor.get('aria-label', '').strip() 
                    # tanggal = container.find('h5', attrs={'class': 'h6 mt-3 mb-0 '}).text  
                    # jam = container.find('small', attrs={'class': 'text-right text-nowrap pull-right'}).text  
                    
                    # Tambahkan data ke list
                    if deskripsi != 'Add submission':
                        data.append((deskripsi))
                    time.sleep(1)
        except AttributeError:
            continue
    
    print("Data collected!\n")
    # Cetak data yang diambil
    print(data)

    print("\nClosing browser...")
    # Tutup browser
    driver.quit()

    print("Browser closed!\n")
    
    if data == []:
        print("No data found!\n")
        print("All done!")
        return

    print("Processing data...\n")
    print("Exporting data to tugas.csv...")
    # Simpan data ke dalam file CSV
    time.sleep(1)
    df = pd.DataFrame(data, columns=['Tugas'])
    df.to_csv('tugas.csv', index=False)
    print("Exported!\n")

    print("Connecting to Google Calendar...")
    # Connect to Google Calendar
    service = connectCalendar(SCOPES)
    print("Connected!\n")

    print("Exporting data to Google Calendar...\n")
    
    for data1 in data:
        if(data1 == '' or data1 == 'Answer the questions'):
            continue

        judul, matkul, tanggal_waktu = proses_data(data1)
        print(f"Judul: {judul}")
        print(f"Nama Matkul: {matkul}")
        print(f"Tanggal dan Waktu: {tanggal_waktu}")
        print("-" * 40)  # Pembatas antar data

        # Parsing string menjadi objek datetime
        date_object = datetime.datetime.strptime(tanggal_waktu, "%d %B %Y, %I:%M %p")

        # Mengonversi objek datetime ke format YYYY-MM-DD
        formatted_date = date_object.strftime("%Y-%m-%d")
        formatted_time = date_object.strftime("%H:%M:%S")

        # Insert data to Google Calendar
        insertCalendar(service, judul, matkul, formatted_date, formatted_time)
        time.sleep(1)
    
    print("\nExported!\n")

    print("\nData processed!\n")

    print("All done!")

if __name__ == '__main__':
    main()