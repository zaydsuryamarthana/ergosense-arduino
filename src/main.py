import customtkinter as ctk
import serial
import serial.tools.list_ports
import threading
import time

class ErgoSenseApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Ergosense - Arduino") # Nama Aplikasi
        self.geometry("400x350") # Ukuran resolusi Aplikasi
        
        # Grid Aplikasi
        self.grid_columnconfigure(0, weight=1) # Buat Kolom 1 dengan Weight = 1
        self.grid_rowconfigure((0, 1, 2, 3, 4), weight=1) # Dari baris dan seterusnya dengan Weight = 1
        
        # Title di dalam Aplikasi
        self.lbl_title = ctk.CTkLabel(self, text="Ergosense Monitor", font=("Roboto Medium",24))
        self.lbl_title.grid(row=0, grid=0, pady=10, sticky="ew")
        
        # Indikator Jarak
        self.lbl_jarak = ctk.CTkLabel(self, text="--", font=("Roboto",80,"bold"), text_color="gray")
        self.lbl_jarak.grid(row=1, column=0, pady=10)
                
        # Status
        self.btn_status = ctk.CTkButton(self, text="Mencari Arduino...", font=("Roboto", 18, "bold"),height=60,fg_color="gray", hover=False)
        self.btn_status.grid(row=2, column=0, padx=40, pady=10, sticky="ew")
        
        self.lbl_info = ctk.CTkLabel(self, text="Scanning Ports...", font=("Arial",12))
        self.lbl_info.grid(row=3, column=0, pady=5)
        
        self.connect = ctk.CTkButton(self, text="Hubungkan Ulang", command=self.start_thread)
        self.connect.grid(row=4, column=0, paddy=20)
        
        self.running = False
        self.serial_conn = None
        
        self.start_thread()
        
    def start_thread(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.read_serial_data)
            self.thread.daemon = True
            self.thread.start()
    
    def cari_port_arduino(self):
        ports = list(serial.tools.list_ports.comports())
        for p in ports :
            if "Arduino" in p.description or "CH340" in p.description or "USB" in p.description:
                return p.device
        return None
    
    def read_serial_data(self):
        port_ditemukan = self.cari_port_arduino()
        if port_ditemukan:
            try:
                self.lbl_info.configure(text=f"Mencoba Koneksi ke {port_ditemukan}...")
                self.serial_conn = serial.Serial(port_ditemukan, 9600, timeout=1)
                time.sleep(2)
                
                self.lbl_info.configure(text=f"Terhubung ke {port_ditemukan}")
                
                while self.running:
                    if self.serial_conn.in_waiting > 0:
                        try:
                            line = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                            if "," in line:
                                data = line.split(",")
                                self.update(data[0], data[1])
                        except Exception:
                            pass
                    time.sleep(0.05)
            except Exception as e:
                self.lbl_info.configure(text=f"Error: {e}")
                self.running = False
        else:
            self.lbl_info.configure(text="Arduino Tidak Ditemukan! Cek Kabel.")
            self.running = False           