import os
import shutil
import sys

from scripts.utils import remove_directory, move_dir, move_all_files_by_ext
from scripts.archivators import make_archive_all
from scripts.converters import compress_png_to_webp, remove_pwebp_files, compress_png_to_jxl, remove_pjxl_files, convert_png_to_npy
from scripts.unpackers import unpack_all, remove_unpacked_files
from scripts.config import Config
from scripts.Repacker import Repacker

def restore():
    src_dir = Config.get('paths.src_dir')
    tmp_dir = Config.get('paths.tmp_dir')

    move_dir(tmp_dir, src_dir)

def main():
    src_dir = input("Введите имя каталога: ").strip()
    if not os.path.isabs(src_dir):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        src_dir = os.path.join(os.path.dirname(script_dir), src_dir)

    repacker = Repacker(src_dir)
    repacker.make_repack()

    compress_png_to_webp()

    make_archive_all()

    restore()
    remove_unpacked_files()
    remove_pwebp_files()

if __name__ == "__main__":
    main()
