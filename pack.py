import os

from scripts.utils import remove_directory, move_dir
from scripts.archivators import make_archive_from_uncompressible, make_archive_zstd
from scripts.converters import compress_png_to_jxl, remove_pjxl_files
from scripts.unpackers import unpack_all, remove_unpacked_files
from scripts.config import Config

def restore():
    src_dir = Config.get('paths.src_dir')
    tmp_dir = Config.get('paths.tmp_dir')

    move_dir(tmp_dir, src_dir)

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    user_input = input("Введите имя каталога: ").strip()
    src_dir = os.path.join(os.path.dirname(script_dir), user_input)
    if not os.path.isdir(src_dir):
        print(f"Ошибка: Каталог '{src_dir}' не существует.")
        return
    
    dst_dir = src_dir + '_result'
    tmp_dir = os.path.join(dst_dir, os.path.basename(src_dir) + '_tmp')

    Config.set('paths.src_dir', src_dir)
    Config.set('paths.dst_dir', dst_dir)
    Config.set('paths.tmp_dir', tmp_dir)
    
    remove_directory(dst_dir)

    unpack_all()
    compress_png_to_jxl()

    make_archive_from_uncompressible()
    make_archive_zstd()

    remove_unpacked_files()
    remove_pjxl_files()

    restore()



if __name__ == "__main__":
    main()
