import UnityPy
import os
import shutil
from pathlib import Path
from typing import List, Dict

def get_object_size(obj) -> int:
    """
    Возвращает размер "сырых" данных объекта в байтах.
    
    :param obj: Объект из UnityPy
    :return: Размер данных в байтах
    """
    try:
        if hasattr(obj, "get_raw_data"):
            raw_data = obj.get_raw_data()
            return len(raw_data) if raw_data else 0
        elif hasattr(obj, "read"):
            data = obj.read()
            if hasattr(data, "get_raw_data"):
                raw_data = data.get_raw_data()
                return len(raw_data) if raw_data else 0
        return 0
    except Exception:
        return 0

def unpack_large_objects(bundle_path: str, output_dir: str, size_threshold: int = 1024 * 1024) -> List[Dict]:
    """
    Распаковывает только самые объемные данные из UnityFS-бандла в указанную директорию.
    
    :param bundle_path: Путь к файлу UnityFS-бандла
    :param output_dir: Путь к директории для распаковки
    :param size_threshold: Порог размера в байтах (по умолчанию 1 МБ)
    :return: Список объектов, которые были распакованы (для последующего удаления)
    """
    if not os.path.exists(bundle_path):
        raise FileNotFoundError(f"Файл UnityFS-бандла не найден: {bundle_path}")

    # Создаем выходную директорию, если она не существует
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)  # Очищаем директорию, если она существует
    os.makedirs(output_dir)

    # Загружаем UnityFS-бандл
    env = UnityPy.load(bundle_path)

    large_objects = []

    # Проходим по всем объектам в бандле
    for obj in env.objects:
        try:
            # Пропускаем объекты, которые не содержат данных (например, контейнеры)
            if not hasattr(obj, "read"):
                continue

            data = obj.read()
            asset_name = f"asset_{obj.path_id}"
            size = get_object_size(obj)

            # Проверяем, превышает ли размер порог
            if size >= size_threshold:
                asset_dir = os.path.join(output_dir, obj.type.name.lower())
                os.makedirs(asset_dir, exist_ok=True)

                # Сохраняем данные в "сыром" виде
                raw_data_path = os.path.join(asset_dir, f"{asset_name}.raw")
                raw_data = obj.get_raw_data() if hasattr(obj, "get_raw_data") else data.get_raw_data()
                if raw_data:
                    with open(raw_data_path, "wb") as f:
                        f.write(raw_data)

                # Сохраняем метаданные объекта (для последующей упаковки)
                metadata_path = os.path.join(asset_dir, f"{asset_name}.meta")
                with open(metadata_path, "w") as f:
                    f.write(f"type: {obj.type.name}\n")
                    f.write(f"path_id: {obj.path_id}\n")
                    if data.name:
                        f.write(f"name: {data.name}\n")

                # Добавляем объект в список для удаления
                large_objects.append({
                    "name": asset_name,
                    "type": obj.type.name,
                    "path_id": obj.path_id,
                    "size": size
                })
                print(f"Распакован объект: {asset_name} ({obj.type.name}), размер: {size / 1024 / 1024:.2f} МБ")

        except Exception as e:
            print(f"Ошибка при распаковке {asset_name} ({obj.type.name}): {e}")

    print(f"Распаковка завершена. Файлы сохранены в: {output_dir}")
    return large_objects

def remove_objects_from_bundle(bundle_path: str, output_cleaned_bundle_path: str, objects_to_remove: List[Dict]):
    """
    Удаляет указанные объекты из бандла и сохраняет очищенный бандл.
    
    :param bundle_path: Путь к исходному UnityFS-бандлу
    :param output_cleaned_bundle_path: Путь для сохранения очищенного бандла
    :param objects_to_remove: Список объектов для удаления
    """
    if not os.path.exists(bundle_path):
        raise FileNotFoundError(f"Файл UnityFS-бандла не найден: {bundle_path}")

    # Загружаем UnityFS-бандл
    env = UnityPy.load(bundle_path)

    # Фильтруем объекты, которые нужно удалить
    objects = []
    for obj in env.objects:
        try:
            if not hasattr(obj, "read"):
                objects.append(obj)
                continue

            data = obj.read()
            asset_name = data.name if data.name else f"asset_{obj.path_id}"
            should_remove = False

            # Проверяем, нужно ли удалить объект
            for remove_criteria in objects_to_remove:
                if ("name" in remove_criteria and remove_criteria["name"] == asset_name and
                    "type" in remove_criteria and remove_criteria["type"] == obj.type.name and
                    "path_id" in remove_criteria and remove_criteria["path_id"] == obj.path_id):
                    should_remove = True
                    break

            if not should_remove:
                objects.append(obj)
            else:
                print(f"Удален объект: {asset_name} ({obj.type.name})")

        except Exception as e:
            print(f"Ошибка при обработке {asset_name} ({obj.type.name}): {e}")
            objects.append(obj)  # Сохраняем объект, если произошла ошибка

    # Создаем новый бандл без удаленных объектов
    env.objects = objects
    with open(output_cleaned_bundle_path, "wb") as f:
        f.write(env.file.save())

    print(f"Очищенный бандл сохранен в: {output_cleaned_bundle_path}")

def repack_unityfs_bundle(input_dir: str, output_bundle_path: str, cleaned_bundle_path: str):
    """
    Упаковывает данные из директории в UnityFS-бандл, используя очищенный бандл как основу.
    
    :param input_dir: Путь к директории с распакованными данными
    :param output_bundle_path: Путь для сохранения нового бандла
    :param cleaned_bundle_path: Путь к очищенному бандлу (без удаленных объектов)
    """
    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"Директория с данными не найдена: {input_dir}")

    if not os.path.exists(cleaned_bundle_path):
        raise FileNotFoundError(f"Очищенный бандл не найден: {cleaned_bundle_path}")

    # Загружаем очищенный бандл как основу
    env = UnityPy.load(cleaned_bundle_path)

    # Проходим по всем объектам в очищенном бандле
    for obj in env.objects:
        try:
            if not hasattr(obj, "read"):
                continue

            data = obj.read()
            asset_name = data.name if data.name else f"asset_{obj.path_id}"
            asset_dir = os.path.join(input_dir, obj.type.name.lower())
            raw_data_path = os.path.join(asset_dir, f"{asset_name}.raw")

            # Проверяем, есть ли данные для этого объекта
            if os.path.exists(raw_data_path):
                with open(raw_data_path, "rb") as f:
                    raw_data = f.read()
                # Заменяем "сырые" данные объекта
                if hasattr(obj, "set_raw_data"):
                    obj.set_raw_data(raw_data)
                else:
                    # Если прямой метод недоступен, используем обходной путь
                    data = obj.read()
                    data.set_raw_data(raw_data)
                    obj.save()
                print(f"Упакован объект: {asset_name} ({obj.type.name})")
            else:
                print(f"Предупреждение: данные для {asset_name} ({obj.type.name}) не найдены")

        except Exception as e:
            print(f"Ошибка при упаковке {asset_name} ({obj.type.name}): {e}")

    # Сохраняем новый бандл
    with open(output_bundle_path, "wb") as f:
        f.write(env.file.save())

    print(f"Упаковка завершена. Новый бандл сохранен в: {output_bundle_path}")

def repack_bundle_large_objects(bundle_path: str, temp_dir: str, output_bundle_path: str, size_threshold: int = 1024 * 1024):
    """
    Полный процесс репака: распаковка крупных объектов -> удаление их из бандла -> упаковка.
    
    :param bundle_path: Путь к исходному UnityFS-бандлу
    :param temp_dir: Временная директория для распаковки
    :param output_bundle_path: Путь для сохранения нового бандла
    :param size_threshold: Порог размера в байтах (по умолчанию 1 МБ)
    """
    # Распаковываем только крупные объекты
    large_objects = unpack_large_objects(bundle_path, temp_dir, size_threshold)

    # Создаем очищенный бандл (без крупных объектов)
    cleaned_bundle_path = os.path.join(temp_dir, "cleaned_bundle.bundle")
    remove_objects_from_bundle(bundle_path, cleaned_bundle_path, large_objects)

    # Упаковываем обратно
    repack_unityfs_bundle(temp_dir, output_bundle_path, cleaned_bundle_path)

    # Очищаем временную директорию
    shutil.rmtree(temp_dir)

# Пример использования
if __name__ == "__main__":
    bundle_path = "c:/Users/slava/projects/repack_tools/scripts/basemoonpool.prefab_ed691f4f40d4e4479b8a1e89b63064e7.bundle"
    temp_dir = "c:/Users/slava/projects/repack_tools/scripts/tmp"
    output_bundle_path = "c:/Users/slava/projects/repack_tools/scripts/2.bundle"

    # Устанавливаем порог размера в 1 МБ (можно изменить)
    size_threshold = 1024 * 1024  # 1 МБ

    repack_bundle_large_objects(bundle_path, temp_dir, output_bundle_path, size_threshold)