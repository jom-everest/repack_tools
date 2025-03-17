import subprocess
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import psutil
import time
import os


from .config import Config
from .utils import get_files_by_ext, move_files_fullpath

class ImageConverter:
    tools_path = {
        'cjxl_path': Config.get('tools.cjxl_path'),
        'cwebp_path':  Config.get('tools.cwebp_path'),
        'djxl_path': Config.get('tools.djxl_path'),
        'dwebp_path':  Config.get('tools.dwebp_path'),
    }
    
    @classmethod
    def set_tool_path(cls, type, tool_path):
        if type in cls.tools_path:
            cls.tools_path[type] = tool_path

    @classmethod
    def convert_png_to_jxl_with_move(cls, src_dir: Path, to_dir: Path, exts): 
        files = get_files_by_ext(src_dir, exts)

        def wrapper(png_path):
            while True:
                memory_info = psutil.virtual_memory()
                free_memory_gb = memory_info.available / (1024 ** 3)
                if free_memory_gb >= 4:
                    break
                time.sleep(10)

            subprocess.run([cls.tools_path['cjxl_path'], png_path, str(png_path) + '.j', '-e', '10', '-q', '100', '--num_threads', '1'], capture_output=True, check=True)

        with ThreadPoolExecutor(max_workers = os.cpu_count()) as executor:
            executor.map(wrapper, files)

        move_files_fullpath(src_dir, to_dir, files)
        del files

    @classmethod
    def convert_png_to_webp_with_move(cls, src_dir: Path, to_dir: Path, exts): 
        files = get_files_by_ext(src_dir, exts)

        with ThreadPoolExecutor(max_workers = os.cpu_count()) as executor:
            executor.map(cls.__convert_png_to_webp, files)

        move_files_fullpath(src_dir, to_dir, files)
        del files

    @classmethod
    def __convert_png_to_webp(cls, png_path: Path):
        subprocess.run([cls.tools_path['cwebp_path'], png_path, '-o', str(png_path) + '.w', '-lossless', '-z', '9'], capture_output=True, check=True)

    @classmethod
    def remove_pwebp_files(cls, target_dir: Path):
        for file_path in target_dir.rglob('.w'):
            os.unlink(file_path)


    @classmethod
    def restore_png_from_webp(cls, target_dir: Path):
        files = get_files_by_ext(target_dir, '.w')

        def wrapper(webp_path):
            subprocess.run([cls.tools_path['dwebp_path'], webp_path, "-o", os.path.splitext(webp_path)[0]], capture_output=True, check=True)
            os.unlink(webp_path)

        with ThreadPoolExecutor(max_workers = os.cpu_count()) as executor:
            executor.map(wrapper, files)

        files = [f[:-2] for f in files]
        subprocess.run([cls.tools_path['oxipng_path'], "-o2", "--strip", "all", "-a", "-t", "16"] + files, check=True)

        del files

    @classmethod
    def restore_png_from_jxl(cls, target_dir: Path):
        files = get_files_by_ext(target_dir, '.j')

        def wrapper(jxl_path):
            subprocess.run([cls.tools_path['djxl_path'], jxl_path, os.path.splitext(jxl_path)[0], '--num_threads', '1'], capture_output=True, check=True)
            os.unlink(jxl_path)

        with ThreadPoolExecutor(max_workers = os.cpu_count()) as executor:
            executor.map(wrapper, files)

        files = [f[:-2] for f in files]
        subprocess.run([cls.tools_path['oxipng_path'], "-o2", "--strip", "all", "-a", "-t", "16"] + files, check=True)

        del files
