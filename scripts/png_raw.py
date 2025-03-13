import numpy as np
import os

# Директория с PNG-файлами
input_dir = 'path/to/png/files'
output_dir = 'path/to/output/files'

# Создаём выходную директорию, если её нет
os.makedirs(output_dir, exist_ok=True)

# Обрабатываем все PNG-файлы в директории
for filename in os.listdir(input_dir):
    if filename.endswith('.png'):
        # Открываем изображение
        image_path = os.path.join(input_dir, filename)
        image = Image.open(image_path)

        # Преобразуем изображение в массив NumPy
        pixel_array = np.array(image)

        # Сохраняем массив в файл .npy
        output_filename = os.path.splitext(filename)[0] + '.npy'
        output_path = os.path.join(output_dir, output_filename)
        np.save(output_path, pixel_array)


from PIL import Image
import numpy as np
import os

# Директория с файлами .npy
input_dir = 'path/to/output/files'
output_dir = 'path/to/restored/images'

# Создаём выходную директорию, если её нет
os.makedirs(output_dir, exist_ok=True)

# Обрабатываем все файлы .npy
for filename in os.listdir(input_dir):
    if filename.endswith('.npy'):
        # Загружаем массив из файла
        input_path = os.path.join(input_dir, filename)
        pixel_array = np.load(input_path)

        # Создаём изображение из массива
        image = Image.fromarray(pixel_array)

        # Сохраняем изображение
        output_filename = os.path.splitext(filename)[0] + '.png'
        output_path = os.path.join(output_dir, output_filename)
        image.save(output_path)

        print(f"Восстановлено: {output_path}")        