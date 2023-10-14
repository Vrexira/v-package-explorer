import base64
import io
import logging
import os
import subprocess
import time
import tkinter as tk
import webbrowser

from tkinter import filedialog, simpledialog, messagebox, ttk
from PIL import Image, ImageTk

from ValkyrieUtils.Crypto import ValkyrieCrypto
from ValkyrieUtils.Options import ValkyrieOptions
from ValkyrieUtils.Package import ValkyriePackage
from ValkyrieUtils.Tools import ValkyrieTools
from ValkyrieUtils.Logger import ValkyrieLogger

from icon import EMBEDDED_ICON  # byte icon data
from utils import get_file_type
from setup import PESetup


SIGNS = ("⇢ ", "🖼 ", "♬ ", "⍲ ", "📄 ", "？ ", "☆ ", "📂 ", "  ", "≯ ", "📦 ")
ICONS = {
    "arrow" : SIGNS[0],
    "image" : SIGNS[1],
    "sound" : SIGNS[2],
    "font"  : SIGNS[3],
    "doc"   : SIGNS[4],
    "?"     : SIGNS[5],
    "star"  : SIGNS[6],
    "dir"   : SIGNS[7],
    "space" : SIGNS[8],
    "code"  : SIGNS[9],
    "pack"  : SIGNS[10]
}
CREATE_NO_WINDOW = 0x08000000


class PackageExplorer:
    def __init__(self, config_path: str, debug: bool = False):
        self.logger = ValkyrieLogger('info', 'logger.log', 'ValkyrieUtils', True, debug)
        for v in valky:
            self.logger.info(v)
        if os.path.exists(config_path):
            self._cfg, self.config = PESetup.read_config(config_path, self.logger, debug)
        else:
            self._cfg, self.config = PESetup.create_config(config_path, self.logger, debug)
        
        # embedded ico
        self.ico = None

        # Setup
        self.argon_key = False
        self.argon_iv = False
        self.author = False

        # General
        self.popup_window = None
        self.window = None
        self.folder_tree = []
        self.byte_dict = {}
        self.expanded_nodes = set()
        self.osid = ValkyrieTools.generateHwid()

        # Setup
        self.image_label = None
        self.file_listbox = None
        self.file_infobox = None

        # Frames
        self.explorer_frame = None
        self.preview_frame = None
        self.info_frame = None

        # Labels
        self.preview_title_label = None

        # Size
        self.minimum_width = 1008
        self.minimum_height = 641
        self.last_width = 0
        self.last_height = 0

        # ARIA Packager
        self.argon_key = self.config['ArgonCrypto']['key']
        self.argon_iv = self.config['ArgonCrypto']['iv']
        crypto_key = ValkyrieCrypto.generate_argon_key(self.argon_key, self.argon_iv)
        self.ap = ValkyriePackage(crypto_key, self.logger, debug)

        # Build the Tkinter window
        self.build_window()

    def show_log(self):
        """Displays the log window with all the logged messages."""
        self.logger.info(f"show log")
        log_window = tk.Toplevel(self.window)
        log_window.title("V Package Explorer | Logger | ..a project by Valky")
        log_window.geometry("1555x500")
        log_window.resizable(False, False)

        log_text = tk.Text(log_window, wrap="word", bg="black", fg="white", state=tk.DISABLED, font=("Consolas", 11))
        log_text.pack(fill="both", expand=True)

        def update_log():
            # Load the log messages from the log file and display them in the window
            try:
                with open("logger.log", "r") as log_file:
                    log_text.config(state=tk.NORMAL)
                    log_text.delete(1.0, tk.END)
                    for line in log_file:
                        log_level = line.split(" | ")[1]  # Extract the log level from the log message
                        if log_level == "INFO":
                            log_text.insert(tk.END, line, "info")  # Use the "info" tag for INFO level logs
                        elif log_level == "WARNING":
                            log_text.insert(tk.END, line, "warning")  # Use the "warning" tag for WARNING level logs
                        elif log_level == "ERROR":
                            log_text.insert(tk.END, line, "error")  # Use the "error" tag for ERROR level logs
                        else:
                            log_text.insert(tk.END, line)

            except FileNotFoundError:
                log_text.insert(tk.END, "Log file not found.")

            log_text.see(tk.END)
            log_text.config(state=tk.DISABLED)
            log_window.after(1000, update_log)

        # Configure tags for different log levels
        log_text.tag_configure("info", foreground="lightgrey")
        log_text.tag_configure("warning", foreground="yellow")
        log_text.tag_configure("error", foreground="red")
        # log_text.config(state = tk.DISABLED)
        update_log()

    def build_window(self):
        """Build the main window."""
        self.logger.info(f"build window")
        self.window = tk.Tk()
        
        icon_data = base64.b64decode(EMBEDDED_ICON)
        icon_image = Image.open(io.BytesIO(icon_data))
        icon_image = icon_image.resize((32, 32))
        self.ico = ImageTk.PhotoImage(icon_image)
        self.window.iconphoto(True, self.ico)
        self.window.title("V Package Explorer | ..a project by Valky")
        self.window.minsize(self.minimum_width, self.minimum_height)

        # Create the menu, explorer, preview and info frame
        self.set_explorer_frame()
        self.set_preview_frame()
        self.set_info_frame()
        self.set_menu_frame()

        # Bind window resize event to update frame widths
        self.window.bind("<Configure>", self.update_frame_widths)

        ws = self.window.winfo_screenwidth()
        hs = self.window.winfo_screenheight()
        x = (ws / 2) - (self.minimum_width / 2)
        y = (hs / 2) - (self.minimum_height / 2)
        self.window.geometry('%dx%d+%d+%d' % (self.minimum_width, self.minimum_height, x, y))

    def build_popup_window(self, title, text, method, uinput=False, udown: list = False):
        self.logger.info(f"build popup window {title}")
        self.popup_window = tk.Toplevel()
        self.popup_window.title(title)
        # icon_data = base64.b64decode(EMBEDDED_ICON)
        # icon_image = Image.open(io.BytesIO(icon_data))
        # icon_image = icon_image.resize((32, 32))
        # self.ico = ImageTk.PhotoImage(icon_image)
        self.popup_window.iconphoto(True, self.ico)

        label = tk.Label(self.popup_window, text=text, justify="left")
        label.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

        if uinput:
            entry = tk.Entry(self.popup_window)
            entry.grid(row=1, column=0, columnspan=4, padx=10, pady=5)
        if udown:
            ddown_var = tk.StringVar()
            ddown_box = ttk.Combobox(self.popup_window, textvariable=ddown_var)
            ddown_box['values'] = udown
            ddown_box.current(0)
            ddown_box.grid(row=1, column=0, columnspan=4, padx=10, pady=10)

        command = (lambda: method(entry.get(), ddown_var.get())) if uinput and udown else (
            lambda: method(entry.get())) if uinput else (lambda: method(ddown_var.get())) if udown else method
        ok_button = tk.Button(self.popup_window, text="OK", command=command, width=10)
        ok_button.grid(row=2 if uinput or udown else 1, column=1, padx=5, pady=5, sticky="e")

        cancel_button = tk.Button(self.popup_window, text="Cancel", command=self.popup_window.destroy, width=10)
        cancel_button.grid(row=2 if uinput or udown else 1, column=2, padx=5, pady=5, sticky="w")

        self.popup_window.resizable(False, False)
        ws = self.popup_window.winfo_screenwidth()
        hs = self.popup_window.winfo_screenheight()
        w = 330
        h = 135
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)
        self.popup_window.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def set_menu_frame(self):
        """Create the menu bar and menus."""
        self.logger.info(f"create menu frame")
        menubar = tk.Menu(self.window)
        self.window.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open...", command=self.open_package)
        file_menu.add_separator()
        file_menu.add_command(label="Create...", command=self.ask_for_creation)
        file_menu.add_command(label="Create bulk...", command=self.ask_for_bulk_creation)
        file_menu.add_separator()
        file_menu.add_command(label="Save", command=self.save_package)
        file_menu.add_command(label="Save as...", command=self.save_as_package)
        file_menu.add_separator()
        file_menu.add_command(label="Show in Explorer", command=self.open_file_explorer)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.window.quit)

        vpk_menu = tk.Menu(menubar, tearoff=0)
        vpk_menu.add_command(label="Add Folder", command=self.create_new_folder)
        vpk_menu.add_command(label="Add Media", command=self.import_media)
        vpk_menu.add_separator()
        vpk_menu.add_command(label="Export...", command=self.export_package)

        setting_menu = tk.Menu(menubar, tearoff=0)
        setting_menu.add_command(label="Author", command=self.ask_for_author)
        setting_menu.add_command(label="Compressor", command=self.ask_for_compressor)
        setting_menu.add_command(label="Encryption Key", command=self.ask_for_crypto_key)
        setting_menu.add_command(label="Encryption Mode", command=self.ask_for_encryption)
        setting_menu.add_separator()
        setting_menu.add_command(label="Show Log", command=self.show_log)

        about_menu = tk.Menu(menubar, tearoff=0)
        about_menu.add_command(label="Open Website", command=self.do_open_website)
        about_menu.add_command(label="Check GitHub", command=self.do_open_github)
        about_menu.add_command(label="Join Discord", command=self.do_open_discord)

        menubar.add_cascade(label="File", menu=file_menu)
        menubar.add_cascade(label="Package", menu=vpk_menu)
        menubar.add_cascade(label="Settings", menu=setting_menu)
        menubar.add_cascade(label="About", menu=about_menu)

    def set_explorer_frame(self):
        """Create the file explorer frame."""
        self.logger.info(f"create explorer frame")
        self.explorer_frame = tk.Frame(self.window)
        self.explorer_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

        # Title label for the explorer frame
        explorer_title_label = tk.Label(self.explorer_frame, text="Object Explorer", font=("Arial", 10, "bold"))
        explorer_title_label.pack(pady=3, anchor="w", padx=10)

        self.file_listbox = tk.Listbox(self.explorer_frame, activestyle="none")
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=5, padx=5)
        self.file_listbox.bind("<<ListboxSelect>>", self.handle_selection)
        # scrollbar = tk.Scrollbar(self.file_listbox, orient=tk.VERTICAL, command=self.file_listbox.yview)
        # scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        # self.file_listbox.config(yscrollcommand=scrollbar.set)

    def set_preview_frame(self):
        """Create the preview frame for displaying images."""
        self.logger.info(f"create preview frame")
        self.preview_frame = tk.Frame(self.window)
        self.preview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

        text = "No Open Package"  # TODO
        self.preview_title_label = tk.Label(self.preview_frame, text=f"Package: {text}", font=("Arial", 10, "bold"))
        self.preview_title_label.pack(pady=3, anchor="w", padx=10)

        # Separator line
        preview_separator = ttk.Separator(self.preview_frame, orient="horizontal")
        preview_separator.pack(fill="x", padx=0, pady=5)

        self.image_label = tk.Label(self.preview_frame)
        self.image_label.pack(padx=50, pady=50)
        self.image_label.config(text="Preview Content", image="")
        self.image_label.xw = 128
        self.image_label.yh = 15

    def set_info_frame(self):
        """Create the info frame for displaying file information."""
        self.logger.info(f"create info frame")
        self.info_frame = tk.Frame(self.window)
        self.info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

        # Title label for the info frame
        info_space_label = tk.Label(self.info_frame, text="", font=("Arial", 10, "bold"))
        info_space_label.pack(pady=3, anchor="w", padx=10)
        # Separator line
        info_separator = ttk.Separator(self.info_frame, orient="horizontal")
        info_separator.pack(fill="x", padx=0, pady=5)
        # Title label for the info frame
        info_title_label = tk.Label(self.info_frame, text="Properties:", font=("Arial", 9))
        info_title_label.pack(pady=0, anchor="w", padx=5)

        self.file_infobox = tk.Listbox(self.info_frame, activestyle="none")
        self.file_infobox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=5, padx=5)
        # scrollbar = tk.Scrollbar(self.info_frame, orient=tk.VERTICAL, command=self.file_infobox.yview)
        # scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        # self.file_infobox.config(yscrollcommand=scrollbar.set)

    def update_frame_widths(self, event):
        """Update the widths of the frames based on window resize event."""
        window_width = self.window.winfo_width()
        window_height = self.window.winfo_height()

        self.last_width = window_width
        self.last_height = window_height

        explorer_width = 250
        view_width = int(window_width - explorer_width)
        preview_width = int(view_width * 0.75)
        info_width = int(view_width * 0.25)

        self.explorer_frame.configure(width=explorer_width)
        self.preview_frame.configure(width=preview_width)
        self.info_frame.configure(width=info_width)

        # Center the content within the preview frame
        content_width = self.image_label.xw
        content_height = self.image_label.yh
        x_offset = (preview_width - content_width) // 2
        y_offset = (self.preview_frame.winfo_height() - content_height) // 2

        self.image_label.place(x=x_offset, y=y_offset)

    def clear_data(self):
        """Clear the data in the file explorer, preview and its info."""
        self.file_listbox.delete(0, tk.END)
        self.file_infobox.delete(0, tk.END)
        self.folder_tree = []
        self.expanded_nodes = set()
        self.ap.byte_dict = None
        self.image_label.config(text="Preview Content", image="")
        self.image_label.xw = 128
        self.image_label.yh = 15

    def set_preview_title(self, title: str = None):
        if self.preview_title_label is not None:
            text = "No Open Package" if title is None else title
            self.preview_title_label.config(text=f"Package: {text}")
            self.window.title(f"V Package Explorer | {text} | ..a project by Valky")

    def open_bulkfile(self):
        self.popup_window.destroy()
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        with open(file_path, "r") as file:
            paths = [line.rstrip('\n') for line in file]

        self.logger.info(f"open bulkfile {file_path}")
        for path in paths:
            self.ap.package = f"{path}.vpk"
            self.ap.directory = path
            self.ap.create_vpk()

        self.clear_data()
        self.ap.load()
        self.set_preview_title()
        self.create_folder_tree()
        self.populate_file_listbox()

    def open_file_explorer(self, targeted=False):
        """Open Windows File Explorer with the location of the VPK file."""
        self.logger.info(f"open file explorer {targeted}")
        vpk_folder: str = None
        if targeted:
            vpk_folder = targeted
        elif self.ap.package:
            vpk_folder = os.path.dirname(self.ap.package)

        if vpk_folder is None:
            logging.error("An error occurred during process: Cannot open file location.")
            messagebox.showerror("Windows Error", f"An error occurred during process:\nCannot open file location.")
            return

        vpk_folder = vpk_folder.replace("/", "\\")
        subprocess.Popen(f'explorer "{vpk_folder}"', creationflags=CREATE_NO_WINDOW)

    def open_package(self):
        """Open a package file and load the data."""
        filetypes = [("V Package Files", "*.vpk")]
        file_path = filedialog.askopenfilename(filetypes=filetypes)
        self.logger.info(f"open package {file_path}")
        if file_path:
            self.clear_data()
            # self.ap.package = file_path
            self.byte_dict = self.ap.read(file_path)
            vpk_title = os.path.basename(file_path)
            self.set_preview_title(vpk_title)
            self.create_folder_tree(vpk_title)
            self.populate_file_listbox()

    def export_package(self):
        """Export all data from the current open VPK package."""
        if not self.ap.byte_dict:
            logging.error("No package data found.")
            messagebox.showerror("Export Error", "No package data found.")
            return

        export_path = filedialog.askdirectory(title="Select Export Folder")
        if not export_path:
            return

        self.logger.info(f"export package {export_path}")
        try:
            for folder, file_dict in self.ap.byte_dict.items():
                folder_path = os.path.join(export_path, folder)
                os.makedirs(folder_path, exist_ok=True)

                for filename, data in file_dict.items():
                    file_path = os.path.join(folder_path, filename)
                    with open(file_path, "wb") as file:
                        file.write(data)

            messagebox.showinfo("Export Successful", "Package data exported successfully.")
            self.open_file_explorer(export_path)

        except Exception as e:
            logging.error(f"An error occurred during export: {str(e)}")
            messagebox.showerror("Export Error", f"An error occurred during export: {str(e)}")

    def create_package(self):
        """Build a new package file from a directory."""
        self.popup_window.destroy()
        folder_path = filedialog.askdirectory(title="Select Directory to Pack")
        self.logger.info(f"create package {folder_path}")
        if folder_path:
            self.clear_data()
            self.ap.package = f"{folder_path}.vpk"
            self.ap.directory = folder_path
            self.ap.create_vpk()
            self.set_preview_title()
            self.create_folder_tree()
            self.populate_file_listbox()

    def save_package(self):
        if self.ap.byte_dict:
            if self.ap.package:
                self.logger.info(f"save package {self.ap.package}")
                self.ap.save()
                messagebox.showinfo("Package Saved", "The package has been saved successfully.")
                self.clear_data()
                self.ap.load()
                self.set_preview_title()
                self.create_folder_tree()
                self.populate_file_listbox()
        else:
            logging.error(f"There is no package data to save.")
            messagebox.showerror("Save Package Error", "There is no package data to save.")

    def save_as_package(self):
        if self.ap.byte_dict:
            filetypes = [("V Package Files", "*.vpk")]
            file_path = filedialog.asksaveasfilename(filetypes=filetypes)
            if file_path:
                self.ap.package = file_path
                self.logger.info(f"save package as {self.ap.package}")
                self.ap.save()
                messagebox.showinfo("Package Saved", "The package has been saved successfully.")
                self.clear_data()
                self.ap.load()
                self.set_preview_title()
                self.create_folder_tree()
                self.populate_file_listbox()
        else:
            logging.error(f"There is no package data to save.")
            messagebox.showerror("Save Package Error", "There is no package data to save.")

    def show_image(self, image_data):
        """Display the image in the preview frame."""
        image_stream = io.BytesIO(image_data)
        image = Image.open(image_stream)
        width, height = image.size
        image.thumbnail((width, height))  # Adjust the size as needed
        image_tk = ImageTk.PhotoImage(image)
        self.image_label.configure(image=image_tk)
        self.image_label.image = image_tk
        self.image_label.xw = width
        self.image_label.yh = height

    def handle_selection(self, event):
        """Handle the selection of an item in the file explorer."""
        selection = self.file_listbox.curselection()
        if selection:
            selection = self.file_listbox.get(self.file_listbox.curselection())
            for sign in SIGNS:
                selection = selection.replace(sign, "")
            item = self.get_selected_item(selection)
            if item:
                if item[1]:
                    self.toggle_folder(item)
                # elif ".vpk" not in item[0]:
                else:
                    try:
                        kind = self.display_file_info(item)
                    except TypeError:
                        kind = None
                    if kind == "image":
                        self.show_image(item[2])
                    else:
                        self.image_label.config(text="Preview Content", image="")
                        self.image_label.xw = 128
                        self.image_label.yh = 15

    def display_file_info(self, item):
        """Display information about the selected file."""
        kind = get_file_type(item[2])
        kind, app_type = kind.split("/")
        match kind:
            case "audio":
                self.get_music_info(item)

            case "image":
                self.get_image_info(item)

            case "application":
                match app_type:
                    case "font" | "font-sfnt":
                        self.get_application_info(item)
                    case "octet-stream":
                        self.get_application_info(item)
                    case _:
                        logging.error(f"Unknown mime type {kind}/{app_type}")
                        pass

            case "text":
                match app_type:
                    case "plain":
                        self.get_application_info(item)
                    case "html":
                        self.get_application_info(item)
                    case _:
                        logging.error(f"Unknown mime type {kind}/{app_type}")
                        pass
            case _:
                logging.error(f"Unknown mime type {kind}/{app_type}")
                pass

        return kind

    def get_music_info(self, item):
        """Display information about the selected audio."""
        try:
            filename = item[0]
            audio_data = item[2]
            audio_size = len(audio_data)
            audio_size_formatted = ValkyrieTools.formatSize(audio_size)
            kind = get_file_type(item[2], True).split("contains:")
            kind = (kind[0] if len(kind) == 1 else kind[1]).split(", ")

            app_type = kind[0]
            if kind[1] == "layer III":
                app_format = "MP3"
            elif kind[1] == "WAVE audio":
                app_format = "WAV"
            else:
                app_format = kind[1]
            app_version = kind[2]
            app_bitrate = kind[3]
            if app_format == "WAV":
                app_hertz = kind[4].split(" ", 1)[1]
                app_balance = kind[4].split(" ", 1)[0]
            else:
                app_hertz = kind[4]
                app_balance = kind[5]
            app_mime = get_file_type(item[2])

            self.file_infobox.delete(0, tk.END)
            self.file_infobox.insert(tk.END, f"File Name: {filename}")
            self.file_infobox.insert(tk.END, f"File Size: {audio_size_formatted}")
            self.file_infobox.insert(tk.END, f"File Type: {app_type}")
            self.file_infobox.insert(tk.END, f"File Format: {app_format}")
            self.file_infobox.insert(tk.END, f"Music Format: {app_version}")
            self.file_infobox.insert(tk.END, f"Music Bitrate: {app_bitrate}")
            self.file_infobox.insert(tk.END, f"Music Hertz: {app_hertz}")
            self.file_infobox.insert(tk.END, f"Music Type: {app_balance}")
            self.file_infobox.insert(tk.END, f"MIME: {app_mime}")
            return True

        except Exception as ex:
            logging.error(f"Error getting music info {ex}")
            return False

    def get_application_info(self, item):
        """Display information about the selected app-data."""
        try:
            filename = item[0]
            app_format = filename.split(".")[-1].upper()
            app_data = item[2]
            app_size = len(app_data)
            app_size_formatted = ValkyrieTools.formatSize(app_size)
            app_mime = get_file_type(item[2])
            kind = get_file_type(item[2], True).split(", ")
            app_encode, app_terminator = None, None

            if "TrueType Font" in kind[0]:
                pass
            elif "text/plain" == app_mime:
                if len(kind) == 2:
                    app_encode = kind[0].split(" ")[0]
                    app_terminator = kind[1].split(" ")[1]
                elif len(kind) == 3:
                    app_encode = kind[0].split(" ")[0]
                    app_terminator = kind[2].split(" ")[1]
            elif "text/html" == app_mime:
                app_encode = kind[1].split(" ")[0]
                app_terminator = kind[2].split(" ")[1]
            elif "application/octet-stream" == app_mime:
                info = self.ap.info(item[2])
                name = info[0].replace("\00", "")
                fileinfo = info[1]
                filesize = info[2]
                author = info[3].replace("\00", "")
                copyright = info[4]
                creation_date = time.strftime("%d %b %Y", time.gmtime(info[5]))
                creation_time = time.strftime("%H:%M:%S", time.gmtime(info[5]))
                encryption = info[6]
                key_length = info[7]
                version = info[8]
                compression = info[9].replace("\00", "").upper()
            else:
                app_format = kind

            app_type = kind[0]
            app_tables, app_names, app_author = None, None, None
            if app_format == "TTF":
                app_tables = kind[1].split(" ")[0]
                app_names = kind[3].split(" ")[0]
                app_author = kind[5].split("\\322")[1]

            self.file_infobox.delete(0, tk.END)
            self.file_infobox.insert(tk.END, f"File Name: {filename}")
            self.file_infobox.insert(tk.END, f"File Size: {app_size_formatted}")
            if app_format == "VPK":
                self.file_infobox.insert(tk.END, f"File Type: {fileinfo}")
            else:
                self.file_infobox.insert(tk.END, f"File Type: {app_type}")
            self.file_infobox.insert(tk.END, f"File Format: {app_format}")
            if app_format == "TTF":
                self.file_infobox.insert(tk.END, f"Font Tables: {app_tables}")
                self.file_infobox.insert(tk.END, f"Font Characters: {app_names}")
                self.file_infobox.insert(tk.END, f"Font Author: {app_author}")
            elif "text/plain" == app_mime or "text/html" == app_mime:
                self.file_infobox.insert(tk.END, f"Encoding: {app_encode}")
                self.file_infobox.insert(tk.END, f"Line Terminator: {app_terminator}")
            elif app_format == "VPK":
                self.file_infobox.insert(tk.END, f"Package Name: {name}")
                self.file_infobox.insert(tk.END, f"Package Version: v{version}")
                self.file_infobox.insert(tk.END, f"Package Author: {author}")
                self.file_infobox.insert(tk.END, f"Package Copyright: {copyright}")
                self.file_infobox.insert(tk.END, f"Creation Date: {creation_date}")
                self.file_infobox.insert(tk.END, f"Creation Time: {creation_time}")
                self.file_infobox.insert(tk.END, f"Encryption Type: {encryption}")
                self.file_infobox.insert(tk.END, f"Encryption Length: {key_length} Bytes")
                self.file_infobox.insert(tk.END, f"Compression Type: {compression}")
            self.file_infobox.insert(tk.END, f"MIME: {app_mime}")
            return True

        except Exception as ex:
            logging.error(f"Error getting application info {ex}")
            return False

    def get_image_info(self, item):
        """Display information about the selected image."""
        try:
            filename = item[0]
            image_data = item[2]
            image_size = len(image_data)
            image_size_formatted = ValkyrieTools.formatSize(image_size)
            image = Image.open(io.BytesIO(image_data))
            image_format = image.format
            width, height = image.size

            kind = get_file_type(item[2], True).split(", ")
            app_icons, app_pixel_bit = None, None
            if image_format == "ICO":
                app_type = kind[0].split(" - ")[0]
                app_icons = kind[0].split(" - ")[1].split(" ")[0]
                app_color_data = kind[3].split("/") if "/" in kind[3] else kind[3].split(" ")
                app_color_bit = app_color_data[0]
                app_color_map = "RGBA" if app_color_data[1] == "colormap" else app_color_data[1].replace("color ", "")
                app_interlace = "False" if "non" in kind[4] else "True"
                app_pixel_bit = kind[5]
            else:
                app_type = kind[0]
                app_color_data = kind[2].split("/") if "/" in kind[2] else kind[2].split(" ")
                app_color_bit = app_color_data[0]
                app_color_map = "RGBA" if app_color_data[1] == "colormap" else app_color_data[1].replace("color ", "")
                app_interlace = "False" if "non" in kind[3] else "True"
            app_mime = get_file_type(item[2])

            self.file_infobox.delete(0, tk.END)
            self.file_infobox.insert(tk.END, f"File Name: {filename}")
            self.file_infobox.insert(tk.END, f"File Size: {image_size_formatted}")
            self.file_infobox.insert(tk.END, f"File Type: {app_type}")
            self.file_infobox.insert(tk.END, f"File Format: {image_format.upper()}")
            self.file_infobox.insert(tk.END, f"Image Width: {width}px")
            self.file_infobox.insert(tk.END, f"Image Height: {height}px")
            self.file_infobox.insert(tk.END, f"Image Bitmap: {app_color_bit}")
            self.file_infobox.insert(tk.END, f"Image Colormap: {app_color_map}")
            if image_format == "ICO":
                self.file_infobox.insert(tk.END, f"Icon Amount: {app_icons}")
                self.file_infobox.insert(tk.END, f"Icon Size: {app_pixel_bit}")
            self.file_infobox.insert(tk.END, f"Interlaced: {app_interlace}")
            self.file_infobox.insert(tk.END, f"MIME: {app_mime}")
            return True

        except Exception as ex:
            logging.error(f"Error getting image info {ex}")
            return False

    def toggle_folder(self, folder):
        """Toggle the display of the child items in a folder."""
        item = folder[0]
        children = folder[1]
        if f"      📂   {item}" in self.expanded_nodes:
            self.expanded_nodes.remove(f"      📂   {item}")
            self.remove_children_from_listbox(f"      📂   {item}", children)
        else:
            self.expanded_nodes.add(f"      📂   {item}")
            self.insert_children_to_listbox(f"      📂   {item}", children)

    def insert_children_to_listbox(self, parent, children):
        """Insert the children items to the file explorer listbox."""
        index = self.file_listbox.get(0, tk.END).index(parent)
        for child in children:
            kind = get_file_type(child[2])
            kind, app_type = kind.split("/")

            match kind:
                case "audio":
                    icon = "♬"

                case "image":
                    icon = "🖼"

                case "application":
                    match app_type:
                        case "font" | "font-sfnt":
                            icon = "⍲"
                        case "octet-stream":
                            icon = "📦"
                        case _:
                            logging.error(kind, app_type)
                            icon = "？"

                case "text":
                    match app_type:
                        case "plain":
                            icon = "📄"
                        case "html":
                            icon = "≯"
                        case _:
                            logging.error(kind, app_type)
                            icon = "？"
                case _:
                    logging.error(kind, app_type)
                    icon = "？"
            self.file_listbox.insert(index + 1, f"          {icon}   {child[0]}")
            index += 1

    def remove_children_from_listbox(self, parent, children):
        """Remove the children items from the file explorer listbox."""
        index = self.file_listbox.get(0, tk.END).index(parent)
        for _ in children:
            self.file_listbox.delete(index + 1)

    def populate_file_listbox(self):
        """Populate the file explorer listbox with folder and file names."""
        i = 0
        for item in self.folder_tree:
            if i < 1:
                self.file_listbox.insert(tk.END, f"  📦   {item[0]}")
            else:
                self.file_listbox.insert(tk.END, f"      📂   {item[0]}")
            i += 1

    def create_folder_tree(self, title: str = "Unknown"):
        """Create the folder tree structure from the loaded data."""
        self.folder_tree = [[title, [], None]]
        for folder, file_dict in self.byte_dict.items():
            folder_parts = folder.split(os.sep)
            curr_level = self.folder_tree
            for i, part in enumerate(folder_parts):
                child = next((x for x in curr_level if x[0] == part), None)
                if child is None:
                    child = [part, [], None]
                    curr_level.append(child)
                if i == len(folder_parts) - 1:
                    for filename, image_data in file_dict.items():
                        child[1].append([filename, None, image_data])
                curr_level = child[1]

    def get_selected_item(self, selection):
        """Get the selected item from the folder tree."""
        for item in self.folder_tree:
            if item[0] == selection:
                return item
            if item[1]:
                child = self.get_selected_child(item[1], selection)
                if child:
                    return child
        return None

    def get_selected_child(self, children, selection):
        """Get the selected child item from the folder tree."""
        for child in children:
            if child[0] == selection:
                return child
            if child[1]:
                nested_child = self.get_selected_child(child[1], selection)
                if nested_child:
                    return nested_child
        return None

    def add_media_to_folder(self, folder_name, file_path, media_info):
        for item in self.folder_tree:
            if item[0] == folder_name:
                # file_extension = os.path.splitext(os.path.basename(file_path))[1].lower()
                media_name = os.path.basename(file_path)
                item[1].append([media_name, None, media_info])
                if self.ap.byte_dict is None:
                    self.ap.byte_dict = {folder_name: {}}
                elif folder_name not in self.ap.byte_dict:
                    self.ap.byte_dict[folder_name] = {}
                self.ap.byte_dict[folder_name][media_name] = media_info
                self.file_listbox.insert(tk.END, f"          ⇢   {media_name}")
                break

    def import_media(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.logger.info(f"import media {file_path}")
            folder_name = simpledialog.askstring("Choose Folder", "Enter the folder name to import the media:")
            if folder_name:
                self.logger.info(f"import media {folder_name}")
                with open(file_path, "rb") as file:
                    byte_data = file.read()
                if byte_data:
                    self.add_media_to_folder(folder_name, file_path, byte_data)

    def create_new_folder(self):
        folder_name = simpledialog.askstring("New Folder", "Enter the name for the new folder:")
        if folder_name:
            self.logger.info(f"create folder {folder_name}")
            if len(self.folder_tree) < 1:
                self.file_listbox.insert(tk.END, f"  📦   New...")
            new_folder = [folder_name, [], None]
            self.folder_tree.append(new_folder)
            self.file_listbox.insert(tk.END, f"      📂   {folder_name}")

    def ask_for_crypto_key(self):
        self.logger.info(f"Argon Crypto")
        argon_key = simpledialog.askstring("Argon Crypto | Step 1",
                                           f"Argon Key: {self.argon_key}\nArgon IV: {self.argon_iv}\n\nEnter the new Argon Key:")
        if argon_key is None:
            self.logger.info(f"Argon Crypto | {argon_key}")
            messagebox.showinfo("Argon Crypto | Cancel",
                                "Operation canceled.\nThe crypto Key and IV has not been changed.")
            return
        elif argon_key == "" or len(argon_key) < 64:
            logging.error(f"Argon Crypto | {argon_key}")
            messagebox.showerror("Argon Crypto | Error",
                                 "The crypto Key must not be empty and set to a minimum length of 64!")
            return

        argon_iv = simpledialog.askstring("Argon Crypto | Step 2",
                                          f"Argon Key: {self.argon_key}\nArgon IV: {self.argon_iv}\n\nEnter the new Argon IV:")
        if argon_iv is None:
            self.logger.info(f"Argon Crypto | {argon_iv}")
            messagebox.showinfo("Argon Crypto | Cancel",
                                "Operation canceled.\nThe crypto Key and IV has not been changed.")
            return
        elif argon_iv == "" or len(argon_iv) < 24:
            logging.error(f"Argon Crypto | {argon_iv}")
            messagebox.showerror("Argon Crypto | Error",
                                 "The crypto IV must not be empty and set to a minimum length of 24!")
            return

        argon_prompt = simpledialog.askstring("Argon Crypto | Step 3",
                                              f"Old Argon Key: {self.argon_key}\nOld Argon IV: {self.argon_iv}\n\nNew Argon Key: {argon_key}\nNew Argon IV: {argon_iv}\n\n\nAre you sure to overwrite the crypto Key and IV?\n\nWrite 'ArgonCrypto' to confirm:")
        if argon_prompt is None:
            self.logger.info(f"Argon Crypto | {argon_prompt}")
            messagebox.showinfo("Argon Crypto | Cancel",
                                "Operation canceled.\nThe crypto Key and IV has not been changed.")
            return
        elif argon_prompt == 'ArgonCrypto':
            self.argon_key = argon_key
            self.argon_iv = argon_iv
            self.config['ArgonCrypto']['key'] = argon_key
            self.config['ArgonCrypto']['iv'] = argon_iv
            self._cfg.save(self.config, r".\settings.vcf")
            # argonize = (self.argon_key, self.argon_iv)
            # self.ap = Packager(argonize, self.config)
            self.logger.info(f"Argon Crypto | Success")
            messagebox.showinfo("Argon Crypto | Success", "The crypto Key and IV has been changed successfully.")
        else:
            logging.error(f"Argon Crypto | {argon_prompt}")
            messagebox.showerror("Argon Crypto | Error", "Wrong prompt! The crypto Key and IV has not been changed!")

    def ask_for_bulk_creation(self):
        title = "Bulk VPK Creation | Choose File"
        text = "Choose a text file containing paths to directories on your\nwindows operation system. "
        text += "Each directory will be packed,\nencrypted and saved as a *.vpk package.\n\n"
        text += "Note: Each path must be on a new line."
        self.build_popup_window(title, text, self.open_bulkfile)

    def ask_for_creation(self):
        title = "VPK Creation | Choose Directory"
        text = "Choose a directory on your windows operation system.\n"
        text += "The package explorer gathers all files and packs them.\n\n"
        text += "Everything will be encrypted and saved as a *.vpk package.\n"
        self.build_popup_window(title, text, self.create_package)

    def ask_for_author(self):
        author = simpledialog.askstring("VPK Settings | Author",
                                        f"Author: {self.config['Settings']['author']}\n{'  ' * 50}\nEnter the new author name:")
        if author is None:
            self.logger.info(f"change author {author}")
            messagebox.showinfo("VPK Settings | Cancel", "Operation canceled.\nThe author name has not been changed.")
            return
        elif author == "" or len(author) > 16:
            logging.error(f"change author {author}")
            messagebox.showerror("VPK Settings | Error", "The author name must not be empty and not greater than 16!")
            return

        self.config['Settings']['author'] = author
        self._cfg.save(self.config, r".\settings.vcf")
        # argonize = (self.argon_key, self.argon_iv)
        # self.ap = Packager(argonize, self.config)
        self.logger.info(f"change author {author}")
        messagebox.showinfo("VPK Settings | Success", "The author name has been changed successfully.")

    def ask_for_encryption(self):
        title = "VPK Settings | Encryption"
        text = "Choose an encryption mode for VPK packages.\n"
        text += "They are offering a different balance of speed and security."
        dropdown = ['AES-GCM (Strong)', 'AES-CTR (Fast)', 'AES-CBC (Basic)']
        self.build_popup_window(title, text, self.set_encryption, udown=dropdown)

    def set_encryption(self, encryption):
        self.popup_window.destroy()
        encryption = encryption.split(" ")[0].lower()
        if encryption is None:
            self.logger.info(f"change encryption {encryption}")
            messagebox.showinfo("VPK Settings | Cancel",
                                "Operation canceled.\nThe encryption method has not been changed.")
            return
        elif encryption == "" or encryption not in ['aes-gcm', 'aes-ctr', 'aes-cbc']:
            logging.error(f"change encryption {encryption}")
            messagebox.showerror("VPK Settings | Error", "Invalid encryption method selected.")
            return

        self.config['ArgonCrypto']['mode'] = encryption
        self._cfg.save(self.config, r".\settings.vcf")
        # argonize = (self.argon_key, self.argon_iv)
        # self.ap = Packager(argonize, self.config)
        self.logger.info(f"change encryption {encryption}")
        messagebox.showinfo("VPK Settings | Success", "The encryption method has been changed successfully.")

    def ask_for_compressor(self):
        title = "VPK Settings | Compressor"
        text = "Choose a compressor do compress and deflate packages.\n"
        text += "The higher compression ration, the slower the time."
        dropdown = ['Gzip (Balanced)', 'ZSTD (Balanced)', 'Bzip2 (Slow)', 'LZMA (Slow)', 'LZ4 (Fast)']
        self.build_popup_window(title, text, self.set_compressor, udown=dropdown)

    def set_compressor(self, compressor):
        self.popup_window.destroy()
        compressor = compressor.split(" ")[0].lower()
        if compressor is None:
            self.logger.info(f"change encryption {compressor}")
            messagebox.showinfo("VPK Settings | Cancel",
                                "Operation canceled.\nThe compression method has not been changed.")
            return
        elif compressor == "" or compressor not in ['gzip', 'zstd', 'bzip2', 'lzma', 'lz4']:
            logging.error(f"change encryption {compressor}")
            messagebox.showerror("VPK Settings | Error", "The author name must not be empty and not greater than 16!")
            return

        self.config['Compressor']['mode'] = compressor
        self._cfg.save(self.config, r".\settings.vcf")
        # argonize = (self.argon_key, self.argon_iv)
        # self.ap = Packager(argonize, self.config)
        self.logger.info(f"change encryption {compressor}")
        messagebox.showinfo("VPK Settings | Success", "The compression method has been changed successfully.")

    def do_open_website(self):
        self.logger.info(f"open website")
        webbrowser.open("https://valky.dev")

    def do_open_github(self):
        self.logger.info(f"open github")
        webbrowser.open("https://github.com/ValkyFischer")

    def do_open_discord(self):
        self.logger.info(f"open discord")
        webbrowser.open("https://discord.gg/vky")


if __name__ == "__main__":
    _debug = False
    
    start_arg = ValkyrieOptions([('config_file', 'str', 'Configuration File Path and filename', 'settings.vcf')])
    parsed_options = start_arg.parse()
    
    _config_file = parsed_options['config_file']

    valky = [
        r"=======================================================================================================",
        r"                                                                                                       ",
        r"          (`-.     ('-.              .-. .-')                      _ .-') _     ('-.        (`-.       ",
        r"        _(OO  )_  ( OO ).-.          \  ( OO )                    ( (  OO) )  _(  OO)     _(OO  )_     ",
        r"    ,--(_/   ,. \ / . --. / ,--.     ,--. ,--.   ,--.   ,--.       \     .'_ (,------.,--(_/   ,. \    ",
        r"    \   \   /(__/ | \-.  \  |  |.-') |  .'   /    \  `.'  /        ,`'--..._) |  .---'\   \   /(__/    ",
        r"     \   \ /   /.-'-'  |  | |  | OO )|      /,  .-')     /         |  |  \  ' |  |     \   \ /   /     ",
        r"      \   '   /, \| |_.'  | |  |`-' ||     ' _)(OO  \   /          |  |   ' |(|  '--.   \   '   /,     ",
        r"       \     /__) |  .-.  |(|  '---.'|  .   \   |   /  /\_         |  |   / : |  .--'    \     /__)    ",
        r"        \   /     |  | |  | |      | |  |\   \  `-./  /.__)        |  '--'  / |  `---.    \   /        ",
        r"         `-'      `--' `--' `------' `--' '--'    `--'             `-------'  `------'     `-'         ",
        r"                                                                                                       ",
        r"======================================================================================================="
    ]

    try:
        APE = PackageExplorer(_config_file, _debug)
        APE.window.mainloop()

    except Exception as exc:
        logging.error(exc)
