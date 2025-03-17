import os
import shutil
import zipfile
import sys
from pathlib import Path
import subprocess


from .config import Config
from .utils import remove_directory


##############
def unzip_file(arc_path, target_dir, suffix):
    new_name = target_dir / f"{arc_path.name.stem}_{arc_path.name.suffix[1:]}"
    with zipfile.ZipFile(arc_path, 'r') as zip_ref:
        file_list = zip_ref.namelist()
        if len(file_list) == 1 and file_list[0] == arc_path.name:
            with zip_ref.open(file_list[0]) as file, open(new_name, 'wb') as new_file:
                new_file.write(file.read())
#            zip_ref.extractall(target_dir)
#            os.rename(target_dir / arc_path.name, new_name)
        else:
            os.makedirs(new_name, exist_ok=True)
            zip_ref.extractall(new_name)
    print(f'Распакован: {arc_path.name}')


    # extract_dir = os.path.join(os.path.dirname(arc_path), os.path.splitext(os.path.basename(arc_path))[0] + suffix)
    # os.makedirs(extract_dir, exist_ok=True)
    # zipfile.ZipFile(arc_path, 'r').extractall(extract_dir)
    # print(f'Распакован: {os.path.basename(arc_path)} -> {extract_dir}')


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
        'pack': zip_file,
        'unpack': unzip_file,
        'exts': {'.zip', '.docx', '.dxanim'},
    },   
    'ue_pak': {
        'suffix': '_ue_pak',
        'unpack': unpak_ue_file,
        'pack': pack_ue_file,
        'test': test_ue_file,
        'exts': {'.pak'},
    },
}

def unpack_all():
    src_dir = Path(Config.get('paths.src_dir'))
    tmp_dir = Path(Config.get('paths.tmp_dir'))

    for file_path in src_dir.rglob('*'):
        if file_path.is_file():
            for _, packer in packers_info.items():
                if file_path.suffix in packer['exts'] and packer['test'] != None and packer['test'](file_path):
                    packer['unpack'](target_dir / file_path.name, packer.get('suffix'))

                    target_dir = tmp_dir / file_path.parent.relative_to(src_dir)
                    target_dir.mkdir(parents=True, exist_ok=True)
                    shutil.move(file_path, target_dir / file_path.name)
                    break

    # for root, _, files in os.walk(src_dir):
    #     for file in files:
    #         for _, packer in packers_info.items():
    #             if os.path.splitext(file)[1] in packer['exts'] and packer['test'] != None and packer['test']():
    #                 packer['unpack'](os.path.join(root, file), packer['suffix'])

    #                 relative_path = Path(root).relative_to(Path(src_dir))
    #                 target_dir = Path(tmp_dir) / relative_path
    #                 target_dir.mkdir(parents=True, exist_ok=True)
    #                 shutil.move(os.path.join(root, file), os.path.join(target_dir, file))
    #                 break

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
