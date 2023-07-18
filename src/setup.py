from tkinter import simpledialog, messagebox


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
