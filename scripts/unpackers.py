import os
import shutil
import zipfile
import sys
from pathlib import Path
import subprocess


from .config import Config
from .utils import remove_directory


##############
def unzip_file(arc_path, suffix):
    extract_dir = os.path.join(os.path.dirname(arc_path), os.path.splitext(os.path.basename(arc_path))[0] + suffix)
    os.makedirs(extract_dir, exist_ok=True)
    zipfile.ZipFile(arc_path, 'r').extractall(extract_dir)
    print(f'Распакован: {os.path.basename(arc_path)} -> {extract_dir}')

def zip_file(dir_path, arc_path):
    Z_PATH = Config.get('tools.7z_path')
    subprocess.run([Z_PATH, 'a', '-tzip', '-mfb=64', '-mx7', arc_path, os.path.join(dir_path, "*")], check=True)

##########
def pack_ue_file(dir_path, arc_path):
    REPAK_PATH = Config.get('tools.repak_path')
    subprocess.run([REPAK_PATH, 'pack', '--compression', 'Zstd', dir_path], check=True)

def unpak_ue_file(arc_path, suffix):
    REPAK_PATH = Config.get('tools.repak_path')
    extract_dir = os.path.join(os.path.dirname(arc_path), os.path.splitext(os.path.basename(arc_path))[0] + suffix)
    subprocess.run([REPAK_PATH, 'unpack', '-o', extract_dir, arc_path], check=True)
    print(f'Распакован: {os.path.basename(arc_path)} -> {extract_dir}')

def test_ue_file(arc_path):
    REPAK_PATH = Config.get('tools.repak_path')
    result = subprocess.run([REPAK_PATH, 'info', arc_path], capture_output=True, check=True)
    if result.returncode != 0:
        return False
    first_line = result.stdout.splitlines()[0]
    if "mount" in first_line.lower():
        return True
    else:
        return False
#############

packers_info = {
    'zip': {
        'ext': 'zip',
        'suffix': '_zip',
        'pack': zip_file,
        'unpack': unzip_file,
    },
    'docx': {
        'ext': 'docx',
        'suffix': '_docx',
        'unpack': unzip_file,
        'pack': zip_file,
    },
    'ue_pak': {
        'ext': 'pak',
        'suffix': '_ue_pak',
        'unpack': unpak_ue_file,
        'pack': pack_ue_file,
        'test': test_ue_file,
    },
}

def unpack_all():
    src_dir = Config.get('paths.src_dir')
    tmp_dir = Config.get('paths.tmp_dir')

    for root, dirs, files in os.walk(src_dir):
        for file in files:
            for _, packer in packers_info.items():
                if file.endswith(packer['ext']) and packer['test'] != None and packer['test']():
                    packer['unpack'](os.path.join(root, file), packer['suffix'])

                    relative_path = Path(root).relative_to(Path(src_dir))
                    target_dir = Path(tmp_dir) / relative_path
                    target_dir.mkdir(parents=True, exist_ok=True)
                    shutil.move(os.path.join(root, file), os.path.join(target_dir, file))
                    break

#    for root, dirs, files in os.walk(src_dir):
#        for file in files:
#            for ext, handler in packers.items():
#                if file.endswith(ext):
#                    handler['unpack'](os.path.join(root, file), handler['suffix'])

#                    relative_path = Path(root).relative_to(Path(src_dir))
#                    target_dir = Path(tmp_dir) / relative_path
#                    target_dir.mkdir(parents=True, exist_ok=True)
#                    shutil.move(os.path.join(root, file), os.path.join(target_dir, file))
#                    break

def remove_unpacked_files():
    src_dir = Path(Config.get('paths.src_dir'))
    suffixes = [info['suffix'] for info in packers_info.values()]

    for dir_path in src_dir.rglob('*'):
        if dir_path.is_dir() and any(dir_path.name.endswith(suffix) for suffix in suffixes):
            shutil.rmtree(dir_path)

def restore_all():
    dst_dir = Path(Config.get('paths.dst_dir'))
    for dir_path in dst_dir.rglob('*'):
        if dir_path.is_dir():
            for _, packer in packers_info.items():
                if str(dir_path.name).endswith(packer['suffix']):  # Проверяем суффикс
                    packer['pack'](dir_path, str(dir_path).removesuffix(packer['suffix']) + packer['ext'])
                    shutil.rmtree(dir_path)
                    break
