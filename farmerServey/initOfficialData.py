'''
Created on 2018年6月29日

@author: so6370
'''
import xlrd
import re
from db_conn import DatabaseConnection

MON_EMP_PATH = '..\\..\\input\\106_MonthlyEmployee.txt'
INSURANCE_PATH = '..\\..\\input\\simple_insurance.xlsx'
COA_PATH = '..\\..\\input\\coa.txt'
SAMPLE_PATH = '..\\..\\input\\simple_sample.txt'
THIS_YEAR = 107

monthly_employee_dict = {}
insurance_data = {}
all_samples = []
households = {}

def load_monthly_employee():
    sample_list = [line.strip().split('\t') for line in open(MON_EMP_PATH, 'r', encoding='utf8')]
    global monthly_employee_dict; monthly_employee_dict = {sample[0].strip() : sample for sample in sample_list} #Key is farmer id

def load_insurance():
    wb = xlrd.open_workbook(INSURANCE_PATH)
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
    # 有效身分證之樣本
    samples_dict = load_samples()
    # 樣本與戶籍對照 dict
    # key: 樣本之身分證字號, value: 樣本之戶號
    comparison_dict = {}
    with open(COA_PATH, 'r', encoding='utf8') as f:
        for coa_data in f:
            person_info = coa_data.strip().split(',')
            pid = person_info[1]
            hhn = person_info[4]
            #以戶號判斷是否存在, 存在則新增資料, 否則新增一戶
            if hhn in households:
                if person_info[11] != '1' and person_info[12].strip() == '':
                    households.get(hhn).append(person_info)
            else:
                # 一戶所有的人
                persons = []
                persons.append(person_info)
                households[hhn] = persons
            #樣本身份證對應到戶籍資料就存到對照 dict
            if pid in samples_dict:
                comparison_dict[pid] = hhn
    build_official_data(comparison_dict)
    
def load_samples():
    global all_samples
    # 將 sample 檔裡所有的資料原封不動存到列表裡
    all_samples = [l.split('\t') for l in open(SAMPLE_PATH, encoding='utf8')]
    samples_dict = {}
    samples_dict = {l[7].strip():l for l in all_samples if l[7].strip() not in samples_dict and re.match('^[A-Z][12][0-9]{8}$', l[7].strip())}
    return samples_dict

def build_official_data(comparison_dict):
    db = DatabaseConnection('fallow')
    for sample in all_samples:
        name, address, birthday, farmer_id, farmer_num = '', '', '', '', ''
        # json 資料
        json_data = {}
        json_household = []
        json_sb_sbdy = []
        json_disaster = []
        json_declaration = ''
        json_crop_sbdy = []
        json_livestock = {}
        # sample 的 id
        farmer_id = sample[7].strip()
        farmer_num = sample[8].strip()
        if farmer_id in comparison_dict:
            household_num = comparison_dict.get(farmer_id)
            if household_num in households:
                # households.get(household_num) : 每戶 
                # person : 每戶的每個人
                for person in households.get(household_num):
                    pid = person[1]
                    person_name = person[2].strip()
                    if pid == sample[7]:
                        name = person[2].strip()
                        address = person[3]
                        birthday = str(int(person[3][:3]))
                    age = THIS_YEAR - int(person[3][:3])
                    DatabaseConnection.pid = pid
                    # 每年不一定會有 insurance 資料
                    json_data['insurance'] = insurance_data.get(farmer_id)
                    # json 裡的 household 對應一戶裡的所有個人資料
                    json_hh_person = [''] * 11
                    json_hh_person[0] = person_name
                    json_hh_person[1] = str(age)
                    # role
                    json_hh_person[2] = person[10]
                    # json_hh_person[5-8]
                    if pid in insurance_data:
                        for index, i in enumerate(insurance_data.get(person[1])):
                            if i > 0:
                                # ex 1234 -> 1,234
                                json_hh_person[index+5] = format(i, '8,d')
                    # 根據年齡來過濾是否訪問 db
                    if age >= 15:
                        json_hh_person[3] = db.get_farmer_insurance()
                        if age >= 65:
                            json_hh_person[4] = db.get_elder_allowance()
                        # 佃農18-55歲，地主至少18歲
                        if age >= 18:
                            json_hh_person[10] = db.get_landlord()
                            if age <= 55:
                                json_hh_person[10] += db.get_tenant_farmer()
                            subsidy = [
                                    person_name,
                                    db.get_tenant_transfer_subsidy(),
                                    db.get_landlord_rent(),
                                    db.get_landlord_retire()
                                ]
                            for i in subsidy[1:]:
                                if i != '0': json_sb_sbdy.append(subsidy); break
                            disaster = db.get_disaster()
                            if len(disaster) != 0:
                                json_disaster += disaster
                            declaration = db.get_declaration()
                            if declaration != 0 and declaration not in json_declaration:
                                json_declaration += declaration + ','
                            crop_sbdy = db.get_crop_subsidy()
                            if len(crop_sbdy) != 0:
                                json_crop_sbdy += crop_sbdy
                            livestock = db.get_livestock()
                            if len(livestock) != 0:
                                json_livestock.update(livestock)
                        if age >= 30:
                            json_hh_person[9] = db.get_scholarship()
                    json_household.append(json_hh_person)
load_monthly_employee()
load_insurance()
data_calssify()