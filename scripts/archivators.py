import os
import shutil
import subprocess
import tarfile
import tempfile
import py7zr
from PIL import Image
import numpy as np


from .config import Config
from .utils import move_all_files_by_ext

def unpack_un():
    src_dir = Config.get('paths.src_dir')
    dst_dir = Config.get('paths.dst_dir')
    target_file = os.path.join(src_dir, 'arc_un.7z')

    if os.path.exists(target_file):
        Z_PATH = Config.get('tools.7z_path')
        subprocess.run([Z_PATH, 'x', target_file, f"-o{dst_dir}"], check=True)

def unpack_c():
    src_dir = Config.get('paths.src_dir')
    dst_dir = Config.get('paths.dst_dir')
    Z_PATH = Config.get('tools.7z_path')
    ZSTD_PATH = Config.get('tools.zstd_path')

    arc_file = os.path.join(src_dir, 'arc_c.7z')
    if (os.path.exists(arc_file)):
        subprocess.run([Z_PATH, 'x', arc_file, f'-o{dst_dir}'])
        return

    arc_file = os.path.join(src_dir, 'arc_c.7z.zstd')
    if (os.path.exists(arc_file)):
        with tempfile.NamedTemporaryFile(dir=dst_dir, suffix='.7z', delete=False) as temp_7z:
            process_zstd = subprocess.Popen([ZSTD_PATH, '-d', '-T0', '--stdout', arc_file], stdout=temp_7z)
            process_zstd.communicate()

        process_7z = subprocess.Popen([Z_PATH, 'x', temp_7z.name, f'-o{dst_dir}'])
        process_7z.wait()
        os.unlink(temp_7z.name) 
        return

    arc_file = os.path.join(src_dir, 'arc_c.tar.zstd')
    if (os.path.exists(arc_file)):
        zstd_process = subprocess.Popen([ZSTD_PATH, '-d', '-T0', '--stdout', arc_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        with tarfile.open(fileobj=zstd_process.stdout, mode='r|*') as tar:
            tar.extractall(path=dst_dir)
#        stdout, stderr = zstd_process.communicate()
#        if zstd_process.returncode != 0:
#            raise RuntimeError(f'Ошибка zstd: {stderr.decode().strip()}')

def make_arc_npy():
    src_dir = Config.get('paths.src_dir')
    dst_dir = Config.get('paths.dst_dir')
    target_dir = os.path.join(dst_dir, 'arc_npy')
    os.makedirs(target_dir, exist_ok=True)

    files_count = move_all_files_by_ext(src_dir, target_dir, '.npy')
    if files_count > 0:
        Z_PATH = Config.get('tools.7z_path')
        target_zip = os.path.join(dst_dir, 'arc_npy.7z')
        subprocess.run([Z_PATH, 'a', '-t7z', '-m0=LZMA2', '-mx9', '-mhe=off', "-ms=on", '-mmt=8', target_zip, os.path.join(target_dir, "*")], check=True)

def unpack_npy():
    src_dir = Config.get('paths.src_dir')
    target_file = os.path.join(src_dir, 'arc_npy.7z')

    with py7zr.SevenZipFile(target_file, mode='r') as archive:
        file_list = archive.getnames()
        for file_name in file_list:
            with archive.read([file_name]) as files:
                image = Image.fromarray(np.load(files[file_name].read(), allow_pickle=True))
                image.save(os.path.join(src_dir, file_name.replace('.npy', '.png')))

def make_archive_from_uncompressible():
    src_dir = Config.get('paths.src_dir')
    dst_dir = Config.get('paths.dst_dir')
    target_dir = os.path.join(dst_dir, 'arc_un')
    os.makedirs(target_dir, exist_ok=True)

    files_count = move_all_files_by_ext(src_dir, target_dir, Config.get('extensions.uncompressible') | Config.get('extensions.user'))

    if files_count > 0:
        Z_PATH = Config.get('tools.7z_path')
        target_zip = os.path.join(dst_dir, 'arc_un.7z')
        subprocess.run([Z_PATH, 'a', '-t7z', '-m0=LZMA2', '-mx3', '-mhe=off', '-mmt=8', "-ms=on", target_zip, os.path.join(target_dir, "*")], check=True)

def make_archive():
    src_dir = Config.get('paths.src_dir')
    dst_dir = Config.get('paths.dst_dir')
    arc_type = Config.get('archive.type')

    Z_PATH = Config.get('tools.7z_path')
    if (arc_type == '7z'):
        target_7z = os.path.join(dst_dir, 'arc_c.7z')
        subprocess.run([Z_PATH, 'a', '-t7z', '-m0=LZMA2', '-mx9', "-ms=on", '-mmt=8', '-mhe=off', target_7z, os.path.join(src_dir, "*")], check=True)

    if (arc_type == '7z.zstd'):
        ZSTD_PATH = Config.get('tools.zstd_path')
        target_zstd = os.path.join(dst_dir, 'arc_c.7z.zstd')
        with tempfile.NamedTemporaryFile(dir=dst_dir, suffix='.7z', delete=False) as temp_7z:
            process_7z = subprocess.Popen([Z_PATH, 'a', '-t7z', "-m0=Copy", "-ms=on", '-mx0', '-mmt=8', '-mhe=off', temp_7z.name, os.path.join(src_dir, "*")])
            process_7z.communicate()
            process_7z.wait()
        process_zstd = subprocess.Popen([ZSTD_PATH, '-f', '-19', '--ultra', '-T0', '--long=31', temp_7z.name, '-o', target_zstd])
        process_zstd.communicate()
        process_zstd.wait()
        os.unlink(temp_7z.name)

    if (arc_type == 'tar.zstd'):
        target_zstd = os.path.join(dst_dir, 'arc_c.tar.zstd')
        process_zstd = subprocess.Popen(
            [ZSTD_PATH, '-z', '--stdout'], stdin=subprocess.PIPE, stdout=open(target_zstd, 'wb'), stderr=subprocess.PIPE
        )
        with tarfile.open(fileobj=process_zstd.stdin, mode='w|') as tar:
            tar.add(dst_dir, arcname=os.path.basename(dst_dir))  # Добавляем каталог в архив
            process_zstd.stdin.close()
            process_zstd.wait()

def make_archive(src_dir, target_name, archive_params):
    Z_PATH = Config.get('tools.7z_path')
    if (archive_params == None):
        type = '7z', m = 'lzma2', mx = '9'
    else:
        type = '7z', m = 'lzma2', mx = '9'

    target_arc = target_name + '.7z'
    m0 = 'lzma2'
    mx = '9'
    if (archive_params.type == 'PPMD'):
        m0 = 'ppmd'
    subprocess.run([Z_PATH, 'a', '-t7z', f'-m0={m0}', f'-mx{mx}', '-mhe=off', '-mmt=8', "-ms=on", target_arc, os.path.join(src_dir, "*")], check=True)

def make_archive_all():
    src_dir = Config.get('paths.src_dir')
    dst_dir = Config.get('paths.dst_dir')

    for key, value in Config.get('groups').items():
        if (key == 'all'): continue

        target_dir = os.path.join(dst_dir, 'arc_' + key)
        exts = value['extensions']
#        os.makedirs(target_dir, exist_ok=True)
        files_count = move_all_files_by_ext(src_dir, target_dir, exts)
        if files_count > 0:
            make_archive(target_dir, target_dir, value.get('archive_params'))

    target_name = os.path.join(dst_dir, 'arc_' + 'all')
    make_archive(src_dir, target_name, Config.get('groups.all.archive_params'))
