import os
import shutil
import tarfile
import subprocess
import zipfile

from .config import Config
from .utils import move_all_files_by_ext

def unpack_un():
    src_dir = Config.get('paths.src_dir')
    dst_dir = Config.get('paths.dst_dir')
    target_file = os.path.join(src_dir, 'arc_un.zip')

    if os.path.exists(target_file):
        with zipfile.ZipFile(target_file, 'r') as zip_ref:
            zip_ref.extractall(path=dst_dir)

#    if os.path.exists(target_file):
#        with tarfile.open(target_file, 'r') as tar:
#            tar.extractall(path=dst_dir)

def unpack_c():
    src_dir = Config.get('paths.src_dir')
    dst_dir = Config.get('paths.dst_dir')
    zst_file = os.path.join(src_dir, 'arc_c.zst')

    if not os.path.exists(zst_file):
        raise FileExistsError(f'Ошибка: {os.path.basename(zst_file)} отсутствует')

    ZSTD_PATH = Config.get('tools.zstd_path')
    zstd_process = subprocess.Popen([ZSTD_PATH, '-d', '--stdout', zst_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    with tarfile.open(fileobj=zstd_process.stdout, mode='r|*') as tar:
        tar.extractall(path=dst_dir)

    stdout, stderr = zstd_process.communicate()
    if zstd_process.returncode != 0:
            raise RuntimeError(f'Ошибка zstd: {stderr.decode().strip()}')

def make_archive_from_uncompressible():
    src_dir = Config.get('paths.src_dir')
    dst_dir = Config.get('paths.dst_dir')
    target_dir = os.path.join(dst_dir, 'arc_un')
    os.makedirs(target_dir, exist_ok=True)

    files_count = move_all_files_by_ext(src_dir, target_dir, Config.get('extensions.uncompressible'))

    if files_count > 0:
        Z_PATH = Config.get('tools.7z_path')
        target_zip = os.path.join(dst_dir, 'arc_un.zip')
        subprocess.run([Z_PATH, 'a', '-tzip', '-mx1', target_zip, os.path.join(target_dir, "*")], check=True)

        target_tar = os.path.join(dst_dir, 'arc_un.tar')
        with tarfile.open(target_tar, 'w', bufsize = 10**8) as tar:
#            tar.add(target_dir, arcname=os.path.basename(target_dir))
            for entry in os.scandir(target_dir):
                tar.add(entry.path, arcname=entry.name)
    shutil.rmtree(target_dir)

def make_archive_zstd():
    ZSTD_PATH = Config.get('tools.zstd_path')
    src_dir = Config.get('paths.src_dir')
    dst_dir = Config.get('paths.dst_dir')
    target_tar = os.path.join(dst_dir, 'arc_c.tar')
    target_zst = os.path.join(dst_dir, 'arc_c.zst')
    Config.set('paths.zstd_archive_file', target_zst)

    with tarfile.open(target_tar, 'w', bufsize = 10**8) as tar:
#        tar.add(src_dir, arcname = os.path.basename(src_dir))
        for entry in os.scandir(src_dir):
            tar.add(entry.path, arcname=entry.name)

    subprocess.run(
        [ZSTD_PATH, '-19', '-T8', '--long', target_tar, '-o', target_zst],
        check=True
    )
    os.remove(target_tar)


def make_archive_zstd_pipe():
    ZSTD_PATH = Config.get('tools.zstd_path')
    src_dir = Config.get('paths.src_dir')
    target_zst = os.path.join(Config.get('paths.dst_dir'), 'arc_c.zst')
    Config.set('paths.zstd_archive_file', target_zst)

    zstd_process = subprocess.Popen(
        [ZSTD_PATH, '-19', '-T8', '--long', '-o', target_zst],
        stdin=subprocess.PIPE,
        bufsize=10**8
    )
    
    with tarfile.open(fileobj=zstd_process.stdin, mode='w|') as tar:
        tar.add(
            src_dir, 
            arcname=os.path.basename(src_dir)
        )
    
    zstd_process.stdin.close()
    zstd_process.wait()
