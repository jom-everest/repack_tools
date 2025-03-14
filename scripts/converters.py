import subprocess
from concurrent.futures import ThreadPoolExecutor
import os
from functools import partial
from pathlib import Path
import tempfile
import psutil
import time
from PIL import Image
import numpy as np
import os


from .config import Config
from .utils import remove_file, get_all_files_by_ext, move_files

def _compress_png_to_jxl(png_path, src_dir):
    while True:
        memory_info = psutil.virtual_memory()
        free_memory_gb = memory_info.available / (1024 ** 3)
        if free_memory_gb >= 4:
            break
        time.sleep(10)

    CJXL_PATH = Config.get('tools.cjxl_path')
    full_png_path = os.path.join(src_dir, png_path)
    output_path = os.path.splitext(full_png_path)[0] + '.pjxl'
    subprocess.run([
        CJXL_PATH, 
        full_png_path, 
        output_path,
        '-e', '10',
        '-q', '100',
        '--num_threads', '1'
    ], capture_output=True, check=True)


def compress_png_to_jxl():
    src_dir = Config.get('paths.src_dir')
    tmp_dir = Config.get('paths.tmp_dir')
    files = get_all_files_by_ext(src_dir, '.png')

    def wrapper(file):
        _compress_png_to_jxl(file, src_dir=src_dir)

    with ThreadPoolExecutor(max_workers = Config.get('max_threads')) as executor:
        executor.map(wrapper, files)

    move_files(src_dir, tmp_dir, files)

def _compress_png_to_webp(png_path, src_dir):
    CWEBP_PATH = Config.get('tools.cwebp_path')
    full_png_path = os.path.join(src_dir, png_path)
    output_path = os.path.splitext(full_png_path)[0] + '.pwebp'
    subprocess.run([
        CWEBP_PATH, 
        full_png_path, 
        '-o', output_path,
        '-lossless',
        '-z', '9'
    ], capture_output=True, check=True)

def compress_png_to_webp():
    src_dir = Config.get('paths.src_dir')
    tmp_dir = Config.get('paths.tmp_dir')
    files = get_all_files_by_ext(src_dir, '.png')

    def wrapper(file):
        _compress_png_to_webp(file, src_dir=src_dir)
#        _compress_png_to_jxl(file, src_dir=src_dir)

    with ThreadPoolExecutor(max_workers = Config.get('max_threads')) as executor:
        executor.map(wrapper, files)
    move_files(src_dir, tmp_dir, files)

def remove_pjxl_files():
    src_dir = Path(Config.get('paths.src_dir'))
    for file_path in src_dir.rglob('*'):
        if file_path.is_file() and file_path.name.endswith('.pjxl'):
            os.unlink(file_path)

def remove_pwebp_files():
    src_dir = Path(Config.get('paths.src_dir'))
    for file_path in src_dir.rglob('*'):
        if file_path.is_file() and file_path.name.endswith('.pwebp'):
            os.unlink(file_path)

def _restore_png_from_webp(webp_path, src_dir):
    DWEBP_PATH = Config.get('tools.dwebp_path')
    OXI_PATH = Config.get('tools.oxi_path')
    full_path = os.path.join(src_dir, webp_path)
    output_path = os.path.splitext(full_path)[0] + '.png'

    subprocess.run([DWEBP_PATH, full_path, "-o", output_path], capture_output=True, check=True)

def restore_png_from_webp():
    target_dir = Config.get('paths.dst_dir')
    files = get_all_files_by_ext(target_dir, '.pwebp')

    def wrapper(file):
        _restore_png_from_webp(file, src_dir=target_dir)
        os.unlink(os.path.join(target_dir, file))

    with ThreadPoolExecutor(max_workers = Config.get('max_threads')) as executor:
        executor.map(wrapper, files)

    OXI_PATH = Config.get('tools.oxi_path')
    subprocess.run([OXI_PATH, "-o2", "--strip", "all", "-a", "-t", "16", '-r', target_dir], check=True)


def _restore_png_from_jxl(jxl_path, src_dir):
    DJXL_PATH = Config.get('tools.djxl_path')
    OXI_PATH = Config.get('tools.oxi_path')
    full_path = os.path.join(src_dir, jxl_path)
    output_path = os.path.splitext(full_path)[0] + '.png'

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        temp_png = tmp.name
    try:
        subprocess.run([DJXL_PATH, full_path, temp_png, '--num_threads', '1'], capture_output=True, check=True)
        subprocess.run([OXI_PATH, "-omax", "--strip", "all", "-a", "--threads", "1", temp_png], check=True)
        os.rename(temp_png, output_path)
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при обработке {jxl_path}: {e}")
        os.remove(temp_png)  # Удаляем временный файл

def restore_png_from_jxl():
    target_dir = Config.get('paths.dst_dir')
    files = get_all_files_by_ext(target_dir, '.pjxl')

    def wrapper(file):
        _restore_png_from_jxl(file, src_dir=target_dir)
        os.unlink(os.path.join(target_dir, file))

    with ThreadPoolExecutor(max_workers = Config.get('max_threads')) as executor:
        executor.map(wrapper, files)

def _convert_png_to_npy(png_path, src_dir):
    full_png_path = os.path.join(src_dir, png_path)
    output_path = os.path.splitext(full_png_path)[0] + '.npy'

    image = Image.open(full_png_path)
    pixel_array = np.array(image)
    np.save(output_path, pixel_array)

def convert_png_to_npy():
    src_dir = Config.get('paths.src_dir')
    tmp_dir = Config.get('paths.tmp_dir')
    files = get_all_files_by_ext(src_dir, '.png')

    def wrapper(file):
        _convert_png_to_npy(file, src_dir=src_dir)

    with ThreadPoolExecutor(max_workers = 2) as executor:
        executor.map(wrapper, files)
    move_files(src_dir, tmp_dir, files)

def _restore_png_from_npy(npy_path, src_dir):
    full_path = os.path.join(src_dir, npy_path)
    png_path = os.path.splitext(full_path)[0] + '.png'

    pixel_array = np.load(full_path)
    image = Image.fromarray(pixel_array)
    image.save(png_path)

def restore_png_from_npy():
    target_dir = Config.get('paths.dst_dir')
    files = get_all_files_by_ext(target_dir, '.npy')

    def wrapper(file):
        _restore_png_from_npy(file, src_dir=target_dir)
        os.unlink(os.path.join(target_dir, file))

    with ThreadPoolExecutor(max_workers = Config.get('max_threads')) as executor:
        executor.map(wrapper, files)

    OXI_PATH = Config.get('tools.oxi_path')
    subprocess.run([OXI_PATH, "-o2", "--strip", "all", "-a", "-t", "16", '-r', target_dir], check=True)

