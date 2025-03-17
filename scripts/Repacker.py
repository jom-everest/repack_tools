import os
from pathlib import Path
import shutil


from scripts import utils
from .packers import PackerZip, PackerUePak

class Repacker():
    def __init__(self, src_dir):
        self.__init_settings()

        if not os.path.isdir(src_dir):
            raise FileNotFoundError(f"Каталога '{src_dir}' не существует.")
    
        dst_dir = src_dir + '_result'
        tmp_dir = os.path.join(dst_dir, os.path.basename(src_dir) + '_tmp')
        utils.remove_directory(dst_dir)

        os.makedirs(tmp_dir)

        self.__src_dir = Path(src_dir)
        self.__dst_dir = Path(dst_dir)
        self.__tmp_dir = Path(tmp_dir)

    def __init_settings(self):
        self.__settings = {
            "optimize_png": False,
        }
        self.__packers_info = [
            {
                'exts': {'.zip', '.docx'},
                'packers': [PackerZip],
                'is_trust': True,
            },
            {
                'exts': {'.pak'},
                'packers': [PackerUePak]
            }
        ]
        self.__update_ext_table()

    def __update_ext_table(self):
        self.__ext_to_packers = {
            ext: item
            for item in self.__packers_info
            for ext in item['exts']
        }

    def set_option(self, key, value):
        if key in self.settings:
                self.settings[key] = value
        else:
            print(f"Настройка '{key}' не найдена.")

    def make_repack(self):
        if self.__src_dir == None:
            raise Exception(f"Исходный каталог не задан.")
        
        self.__unpack_all()
        self.__conversions()

    def __get_packer(self, file_path: Path):
        packers_obj = self.__ext_to_packers.get(file_path.suffix)
        if packers_obj.get('is_trust', False) == True:
            return packers_obj['packers'][0]
        else:
            for packer in packers_obj.get('packers'):
                if packer().test(file_path):
                    return packer
                
        return None

    def __unpack_all(self):
        file_list = [file for file in self.__src_dir.glob('*')  if file.is_file() and file.suffix in self.__ext_to_packers]
        for file_path in file_list:
            packer = self.__get_packer(file_path)
            if packer:
                to_path = file_path.with_name(file_path.stem + file_path.suffix.replace(".", "_"))
                packer().unpack(file_path, to_path)

                target_dir = self.__tmp_dir / file_path.parent.relative_to(self.__src_dir)
                target_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(file_path, target_dir / file_path.name)

        del file_list

    def __convert_png_to_webp(self):


    def __conversions(self):
        if self.__settings.get('optimize_png'):
            self.__convert_png_to_webp()


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

