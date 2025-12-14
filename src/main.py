import customtkinter as ctk
import serial
import serial.tools.list_ports
import threading
import time

# --- KONFIGURASI TEMA ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class ErgoSenseMonitor(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. Konfigurasi Jendela (Kanan Bawah)
        self.window_width = 400
        self.window_height = 250
        self.setup_window_position()
        
        self.title("ErgoSense Monitor")
        self.resizable(False, False)

        # 2. Grid Layout Configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # 3. UI Components (Modern Minimalist)
        
        # Header
        self.lbl_title = ctk.CTkLabel(self, text="ERGOSENSE LIVE", 
                                      font=("Roboto Medium", 14), text_color="#aaaaaa")
        self.lbl_title.grid(row=0, column=0, pady=(15, 0), sticky="s")

        # Indikator Utama (Angka Jarak)
        self.lbl_jarak = ctk.CTkLabel(self, text="--", 
                                      font=("Roboto", 70, "bold"), 
                                      text_color="white")
        self.lbl_jarak.grid(row=1, column=0, pady=0)
        self.lbl_unit = ctk.CTkLabel(self, text="cm", font=("Roboto", 16))
        self.lbl_unit.place(relx=0.7, rely=0.5) # Tempel manual di samping angka

        # Kotak Status (Indikator Bahaya/Aman)
        self.btn_status = ctk.CTkButton(self, text="MENCARI PERANGKAT...", 
                                        height=40,
                                        width=250,
                                        corner_radius=20,
                                        font=("Roboto", 14, "bold"),
                                        fg_color="#333333", 
                                        hover=False)
        self.btn_status.grid(row=2, column=0, pady=(0, 20), sticky="n")

        # Footer Info (Port Connection)
        self.lbl_port = ctk.CTkLabel(self, text="Menunggu USB...", font=("Arial", 10), text_color="#555555")
        self.lbl_port.place(relx=0.5, rely=0.95, anchor="center")

        # 4. System Logic
        self.running = True
        self.serial_conn = None
        
        # Thread terpisah agar GUI tidak macet saat membaca serial
        self.thread = threading.Thread(target=self.serial_worker, daemon=True)
        self.thread.start()

    def setup_window_position(self):
        """Menempatkan jendela otomatis di pojok kanan bawah layar"""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        x_pos = screen_width - self.window_width - 20 # Geser 20px dari kanan
        y_pos = screen_height - self.window_height - 60 # Geser 60px dari bawah (hindari taskbar)
        
        self.geometry(f"{self.window_width}x{self.window_height}+{x_pos}+{y_pos}")

    def cari_port_otomatis(self):
        """Mencari port yang memiliki deskripsi Arduino atau CH340"""
        ports = serial.tools.list_ports.comports()
        for p in ports:
            # Filter kata kunci umum driver Arduino
            if "Arduino" in p.description or "CH340" in p.description or "USB Serial" in p.description:
                return p.device
        return None

    def update_ui(self, jarak, status):
        """Mengupdate tampilan berdasarkan data Arduino"""
        try:
            # Update Angka
            self.lbl_jarak.configure(text=jarak)
            
            # Logika Warna Status
            color_safe = "#00C853"    # Hijau Cerah
            color_warn = "#FFAB00"    # Kuning/Oranye
            color_danger = "#D50000"  # Merah Darah
            color_standby = "#2962FF" # Biru
            color_calib = "#AA00FF"   # Ungu
            
            if status == "AMAN":
                self.btn_status.configure(text="POSISI IDEAL", fg_color=color_safe)
            elif status == "WARNING":
                self.btn_status.configure(text="TERDETEKSI MEMBUNGKUK", fg_color=color_warn)
            elif status == "BAHAYA":
                self.btn_status.configure(text="!!! PERINGATAN !!!", fg_color=color_danger)
            elif status == "STANDBY" or status == "JAUH":
                self.btn_status.configure(text="MODE STANDBY", fg_color=color_standby)
            elif "CALIB" in status:
                self.btn_status.configure(text="SEDANG KALIBRASI...", fg_color=color_calib)
            else:
                self.btn_status.configure(text=status, fg_color="#333333")
                
        except Exception as e:
            print(f"UI Error: {e}")

    def serial_worker(self):
        """Looping utama pembacaan data di background"""
        while self.running:
            try:
                if self.serial_conn is None:
                    # MODE SEARCHING: Cari port
                    port = self.cari_port_otomatis()
                    if port:
                        self.lbl_port.configure(text=f"Menghubungkan ke {port}...")
                        try:
                            self.serial_conn = serial.Serial(port, 9600, timeout=1)
                            time.sleep(2) # Tunggu bootloader Arduino selesai
                            self.lbl_port.configure(text=f"Terhubung: {port}", text_color="#00C853")
                        except:
                            self.serial_conn = None
                    else:
                        self.lbl_port.configure(text="Menunggu Koneksi USB...", text_color="#555555")
                        self.btn_status.configure(text="TIDAK ADA PERANGKAT", fg_color="#333333")
                        self.lbl_jarak.configure(text="--")
                        time.sleep(1) # Cek setiap 1 detik

                else:
                    # MODE READING: Baca data
                    if self.serial_conn.in_waiting > 0:
                        try:
                            # Baca data mentah: "45,AMAN"
                            line = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                            
                            if "," in line:
                                data_split = line.split(",")
                                if len(data_split) >= 2:
                                    raw_jarak = data_split[0]
                                    raw_status = data_split[1]
                                    self.update_ui(raw_jarak, raw_status)
                                    
                        except serial.SerialException:
                            # Jika kabel dicabut tiba-tiba
                            self.serial_conn.close()
                            self.serial_conn = None
                            self.lbl_port.configure(text="Koneksi Terputus!", text_color="red")
                        except Exception as e:
                            print(f"Data Error: {e}")
                    
                    time.sleep(0.01) # Istirahat CPU ringan

            except Exception:
                self.serial_conn = None
                time.sleep(1)

if __name__ == "__main__":
    app = ErgoSenseMonitor()
    app.mainloop()
