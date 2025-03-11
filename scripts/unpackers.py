import os
import shutil
import zipfile
import sys
from pathlib import Path


from .config import Config
from .utils import remove_directory

def unzip_file(zip_path):
    print("This is a placeholder")

def unrar_file(rar_path):
    print("This is a placeholder")

packers = {
    '.zip': {
        'unpack': unzip_file,
        'suffix': '_zip',
    },
    '.rar': {
        'unpack': unrar_file,
        'suffix': '_rar',
    }
}

def unzip_file(zip_path, suffix):
    extract_dir = os.path.join(os.path.dirname(zip_path), os.path.splitext(os.path.basename(zip_path))[0] + suffix)
    os.makedirs(extract_dir, exist_ok=True)
    zipfile.ZipFile(zip_path, 'r').extractall(extract_dir)
    print(f'Распакован: {os.path.basename(zip_path)} -> {extract_dir}')

packers['.zip']['unpack'] = unzip_file

def unpack_all():
    src_dir = Config.get('paths.src_dir')
    tmp_dir = Config.get('paths.tmp_dir')
    os.makedirs(tmp_dir, exist_ok=True)

    for root, dirs, files in os.walk(src_dir):
        for file in files:
            for ext, handler in packers.items():
                if file.endswith(ext):
                    handler['unpack'](os.path.join(root, file), handler['suffix'])
                    shutil.move(os.path.join(root, file), os.path.join(tmp_dir, file))
                    break

def remove_unpacked_files():
    src_dir = Path(Config.get('paths.src_dir'))
    suffixes = [info['suffix'] for info in packers.values()]

    for dir_path in src_dir.rglob('*'):
        if dir_path.is_dir() and any(dir_path.name.endswith(suffix) for suffix in suffixes):
            shutil.rmtree(dir_path)