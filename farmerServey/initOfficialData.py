'''
Created on 2018年6月29日

@author: so6370
'''
import xlrd
import re

monthly_employee_dict = {}
insurance_data = {}
all_samples = []
households = {}

def load_monthly_employee():
    sample_list = [line.strip().split('\t') for line in open('..\\..\\input\\106_MonthlyEmployee.txt', 'r', encoding='utf8')]
    global monthly_employee_dict; monthly_employee_dict = {sample[0].strip() : sample for sample in sample_list} #Key is farmer id

def load_insurance():
    wb = xlrd.open_workbook('..\\..\\input\\insurance.xlsx')
    sheet = wb.sheet_by_index(0)
    distinct_dict = {}
    
    for i in range(1, sheet.nrows):
        row = sheet.row_values(i)
        farm_id = row[0]
        id_type = farm_id + '-' + row[1]
        
        if not id_type in distinct_dict:
            value = int(row[2])
            insurance_type = int(row[1])
            
            if insurance_type == 60 or insurance_type == 66:
                add_insurance(farm_id, value, 0)
            
            else:
                distinct_dict[id_type] = value * 12
                add_insurance(farm_id, value * 12, 0)
    
#     for e in distinct_dict:
#         print(e, ':', distinct_dict[e])
    del distinct_dict
    
    annuity = [45, 48, 35, 36, 37, 38, 55, 56, 57, 59]
    sheet = wb.sheet_by_index(1)
    count, prev_id, prev_value = 0, '', 0
    
    for i in range(1, sheet.nrows):
        row = sheet.row_values(i)
        farm_id = row[0]
        insurance_type = int(row[1])
        value = int(row[2])
        
        if prev_id == '':   prev_id = farm_id
    
        if insurance_type in annuity:
            pay = value
            count += 1
            
            if not farm_id == prev_id:
                prev_id = farm_id
                prev_value = value
                pay = prev_value * (13 - count)
                count = 0
            
            add_insurance(farm_id, pay, 1)
            
        else:
            add_insurance(farm_id, value, 1)
    
    sheet = wb.sheet_by_index(2)
    for i in range(1, sheet.nrows):
        row = sheet.row_values(i)
        farm_id = row[0]
        value = int(row[2])
        add_insurance(farm_id, value, 2)
        
    sheet = wb.sheet_by_index(3)
    for i in range(1, sheet.nrows):
        row = sheet.row_values(i)
        farm_id = row[0]
        value = int(row[2])
        add_insurance(farm_id, value, 3)

def add_insurance(k, v, i):
    if k in insurance_data:
        insurance_data.get(k)[i] += v
    
    else:
        value_list = [0] * 4
        value_list[i] = v
        insurance_data[k] = value_list

def data_calssify():
    #有效身分證之樣本
    samples_dict = load_samples()
    
    #樣本與戶籍對照 dict
    #key: 樣本之身分證字號, value: 樣本之戶號
    comparison_dict = {}
    
    for coa_data in open('..\\..\\input\\coa_d03_10611.txt', 'r', encoding='utf8'):
        person_info = coa_data.strip().split(',')
        
        #以戶號判斷是否存在, 存在則新增資料, 否則新增一戶
        if person_info[4] in households:
            if not person_info[11] == 1 and person_info[12].strip() == '':
                households.get(person_info[4]).append(person_info)
        else:
            person = []
            person.append(person_info)
            households[person_info[4]] = person
        
        #樣本身份證對應到戶籍資料就存到對照 dict
        if samples_dict.get(person_info[1]) != None:
            comparison_dict[person_info[1]] = person_info[4]
            
    build_official_data(comparison_dict)
    
def load_samples():
    global all_samples
    all_samples = [l.replace(u'\u3000', '').strip().split('\t') for l in open('..\\..\\input\\sample.txt', 'r', encoding='utf8')]
    samples_dict = {}
    samples_dict = {l[7].strip():l for l in all_samples if l[7].strip() not in samples_dict and re.match('^[A-Z][12][0-9]{8}$', l[7].strip())}
    return samples_dict

def build_official_data(comparison_dict):
    ...

# load_monthly_employee()
# load_insurance()
data_calssify()
