import json
import pickle
import subprocess
import sys
import winreg
import magic
import argoncrypto as ac
from setup import PESetup


CREATE_NO_WINDOW = 0x08000000


def get_file_data(path):
    with open(path, 'rb') as file:
        return file.read()


def get_file_type(item_data, no_meme = False):
    """Get info about file data."""
    kind = magic.from_buffer(item_data, mime = False)
    kind_meme = magic.from_buffer(item_data, mime = True)
    return kind_meme if not no_meme else kind


def format_file_size(size):
    """Format the file size in a human-readable format."""
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB']
    index = 0
    while size >= 1024 and index < len(suffixes) - 1:
        size /= 1024
        index += 1
    return f"{size:.2f} {suffixes[index]}"

def read_config(file_path):
    """Read encrypted configuration file and return the parsed data."""
    with open(file_path) as file:
        data = file.read()
    
    if not data:
        raise Exception("Cannot read config!")
    
    crypto_key = str(get_uniqueid())[2:].encode('utf-8')
    encrypted_data = json.loads(data)
    decrypted_data = ac.decrypt_data(crypto_key, encrypted_data)
    config = pickle.loads(decrypted_data)
    
    return config

def save_config(file_path, data):
    """Save the data in an encrypted configuration file."""
    pickled_data = pickle.dumps(data)
    crypto_key = str(get_uniqueid())[2:].encode('utf-8')
    encrypted_data = ac.encrypt_data(crypto_key, pickled_data)
    with open(file_path, "w") as file:
        file.write(json.dumps(encrypted_data))
    
def create_config(path):
    argon_key = False
    while argon_key is False:
        argon_key = PESetup.setup_crypto_key()
    if argon_key is None:
        sys.exit()
    
    argon_iv = False
    while argon_iv is False:
        argon_iv = PESetup.setup_crypto_iv()
    if argon_iv is None:
        sys.exit()
    
    author = False
    while author is False:
        author = PESetup.setup_author()
    if author is None:
        sys.exit()
    
    compressor = False
    while compressor is False:
        compressor = PESetup.setup_compressor()
    if compressor is None:
        sys.exit()
        
    data = {
        "Settings": {"author": author},
        "ArgonCrypto": {"key": argon_key, "iv" : argon_iv},
        "Compressor": {"mode": compressor}
    }
    save_config(path, data)
    return read_config(r".\settings.argon")

def get_osid():
    key = winreg.OpenKey(
        winreg.HKEY_LOCAL_MACHINE,
        "SOFTWARE\\Microsoft\\Cryptography",
        0,
        winreg.KEY_READ | winreg.KEY_WOW64_64KEY
    )

    osid = winreg.QueryValueEx(key, "MachineGuid")
    hexid = osid[0].replace('-', '').upper()
    return int(f"0x{hexid}", 0)

def get_uuid() -> int:
    uuid = subprocess.check_output('wmic csproduct get uuid', creationflags=CREATE_NO_WINDOW)
    hexid = uuid.decode().split('\n')[1].strip().replace('-', '')
    return int(f"0x{hexid}", 0)

def get_cpuid() -> int:
    cpuid = subprocess.check_output('wmic cpu get ProcessorId', creationflags=CREATE_NO_WINDOW)
    hexid = cpuid.decode().split('\n')[1].strip()
    return int(f"0x{hexid}", 0)

def get_hddid() -> int:
    hddid = subprocess.check_output('wmic diskdrive get Name, SerialNumber', creationflags=CREATE_NO_WINDOW)
    serials = hddid.decode().split('\n')[1:]
    for serial in serials:
        if 'DRIVE0' in serial:
            hexid = serial.split('DRIVE0')[-1].strip()
            return int(f"0x{hexid}", 0)

def get_uniqueid() -> hex:
    uuid = get_uuid()
    hddid = get_hddid()
    cpuid = get_cpuid()
    osid = get_osid()

    identifier = uuid + hddid + cpuid + osid

    return hex(identifier)
