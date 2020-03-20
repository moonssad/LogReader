import os
import time
from datetime import datetime
from text import detect_decoding_errors_line
import re
import csv
import copy
import pandas as pd

detail_list = list()
detail_dict = dict()


def read_file(filename):
    global detail_list
    global detail_dict
    with open(filename, 'r', errors="surrogateescape") as f:
        try:
            for line in f:
                errors = detect_decoding_errors_line(line)
                if errors:
                    pass
                elif line.__contains__('RecorderPresenterImpl'):
                    # 语音结束', '识别结果', '结束时间', '识别时间', '时间差
                    if line.__contains__('RecorderPresenterImpl: 检测到语音结束点，正在进行识别处理,不需要再写入数据'):
                        pattern = "\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}.\d{1,3}"
                        result = re.search(pattern, line)
                        time = str_2_time(result[0])
                        detail_dict['start'] = 'start'
                        detail_dict['start_time'] = time
                    if line.__contains__('RecorderPresenterImpl: ---识别结果------'):
                        pattern = "\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}.\d{1,3}"
                        result = re.search(pattern, line)
                        time = str_2_time(result[0])
                        detail_dict['end'] = 'end'
                        detail_dict['end_time'] = time
                        if detail_dict.get('start_time') is not None:
                            time_difference = time - detail_dict.get('start_time')
                            detail_dict["time_difference"] = time_difference
                            deatail = copy.deepcopy(detail_dict)
                            detail_list.append(deatail)
                            detail_dict.clear()

        except UnicodeDecodeError:
            print('当前分母为0')


def str_2_time(str):
    real_time = "2020-{}".format(str)
    datetime_obj = datetime.strptime(real_time, "%Y-%m-%d %H:%M:%S.%f")
    obj_stamp = int(time.mktime(datetime_obj.timetuple()) * 1000.0 + datetime_obj.microsecond / 1000.0)
    return obj_stamp


#
def read_dir(rootdir):
    list = os.listdir(rootdir)  # 列出文件夹下所有的目录与文件
    for i in range(0, len(list)):
        path = os.path.join(rootdir, list[i])
        if os.path.isfile(path):
            read_file(path)
    add_2_csv(detail_list, 'tongji_all_3_20')
    # save_csv_pd(detail_list,'tongji_pd.csv')


def save_csv(data, filename):
    with open(filename + ".csv", 'w', encoding="utf-8") as f:
        headers = ['start', 'start_time', 'end', 'end_time', 'time_difference']
        writers = csv.DictWriter(f, headers)
        writers.writeheader()
        for date in data:
            print(date)
            writers.writerow(date)
        data.clear()

#文件追加模式里的数据。
def add_2_csv(data, filename):
    if os.path.exists(filename+'.csv'):
        with open(filename + ".csv", "a") as f:
            headers = ['start', 'start_time', 'end', 'end_time', 'time_difference']
            writer = csv.DictWriter(f,headers)
            for date in data:
                print(date)
                writer.writerow(date)
        data.clear()
    else :
        save_csv(data, filename)


def save_csv_pd(data, filename):
    pd.DataFrame(data).to_csv(filename)


read_dir("data/")
