import json
import xlrd
import re
import time
from collections import namedtuple
from collections import OrderedDict
from db_conn import DatabaseConnection
from log import log, err_log

MAIN = False
MON_EMP_PATH = '..\\..\\input\\106_MonthlyEmployee.txt'
# INSURANCE_PATH = '..\\..\\input\\simple_insurance.xlsx'
INSURANCE_PATH = '..\\..\\input\\107_insurance.xlsx'
# COA_PATH = '..\\..\\input\\107.txt'
COA_PATH = '..\\..\\input\\coa_d03_10711.txt'
# SAMPLE_PATH = '..\\..\\input\\easy.txt'
SAMPLE_PATH = '..\\..\\input\\main_107farmerSurvey.txt' if MAIN else '..\\..\\input\\sub_107farmerSurvey.txt'
OUTPUT_PATH = '..\\..\\output\\json\\公務資料.json' if MAIN else '..\\..\\output\\json\\公務資料_備選.json'
THIS_YEAR = 107
ANNOTATION_DICT = {'0': '', '1': '死亡', '2': '除戶'}
# defined namedtuple attribute
SAMPLE_ATTR = [
        'layer',
        'name',
        'tel',
        'addr',
        'county',
        'town',
        'link_num',
        'id',
        'num',
        'main_type',
        'area',
        'sample_num',
    ]
PERSON_ATTR = [
        'addr_code',
        'id',
#         'name',
        'birthday',
        'household_num',
#         'h_name',
        'addr',
        'role',
        'annotation',
        'h_type',
        'h_code',
    ]

# use namedtuple promote the readable and flexibility of code
Sample = namedtuple('Sample', SAMPLE_ATTR)
Person = namedtuple('Person', PERSON_ATTR)

monthly_employee_dict = {}
insurance_data = {}
# every element is a Sample obj
all_samples = []
households = {}
official_data = {}
sample_count = 0

def load_monthly_employee() -> None:
    sample_list = [line.strip().split('\t') for line in open(MON_EMP_PATH, 'r', encoding='utf8')]
    global monthly_employee_dict; monthly_employee_dict = {sample[0].strip() : sample[1:] for sample in sample_list} #Key is farmer id

def load_insurance() -> None:
    wb = xlrd.open_workbook(INSURANCE_PATH)
    sheet = wb.sheet_by_index(0)
    distinct_dict = {}
    
    # 國保給付
    for i in range(1, sheet.nrows):
        row = sheet.row_values(i)
        farm_id = row[0]
        id_type = farm_id + '-' + row[1]
        
        if id_type not in distinct_dict:
            value = int(row[3])
            insurance_type = int(row[1])
            
            if insurance_type == 60 or insurance_type == 66:
                add_insurance(farm_id, value, 0)
            else:
                mon_start = int(row[2][-2:])
                allance = value * (13-mon_start) 
                distinct_dict[id_type] = allance
                add_insurance(farm_id, allance, 0)
        
        else:
            value = int(row[3])
            insurance_type = int(row[1])
            if insurance_type == 60 or insurance_type == 66:
                add_insurance(farm_id, value, 0)
    
    distinct_dict.clear()
    
    # 勞保給付
    annuity = [45, 48, 35, 36, 37, 38, 55, 56, 57, 59]
    sheet = wb.sheet_by_index(1)
    
    for i in range(1, sheet.nrows):
        row = sheet.row_values(i)
        farm_id = row[0]
        id_type = farm_id + '-' + row[1]
        
        if id_type not in distinct_dict:
            value = int(row[3])
            insurance_type = int(row[1])
            
            if insurance_type not in annuity:
                add_insurance(farm_id, value, 1)
            else:
                mon_start = int(row[2][-2:])
                allance = value * (13-mon_start) 
                distinct_dict[id_type] = allance
                add_insurance(farm_id, allance, 1)
        
        else:
            value = int(row[3])
            insurance_type = int(row[1])
            if insurance_type not in annuity:
                add_insurance(farm_id, value, 1)
#     count, prev_id, prev_value = 0, '', 0
#     
#     for i in range(1, sheet.nrows):
#         row = sheet.row_values(i)
#         farm_id = row[0]
#         insurance_type = int(row[1])
#         value = int(row[2])
#         
#         if prev_id == '':
#             prev_id = farm_id
#     
#         if insurance_type in annuity:
#             pay = value
#             count += 1
#             
#             if not farm_id == prev_id:
#                 prev_id = farm_id
#                 prev_value = value
#                 pay = prev_value * (13 - count)
#                 count = 0
#             
#             add_insurance(farm_id, pay, 1)
#             
#         else:
#             add_insurance(farm_id, value, 1)
    
    # 勞退
    sheet = wb.sheet_by_index(2)
    for i in range(1, sheet.nrows):
        row = sheet.row_values(i)
        farm_id = row[0]
        value = int(row[2])
        add_insurance(farm_id, value, 2)
        
    # 農保給付
    sheet = wb.sheet_by_index(3)
    for i in range(1, sheet.nrows):
        row = sheet.row_values(i)
        farm_id = row[0]
        value = int(row[2])
        add_insurance(farm_id, value, 3)

def add_insurance(k, v, i) -> None:
    if k in insurance_data:
        insurance_data.get(k)[i] += v
    
    else:
        value_list = [0] * 4
        value_list[i] = v
        insurance_data[k] = value_list

def data_calssify() -> None:
    # 有效身分證之樣本
    samples_dict = load_samples()
    # 樣本與戶籍對照 dict
    # key: 樣本之身分證字號, value: 樣本之戶號
    comparison_dict = {}
    with open(COA_PATH, 'r', encoding='utf8') as f:
        for coa_data in f:
            # create Person object
            person = Person._make(coa_data.strip().split(','))
            pid = person.id
            hhn = person.household_num
            #以戶號判斷是否存在, 存在則新增資料, 否則新增一戶
            if hhn in households:
#                 if person_info[11] != '1' and person_info[12].strip() == '':
                    # 避免人重複
#                     if all((i.id.find(person.id) == -1) for i in households.get(hhn)):
                households.get(hhn).append(person)
            else:
                # 一戶所有的人
                persons = []
                persons.append(person)
                households[hhn] = persons
            #樣本身份證對應到戶籍資料就存到對照 dict
            if pid in samples_dict:
                comparison_dict[pid] = hhn
    build_official_data(comparison_dict)
    
def load_samples() -> dict:
    no_id_count = 0
    global all_samples
    # 將 sample 檔裡所有的資料原封不動存到列表裡
    all_samples = [Sample._make(l.split('\t')) for l in open(SAMPLE_PATH, encoding='utf8')]
    samples_dict = {}
    for s in all_samples:
        if s.id not in samples_dict and re.match('^[A-Z]{1}[1-2]{1}[0-9]{8}$', s.id):
            samples_dict[s.id] = s
        else:
            no_id_count += 1
            err_log.error(no_id_count, ', sample name = ', s.name, ', sample id = ', s.id)
    global sample_count; sample_count = len(all_samples)
    return samples_dict

def build_official_data(comparison_dict) -> None:
    no_hh_count = 0
    count = 0
    db = DatabaseConnection()
    person_key = ['birthday', 'role', 'annotation', 'farmer_insurance', 'elder_allowance', 'national_pension',
                  'labor_insurance', 'labor_pension', 'farmer_insurance_payment', 'scholarship', 'sb']
    #key dict: for readable
    k_d = {person_key[i]:i for i in range(len(person_key))}
    # every element is a Sample object
    for sample in all_samples:
        count += 1
        name, address, birthday, farmer_id, farmer_num = '', '', '', '', ''
        # json 資料
        json_data = OrderedDict()
        json_household = []
        json_sb_sbdy = []
        json_disaster = []
        json_declaration = ''
        json_crop_sbdy = []
        json_livestock = {}
        farmer_id = sample.id
        farmer_num = sample.num
        if farmer_id in comparison_dict:
            household_num = comparison_dict.get(farmer_id)
            if household_num in households:
                # households.get(household_num) : 每戶 
                # person : 每戶的每個人
                # person is a Person object
                for person in households.get(household_num):
                    pid = person.id
                    # json data 主要以 sample 的人當資料，所以要判斷戶內人是否為 sample
                    if pid == sample.id:
                        name = sample.name
                        address = sample.addr
                        # 民國年
                        birthday = str(int(person.birthday[:3]))
                    # 轉成實際年齡
                    age = THIS_YEAR - int(person.birthday[:3])
                    DatabaseConnection.pid = pid
                    # 每年不一定會有 insurance 資料
                    if farmer_id in insurance_data:
                        json_data['insurance'] = insurance_data.get(farmer_id)
                        
                    # json 裡的 household 對應一戶裡的所有個人資料
                    json_hh_person = [''] * 11
                    
                    json_hh_person[k_d['birthday']] = str(int(person.birthday[:3]))
                    json_hh_person[k_d['role']] = person.role
                    
                    if pid != sample.id:
                        json_hh_person[k_d['annotation']] = ANNOTATION_DICT.get(person.annotation)
                    if pid in insurance_data:
                        for index, i in enumerate(insurance_data.get(person.id)):
                            if i > 0:
                                # format : 1234 -> 1,234
                                if index == 0:
                                    json_hh_person[k_d['national_pension']] = format(i, '8,d')
                                if index == 1:
                                    json_hh_person[k_d['labor_insurance']] = format(i, '8,d')
                                if index == 2:
                                    json_hh_person[k_d['labor_pension']] = format(i, '8,d')
                                if index == 3:
                                    json_hh_person[k_d['farmer_insurance_payment']] = format(i, '8,d')
                                
                    # 根據年齡來過濾是否訪問 db
                    # 農保至少15歲
                    if age >= 15:
                        json_hh_person[k_d['farmer_insurance']] = db.get_farmer_insurance()
                        # 老農津貼至少65歲
                        if age >= 65:
                            json_hh_person[k_d['elder_allowance']] = db.get_elder_allowance()
                        # 佃農18-55歲，地主至少18歲
                        if age >= 18:
                            json_hh_person[k_d['sb']] = db.get_landlord()
                            if age <= 55:
                                json_hh_person[k_d['sb']] += db.get_tenant_farmer()
                            subsidy = [
                                    name,
                                    db.get_tenant_transfer_subsidy(),
                                    db.get_landlord_rent(),
                                    db.get_landlord_retire()
                                ]
                            if any((i != '0') for i in subsidy[1:]):
                                json_sb_sbdy.append(subsidy)
                                log.info(pid, ', sbSbdy = ', json_sb_sbdy)
                                
                            disaster = db.get_disaster()
                            if disaster:
                                json_disaster.extend(disaster)
                                log.info(pid, ', disaster = ', json_disaster)
                                
                            declaration = db.get_declaration()
                            if declaration and declaration not in json_declaration:
                                json_declaration += declaration + ','
                                assert len(json_declaration) != 0
                                log.info(pid, ', declaration = ', json_declaration)
                                
                            crop_sbdy = db.get_crop_subsidy()
                            if crop_sbdy:
                                json_crop_sbdy.extend(crop_sbdy)
                                log.info(pid, ', crop_sbdy = ', json_crop_sbdy)
                                
                            livestock = db.get_livestock()
                            if livestock:
                                json_livestock.update(livestock)
                                log.info(pid, ', livestock = ', json_livestock)
                                
                        # 獎學金申請人資格，申請對象至少15歲，故假設申請人30歲
                        if age >= 30:
                            json_hh_person[k_d['scholarship']] = db.get_scholarship()
                            
                    
                    json_household.append(json_hh_person)
        else:
            DatabaseConnection.pid = farmer_id
            address = sample.addr
            json_hh_person = [''] * 11
            json_household.append(json_hh_person)
            if sample.id:
                no_hh_count += 1
                err_log.error(no_hh_count, ', Not in household file. ', sample)
            
        # create json data
        json_data['name'] = sample.name
        json_data['address'] = address
        json_data['birthday'] = birthday
        json_data['farmerId'] = farmer_id
        json_data['telephone'] = sample.tel
        json_data['layer'] = sample.layer
        json_data['serial'] = farmer_num[-5:]
        json_data['household'] = json_household
        json_data['monEmp'] = monthly_employee_dict.get(farmer_num, [])
        json_data['declaration'] = json_declaration[:-1]
        json_data['cropSbdy'] = json_crop_sbdy
        json_data['disaster'] = json_disaster
        json_data['livestock'] = json_livestock
        json_data['sbSbdy'] = json_sb_sbdy
        official_data[farmer_num] = json_data
        print('%.2f%%' %(count/sample_count * 100))
    db.close_conn()
    output_josn(official_data)
    

def output_josn(data) -> None:
    with open(OUTPUT_PATH, 'w', encoding='utf8') as f:
        f.write(json.dumps(data,  ensure_ascii=False))
    print('complete', len(official_data), ' records')
    log.info(len(official_data), ' records')

# if __name__ == '__main__':
start_time = time.time()
#     load_monthly_employee()
load_insurance()
data_calssify()
m, s = divmod(time.time()-start_time, 60)
print(int(m), 'min', round(s, 1), 'sec')
log.info(int(m), ' min ', round(s, 1), ' sec')
    