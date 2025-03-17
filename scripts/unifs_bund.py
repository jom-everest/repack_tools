import os
import UnityPy
from pathlib import Path
from typing import Dict, Any

class UnityBundleBinaryRepacker:
    def __init__(self, bundle_path: str, output_dir: str):
        self.bundle_path = Path(bundle_path)
        self.output_dir = Path(output_dir)
        self.extracted_data_dir = self.output_dir / "extracted_binary_data"
        self.modified_bundle_path = self.output_dir / f"modified_{self.bundle_path.name}"
        self.restored_bundle_path = self.output_dir / f"restored_{self.bundle_path.name}"

    def ensure_directories(self) -> None:
        """Создает необходимые директории, если они не существуют."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.extracted_data_dir.mkdir(parents=True, exist_ok=True)

    def is_object_processable(self, obj: Any) -> bool:
        """Проверяет, можно ли обработать объект (извлечь и сохранить его бинарные данные)."""
        try:
            # Проверяем, что объект поддерживает чтение
            if not hasattr(obj, 'read'):
                return False
            
            # Читаем данные объекта
            data = obj.read()
            if data is None:
                return False
            
            # Проверяем наличие serialized_data (сырых бинарных данных)
            if not hasattr(obj, 'serialized_data') or obj.serialized_data is None:
                return False
            
            # Проверяем, что данные не пустые
            if len(obj.serialized_data) == 0:
                return False
            
            return True
        except Exception as e:
            print(f"Ошибка при проверке объекта {obj.type.name}: {e}")
            return False

    def extract_binary_data(self) -> None:
        """Извлекает бинарные данные из бандла и сохраняет их в файлы."""
        try:
            print(f"Извлечение бинарных данных из {self.bundle_path}...")
            env = UnityPy.load(str(self.bundle_path))

            for obj in env.objects:
                if not self.is_object_processable(obj):
                    print(f"Пропущен объект {obj.type.name} (невозможно обработать)")
                    continue

                # Читаем объект
                data = obj.read()
                obj_name = data.name or f"unnamed_{obj.type.name}_{obj.path_id}"
                obj_dir = self.extracted_data_dir / obj.type.name
                obj_dir.mkdir(parents=True, exist_ok=True)

                # Сохраняем сырые бинарные данные
                file_path = obj_dir / f"{obj_name}.bin"
                with open(file_path, "wb") as f:
                    f.write(obj.serialized_data)
                print(f"Извлечены бинарные данные: {obj.type.name}/{obj_name}")

        except Exception as e:
            print(f"Ошибка при извлечении бинарных данных: {e}")

    def remove_data_from_bundle(self) -> None:
        """Удаляет бинарные данные из бандла, сохраняя структуру."""
        try:
            print(f"Удаление бинарных данных из {self.bundle_path}...")
            env = UnityPy.load(str(self.bundle_path))

            for obj in env.objects:
                if not self.is_object_processable(obj):
                    print(f"Пропущен объект {obj.type.name} (невозможно удалить данные)")
                    continue

                # Очищаем бинарные данные
                obj.serialized_data = b""
                # Сохраняем изменения обратно в объект
                obj.save()
                print(f"Удалены данные из объекта: {obj.type.name}")

            # Сохраняем модифицированный бандл
            with open(self.modified_bundle_path, "wb") as f:
                f.write(env.file.save())
            print(f"Модифицированный бандл сохранен как {self.modified_bundle_path}")

        except Exception as e:
            print(f"Ошибка при удалении бинарных данных: {e}")

    def restore_data_to_bundle(self) -> None:
        """Восстанавливает бинарные данные в бандл из сохраненных файлов."""
        try:
            print(f"Восстановление бинарных данных в {self.modified_bundle_path}...")
            env = UnityPy.load(str(self.modified_bundle_path))

            for obj in env.objects:
                if not self.is_object_processable(obj):
                    print(f"Пропущен объект {obj.type.name} (невозможно восстановить данные)")
                    continue

                # Читаем объект
                data = obj.read()
                obj_name = data.name or f"unnamed_{obj.type.name}_{obj.path_id}"
                obj_dir = self.extracted_data_dir / obj.type.name

                # Путь к файлу с бинарными данными
                file_path = obj_dir / f"{obj_name}.bin"
                if file_path.exists():
                    with open(file_path, "rb") as f:
                        obj.serialized_data = f.read()
                    # Сохраняем изменения обратно в объект
                    obj.save()
                    print(f"Восстановлены бинарные данные: {obj.type.name}/{obj_name}")
                else:
                    print(f"Файл с данными не найден: {file_path}")

            # Сохраняем восстановленный бандл
            with open(self.restored_bundle_path, "wb") as f:
                f.write(env.file.save())
            print(f"Восстановленный бандл сохранен как {self.restored_bundle_path}")

        except Exception as e:
            print(f"Ошибка при восстановлении бинарных данных: {e}")

    def run(self) -> None:
        """Запускает полный процесс: извлечение, удаление, восстановление."""
        self.ensure_directories()
        self.extract_binary_data()
        self.remove_data_from_bundle()
        self.restore_data_to_bundle()

if __name__ == "__main__":
    # Пример использования
    bundle_path = "c:/Users/slava/projects/repack_tools/scripts/basemoonpool.prefab_ed691f4f40d4e4479b8a1e89b63064e7.bundle"
    output_dir = "output"  # Укажите директорию для вывода

    repacker = UnityBundleBinaryRepacker(bundle_path, output_dir)
    repacker.run()