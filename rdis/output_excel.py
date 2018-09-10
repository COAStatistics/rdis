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

# if not os.path.isdir(FOLDER_PATH):
#     os.mkdir(FOLDER_PATH)
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
            scholarship = ''
            sb = ''
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
                        scholarship += person[9]
                        continue
                    if index == 10 and person[10] not in sb:
                        sb += person[10]
                        break
                    sheet.cell(column=index + 2, row=row_index).value = p_data
            # 輸出申報核定資料，檢查是否有資料
            declaration = sample_data.get('declaration')
            if declaration != '':
                row_index += 1
                sheet.cell(column=1, row=row_index).value = '[申報核定]'
                sheet.cell(column=2, row=row_index).value = declaration
            # 輸出轉作補貼資料，檢查是否有資料
            crop_sbdy = sample_data.get('cropSbdy')
            if len(crop_sbdy) != 0:
                crop_d = {}
                for i in crop_sbdy:
                    crop_name = i[0]
                    amount = int(i[1])
                    if crop_name not in crop_d:
                        crop_d[crop_name] = amount
                    else:
                        crop_d[crop_name] = crop_d.get(crop_name) + amount
                row_index += 1
                item_index = 0
                titles = ['[轉作補貼]', '項目', '作物名稱', '金額', '期別']
                for index, title in enumerate(titles, start=1):
                    sheet.cell(column=index, row=row_index).value = title
                for k, v in crop_d.items():
                    row_index += 1
                    item_index += 1
                    sheet.cell(column=2, row=row_index).value = item_index
                    sheet.cell(column=3, row=row_index).value = k
                    sheet.cell(column=4, row=row_index).value = format(v, '8,d')
                    sheet.cell(column=5, row=row_index).value = '1'
            # 輸出災害補助資料，檢查是否有資料
            disaster = sample_data.get('disaster')
            if len(disaster) != 0:
                item_index = 0
                disaster_d = {}
                for i in disaster:
                    data = {}
                    disaster_name = i[0] + '-' + i[1]
                    area = float(i[2])
                    amount = int(i[3])
                    if disaster_name not in disaster_d:
                        data['area'] = area
                        data['amount'] = amount
                    else:
                        data = disaster_d.get(disaster_name)
                        data['area'] = data.get('area') + area
                        data['amount'] = data.get('amount') + amount
                    disaster_d[disaster_name] = data
                row_index += 1
                titles = ['[災害]', '項目', '災害', '核定作物', '核定面積', '金額']
                for index, title in enumerate(titles, start=1):
                    sheet.cell(column=index, row=row_index).value = title
                for k, v in disaster_d.items():
                    row_index += 1
                    item_index += 1
                    sheet.cell(column=2, row=row_index).value = item_index
                    l = k.split('-')
                    sheet.cell(column=3, row=row_index).value = l[0]
                    sheet.cell(column=4, row=row_index).value = l[1]
                    sheet.cell(column=5, row=row_index).value = v.get('area')
                    sheet.cell(column=6, row=row_index).value = format(v.get('amount'), '8,d')
            # 輸出小大補助資料，檢查是否有資料
            sb_sbdy = sample_data.get('sbSbdy')
            if len(sb_sbdy) != 0:
                row_index += 1
                titles = ['[105小大]', '姓名', '災害', '大專業農轉契作', '小地主出租給付', '離農獎勵']
                for index, title in enumerate(titles, start=1):
                    sheet.cell(column=index, row=row_index).value = title
                for i in sb_sbdy:
                    row_index += 1
                    for index, j in enumerate(i, start=1):
                        sheet.cell(column=index, row=row_index).value = j
                        
            # 輸出畜牧資料，檢查是否有資料
            livestock = sample_data.get('livestock')
#         wb.save(FOLDER_PATH + '\\' + k + '.xlsx')
read_official_data()
read_sample()
output_excel()