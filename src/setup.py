import base64
import io
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
from PIL import Image, ImageTk

from icon import EMBEDDED_ICON


class PESetup:
    @staticmethod
    def setup_crypto_key():
        argon_key = simpledialog.askstring("VPK Setup | Crypto Key", f"Enter the Crypto Key: {'  ' * 50}")
        if argon_key is None:
            messagebox.showinfo("VPK Setup | Crypto Key",
                                "Operation canceled.\nThe crypto Key and IV has not been changed.")
            return None
        elif argon_key == "" or len(argon_key) < 64:
            messagebox.showerror("VPK Setup | Crypto Key",
                                 "The crypto Key must not be empty and set to a minimum length of 64!")
            return False
        return argon_key
    
    @staticmethod
    def setup_crypto_iv():
        argon_iv = simpledialog.askstring("VPK Setup | Crypto IV", f"Enter the Crypto IV:  {'  ' * 50}")
        if argon_iv is None:
            messagebox.showinfo("VPK Setup | Crypto IV",
                                "Operation canceled.\nThe crypto Key and IV has not been changed.")
            return None
        elif argon_iv == "" or len(argon_iv) < 24:
            messagebox.showerror("VPK Setup | Crypto IV",
                                 "The crypto IV must not be empty and set to a minimum length of 24!")
            return False
        return argon_iv
    
    @staticmethod
    def setup_author():
        author = simpledialog.askstring("VPK Setup | Author", f"Enter the Author name:{'  ' * 50}")
        if author is None:
            messagebox.showinfo("VPK Setup | Author", "Operation canceled.\nThe author name has not been changed.")
            return None
        elif author == "" or len(author) > 16:
            messagebox.showerror("VPK Setup | Author", "The author name must not be empty and not greater than 16!")
            return False
        return author
    
    @staticmethod
    def setup_compressor(child = False):
        compression: list[str] = [None]
        
        def confirm_selection():
            selected_compressor = compression_var.get()
            if selected_compressor:
                # nonlocal compression
                compression[0] = selected_compressor
                window.destroy()
            else:
                # nonlocal compression
                compression[0] = None
                window.destroy()
                messagebox.showerror("VPK Setup | Compressor", "No compression method selected.")
        
        # Create a new tkinter window
        window = tk.Tk() if not child else tk.Toplevel()
        window.title("VPK Setup | Compressor")
        icon_data = base64.b64decode(EMBEDDED_ICON)
        icon_image = Image.open(io.BytesIO(icon_data))
        icon_image = icon_image.resize((32, 32))
        ico = ImageTk.PhotoImage(icon_image)
        window.iconphoto(True, ico)
        window.eval('tk::PlaceWindow %s center' % window.winfo_toplevel())
        
        # Create a label and dropdown menu
        label = tk.Label(window, text=f"Choose the compression method:{'  ' * 40}", justify="left")
        label.grid(row=0, column=0, columnspan=4, padx=10, pady=10)
        
        compression_var = tk.StringVar()
        compression_combobox = ttk.Combobox(window, textvariable = compression_var)
        compression_combobox['values'] = ['Gzip (Balanced)', 'ZSTD (Balanced)', 'Bzip2 (Slow)', 'LZMA (Slow)', 'LZ4 (Fast)']
        compression_combobox.current(0)
        compression_combobox.grid(row=1, column=1, columnspan=2, padx=10, pady=10)
        
        # Create a button to confirm the selection
        # confirm_button = ttk.Button(window, text = "Confirm", command = confirm_selection)
        # confirm_button.pack(padx = 10, pady = 10)
        
        ok_button = tk.Button(window, text = "OK", command = confirm_selection, width = 10)
        ok_button.grid(row = 2, column = 1, padx = 5, pady = 5, sticky = "e")
        
        cancel_button = tk.Button(window, text = "Cancel", command = window.destroy, width = 10)
        cancel_button.grid(row = 2, column = 2, padx = 5, pady = 5, sticky = "w")
        
        # Start the tkinter event loop
        window.resizable(False, False)
        if not child: window.mainloop()
        
        return compression[0].split(" ")[0].lower()
    
    @staticmethod
    def setup_encryption(child = False):
        encryption: list[str] = [None]
        
        def confirm_selection():
            selected_encryption = encryption_var.get()
            if selected_encryption:
                # nonlocal encryption
                encryption[0] = selected_encryption
                window.destroy()
            else:
                # nonlocal encryption
                encryption[0] = None
                window.destroy()
                messagebox.showerror("VPK Setup | Encryption", "No encryption method selected.")
        
        # Create a new tkinter window
        window = tk.Tk() if not child else tk.Toplevel()
        window.title("VPK Setup | Encryption")
        icon_data = base64.b64decode(EMBEDDED_ICON)
        icon_image = Image.open(io.BytesIO(icon_data))
        icon_image = icon_image.resize((32, 32))
        ico = ImageTk.PhotoImage(icon_image)
        window.iconphoto(True, ico)
        window.eval('tk::PlaceWindow %s center' % window.winfo_toplevel())
        
        # Create a label and dropdown menu
        label = tk.Label(window, text=f"Choose the encryption method:{'  ' * 40}", justify="left")
        label.grid(row=0, column=0, columnspan=4, padx=10, pady=10)
        
        encryption_var = tk.StringVar()
        encryption_combobox = ttk.Combobox(window, textvariable = encryption_var)
        encryption_combobox['values'] = ['AES-GCM (Strong)', 'AES-CTR (Fast)', 'AES-CBC (Basic)']
        encryption_combobox.current(0)
        encryption_combobox.grid(row=1, column=1, columnspan=2, padx=10, pady=10)
        
        # Create a button to confirm the selection
        # confirm_button = ttk.Button(window, text = "Confirm", command = confirm_selection)
        # confirm_button.pack(padx = 10, pady = 10)
        
        ok_button = tk.Button(window, text = "OK", command = confirm_selection, width = 10)
        ok_button.grid(row = 2, column = 1, padx = 5, pady = 5, sticky = "e")
        
        cancel_button = tk.Button(window, text = "Cancel", command = window.destroy, width = 10)
        cancel_button.grid(row = 2, column = 2, padx = 5, pady = 5, sticky = "w")
        
        # Start the tkinter event loop
        window.resizable(False, False)
        if not child: window.mainloop()
        
        return encryption[0].split(" ")[0].lower()
