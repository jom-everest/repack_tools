import os
import shutil
import subprocess

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
    zst_file = os.path.join(src_dir, 'arc_c.zst')

    if not os.path.exists(zst_file):
        raise FileExistsError(f'Ошибка: {os.path.basename(zst_file)} отсутствует')

    ZSTD_PATH = Config.get('tools.zstd_path')
    Z_PATH = Config.get('tools.7z_path')
    process_zstd = subprocess.Popen([ZSTD_PATH, '-d', '--stdout', zst_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process_7z = subprocess.Popen([Z_PATH, 'x', '-si', "-o" + dst_dir], stdin=process_zstd.stdout)
    process_zstd.wait()
    process_7z.wait()
    
def make_arc_pipe():
    ZSTD_PATH = Config.get('tools.zstd_path')
    Z_PATH = Config.get('tools.7z_path')
    src_dir = Config.get('paths.src_dir')
    dst_dir = Config.get('paths.dst_dir')
    target_zst = os.path.join(dst_dir, 'arc_c.zst')

    process_7z = subprocess.Popen(
        [Z_PATH, "a", "-t7z", "-m0=Copy", "-mx=0", '-mhe=off', "-ms=on", "-so", os.path.join(src_dir, "*")], 
        stdout=subprocess.PIPE
    )
    process_zstd = subprocess.Popen(
        [ZSTD_PATH, "-19", "--ultra", "--long=31", "-f", "-T0", "-o", target_zst], 
        stdin=process_7z.stdout
    )
    process_7z.stdout.close()
    process_7z.wait()
    process_zstd.wait()

def make_archive_from_uncompressible():
    src_dir = Config.get('paths.src_dir')
    dst_dir = Config.get('paths.dst_dir')
    target_dir = os.path.join(dst_dir, 'arc_un')
    os.makedirs(target_dir, exist_ok=True)

    files_count = move_all_files_by_ext(src_dir, target_dir, Config.get('extensions.uncompressible') | Config.get('extensions.user'))

    if files_count > 0:
        Z_PATH = Config.get('tools.7z_path')
        target_zip = os.path.join(dst_dir, 'arc_un.7z')
        subprocess.run([Z_PATH, 'a', '-t7z', '-m0=LZMA2', '-mx1', '-mhe=off', "-ms=on", target_zip, os.path.join(target_dir, "*")], check=True)

def make_archive_zstd():
    ZSTD_PATH = Config.get('tools.zstd_path')
    src_dir = Config.get('paths.src_dir')
    dst_dir = Config.get('paths.dst_dir')
    target_zst = os.path.join(dst_dir, 'arc_c.zst')
    Config.set('paths.zstd_archive_file', target_zst)

    Z_PATH = Config.get('tools.7z_path')
    target_7z = os.path.join(dst_dir, 'arc_c.7z')
    subprocess.run([Z_PATH, 'a', '-t7z', "-m0=Copy", '-mx0', "-ms=on", '-mhe=off', target_7z, os.path.join(src_dir, "*")], check=True)
    
    subprocess.run(
        [ZSTD_PATH, '-f', '-19', '--ultra', '-T0', '--long=31', target_7z, '-o', target_zst],
        check=True
    )
    os.unlink(target_7z)
    subprocess.run([Z_PATH, 'a', '-t7z', '-m0=LZMA2', '-mx9', "-ms=on", '-mhe=off', target_7z, os.path.join(src_dir, "*")], check=True)

