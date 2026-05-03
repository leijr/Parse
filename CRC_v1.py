
import os
import pandas as pd
import datetime

_CRC8_PROFILE1_TABLE = [
    0x00, 0x1D, 0x3A, 0x27, 0x74, 0x69, 0x4E, 0x53,
    0xE8, 0xF5, 0xD2, 0xCF, 0x9C, 0x81, 0xA6, 0xBB,
    0xCD, 0xD0, 0xF7, 0xEA, 0xB9, 0xA4, 0x83, 0x9E,
    0x25, 0x38, 0x1F, 0x02, 0x51, 0x4C, 0x6B, 0x76,
    0x87, 0x9A, 0xBD, 0xA0, 0xF3, 0xEE, 0xC9, 0xD4,
    0x6F, 0x72, 0x55, 0x48, 0x1B, 0x06, 0x21, 0x3C,
    0x4A, 0x57, 0x70, 0x6D, 0x3E, 0x23, 0x04, 0x19,
    0xA2, 0xBF, 0x98, 0x85, 0xD6, 0xCB, 0xEC, 0xF1,
    0x13, 0x0E, 0x29, 0x34, 0x67, 0x7A, 0x5D, 0x40,
    0xFB, 0xE6, 0xC1, 0xDC, 0x8F, 0x92, 0xB5, 0xA8,
    0xDE, 0xC3, 0xE4, 0xF9, 0xAA, 0xB7, 0x90, 0x8D,
    0x36, 0x2B, 0x0C, 0x11, 0x42, 0x5F, 0x78, 0x65,
    0x94, 0x89, 0xAE, 0xB3, 0xE0, 0xFD, 0xDA, 0xC7,
    0x7C, 0x61, 0x46, 0x5B, 0x08, 0x15, 0x32, 0x2F,
    0x59, 0x44, 0x63, 0x7E, 0x2D, 0x30, 0x17, 0x0A,
    0xB1, 0xAC, 0x8B, 0x96, 0xC5, 0xD8, 0xFF, 0xE2,
    0x26, 0x3B, 0x1C, 0x01, 0x52, 0x4F, 0x68, 0x75,
    0xCE, 0xD3, 0xF4, 0xE9, 0xBA, 0xA7, 0x80, 0x9D,
    0xEB, 0xF6, 0xD1, 0xCC, 0x9F, 0x82, 0xA5, 0xB8,
    0x03, 0x1E, 0x39, 0x24, 0x77, 0x6A, 0x4D, 0x50,
    0xA1, 0xBC, 0x9B, 0x86, 0xD5, 0xC8, 0xEF, 0xF2,
    0x49, 0x54, 0x73, 0x6E, 0x3D, 0x20, 0x07, 0x1A,
    0x6C, 0x71, 0x56, 0x4B, 0x18, 0x05, 0x22, 0x3F,
    0x84, 0x99, 0xBE, 0xA3, 0xF0, 0xED, 0xCA, 0xD7,
    0x35, 0x28, 0x0F, 0x12, 0x41, 0x5C, 0x7B, 0x66,
    0xDD, 0xC0, 0xE7, 0xFA, 0xA9, 0xB4, 0x93, 0x8E,
    0xF8, 0xE5, 0xC2, 0xDF, 0x8C, 0x91, 0xB6, 0xAB,
    0x10, 0x0D, 0x2A, 0x37, 0x64, 0x79, 0x5E, 0x43,
    0xB2, 0xAF, 0x88, 0x95, 0xC6, 0xDB, 0xFC, 0xE1,
    0x5A, 0x47, 0x60, 0x7D, 0x2E, 0x33, 0x14, 0x09,
    0x7F, 0x62, 0x45, 0x58, 0x0B, 0x16, 0x31, 0x2C,
    0x97, 0x8A, 0xAD, 0xB0, 0xE3, 0xFE, 0xD9, 0xC4,
]

_CRC16_PROFILE5_TABLE = [
    0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50a5, 0x60c6, 0x70e7,
    0x8108, 0x9129, 0xa14a, 0xb16b, 0xc18c, 0xd1ad, 0xe1ce, 0xf1ef,
    0x1231, 0x0210, 0x3273, 0x2252, 0x52b5, 0x4294, 0x72f7, 0x62d6,
    0x9339, 0x8318, 0xb37b, 0xa35a, 0xd3bd, 0xc39c, 0xf3ff, 0xe3de,
    0x2462, 0x3443, 0x0420, 0x1401, 0x64e6, 0x74c7, 0x44a4, 0x5485,
    0xa56a, 0xb54b, 0x8528, 0x9509, 0xe5ee, 0xf5cf, 0xc5ac, 0xd58d,
    0x3653, 0x2672, 0x1611, 0x0630, 0x76d7, 0x66f6, 0x5695, 0x46b4,
    0xb75b, 0xa77a, 0x9719, 0x8738, 0xf7df, 0xe7fe, 0xd79d, 0xc7bc,
    0x48c4, 0x58e5, 0x6886, 0x78a7, 0x0840, 0x1861, 0x2802, 0x3823,
    0xc9cc, 0xd9ed, 0xe98e, 0xf9af, 0x8948, 0x9969, 0xa90a, 0xb92b,
    0x5af5, 0x4ad4, 0x7ab7, 0x6a96, 0x1a71, 0x0a50, 0x3a33, 0x2a12,
    0xdbfd, 0xcbdc, 0xfbbf, 0xeb9e, 0x9b79, 0x8b58, 0xbb3b, 0xab1a,
    0x6ca6, 0x7c87, 0x4ce4, 0x5cc5, 0x2c22, 0x3c03, 0x0c60, 0x1c41,
    0xedae, 0xfd8f, 0xcdec, 0xddcd, 0xad2a, 0xbd0b, 0x8d68, 0x9d49,
    0x7e97, 0x6eb6, 0x5ed5, 0x4ef4, 0x3e13, 0x2e32, 0x1e51, 0x0e70,
    0xff9f, 0xefbe, 0xdfdd, 0xcffc, 0xbf1b, 0xaf3a, 0x9f59, 0x8f78,
    0x9188, 0x81a9, 0xb1ca, 0xa1eb, 0xd10c, 0xc12d, 0xf14e, 0xe16f,
    0x1080, 0x00a1, 0x30c2, 0x20e3, 0x5004, 0x4025, 0x7046, 0x6067,
    0x83b9, 0x9398, 0xa3fb, 0xb3da, 0xc33d, 0xd31c, 0xe37f, 0xf35e,
    0x02b1, 0x1290, 0x22f3, 0x32d2, 0x4235, 0x5214, 0x6277, 0x7256,
    0xb5ea, 0xa5cb, 0x95a8, 0x8589, 0xf56e, 0xe54f, 0xd52c, 0xc50d,
    0x34e2, 0x24c3, 0x14a0, 0x0481, 0x7466, 0x6447, 0x5424, 0x4405,
    0xa7db, 0xb7fa, 0x8799, 0x97b8, 0xe75f, 0xf77e, 0xc71d, 0xd73c,
    0x26d3, 0x36f2, 0x0691, 0x16b0, 0x6657, 0x7676, 0x4615, 0x5634,
    0xd94c, 0xc96d, 0xf90e, 0xe92f, 0x99c8, 0x89e9, 0xb98a, 0xa9ab,
    0x5844, 0x4865, 0x7806, 0x6827, 0x18c0, 0x08e1, 0x3882, 0x28a3,
    0xcb7d, 0xdb5c, 0xeb3f, 0xfb1e, 0x8bf9, 0x9bd8, 0xabbb, 0xbb9a,
    0x4a75, 0x5a54, 0x6a37, 0x7a16, 0x0af1, 0x1ad0, 0x2ab3, 0x3a92,
    0xfd2e, 0xed0f, 0xdd6c, 0xcd4d, 0xbdaa, 0xad8b, 0x9de8, 0x8dc9,
    0x7c26, 0x6c07, 0x5c64, 0x4c45, 0x3ca2, 0x2c83, 0x1ce0, 0x0cc1,
    0xef1f, 0xff3e, 0xcf5d, 0xdf7c, 0xaf9b, 0xbfba, 0x8fd9, 0x9ff8,
    0x6e17, 0x7e36, 0x4e55, 0x5e74, 0x2e93, 0x3eb2, 0x0ed1, 0x1ef0,
]

# .\pyinstaller -F F:\11_PythonProject\03_FH\CRC_v1.py
# Mapping from CAN frame ID to data payload ID used in CRC16 Profile 5 calculation.
# Defined by the DCU communication matrix. When a CAN frame carries data,
# the CRC is calculated over the data payload identified by this mapped ID.
_CANID_DATAID_MAP: dict[str, str] = {
    '198': '322',
    '32c': '31A',
    '3b0': '332',
    '268': '11A',
    '160': '409',
    '180': '339',
    '188': '341',
    '338': '349',
    '3b8': '351',
    '3a2': '302',
    '370': '329',
    '170': '301',
    '360': '309',
    '179': '311',
    '171': '306',
    '362': '307',
    '332': '32d',
}


class CRC_calculation():

    id_list_dict = {} # 用于存放id的内容
    length_contents = []
    output_result_str = []  # 用于输出到弹框界面
    max_num_id = 100  # 累计200个 id周期：比如10ms*200= 2000ms =2s 相当于2s左右的数据量


    filename = None
    file_format = None

    def __init__(self, id_list, ascfilepath, cantype):
        self.id_list = id_list
        self.filepath = ascfilepath
        self.can_type_get = cantype

    def crc_data_procedure(self):

        self.id_list_dict = {}

        #根据id创建数据库
        for i in self.id_list:
            self.id_list_dict[i] = {'contents': [],
                                 'check_result': [],
                                 'result_str': []}

        # 1、打开asc文件并提取原始数据 --- canfd 64位数据; --- can 8位数据
        self.crc_data_get()
        # 2、计算crc
        self.crc_cal()
        # 3、保存asc文件
        self.save_csv()

        return self.output_result_str

    def crc_data_get(self):
        # can_type_get : 1代表CANFD-CRC16 Profile5 ；2代表can（CRC8-Profile1）
        self.filename = os.path.basename(self.filepath).replace(os.path.basename(self.filepath)[-4:], '')  # 获取文件名，并去掉后缀
        self.file_format = (self.filepath[-4:]).lower()  # 把数据格式名称转换成小写
        if self.file_format == '.asc':
            log_file = open(self.filepath, 'r')
            for line in log_file:
                line_replace = line.replace(' ', '')
                for i in range(0, len(line_replace)):
                    if line_replace[i:i + 2] == 'Rx':
                        if self.can_type_get == 1:           # 1代表CANFD-CRC16 Profile5
                            if line_replace[i+2:i+5].lower() in self.id_list_dict.keys():   # 判断读取的内容的ID是否在id_list里面
                                if len(self.id_list_dict[line_replace[i+2:i+5].lower()]['contents']) \
                                        < self.max_num_id:
                                    for j in range(0, len(line_replace)):
                                        if line_replace[j:j+3] == 'f64' and j-i < 25:
                                            self.id_list_dict[line_replace[i+2:i+5].lower()]['contents'].\
                                                append(line_replace[j+3:j+3+128])
                                            break
                                            # print(line_replace[j+3:j+3+128])
                                else:
                                    break
                        elif self.can_type_get == 2:      # 2代表can（CRC8-Profile1）
                            if line_replace[i-3:i].lower() in self.id_list_dict.keys():  # 判断读取的内容的ID是否在id_list里面
                                if len(self.id_list_dict[line_replace[i-3:i].lower()]['contents']) < self.max_num_id:
                                    self.id_list_dict[line_replace[i-3:i].lower()]['contents'].append(
                                        line_replace[i + 4:i + 4 + 16])
                                else:
                                    break
            print(self.id_list_dict)

    def crc_cal(self):
        self.output_result_str = []
        for key, value in self.id_list_dict.items():
            print(key)
            str_temp = []
            length = len(self.id_list_dict[key]['contents'])
            self.length_contents.append(length)
            if length == 0:
                self.output_result_str.append(key + ':ASC数据中没有此CANID数据')
            else:
                for i in range(length):
                    if self.can_type_get == 1:
                        check_temp = crc16_profile5(key, self.id_list_dict[key]['contents'][i])  # 根据算法计算得到的结果
                        self.id_list_dict[key]['check_result'].append(check_temp)
                        # CANFD格式的checksum在前面两个byte
                        if check_temp == self.id_list_dict[key]['contents'][i][:4].lower():
                            str_temp.append(1)
                            self.id_list_dict[key]['result_str'].append(1)
                        else:
                            str_temp.append(0)
                            self.id_list_dict[key]['result_str'].append(0)
                    elif self.can_type_get == 2:
                        check_temp = crc8_profile1(key, self.id_list_dict[key]['contents'][i])  # 根据算法计算得到的结果
                        self.id_list_dict[key]['check_result'].append(check_temp)
                        # print(check_temp)
                        # CAN的checksum在第7个（最后一个）byte
                        if check_temp == self.id_list_dict[key]['contents'][i][-2:].lower():
                            str_temp.append(1)
                            self.id_list_dict[key]['result_str'].append(1)
                        else:
                            str_temp.append(0)
                            self.id_list_dict[key]['result_str'].append(0)
                if 0 in str_temp:
                    self.output_result_str.append(key + ':校验错误!!!!!!!!!!')
                else:
                    self.output_result_str.append(key + ':校验正确')
                # msg = '          \n         '.join(self.output_result_str)

    def save_csv(self):
            ## 冗余长度判断 to be continue
            min_len = min(self.length_contents)
            if min_len < self.max_num_id:
                row = -1
                for key, value in self.id_list_dict.items():
                    row += 1
                    if self.length_contents[row] < self.max_num_id:
                        for i in range(self.max_num_id - self.length_contents[row]):
                            self.id_list_dict[key]['contents'].append(' ')
                            self.id_list_dict[key]['check_result'].append(' ')
                            self.id_list_dict[key]['result_str'].append(' ')
                    else:
                        continue

            csv_dict = {}
            for idx, id in enumerate(self.id_list_dict):
                # str_temp = self.id_list[idx]
                csv_dict[id + '_Data'] = self.id_list_dict[id]['contents']
                csv_dict[id + '_Calculation'] = self.id_list_dict[id]['check_result']
                csv_dict[id + '_Check_Result'] = self.id_list_dict[id]['result_str']

            dataframe = pd.DataFrame(csv_dict)
            file_root = os.getcwd()
            tool_nowday = str(datetime.datetime.now().year) + "_" + str(datetime.datetime.now().month) + "_" + str(
                datetime.datetime.now().day) + "_" + str(datetime.datetime.now().hour) + "_" + str(datetime.datetime.now().minute) +"_"
            csv_path = file_root + '/' + str(self.filename) + '_CRC_Calculation_' + str(tool_nowday) + '.csv'
            dataframe.to_csv(csv_path)

def crc8_profile1(id_input, data_input):
    """
    输入的id_input为字符串格式，data_input也为字符串格式
    example：id_input = ‘170’,  data-input = ‘01020304050607’
    return值为字符
    """
    id_input = int(id_input, 16)
    table = _CRC8_PROFILE1_TABLE
    crcTemp = 0xFF
    crcTemp ^= id_input & 0x00ff
    crcTemp = table[int(crcTemp)]
    crcTemp ^= ((id_input >> 8) & 0x00ff)
    crcTemp = table[int(crcTemp)]

    for i in range(7):
        data_input_temp = int(data_input[(2*i):(2*i+2)], 16)
        crcTemp ^= data_input_temp
        crcTemp = table[int(crcTemp)]
    crcTemp ^= 0xFF
    crcTemp = str(hex(crcTemp))
    if len(crcTemp) == 3:
        crcTemp = '0' + crcTemp[2:]
    else:
        crcTemp = crcTemp[2:]
    return crcTemp


def crc16_profile5(id_input, data_input):
    """
    输入的id_input为字符串格式，data_input也为字符串格式
    example：id_input = ‘170’,  data-input = ‘0102030405060708090000000000000000000000000000000~’
    return值为字符
    """
    table = _CRC16_PROFILE5_TABLE
    crcTemp = 0xFFFF
    for i in range(2, 56):
        data_input_temp = int(data_input[(2 * i):(2 * i + 2)], 16)
        crcTemp ^= (data_input_temp << 8)
        # print(hex(crcTemp))
        crcTemp = ((crcTemp << 8) & 0xFFFF) ^ table[int((crcTemp >> 8) & 0xFF)]
        # print(hex(crcTemp))
    data_id = _CANID_DATAID_MAP.get(id_input, id_input)
    data_id = int(data_id, 16)
    crcTemp ^= data_id << 8
    crcTemp = ((crcTemp << 8) & 0xFFFF) ^ table[(crcTemp >> 8) & 0xff]
    crcTemp ^= data_id & 0xFF00
    crcTemp = ((crcTemp << 8) & 0xFFFF) ^ table[(crcTemp >> 8) & 0xff]
    crcTemp ^= 0x0000
    crcTemp = str(hex(crcTemp))[2:]

    if len(crcTemp) < 4:
        gap = 4-len(crcTemp)
        temp = ''
        for i in range(gap):
            temp += '0'
        crcTemp = temp + crcTemp[:]
        crcTemp = crcTemp[-2:] + crcTemp[:2]
    else:
        crcTemp = crcTemp[-2:] + crcTemp[:2]
    # print(crcTemp)

    return crcTemp


