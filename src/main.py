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

        # 1. Konfigurasi Jendela
        self.window_width = 380
        self.window_height = 260 # Sedikit dipertinggi untuk label baru
        self.setup_window_position()
        
        self.title("ErgoSense Monitor")
        self.resizable(False, False)

        # 2. Grid Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2, 3), weight=1)

        # 3. Komponen UI
        
        # Header
        self.lbl_title = ctk.CTkLabel(self, text="ERGOSENSE LIVE MONITOR", 
                                      font=("Roboto Medium", 12), text_color="#888888")
        self.lbl_title.grid(row=0, column=0, pady=(15, 0), sticky="s")

        # --- [BARU] Label Target Ideal (Persistent) ---
        self.lbl_ideal = ctk.CTkButton(self, text="Target Ideal: --", 
                                       height=24,
                                       fg_color="#2B2B2B", # Warna background gelap
                                       hover=False,
                                       font=("Arial", 11), 
                                       text_color="#AAAAAA",
                                       corner_radius=12)
        self.lbl_ideal.grid(row=1, column=0, pady=(5, 0), sticky="n")

        # Angka Jarak Realtime (Besar)
        self.lbl_jarak = ctk.CTkLabel(self, text="--", 
                                      font=("Roboto", 80, "bold"), 
                                      text_color="white")
        self.lbl_jarak.grid(row=2, column=0, pady=0)
        
        # Satuan cm
        self.lbl_unit = ctk.CTkLabel(self, text="cm", font=("Roboto", 16), text_color="#aaaaaa")
        self.lbl_unit.place(relx=0.75, rely=0.55, anchor="w")

        # Status Bar
        self.btn_status = ctk.CTkButton(self, text="MENUNGGU PERANGKAT...", 
                                        height=45,
                                        width=300,
                                        corner_radius=10,
                                        font=("Roboto", 14, "bold"),
                                        fg_color="#333333", 
                                        hover=False)
        self.btn_status.grid(row=3, column=0, pady=(0, 20), sticky="n")

        # Footer
        self.lbl_port = ctk.CTkLabel(self, text="Silakan hubungkan USB...", font=("Arial", 10), text_color="#444444")
        self.lbl_port.place(relx=0.5, rely=0.95, anchor="center")

        # 4. Logic Variables
        self.running = True
        self.serial_conn = None
        
        # Thread Serial
        self.thread = threading.Thread(target=self.serial_worker, daemon=True)
        self.thread.start()

    def setup_window_position(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_pos = screen_width - self.window_width - 20
        y_pos = screen_height - self.window_height - 50 
        self.geometry(f"{self.window_width}x{self.window_height}+{x_pos}+{y_pos}")

    def cari_port_otomatis(self):
        ports = serial.tools.list_ports.comports()
        for p in ports:
            if "Arduino" in p.description or "CH340" in p.description or "USB Serial" in p.description or "USB-SERIAL" in p.description:
                return p.device
        return None

    def update_ui(self, jarak, status):
        try:
            # Warna Tema
            C_AMAN = "#00C853"      
            C_WARNING = "#FFAB00"   
            C_BAHAYA = "#D50000"    
            C_OFF = "#333333"       
            C_CALIB = "#AA00FF"     

            # --- LOGIKA MENANGKAP JARAK IDEAL (FITUR BARU) ---
            # Kita cek apakah status mengandung kata "CALIBRATED"
            if "CALIBRATED" in status:
                # Update Label Kecil (Permanen)
                self.lbl_ideal.configure(text=f"Target Ideal: {jarak} cm", text_color="#00C853")
                
                # Feedback visual sesaat di tombol status
                if "MEM" in status:
                     self.btn_status.configure(text=f"MEMORI TERMUAT", fg_color=C_AMAN)
                else:
                     self.btn_status.configure(text=f"KALIBRASI SELESAI", fg_color=C_AMAN)
                
                # Update angka besar juga
                self.lbl_jarak.configure(text=jarak, text_color=C_AMAN)

            # --- LOGIKA TAMPILAN REALTIME BIASA ---
            elif "CALIB_" in status: # Countdown
                detik = status.split("_")[1]
                self.lbl_jarak.configure(text=detik, text_color=C_CALIB)
                self.btn_status.configure(text="PERSIAPAN KALIBRASI...", fg_color=C_CALIB)
            
            elif "CALIBRATING" in status:
                self.lbl_jarak.configure(text=jarak, text_color="white")
                self.btn_status.configure(text="MENGAMBIL SAMPEL...", fg_color=C_CALIB)

            elif status == "AMAN":
                self.lbl_jarak.configure(text=jarak, text_color=C_AMAN)
                self.btn_status.configure(text="POSISI AMAN", fg_color=C_AMAN)

            elif status == "WARNING":
                self.lbl_jarak.configure(text=jarak, text_color=C_WARNING)
                self.btn_status.configure(text="HATI-HATI (BUNGKUK)", fg_color=C_WARNING)

            elif status == "BAHAYA":
                self.lbl_jarak.configure(text=jarak, text_color=C_BAHAYA)
                self.btn_status.configure(text="!!! PERINGATAN !!!", fg_color=C_BAHAYA)
            
            elif status == "STANDBY" or status == "JAUH":
                self.lbl_jarak.configure(text=jarak, text_color="gray")
                self.btn_status.configure(text="MODE STANDBY", fg_color=C_OFF)
            
            elif status == "ERROR":
                self.lbl_jarak.configure(text="ERR")
                self.btn_status.configure(text="BUTUH KALIBRASI", fg_color=C_OFF)

        except Exception as e:
            print(f"UI Error: {e}")

    def serial_worker(self):
        while self.running:
            if self.serial_conn is None:
                port = self.cari_port_otomatis()
                if port:
                    self.lbl_port.configure(text=f"Menghubungkan ke {port}...", text_color="#FFAB00")
                    try:
                        self.serial_conn = serial.Serial(port, 9600, timeout=1)
                        time.sleep(2) 
                        self.lbl_port.configure(text=f"Terhubung: {port}", text_color="#00C853")
                    except:
                        self.serial_conn = None
                else:
                    self.lbl_port.configure(text="Menunggu Koneksi USB...", text_color="#666666")
                    self.btn_status.configure(text="TIDAK ADA PERANGKAT", fg_color="#333333")
                    self.lbl_jarak.configure(text="--", text_color="gray")
                    # Reset Label Ideal jika putus
                    self.lbl_ideal.configure(text="Target Ideal: --", text_color="#AAAAAA")
                    time.sleep(1)
            else:
                try:
                    if self.serial_conn.in_waiting > 0:
                        line = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                        if "," in line:
                            parts = line.split(",")
                            if len(parts) >= 2:
                                self.update_ui(parts[0], parts[1])
                except serial.SerialException:
                    self.serial_conn.close()
                    self.serial_conn = None
                    self.lbl_port.configure(text="Koneksi Terputus!", text_color="#D50000")
                except Exception:
                    pass
                time.sleep(0.01)

if __name__ == "__main__":
    app = ErgoSenseMonitor()
    app.mainloop()
