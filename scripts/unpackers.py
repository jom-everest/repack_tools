import os
import shutil
import zipfile
import sys
from pathlib import Path
import subprocess


from .config import Config
from .utils import remove_directory

def unzip_file(arc_path, suffix):
    extract_dir = os.path.join(os.path.dirname(arc_path), os.path.splitext(os.path.basename(arc_path))[0] + suffix)
    os.makedirs(extract_dir, exist_ok=True)
    zipfile.ZipFile(arc_path, 'r').extractall(extract_dir)
    print(f'Распакован: {os.path.basename(arc_path)} -> {extract_dir}')

def zip_file(dir_path, arc_path):
    Z_PATH = Config.get('tools.7z_path')
    subprocess.run([Z_PATH, 'a', '-tzip', '-mfb=64', '-mx7', arc_path, os.path.join(dir_path, "*")], check=True)

packers = {
    '.zip': {
        'unpack': unzip_file,
        'pack': zip_file,
        'suffix': '_zip',
    },
    '.docx': {
        'unpack': unzip_file,
        'pack': zip_file,
        'suffix': '_docx',
    }
}

def unpack_all():
    src_dir = Config.get('paths.src_dir')
    tmp_dir = Config.get('paths.tmp_dir')
    os.makedirs(tmp_dir, exist_ok=True)

    for root, dirs, files in os.walk(src_dir):
        for file in files:
            for ext, handler in packers.items():
                if file.endswith(ext):
                    handler['unpack'](os.path.join(root, file), handler['suffix'])

                    relative_path = Path(root).relative_to(Path(src_dir))
                    target_dir = Path(tmp_dir) / relative_path
                    target_dir.mkdir(parents=True, exist_ok=True)
                    shutil.move(os.path.join(root, file), os.path.join(target_dir, file))
                    break

def remove_unpacked_files():
    src_dir = Path(Config.get('paths.src_dir'))
    suffixes = [info['suffix'] for info in packers.values()]

    for dir_path in src_dir.rglob('*'):
        if dir_path.is_dir() and any(dir_path.name.endswith(suffix) for suffix in suffixes):
            shutil.rmtree(dir_path)

def restore_all():
    dst_dir = Path(Config.get('paths.dst_dir'))
    for dir_path in dst_dir.rglob('*'):
        if dir_path.is_dir():
            for ext, packer in packers.items():
                if str(dir_path.name).endswith(packer['suffix']):  # Проверяем суффикс
                    packer['pack'](dir_path, str(dir_path).removesuffix(packer['suffix']) + ext)
                    shutil.rmtree(dir_path)
                    break
