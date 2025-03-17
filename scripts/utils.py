import os
import sys
import shutil
from pathlib import Path

def remove_directory(directory_path):
    try:
        if os.path.exists(directory_path):
            shutil.rmtree(directory_path)
    except (PermissionError, OSError) as e:
        print(f"ОШИБКА: Не удалось удалить директорию {directory_path}")
        print(f"Причина: {e}")
        sys.exit(1)

def remove_file(file_path):
    try:
        os.remove(file_path)
    except OSError as e:
        print(f"ОШИБКА: Не удалось удалить {file_path}: {e}")
        sys.exit(1)

def remove_files(src_dir, exts):
    for entry in os.scandir(src_dir):
        if entry.is_file() and any(entry.name.lower().endswith(ext) for ext in exts):
            try:
                os.unlink(entry.path)
            except OSError as e:
                print(f"ОШИБКА: Не удалось удалить {entry.path}: {e}")
                sys.exit(1)
                
def move_all_files_by_ext(src_dir, dst_dir, exts):
    src_dir, dst_dir = Path(src_dir), Path(dst_dir)
    #dst_dir.mkdir(parents=True, exist_ok=True)
    
    # Нормализуем расширения
    ext_set = {ext if ext.startswith('.') else f'.{ext}' for ext in (set(exts) if not isinstance(exts, str) else {exts})}
    
    files_count = 0
    for file_path in src_dir.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in ext_set:
            dst_path = dst_dir / file_path.relative_to(src_dir)
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            
            if dst_path.exists():
                raise FileExistsError(f"Файл {dst_path} уже существует в целевой директории")
            shutil.move(str(file_path), str(dst_path))
            files_count += 1

    return files_count

def move_dir3(src_dir, dst_dir):
    src_dir, dst_dir = Path(src_dir), Path(dst_dir)
    dst_dir.mkdir(parents=True, exist_ok=True)
    
    all_files = [f for f in src_dir.rglob('*') if f.is_file()]
    dirs_to_create = {(dst_dir / f.relative_to(src_dir)).parent for f in all_files}

    for dir_path in dirs_to_create:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    for file_path in all_files:
        dst_file = dst_dir / file_path.relative_to(src_dir)
        if dst_file.exists():
            raise FileExistsError(f"Файл {dst_file} уже существует в целевой директории")
        shutil.move(str(file_path), str(dst_file))
    
    shutil.rmtree(src_dir)
    del all_files

def move_dir(src_dir, dst_dir):
    src_dir = Path(src_dir)
    dst_dir = Path(dst_dir)
    dst_dir.mkdir(parents=True, exist_ok=True)

    for file_path in src_dir.rglob('*'):
        if file_path.is_file():
            dst_file = dst_dir / file_path.relative_to(src_dir)
            if dst_file.exists():
                raise FileExistsError(f"Файл {dst_file} уже существует в целевой директории")
                
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(file_path), str(dst_file))

    shutil.rmtree(src_dir)

def move_dir2(src_dir, dst_dir):
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    for root, dirs, files in os.walk(src_dir):
        relative_path = os.path.relpath(root, src_dir)
        target_dir = os.path.join(dst_dir, relative_path)

        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        for file in files:
            src_file = os.path.join(root, file)
            dst_file = os.path.join(target_dir, file)
            
            if os.path.exists(dst_file):
                print(f"Файл {dst_file} уже существует в целевой директории")
                sys.exit(1)

            try:
                shutil.move(src_file, dst_file)
            except Exception as e:
                print(f"ОШИБКА: Не удалось переместить {src_file}: {e}")
                sys.exit(1)

    shutil.rmtree(src_dir)


def get_files_by_ext(src_dir, exts):
    if isinstance(exts, str):
        ext_set = {exts}
    else:
        ext_set = set(exts) if not isinstance(exts, set) else exts

    return [file for file in src_dir.rglob('*') if file.is_file() and file.suffix in exts]

def get_all_files_by_ext2(src_dir, exts):
    src_dir = Path(src_dir)
    
    if isinstance(exts, str):
        ext_set = {exts if exts.startswith('.') else f'.{exts}'}
    else:
        ext_set = {ext if ext.startswith('.') else f'.{ext}' for ext in exts}
        
    return [
        str(file_path.relative_to(src_dir))
        for file_path in src_dir.rglob('*')
        if file_path.is_file() and file_path.suffix.lower() in ext_set
    ]

def move_files_fullpath(src_dir, dst_dir, full_paths):
    for path in full_paths:
        dst_path = dst_dir / path.relative_to(src_dir)
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            path.rename(dst_path)
#            shutil.move(str(path), str(dst_path))
        except Exception as e:
            print(f"ОШИБКА: Не удалось переместить {path}: {e}")
