import Metashape
import os
import subprocess

# для работы установите в path exiftool.exe (https://exiftool.org/)
# Metashape version 2.0 or later

exif_tags = [
    "-filename",
    "-FocusDistance",
]

exif_columns = " ".join(exif_tags)


def export_raw_file(exif_columns: str, folder: str):
    focus_photo = {}    # словарь, где ключ - фокусное расстояние, значение - список фотографий 
    export_file = f'{folder}\\out.txt'

    find = f'exiftool -r {exif_columns} -T -n {folder} > {export_file}'
    subprocess.run(find, shell=True, capture_output=True, text=True)

    with open(export_file, 'r', encoding='utf-8') as f:
        for line in f:
            cleaned_line = line.strip()
            parts = cleaned_line.split('\t')

            if len(parts) < 2:
                continue    

            if parts[0] == 'out.txt':
                continue

            photo_name = parts[0]
            focus_value = parts[1]

            if focus_value not in focus_photo:
                focus_photo[focus_value] = []

            focus_photo[focus_value].append(photo_name)

    os.remove(f'{export_file}')
    return focus_photo


def main():
    doc = Metashape.app.document
    chunk = doc.chunk 


    for camera in chunk.cameras:
        image_path = camera.photo.path 
        folder_path = os.path.dirname(image_path) # путь для exiftool 


    result = export_raw_file(exif_columns, folder_path)  # результат словарь, где ключ - фокусное расстояние, значение - список фотографий 

    for k, v in result.items():
        print(f'focus {k}, count photos: {len(v)}')

    # Получаем словарь photo_to_focus, где ключ — имя фото, значение — фокус
    photo_to_focus = {}
    for focus_value, photo_list in result.items():
        for photo in photo_list:
            photo_to_focus[photo] = focus_value

    # словарь для хранения сенсоров по фокусным расстояниям
    focus_sensors = {}


    for camera in chunk.cameras:
        photo_name = os.path.basename(camera.photo.path)  # Получаем имя фото
        focus_value = photo_to_focus.get(photo_name)  # Получаем фокусное расстояние из словаря

        if focus_value:
            # Если сенсор для этого фокусного расстояния ещё не существует, создаём его
            if focus_value not in focus_sensors:
                # Создаём новый сенсор для этого фокуса
                new_sensor = chunk.addSensor()
                new_sensor.label = f"Focal {focus_value}"
                focus_sensors[focus_value] = new_sensor

                # Копируем параметры сенсора из исходного сенсора
                current_sensor = camera.sensor  # Исходный сенсор камеры
                if current_sensor:
                    # Копируем параметры 
                    new_sensor.pixel_size = current_sensor.pixel_size 
                    new_sensor.width = current_sensor.width
                    new_sensor.height = current_sensor.height
                    new_sensor.focal_length = current_sensor.focal_length
                    #new_sensor.resolution = current_sensor.resolution 
                    new_sensor.calibration = current_sensor.calibration

            # Назначаем камеру в соответствующий сенсор
            camera.sensor = focus_sensors[focus_value]

    #print(focus_sensors)


Metashape.app.addMenuItem("🛠 GIS scripts/FocusGroup [group_by_focus.py]", main)