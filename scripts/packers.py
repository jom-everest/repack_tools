import subprocess
import zipfile
import os
from pathlib import Path

from scripts.config import Config

class PackerUePak : pass

class PackerZip :
    Z_PATH = Config.get('tools.7z_path')

    @classmethod
    def pack(cls, target_path: Path, arc_name = None):
        if target_path.is_dir:
            subprocess.run([cls.Z_PATH, 'a', '-tzip', '-mfb=64', '-mx7', arc_name, str(target_path / "*")], check=True)
        elif target_path.is_file:
            subprocess.run([cls.Z_PATH, 'a', '-tzip', '-mfb=64', '-mx7', arc_name, str(target_path)], check=True)

    @classmethod
    def unpack(cls, arc_path: Path, to_path):
        with zipfile.ZipFile(arc_path, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            if len(file_list) == 1 and file_list[0] == arc_path.name:
                with zip_ref.open(file_list[0]) as file, open(to_path, 'wb') as new_file:
                    new_file.write(file.read())
            else:
                os.makedirs(to_path, exist_ok=True)
                zip_ref.extractall(to_path)
        print(f'Распакован: {arc_path.name}')

