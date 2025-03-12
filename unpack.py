import os

from scripts.config import Config
from scripts.archivators import unpack_c, unpack_un
from scripts.unpackers import restore_all
from scripts.converters import restore_png_from_jxl

def main():
    src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dst_dir = input("Введите имя каталога установки: ").strip()
    if not os.path.isdir(dst_dir):
        dst_dir = os.path.join(os.path.dirname(src_dir), dst_dir)

    Config.set('paths.src_dir', src_dir)
    Config.set('paths.dst_dir', dst_dir)

    unpack_un()
    unpack_c()

    restore_png_from_jxl()
    restore_all()

if __name__ == "__main__":
    main()
