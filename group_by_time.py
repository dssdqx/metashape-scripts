import Metashape
import os
import math
from datetime import datetime


d_time_cut = 12  # пороговое значение времени в сек для группировки фото по умолчанию 

custom_cameras_time = {'ILX-LR1': 200, 'FC6310' : 200, 'FC6310R' : 20}


def prepare_diff(photo_time: dict):
    sorted_photo_time = dict(sorted(photo_time.items(), key=lambda x: x[1]))  # сортируем т.к. по умолчанию в мш сортировка по названию фото, буквы -> цифры и не учитывает время создания фото
    prev_time = None
    photo_diff = {}

    for photo, time in sorted_photo_time.items():
        if prev_time is None:
            photo_diff[photo] = 0  # для первого фото разница во времени будет 0
        else:
            time_diff = (time - prev_time).total_seconds()  # в секундах разница между datatime
            photo_diff[photo] = time_diff
        prev_time = time  # обновляем prev_time на текущее время

    return photo_diff


def statistic_time(data: list):
    mean = round(sum(data) / len(data),1)
    variance = sum((x - mean) ** 2 for x in data) / len(data)
    stddev = math.sqrt(variance)
    print(f'severance time MEAN: {mean}, stddev: {stddev}')

def divide(photo_time_diff: dict, chunk, time_cut: int, original_psz_cal: dict):

    group_counter = {}
    photo_cal_group = {} # фото - калибровка с сохранением исходной
    time_sensors = {}  

    for photo, time in photo_time_diff.items():
        original_value = original_psz_cal.get(photo)

        if original_value not in group_counter: # Если группа еще не была инициализирована, начинаем с 1
            group_counter[original_value] = 1


        if time > time_cut and time != 0:
            group_counter[original_value] += 1


        group_value = f"{original_value}_{group_counter[original_value]}"  # для группы original_value добавляем номер
        photo_cal_group[photo] = group_value

        print(f'{photo} o_cal {original_value} diff {time} new group name {group_value}')

    # Назначаем камеры в соответствующие группы
    for camera in chunk.cameras:
        photo_name = os.path.basename(camera.photo.path)
        group_value = photo_cal_group.get(photo_name)

        if group_value not in time_sensors:
            new_sensor = chunk.addSensor()
            new_sensor.label = f"TimeMission{group_value}"
            time_sensors[group_value] = new_sensor

            current_sensor = camera.sensor
            if current_sensor:
                new_sensor.pixel_size = current_sensor.pixel_size
                new_sensor.width = current_sensor.width
                new_sensor.height = current_sensor.height
                new_sensor.focal_length = current_sensor.focal_length
                new_sensor.calibration = current_sensor.calibration

        camera.sensor = time_sensors[group_value]

    print(f'SAVED original calibration separation + grouped by time')

def group_by_time(photo_time_diff: dict, chunk, time_cut):

    group = 1  
    photo_calibration_group = {}
    
    # группируем фото по скачкам времени 
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
    for k,v in photo_time_diff.items():
        group = photo_calibration_group.get(k)
        diff = photo_time_diff.get(k)
        print(f'{k} {v} diff {diff} in {group} group/mission') 
    print('done!')


def main():
    doc = Metashape.app.document
    chunk = doc.chunk
    photo_time = {}   # фото и date time 
    model = set() # модель камеры
    original_psz_cal = {} # оригинальная калибровка, если есть
    count_original_cal = set()
    
    for camera in chunk.cameras:
        if camera.photo:  # Проверяем, есть ли фото в чанке и exif
            photo = os.path.basename(camera.photo.path)
            date_time = camera.photo.meta["Exif/DateTime"]
            model.add(camera.photo.meta['Exif/Model'])

            original_psz_cal[photo] = camera.sensor.key
            count_original_cal.add(camera.sensor.key)

            if date_time:
                parsed_datetime = datetime.strptime(date_time, "%Y:%m:%d %H:%M:%S")
                photo_time[photo] = parsed_datetime
            else:
                print('error! EXIF does not contain meta Exif/DateTime\nexit')
                return
        else:
            return

    photo_time_diff = prepare_diff(photo_time)
    statistic_time(list(photo_time_diff.values())) # просто инфо не используется пока 

    if len(model) == 1:
        camera = next(iter(model)) # берём первое значение из множества
        global d_time_cut  # изменяем переменную глобально для норм вызова дальше в другой ветке 
        d_time_cut = custom_cameras_time.get(camera, d_time_cut)  # берём значение для разбивки из словаря, если нет то берём по умолчанию 

    if len(count_original_cal) > 1:
        print(f'there are {len(count_original_cal)} original calibration groups in project. we will SAVE them when grouping by time.\nIf not needed, just merge the groups in the calibration menu')
        divide(photo_time_diff, chunk, d_time_cut, original_psz_cal)

    else:
        group_by_time(photo_time_diff, chunk, d_time_cut)

Metashape.app.addMenuItem("🛠 GIS scripts/TimeGroup [group_by_time.py]", main)




#camera.sensor.key   - индикатор если были первоначальные группы в проекте, разные дроны или dewarping on\off