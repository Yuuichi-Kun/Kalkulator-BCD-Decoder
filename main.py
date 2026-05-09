import tkinter as tk
import customtkinter as ctk
from PIL import Image

# Mapping BCD (4 bit) ke 7-segment (a, b, c, d, e, f, g)
bcd_to_7seg = {
    "0000": (1, 1, 1, 1, 1, 1, 0),  "0001": (0, 1, 1, 0, 0, 0, 0),
    "0010": (1, 1, 0, 1, 1, 0, 1),  "0011": (1, 1, 1, 1, 0, 0, 1),
    "0100": (0, 1, 1, 0, 0, 1, 1),  "0101": (1, 0, 1, 1, 0, 1, 1),
    "0110": (1, 0, 1, 1, 1, 1, 1),  "0111": (1, 1, 1, 0, 0, 0, 0),
    "1000": (1, 1, 1, 1, 1, 1, 1),  "1001": (1, 1, 1, 1, 0, 1, 1),
}

# Fungsi untuk membuat frame collapsible
class CollapsibleFrame(ctk.CTkFrame):
    def __init__(self, parent, title="", *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.title_text = title
        self.is_cokked = True

        self.header = ctk.CTkButton(self, text=f"▶  {title}", command=self.toggle, anchor="w")
        self.header.pack(fill="x", padx=2, pady=2)

        self.content = ctk.CTkFrame(self)

    def toggle(self):
        if self.is_cokked:
            self.content.pack(fill="both", expand=True, padx=10, pady=5)
            self.header.configure(text=f"▼  {self.title_text}")
        else:
            self.content.forget()
            self.header.configure(text=f"▶  {self.title_text}")
        self.is_cokked = not self.is_cokked

    def add_log(self, message):
        self.content.log_box.insert(tk.END, message + "\n")
        self.content.log_box.see(tk.END)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Kalkulator BCD-Decoder")
        self.geometry("1024x768")

        # Pakai grid di main_container, lebih stabil dari pack untuk 2 kolom
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        self.main_container.columnconfigure(0, weight=1)
        self.main_container.columnconfigure(1, weight=1)
        self.main_container.rowconfigure(0, weight=1)

        

        # ── KIRI ──────────────────────────────────────────────────────
        self.left_column = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.left_column.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.label = ctk.CTkLabel(
            self.left_column,
            text="===== Kalkulator BCD-Decoder =====",
            font=("Arial", 24, "bold"),
            text_color="#000000"
        )
        self.label.pack(pady=20)

        self.button_frame = ctk.CTkFrame(self.left_column, fg_color="grey")
        self.button_frame.pack(pady=10)

        for i in range(10):
            button = ctk.CTkButton(
                self.button_frame, text=str(i), font=("Arial", 20),
                command=lambda x=i: self.on_button_click(x)
            )
            button.grid(row=i // 3, column=i % 3, padx=10, pady=10)

        self.operasi_frame = ctk.CTkFrame(self.left_column, fg_color="grey")
        self.operasi_frame.pack(pady=10)

        tombol_operasi = [
            ("+", self.tambah), ("-", self.kurang),
            ("*", self.kali), ("/", self.bagi),
            ("=", self.hitung_hasil), ("AC", self.clear)
        ]

        for i, (symbol, func) in enumerate(tombol_operasi):
            button = ctk.CTkButton(
                self.operasi_frame, text=symbol, font=("Arial", 20),
                command=func
            )
            button.grid(row=i // 3, column=i % 3, padx=10, pady=10)

        self.image_button = ctk.CTkButton(self.left_column, text="Lihat Tabel Kebenaran", font=("Arial", 16), command=self.show_truth_table)
        self.image_button.pack(pady=10)
        

        # ── KANAN ─────────────────────────────────────────────────────
        self.right_column = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.right_column.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.bcd_entry = ctk.CTkEntry(
            self.right_column,
            font=("Arial", 24, "bold"),
            width=400, height=60,
            corner_radius=15, border_width=2,
            border_color="#1f538d",
            fg_color="#2b2b2b",
            text_color="#00FF00",
            placeholder_text="0",
            justify="center"
        )
        self.bcd_entry.pack(pady=30)

        # 7 Segment Display Label
        self.seg_label = ctk.CTkLabel(
            self.right_column,
            text="[Seven Segment Display]",
            font=("Arial", 16),
            text_color="grey"
        )

        # Canvas untuk 7-segment display
        self.canvas = ctk.CTkCanvas(self.right_column, width=200, height=300, bg="#2b2b2b", highlightthickness=0)
        self.canvas.pack(pady=20)
        self.segments = {}
        self.segmen_7_visualization("0000")  # Inisialisasi dengan 0

        self.seg_label.pack(pady=20)

        self.log_frame = CollapsibleFrame(self.right_column, title="Log Operasi")
        self.log_frame.pack(fill="x", padx=10, pady=10)

        # Tambahkan textbox log di dalam content
        self.log_box = ctk.CTkTextbox(self.log_frame.content, height=150, font=("Courier", 13))
        self.log_box.pack(fill="both", expand=True, padx=5, pady=5)
        self.log_frame.content.log_box = self.log_box  # referensi untuk add_log

        self.angka_pertama = 0
        self.operasi = None

    # ── FUNCTIONS ───────────────────────────────────────────────────── 
    def on_button_click(self, number):
        current_text = self.bcd_entry.get()
        new_text = current_text + str(number)
        self.bcd_entry.delete(0, tk.END)
        self.bcd_entry.insert(0, new_text)

        bcd_code = format(number, '04b')
        if bcd_code in bcd_to_7seg:
            self.segmen_7_visualization(bcd_code)
            print(f"Button {number} clicked -> BCD: {bcd_code} -> 7-segment: {bcd_to_7seg[bcd_code]}")
    
    def log(self, message):
        self.log_frame.add_log(message)

    def tambah(self):
        val = self.bcd_entry.get()
        if val:
            angka = int(float(val))
            if not (0 <= angka <= 9):
                self.bcd_entry.delete(0, tk.END)
                self.bcd_entry.insert(0, "Error")
                self.log(f"Error: angka pertama ({angka}) harus 0-9")
                return
            self.angka_pertama = float(val)
            self.operasi = "+"
            self.log(f"Input angka pertama: {val} | BCD-Code: {format(int(float(val)), '04b')} | operasi: {self.operasi}")
            self.bcd_entry.delete(0, tk.END)

    def kurang(self):
        val = self.bcd_entry.get()
        if val:
            angka = int(float(val))
            if not (0 <= angka <= 9):
                self.bcd_entry.delete(0, tk.END)
                self.bcd_entry.insert(0, "Error")
                self.log(f"Error: angka pertama ({angka}) harus 0-9")
                return
            self.angka_pertama = float(val)
            self.operasi = "-"
            self.log(f"Input angka pertama: {val} | BCD-Code: {format(int(float(val)), '04b')} | operasi: {self.operasi}")
            self.bcd_entry.delete(0, tk.END)

    def kali(self):
        val = self.bcd_entry.get()
        if val:
            angka = int(float(val))
            if not (0 <= angka <= 9):
                self.bcd_entry.delete(0, tk.END)
                self.bcd_entry.insert(0, "Error")
                self.log(f"Error: angka pertama ({angka}) harus 0-9")
                return
            self.angka_pertama = float(val)
            self.operasi = "*"
            self.log(f"Input angka pertama: {val} | BCD-Code: {format(int(float(val)), '04b')} | operasi: {self.operasi}")
            self.bcd_entry.delete(0, tk.END)

    def bagi(self):
        val = self.bcd_entry.get()
        if val:
            angka = int(float(val))
            if not (0 <= angka <= 9):
                self.bcd_entry.delete(0, tk.END)
                self.bcd_entry.insert(0, "Error")
                self.log(f"Error: angka pertama ({angka}) harus 0-9")
                return
            self.angka_pertama = float(val)
            self.operasi = "/"
            self.log(f"Input angka pertama: {val} | BCD-Code: {format(int(float(val)), '04b')} | operasi: {self.operasi}")
            self.bcd_entry.delete(0, tk.END)

    def hitung_hasil(self):
        input_user = self.bcd_entry.get()
        if input_user and self.operasi:
            try:
                angka_kedua = float(input_user)

                # Validasi angka kedua
                if not (0 <= int(angka_kedua) <= 9):
                    self.bcd_entry.delete(0, tk.END)
                    self.bcd_entry.insert(0, "Error")
                    self.log(f"Error: angka kedua ({int(angka_kedua)}) harus 0-9")
                    return

                self.log(f"Input angka kedua: {input_user} | BCD-Code: {format(int(angka_kedua), '04b')}")

                if self.operasi == "+":   hasil = self.angka_pertama + angka_kedua
                elif self.operasi == "-": hasil = self.angka_pertama - angka_kedua
                elif self.operasi == "*": hasil = self.angka_pertama * angka_kedua
                elif self.operasi == "/":
                    hasil = self.angka_pertama / angka_kedua if angka_kedua != 0 else "Error"

                self.bcd_entry.delete(0, tk.END)

                if isinstance(hasil, (int, float)) and hasil != "Error":
                    hasil_int = int(hasil)

                    # Validasi hasil
                    if not (0 <= hasil_int <= 9):
                        self.bcd_entry.insert(0, "Error")
                        self.segmen_7_visualization("0000", dim=True)
                        self.log(f"Error: hasil ({hasil_int}) di luar jangkauan BCD (0-9)")
                        return

                    bcd_code = format(hasil_int, '04b')
                    self.bcd_entry.insert(0, str(hasil_int))
                    self.segmen_7_visualization(bcd_code)
                    self.log(f"Hasil: {hasil_int} | BCD: {bcd_code} | 7-seg: {bcd_to_7seg[bcd_code]}")
                else:
                    self.bcd_entry.insert(0, "Error")
                    self.log("Error: pembagian dengan nol")
            except:
                self.bcd_entry.insert(0, "Error")
                self.log("Error: input tidak valid")

    # Fungsi untuk menggambar 7-segment display berdasarkan kode BCD
    def segmen_7_visualization(self, bcd_code, dim=False):
        self.canvas.delete("all")  # Bersihkan canvas sebelum menggambar ulang

        coord = {
            'a': (50, 20, 150, 40),
            'b': (160, 30, 180, 130),
            'c': (160, 150, 180, 250),
            'd': (50, 260, 150, 280),
            'e': (30, 150, 50, 250),
            'f': (30, 30, 50, 130),
            'g': (50, 140, 150, 160)
        }
        segments = bcd_to_7seg.get(bcd_code)
        if not segments:
            return
        
        for seg, on in zip(['a', 'b', 'c', 'd', 'e', 'f', 'g'], segments):
            if dim:
                color = "#3a3a3a"  # Warna redup untuk dim
            else:
                color = "red" if on else "#3a0000"
            self.canvas.create_rectangle(*coord[seg], fill=color, outline="")
            
    # Fungsi untuk membersihkan input dan reset state
    def clear(self):
        self.bcd_entry.delete(0, tk.END)
        self.angka_pertama = 0
        self.operasi = None
        self.segmen_7_visualization("0000", dim=True)  # Reset ke 0

    
    def show_truth_table(self):
        table_window = ctk.CTkToplevel(self)
        table_window.title("Tabel Kebenaran BCD-7Seg")
        table_window.grab_set()

        original_image = Image.open("assets/Tabel_Kebenaran.png")
        w, h = original_image.size

        table_window.geometry(f"{w}x{h}")

        full_image = ctk.CTkImage(original_image, size=(w, h))

        table_window.full_image = full_image

        self.label = ctk.CTkLabel(table_window, image=full_image, text="")
        self.label.pack(expand=True, fill="both")

    # Fungsi untuk menjalankan aplikasi
    def run(self):
        self.mainloop()

if __name__ == "__main__":
    app = App()
    app.run()