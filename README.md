# V Package Explorer

V Package Explorer is a Python application that allows you to explore and manage packages stored in a VPK (Valky's 
Package) format. With the V Package Explorer, you can browse through the contents of VPK packages, create new packages, 
import media files into existing packages, and toggle the display of child items in folders.

*NOTE: This tool is only usable for machines using Microsoft Windows operating systems.*

<br><br>

## Features

- **Package Exploration**: Browse and explore the contents of VPK (Valky's Package) packages.
- **Folder Navigation**: Toggle the display of child items in folders for easy navigation.
- **File and Folder Management**: Create new folders, import media files into existing folders, and remove items from the package.
- **Encryption and Decryption**: V Package Explorer uses AES-GCM (Advanced Encryption Standard-Galois/Counter Mode) with a key derived from Argon2 for encryption and decryption of package contents, providing strong security.
- **Argon2 Key Derivation**: The encryption key for AES-GCM is derived using Argon2, a memory-hard password hashing function, ensuring the security and confidentiality of package contents.
- **Crypto Key and IV Configuration**: Change the cryptographic key and initialization vector (IV) used for encryption and decryption of package contents.
- **VPK Creation**: Create new VPK (Valky's Package) packages from a selected directory or multiple directories listed in a text file.
- **Settings Configuration**: Configure author name and other settings for the VPK (Valky's Package) packages.

<br><br>

## Prerequisites

Before running the V Package Explorer, make sure you have the following Python modules installed:

- Pillow 10.0.0
- argon2-cffi 21.3.0
- argon2-cffi-bindings 21.2.0
- cffi 1.15.1
- pycparser 2.21
- pycryptodomex 3.18.0
- python-magic 0.4.27
- python-magic-bin 0.4.14

You can install these modules using the following command:

```bash
pip install Pillow==10.0.0 argon2-cffi==21.3.0 argon2-cffi-bindings==21.2.0 cffi==1.15.1 pycparser==2.21 pycryptodomex==3.18.0 python-magic==0.4.27 python-magic-bin==0.4.14
```

Make sure you have a working Python environment with the necessary dependencies before proceeding.

<br><br>

## Encryption and Security

V Package Explorer ensures the security of your package contents by using the following encryption and key derivation mechanisms:

- **Encryption Algorithm**: AES-GCM (Advanced Encryption Standard-Galois/Counter Mode)
- **Key Derivation Function**: Argon2 (Memory-Hard Password Hashing)
- **Cryptographic Key Size**: 256 bits (32 bytes)
- **Initialization Vector (IV) Size**: 96 bits (12 bytes)

The Argon2 key derivation function is used to securely derive the encryption key from a user-provided passphrase. 
The memory-hardness property of Argon2 makes it resistant to various attacks, including brute-force and dictionary attacks.

<br><br>

## Usage

### Start
 - Open a terminal or command prompt and navigate to the project directory. 
 - Run the following command to start the V Package Explorer application:
    ```shell
    python explorer.py
    ```


### Navigation
 - The V Package Explorer window will open, displaying the file explorer on the left and the package contents on the right. 
 - Use the file explorer to navigate through the package contents and folders. 
 - To toggle the display of child items in a folder, click on the folder icon.


### Tools
 - To create a new folder, click on the "Add Folder" button in the "Package" menu, and enter the desired folder name when prompted. 
 - To import a media file into an existing folder, click on the "Add Media" button in the "Package" menu, and select the file from your system. 
 - To create a new VPK (Valky's Package) package from a selected directory, click on the "Create Package" button and choose the directory when prompted. 
 - To create VPK (Valky's Package) packages from multiple directories listed in a text file, click on the "Bulk VPK Creation" button and choose the text file when prompted.


### Settings
 - On first use, you will be prompted to enter a key and IV, as well as your name to sign your VPK packages.
 - To change the cryptographic key and IV, click on the "Argon Crypto" button in the "Settings" menu, and follow the prompts. 
 - To change the author name for the VPK package creation, click on the "Settings" menu and select "Set Author" Enter the new author name when prompted. 
 - All settings are stored in an encrypted file, using a unique key based on your windows operating system and hardware pieces.


### Help
 - To access additional resources and support, click on the following links:
    - [VALKYTEQ Website](https://dev.valkyteq.com)
    - [GitHub Repository](https://github.com/ValkyFischer)
    - [VALKYTEQ Discord Community](https://discord.com/invite/Nu7p6wX9Nb)

<br><br>

## Community

### Creator
The V Package Explorer is developed by [ValkyFischer](https://github.com/ValkyFischer), contact me if needed.

### Contributions
Contributions to the V Package Explorer project are welcome! If you find any bugs or have suggestions for 
improvements, please submit an issue or a pull request on the [GitHub repository](https://github.com/ValkyFischer/v-package-explorer).

### Acknowledgments
I would like to acknowledge the following contributors for their support and contributions to this project:
- *None*

<br><br>

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

<br><br>

## Support

For any questions or issues regarding the V Package Explorer application, please join the 
[VALKYTEQ Discord community](https://discord.com/invite/Nu7p6wX9Nb) and ask for assistance in the `#help` channel.

<br><br>

---

**Note:** This is a simplified README file generated by *[L.U.N.A.](https://luna.valkyteq.com/)* based on the provided code. 
