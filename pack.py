import os
import shutil

from scripts.utils import remove_directory, move_dir, move_all_files_by_ext
from scripts.archivators import make_archive_from_uncompressible, make_archive, make_arc_npy, make_archive_all
from scripts.converters import compress_png_to_webp, remove_pwebp_files, compress_png_to_jxl, remove_pjxl_files, convert_png_to_npy
from scripts.unpackers import unpack_all, remove_unpacked_files
from scripts.config import Config

def restore():
    src_dir = Config.get('paths.src_dir')
    tmp_dir = Config.get('paths.tmp_dir')
    dst_dir = Config.get('paths.dst_dir')
    target_dir = os.path.join(dst_dir, 'arc_un')

    move_dir(tmp_dir, src_dir)

    move_all_files_by_ext(target_dir, src_dir, Config.get('extensions.uncompressible'))
    shutil.rmtree(target_dir)
    shutil.rmtree(os.path.join(dst_dir, 'arc_npy'))

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    user_input = input("Введите имя каталога: ").strip()
    src_dir = os.path.join(os.path.dirname(script_dir), user_input)
#    src_dir = user_input
    if not os.path.isdir(src_dir):
        print(f"Ошибка: Каталог '{src_dir}' не существует.")
        return
    
    dst_dir = src_dir + '_result'
    tmp_dir = os.path.join(dst_dir, os.path.basename(src_dir) + '_tmp')

    Config.set('paths.src_dir', src_dir)
    Config.set('paths.dst_dir', dst_dir)
    Config.set('paths.tmp_dir', tmp_dir)
    Config.set('archive.type', '7z')
    
    remove_directory(dst_dir)
    os.makedirs(tmp_dir, exist_ok=True)

#    convert_png_to_npy()
#    restore_png_from_npy()
    unpack_all()
    compress_png_to_webp()
#    convert_png_to_npy()

    make_archive_all()
#    make_archive_from_uncompressible()
#    make_arc_npy()
#    make_archive()

    restore()

    remove_unpacked_files()
    remove_pwebp_files()


if __name__ == "__main__":
    main()
