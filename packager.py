import os
import pickle
import struct
import time
from tkinter import messagebox

import argoncrypto as ac
from utils import get_file_data

HEADER_FORMAT = '16s22sI16s17sI7sII'  # Example format: 16 bytes for name, 32 bytes for description, 4 bytes for size


def get_vpk_info(data, bin=False):
    if not bin:
        # read the header from a file in binary mode
        with open(data, 'rb') as file:
            header_data = file.read(struct.calcsize(HEADER_FORMAT))
            filename, fileinfo, filesize, author, copyright, timestamp, encryption, key_length, version = struct.unpack(HEADER_FORMAT, header_data)
    
    else:
        # read the header from binary data
        header_data = data[:struct.calcsize(HEADER_FORMAT)]
        filename, fileinfo, filesize, author, copyright, timestamp, encryption, key_length, version = struct.unpack(HEADER_FORMAT, header_data)
    
    return filename.decode(), fileinfo.decode(), filesize, author.decode(), copyright.decode(), timestamp, encryption.decode(), key_length, version

class Packager:
    def __init__(self, argonize: tuple, config: dict):
        self.mode = 0
        self.timestamp = None
        self.byte_dict: dict = None
        self.directory: str = None
        self.package: str = None
        self.config: dict = config
        self.argonize = ac.generate_argon_key(argonize[0], argonize[1])
        
    def read_files(self) -> int:
        # Iterate through each file and sub-folder in the directory
        found_files = 0
        for root, _, files in os.walk(self.directory):
            for filename in files:
                # file_extension = os.path.splitext(filename)[1].lower()
                file_path = os.path.join(root, filename)
                
                folder_name = os.path.basename(root)
                file_dict = self.byte_dict.setdefault(folder_name, {})
                
                file_dict[filename] = get_file_data(file_path)
                found_files += 1
                
        return found_files
    
    def save(self):
        pickled_data = pickle.dumps(self.byte_dict)
        encrypted_data = ac.encrypt_data(self.argonize, pickled_data, mode = self.mode)
        encrypted_data_bytes = pickle.dumps(encrypted_data)
        
        if "/" in self.package:
            filename = self.package.split("/")[-1].replace(".vpk", "").encode('utf-8')
        elif "\\" in self.package:
            filename = self.package.split("\\")[-1].replace(".vpk", "").encode('utf-8')
        else:
            filename = self.package.replace(".vpk", "").encode('utf-8')
        fileinfo = "Encrypted data package".encode('utf-8')
        filesize = len(encrypted_data_bytes)
        author    = self.config['Settings']['author'].encode('utf-8')
        copyright = "VALKYTEQ ⓒ 2023".encode('utf-8')
        timestamp = int(time.time())
        encryption = ac.MODES[self.mode].encode('utf-8')
        key_length = len(self.argonize)
        version = 1
        
        header_data = struct.pack(HEADER_FORMAT, filename, fileinfo, filesize, author, copyright, timestamp, encryption, key_length, version)
        v_package = header_data + encrypted_data_bytes
        
        with open(self.package, 'wb') as file:
            file.write(v_package)
    
    def load(self):
        with open(self.package, 'rb') as file:
            header_data = file.read(struct.calcsize(HEADER_FORMAT))
            info = struct.unpack(HEADER_FORMAT, header_data)
            encrypted_data = file.read(info[2])
        
        try:
            decrypted_data_bytes = pickle.loads(encrypted_data)
            decrypted_data = ac.decrypt_data(self.argonize, decrypted_data_bytes, mode = 0)
            self.byte_dict = pickle.loads(decrypted_data)
            
        except ValueError:
            messagebox.showerror("Argon Crypto | Error", "The crypto Key and IV do not match for this package!")
    
    def create_vpk(self):
        if self.directory != str and self.directory != '' and self.directory is not None:
            self.timestamp = time.time()
            
            self.byte_dict: dict = {}
            self.package = f"{self.directory}.vpk"
            
            i = self.read_files()
            file_amount = ('{: >8}'.format(str(i)))
            
            package = self.directory.split('\\')[-1]
            package_name = ('{: >20}'.format(str(package)))

            self.save()
            
            elapsed = round(time.time()-self.timestamp, 2)
            elapsed_time = ('{: >10}'.format(str(elapsed)))
            print(f"Finished | {package_name}.vpk | {file_amount} Files | {elapsed_time} sec")
        else:
            raise Exception("Error in directory path!")


if __name__ == '__main__':
    dirs = [
        # audio
        r'E:\GitHub\aria\Game\audio\effects',
        r'E:\GitHub\aria\Game\audio\levels',
        r'E:\GitHub\aria\Game\audio\overworld',
        # graphics | actor
        r'E:\GitHub\aria\Game\graphics\actor\feathers',
        r'E:\GitHub\aria\Game\graphics\actor\portal',
        r'E:\GitHub\aria\Game\graphics\actor\powerups',
        # graphics | character
        r'E:\GitHub\aria\Game\graphics\character\Angelica',
        r'E:\GitHub\aria\Game\graphics\character\Nathalie',
        r'E:\GitHub\aria\Game\graphics\character\Sigrun',
        r'E:\GitHub\aria\Game\graphics\character\Unknown',
        r'E:\GitHub\aria\Game\graphics\character\utils',
        # graphics | enemy
        r'E:\GitHub\aria\Game\graphics\enemy\barbarian',
        r"E:\GitHub\aria\Game\graphics\enemy\bat_dark",
        r"E:\GitHub\aria\Game\graphics\enemy\bat_gold",
        r"E:\GitHub\aria\Game\graphics\enemy\bee_blue",
        r"E:\GitHub\aria\Game\graphics\enemy\bee_gold",
        r"E:\GitHub\aria\Game\graphics\enemy\boar",
        r"E:\GitHub\aria\Game\graphics\enemy\crow",
        r"E:\GitHub\aria\Game\graphics\enemy\kong",
        r"E:\GitHub\aria\Game\graphics\enemy\pingu_blue",
        r"E:\GitHub\aria\Game\graphics\enemy\pingu_pink",
        r"E:\GitHub\aria\Game\graphics\enemy\shroom",
        r"E:\GitHub\aria\Game\graphics\enemy\skeleton_axe",
        r"E:\GitHub\aria\Game\graphics\enemy\skeleton_spear",
        r"E:\GitHub\aria\Game\graphics\enemy\slime_green",
        r"E:\GitHub\aria\Game\graphics\enemy\slime_pink",
        r"E:\GitHub\aria\Game\graphics\enemy\turtle",
        r"E:\GitHub\aria\Game\graphics\enemy\wolf",
        r"E:\GitHub\aria\Game\graphics\enemy\zombie_f",
        r"E:\GitHub\aria\Game\graphics\enemy\zombie_m",
        # graphics | overworld
        r"E:\GitHub\aria\Game\graphics\overworld\beach",
        r"E:\GitHub\aria\Game\graphics\overworld\desert",
        r"E:\GitHub\aria\Game\graphics\overworld\grave",
        r"E:\GitHub\aria\Game\graphics\overworld\scifi",
        r"E:\GitHub\aria\Game\graphics\overworld\winter",
        # graphics | particles
        r"E:\GitHub\aria\Game\graphics\particles\dust",
        r"E:\GitHub\aria\Game\graphics\particles\explosion",
        # graphics | terrain
        r"E:\GitHub\aria\Game\graphics\terrain\lighting",
        r"E:\GitHub\aria\Game\graphics\terrain\objects",
        r"E:\GitHub\aria\Game\graphics\terrain\palms",
        r"E:\GitHub\aria\Game\graphics\terrain\sky",
        r"E:\GitHub\aria\Game\graphics\terrain\tiles",
        r"E:\GitHub\aria\Game\graphics\terrain\water",
        # graphics | ui
        r'E:\GitHub\aria\Game\graphics\ui',
        # levels
        r"E:\GitHub\aria\Game\levels\castle",
        r"E:\GitHub\aria\Game\levels\world_0",
        r"E:\GitHub\aria\Game\levels\world_1",
        r"E:\GitHub\aria\Game\levels\world_2",
        r"E:\GitHub\aria\Game\levels\world_3",
        # splash
        r'E:\GitHub\aria\Game\splash',
    ]
    from utils import read_config
    config = read_config(r".\settings.argon")
    AP = Packager((config['ArgonCrypto']['key'], config['ArgonCrypto']['iv']), config)
    for d in dirs:
        AP.directory = d
        AP.create_vpk()
    
