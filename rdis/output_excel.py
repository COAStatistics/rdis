import datetime
import json
import openpyxl
import os
from log import log
from openpyxl.utils import get_column_letter

SAMPLE_PATH = '..\\..\\input\\simple_sample.txt'
JSON_PATH = '..\\..\\output\\json\\公務資料.json'
FOLDER_PATH = '..\\..\\output\\'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+''
TYPE_FLAG = '主選'

if not os.path.isdir(FOLDER_PATH):
    os.mkdir(FOLDER_PATH)
# sorted by county
sample_dict = {}
official_data = {}

def read_official_data() -> None:
    with open(JSON_PATH, encoding='utf8') as f:
        global official_data
        official_data = json.loads(f.read())

def read_sample() -> None:
    with open(SAMPLE_PATH, encoding='utf8') as f:
        for line in f:
            sample = line.split('\t')
            county = sample[4]
            if county not in sample_dict:
                county_l = []
                county_l.append(sample)
                sample_dict[county] = county_l
            else:
                sample_dict.get(county).append(sample)


def output_excel(type_flag=TYPE_FLAG) -> None:
    for k, v in sample_dict.items():
        log.info('county : ' + k)
        if type_flag == '主選':
            v.sort(key=lambda x:x[5])
        else:
            v.sort(key=lambda x:x[8][-5:])
        wb = openpyxl.Workbook()
        col_index = 1
        row_index = 1
        county = k
        town = v[0][5]
        log.info('town : ' + town)
        sheet = wb.active
        sheet.title = town if type_flag == '主選' else 'sheet'+str(row_index+1)
        for person in v:
            log.info('person name : ' + person[1])
            farmer_num = person[8]
            sample_data = official_data.get(farmer_num)
            if type_flag == '主選' and town != person[5]:
                town = person[5]
                sheet = wb.create_sheet(town)
                row_index = 1
            if row_index-1 == 0:
                width = list(map(lambda x: x*1.054,[14.29, 9.29, 16.29, 37.29, 9.29, 11.29, 11.29, 11.29, 11.29]))
                for i in range(1, len(width)+1):
                    sheet.column_dimensions[get_column_letter(i)].width = width[i-1]
            titles = ['農戶編號', '調查姓名', '電話', '地址', '出生年', '原層別', '連結編號']
            for index, title in enumerate(titles):
                sheet.cell(column=index+1, row=row_index).value = title
            row_index += 1
            info = [
                farmer_num, sample_data.get('name'), sample_data.get('telephone'), sample_data.get('address'),
                sample_data.get('birthday'), sample_data.get('layer'), sample_data.get('serial')
            ]
            for index, value in enumerate(info):
                sheet.cell(column=index + 1, row=row_index).value = value
            row_index += 1
            sheet.cell(column=col_index, row=row_index).value = ' ========================== '
            row_index += 1
            titles = ['[戶籍檔]', '姓名', '出生年', '關係', '農保', '老農津貼', '國民年金', '勞保給付', '勞退給付', '農保給付']
            for index, title in enumerate(titles):
                sheet.cell(column=index + 1, row=row_index).value = title
            household = sample_data.get('household')
            household.sort(key=lambda x: x[1])

            for person in household:
                row_index += 1
                for index, p_data in enumerate(person):
                    if index == 9:
                        break
                    sheet.cell(column=index + 2, row=row_index).value = p_data
            
        wb.save(FOLDER_PATH + '\\' + k + '.xlsx')
read_official_data()
read_sample()
output_excel()