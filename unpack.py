import os

from scripts.config import Config
from scripts.archivators import unpack_c, unpack_un

def main():
    src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dst_dir = input("Введите имя каталога установки: ").strip()
    if not os.path.isdir(dst_dir):
        dst_dir = os.path.join(os.path.dirname(src_dir), dst_dir)

    Config.set('paths.src_dir', src_dir)
    Config.set('paths.dst_dir', dst_dir)

    unpack_un()
    unpack_c()


if __name__ == "__main__":
    main()
