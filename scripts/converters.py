import subprocess
from concurrent.futures import ThreadPoolExecutor
import os
import shutil
import sys
from functools import partial
from pathlib import Path


from .config import Config
from .utils import remove_file, get_all_files_by_ext, move_files


def _compress_png_to_jxl(png_path, src_dir):
    CJXL_PATH = Config.get('tools.cjxl_path')
    full_png_path = os.path.join(src_dir, png_path)
    output_path = os.path.splitext(full_png_path)[0] + '.pjxl'
    subprocess.run([
        CJXL_PATH, 
        full_png_path, 
        output_path,
        '-e', '10',
        '--lossless_jpeg=1',
        '--num_threads', '1'
    ], capture_output=True, check=True)


def compress_png_to_jxl():
    src_dir = Config.get('paths.src_dir')
    tmp_dir = Config.get('paths.tmp_dir')
    max_workers = Config.get('converters.png_to_jxl.threads')
    files = get_all_files_by_ext(src_dir, '.png')

    def wrapper(file):
        _compress_png_to_jxl(file, src_dir=src_dir)

    with ThreadPoolExecutor(max_workers) as executor:
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
    max_workers = Config.get('converters.webp_to_jxl.threads')
    files = get_all_files_by_ext(src_dir, '.png')

    def wrapper(file):
        _compress_png_to_webp(file, src_dir=src_dir)

    with ThreadPoolExecutor(max_workers) as executor:
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

