import Metashape
import os
from datetime import datetime


def group_by_time(photo_time: dict, chunk):

    prev_time = None
    photo_time_diff = {}

    time_cut = 9  # пороговое значение времени в сек для группировки фото

    group = 1  
    photo_calibration_group = {}

    for k, v in photo_time.items():
        current_time = datetime.combine(datetime.min, v)
        
        if prev_time is None:
            photo_time_diff[k] = 0  # для первого фото разница во времени будет 0
        else:
            time_diff = (current_time - prev_time).total_seconds()  # в сек разница кадров
            photo_time_diff[k] = time_diff
        prev_time = current_time

    # Группируем фото по времени
    for k, v in photo_time_diff.items():
        if v > time_cut:
            group += 1  # если разница во времени больше порога, новая группа
        photo_calibration_group[k] = group

    time_sensors = {} # группы калибровки тут будут

    for camera in chunk.cameras:
        photo_name = os.path.basename(camera.photo.path)  # имя фото
        group_value = photo_calibration_group.get(photo_name)  # получаем группу (что есть следующий скачок)  из словаря

        if group_value:
            # Если сенсор для этой группы по времени ещё не существует, создаём его
            if group_value not in time_sensors:
                # Создаём новый сенсор для этой группы
                new_sensor = chunk.addSensor()
                new_sensor.label = f"TimeMission{group_value}"
                time_sensors[group_value] = new_sensor

                current_sensor = camera.sensor  
                if current_sensor:
                    # ккопируем параметры фото
                    new_sensor.pixel_size = current_sensor.pixel_size 
                    new_sensor.width = current_sensor.width
                    new_sensor.height = current_sensor.height
                    new_sensor.focal_length = current_sensor.focal_length
                    new_sensor.calibration = current_sensor.calibration

            # назначаем камеру в соответствующий сенсор типа группы
            camera.sensor = time_sensors[group_value]

    print('working group_by_time...')# это чисто для проверки в консоли вывода далее
    for k,v in photo_time.items():
        group = photo_calibration_group.get(k)
        diff = photo_time_diff.get(k)
        print(f'{k} {v} diff {diff} in {group} group/mission')      


def main():
    doc = Metashape.app.document
    chunk = doc.chunk
    photo_time = {}   # фото и gps time 

    for camera in chunk.cameras:
        if camera.photo:  # Проверяем, есть ли фото у камеры
            photo = os.path.basename(camera.photo.path)
            gps_time = camera.photo.meta["Exif/GPSTime"]

            if gps_time == None:                                            # в EXIF камеры типа M4E нет тега GPSTime, версию я не понял как отлавливать 
                gps_time = camera.photo.meta["Exif/DateTime"]
                date_part, time_part = gps_time.split()
                parsed_time = datetime.strptime(time_part, "%H:%M:%S").time()
                photo_time[photo] = parsed_time

            else:
                parsed_time = datetime.strptime(gps_time, "%H:%M:%S").time()
                photo_time[photo] = parsed_time

    group_by_time(photo_time, chunk)


Metashape.app.addMenuItem("🛠 GIS scripts/TimeGroup [group_by_time.py]", main)