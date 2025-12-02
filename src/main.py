import customtkinter as ctk
import serial
import threading
import time

# --- KONFIGURASI ---
# Sesuaikan port ini dengan port Arduino di Arch Linux kamu!
# Biasanya /dev/ttyUSB0 atau /dev/ttyACM0
SERIAL_PORT = '/dev/ttyUSB0' 
BAUD_RATE = 9600

class ErgoSenseApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Setup Jendela Utama
        self.title("ErgoSense Dashboard")
        self.geometry("500x400")
        ctk.set_appearance_mode("Dark") # Mode Gelap ala Hacker
        ctk.set_default_color_theme("blue")

        # Grid Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2, 3), weight=1)

        # 1. Header
        self.lbl_title = ctk.CTkLabel(self, text="ERGOSENSE MONITOR", font=("Roboto Medium", 24))
        self.lbl_title.grid(row=0, column=0, pady=10, sticky="ew")

        # 2. Lingkaran Indikator Jarak (Angka Besar)
        self.lbl_jarak = ctk.CTkLabel(self, text="0 cm", font=("Roboto", 80, "bold"), text_color="#3B8ED0")
        self.lbl_jarak.grid(row=1, column=0, pady=10)

        # 3. Kotak Status
        self.btn_status = ctk.CTkButton(self, text="MENUNGGU KONEKSI...", 
                                        font=("Roboto", 18, "bold"),
                                        height=60, 
                                        fg_color="gray", 
                                        hover=False)
        self.btn_status.grid(row=2, column=0, padx=40, pady=10, sticky="ew")

        # 4. Footer Info
        self.lbl_info = ctk.CTkLabel(self, text="Menghubungkan ke Arduino...", font=("Arial", 12))
        self.lbl_info.grid(row=3, column=0, pady=10)

        # Variable System
        self.running = True
        
        # Mulai Thread Pembaca Serial (Agar aplikasi tidak macet/not responding)
        self.thread = threading.Thread(target=self.read_serial_data)
        self.thread.daemon = True
        self.thread.start()

    def read_serial_data(self):
        """Fungsi ini berjalan di latar belakang untuk membaca data USB"""
        try:
            ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            print(f"Berhasil terhubung ke {SERIAL_PORT}")
            self.lbl_info.configure(text=f"Terhubung: {SERIAL_PORT}")

            while self.running:
                if ser.in_waiting > 0:
                    # Baca baris data: "45,AMAN"
                    try:
                        line = ser.readline().decode('utf-8').strip()
                        if "," in line:
                            data = line.split(",")
                            jarak_str = data[0]
                            status_str = data[1]

                            # Update UI (Harus real-time)
                            self.update_gui(jarak_str, status_str)
                    except Exception as e:
                        print(f"Data Error: {e}")
                
                time.sleep(0.05) # Istirahat dikit biar CPU gak panas

        except serial.SerialException:
            self.lbl_info.configure(text="GAGAL: Cek Port USB / Izin Akses!")
            self.btn_status.configure(text="DISCONNECTED", fg_color="gray")

    def update_gui(self, jarak, status):
        """Mengupdate warna dan angka di layar"""
        # Update Angka
        self.lbl_jarak.configure(text=f"{jarak} cm")

        # Update Warna Status
        if status == "AMAN":
            self.btn_status.configure(text="POSISI AMAN", fg_color="#2CC985") # Hijau
            self.lbl_jarak.configure(text_color="#2CC985")
        
        elif status == "WARNING":
            self.btn_status.configure(text="TERDETEKSI MEMBUNGKUK...", fg_color="#F29F05") # Kuning/Oranye
            self.lbl_jarak.configure(text_color="#F29F05")
            
        elif status == "BAHAYA":
            self.btn_status.configure(text="!!! PERINGATAN POSTUR !!!", fg_color="#C0392B") # Merah
            self.lbl_jarak.configure(text_color="#C0392B")
            
        elif status == "ERROR":
            self.btn_status.configure(text="BUTUH KALIBRASI", fg_color="gray")

if __name__ == "__main__":
    app = ErgoSenseApp()
    app.mainloop()