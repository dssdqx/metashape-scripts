import Metashape
import os
from datetime import datetime


d_time_cut = 12  # пороговое значение времени в сек для группировки фото по миссиям

custom_cameras_time = {'ILX-LR1': 200, 'FC6310' : 200, 'FC6310R' : 20}


def group_by_time(photo_time: dict, chunk, time_cut):

    prev_time = None
    photo_time_diff = {}
    group = 1  
    photo_calibration_group = {}

    for photo, time in photo_time.items():
        if prev_time is None:
            photo_time_diff[photo] = 0  # для первого фото разница во времени будет 0
        else:
            time_diff = (time - prev_time).total_seconds()  # в секундах разница между datatime
            photo_time_diff[photo] = time_diff
        prev_time = time  # обновляем prev_time на текущее время

    # группируем фото по скачкам времени 
    for k, v in photo_time_diff.items():
        if v > time_cut:
            group += 1  # если разница во времени больше порога, новая группа
        photo_calibration_group[k] = group

    time_sensors = {} # группы калибровки 

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
    photo_time = {}   # фото и date time 
    model = set()

    for camera in chunk.cameras:
        if camera.photo: 
            photo = os.path.basename(camera.photo.path)
            date_time = camera.photo.meta["Exif/DateTime"]
            model.add(camera.photo.meta['Exif/Model'])
            if date_time:
                parsed_datetime = datetime.strptime(date_time, "%Y:%m:%d %H:%M:%S")
                photo_time[photo] = parsed_datetime
            else:
                print('error! EXIF does not contain meta Exif/DateTime\nexit')

    sorted_photo_time = dict(sorted(photo_time.items(), key=lambda x: x[1]))  # сортируем т.к. по умолчанию в мш сортировка по названию фото, буквы -> цифры и не учитывает время создания фото

    if len(model) == 1:
        camera = next(iter(model)) 
        time_cut = custom_cameras_time.get(camera, d_time_cut)  # берём значение для разбивки из словаря, если нет то берём по умолчанию 

    group_by_time(sorted_photo_time, chunk, time_cut)

Metashape.app.addMenuItem("🛠 GIS scripts/TimeGroup [group_by_time.py]", main)


