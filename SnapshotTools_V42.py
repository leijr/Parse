import os
from asammdf import MDF  # 用于处理MDF文件
import datetime
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

# .\pyinstaller -F F:\11_PythonProject\03_FH\SnapshotTools_V3.py

class SnapShot():

    def __init__(self, filePath_choosen, project_choosen, bigdata_choosen, signal_name):

        self.filename = None
        self.file_format = None
        self.cycle_num = 0
        self.uint_100points_num_total = 0,  # 所有100个点数据的总行数，初始化为0
        self.basic_para = {
            "gac_nidec":
            {"data_len": 213,
            "byte_num_per_frame": 32,
            "uint8_number": 9,  # uint8变量的个数
            "uint16_number": 25,  # uint16变量的个数
            "uint8_frame_num": 4,  # 每一个8位的变量占据的帧数
            "uint16_frame_num": 7,  # 每一个16位的变量占据的帧数
            "real32_frame_num": None,  # 每一个32位的变量占据的帧数
            "len_other": 6,  # 除了uint8和uint16之外的变量个数
            "len_all": 40,  # 所有变量的个数
            "len_uint": 34,  # uint8和uint16的变量个数},
             },
            "gac_lv":
            {"data_len": 744,
            "byte_num_per_frame": 8,
            "uint8_number": 5,  # uint8变量的个数
            "uint16_number": 3,  # uint16变量的个数
            "uint32_number": 12,  # uint32变量的个数
            "uint8_frame_num": 13,  # 每一个8位的变量占据的帧数
            "uint16_frame_num": 25,  # 每一个16位的变量占据的帧数
            "real32_frame_num": 50,  # 每一个32位的变量占据的帧数
            "len_other": 4,  # 2frames(uint16_pga411(reserved))+ 1frame(uint8_date) + 1frame(keyontime +keyontimer)
            "len_all": 24,  # 所有变量的个数
            "len_uint": 20,  # uint8和uint16和real32的变量个数
            },
            "gac_hv":
                {"data_len": 746,
                 "byte_num_per_frame": 8,
                 "uint8_number": 5,  # uint8变量的个数
                 "uint16_number": 3,  # uint16变量的个数
                 "uint32_number": 12,  # uint32变量的个数
                 "uint8_frame_num": 13,  # 每一个8位的变量占据的帧数
                 "uint16_frame_num": 25,  # 每一个16位的变量占据的帧数
                 "real32_frame_num": 50,  # 每一个32位的变量占据的帧数
                 "len_other": 2,  # 2frames(uint16_pga411(reserved))+ 4frame(uint16_pga3160)
                 "len_all": 22,  # 所有变量的个数
                 "len_uint": 20,  # uint8和uint16和real32的变量个数
                 },
            "gac_xof":
                {"data_len": 1464,
                 "byte_num_per_frame": 8,
                 "uint8_number": 14,  # uint8变量的个数
                 "uint16_number": 25,  # uint16变量的个数
                 "uint32_number": 13,  # uint32变量的个数
                 "uint8_frame_num": 13,  # 每一个8位的变量占据的帧数
                 "uint16_frame_num": 25,  # 每一个16位的变量占据的帧数
                 "real32_frame_num": 50,  # 每一个32位的变量占据的帧数
                 "len_other": 7,  # 2frames(uint16_pga411(reserved))+ 4frame(uint16_pga3160)
                 "len_all": 59,  # 所有变量的个数 所有变量的个数 所有变量的个数 distribution_osc_data的变量个数
                 "len_uint": 52,  # uint8和uint16和real32的变量个数
                 },

        }

        self.bigdata_list_str = ['DCU_FaultData_RC', 'DCU_stPWMEna', 'DCU_stMode', 'DCU_uLowVolt', 'DCU_FaultData_1Bit_1',
                            'DCU_FaultData_1Bit_2', 'DCU_FaultData_1Bit_3', 'DCU_FaultData_1Bit_4',
                            'DCU_FaultData_4Bit_1', 'DCU_stASCProt',
                            'DCU_agRotorPosn', 'DCU_stFaultFlag100us', 'DCU_PWMFreq', 'DCU_uDcVolt',
                            'DCU_iCurdFinalRef',
                            'DCU_iCurqFinalRef', 'DCU_iCurdFb', 'DCU_iCurqFb', 'DCU_iPhaCurU', 'DCU_iPhaCurV',
                            'DCU_iPhaCurW',
                            'DCU_uVoltdFinalRef', 'DCU_uVoltqFinalRef', 'DCU_iDcCur', 'DCU_ResFaultFlag', 'DCU_stTsc',
                            'DCU_IGBTSt_UT',
                            'DCU_IGBTSt_UB', 'DCU_IGBTSt_VT', 'DCU_IGBTSt_VB', 'DCU_IGBTSt_WT', 'DCU_IGBTSt_WB',
                            'DCU_FaultData_12Bit_1',
                            'DCU_FaultData_16Bit_1']
        self.bigdata_distribution = {key: [] for key in self.bigdata_list_str}

        # 从distribution里面挑选出你需要画图的变量序号
        self.plot_list_from_distribution = {
            "gac_nidec":
                [[[10], "转子位置"], [[2, 3], "控制器模式 | 低压电压"], [[18, 19, 20], "三相电流"],
                 [[0, 1, 9], "使能标志位"], [[14, 16], "d轴电流"], [[13, 23], "母线电压/V | 母线电流/A"],
                 [[15, 17], "q轴电流"], [[21, 22], "d、q轴电压"]],
            "gac_lv":
                [[[5], "转子位置"], [[3, 9], "控制器模式 | 低压电压"], [[14, 15, 16], "三相电流"],
                 [[0, 1, 2], "使能标志位"], [[10, 12], "d轴电流"], [[8, 19], "母线电压/V | 母线电流/A"],
                 [[11, 13], "q轴电流"], [[17, 18], "d、q轴电压"]],
            "gac_hv":
                [[[5], "转子位置"], [[3, 9], "控制器模式 | 低压电压"], [[14, 15, 16], "三相电流"],
                 [[0, 1, 2], "使能标志位"], [[10, 12], "d轴电流"], [[8, 19], "母线电压/V | 母线电流/A"],
                 [[11, 13], "q轴电流"], [[17, 18], "d、q轴电压"]],
            "gac_xof":
                [[[14], "转子位置"], [[3, 40], "控制器模式 | 低压电压"], [[45, 46, 47], "三相电流"],
                 [[0, 1, 2], "使能标志位"], [[41, 43], "d轴电流"], [[51, 50], "母线电压/V | 母线电流/A"],
                 [[42, 44], "q轴电流"], [[48, 49], "d、q轴电压"]],
        }

        # distribution_osc_data format: each signal is a list of 7 elements:
        #   [0] index      — signal index for iteration
        #   [1] data_list  — decoded sample values (populated at runtime)
        #   [2] name       — signal name string
        #   [3] frame_num  — number of CAN frames this signal spans
        #   [4] byte_size  — bytes per data point (1=uint8, 2=uint16, 4=real32)
        #   [5] offset     — start byte offset within the OSC data block
        #   [6] extra      — secondary offset / calibration layer indicator
        self.distribution_osc_data = {
            "gac_nidec":
                [
                    [0, [], 'debug5_stBigDataTrigger', self.basic_para["gac_nidec"]["uint8_frame_num"], 1, 0, 1],
                    [1, [], 'debug5_stPWMEna', self.basic_para["gac_nidec"]["uint8_frame_num"], 1, 0, 1],
                    [2, [], 'debug5_stMode', self.basic_para["gac_nidec"]["uint8_frame_num"], 1, 0, 1],
                    [3, [], 'debug5_uLowVolt', self.basic_para["gac_nidec"]["uint8_frame_num"], 1, 0, 0.1],
                    [4, [], 'debug5_FaultData_1Bit_1', self.basic_para["gac_nidec"]["uint8_frame_num"], 1, 0, 1],
                    [5, [], 'debug5_FaultData_1Bit_2', self.basic_para["gac_nidec"]["uint8_frame_num"], 1, 0, 1],
                    [6, [], 'debug5_FaultData_1Bit_3', self.basic_para["gac_nidec"]["uint8_frame_num"], 1, 0, 1],
                    [7, [], 'debug5_FaultData_1Bit_4', self.basic_para["gac_nidec"]["uint8_frame_num"], 1, 0, 1],
                    [8, [], 'debug5_FaultData_4Bit_1', self.basic_para["gac_nidec"]["uint8_frame_num"], 1, 0, 1],
                    [9, [], 'debug5_stASCDuty', self.basic_para["gac_nidec"]["uint16_frame_num"], 2, 0, 1],
                    [10, [], 'debug5_agRotorPosn', self.basic_para["gac_nidec"]["uint16_frame_num"], 2, 0, 1],
                    [11, [], 'debug5_stFaultFlag100us', self.basic_para["gac_nidec"]["uint16_frame_num"], 2, 0, 1],
                    [12, [], 'debug5_PWMFreq', self.basic_para["gac_nidec"]["uint16_frame_num"], 2, 0, 1],
                    [13, [], 'debug5_uDcVolt', self.basic_para["gac_nidec"]["uint16_frame_num"], 2, 0, 1],
                    [14, [], 'debug5_iCurdFinalRef', self.basic_para["gac_nidec"]["uint16_frame_num"], 2, -2048, 1],
                    [15, [], 'debug5_iCurqFinalRef', self.basic_para["gac_nidec"]["uint16_frame_num"], 2, -2048, 1],
                    [16, [], 'debug5_iCurdFb', self.basic_para["gac_nidec"]["uint16_frame_num"], 2, -2048, 1],
                    [17, [], 'debug5_iCurqFb', self.basic_para["gac_nidec"]["uint16_frame_num"], 2, -2048, 1],
                    [18, [], 'debug5_iPhaCurU', self.basic_para["gac_nidec"]["uint16_frame_num"], 2, -2048, 1],
                    [19, [], 'debug5_iPhaCurV', self.basic_para["gac_nidec"]["uint16_frame_num"], 2, -2048, 1],
                    [20, [], 'debug5_iPhaCurW', self.basic_para["gac_nidec"]["uint16_frame_num"], 2, -2048, 1],
                    [21, [], 'debug5_uVoltdFinalRef', self.basic_para["gac_nidec"]["uint16_frame_num"], 2, -2048, 1],
                    [22, [], 'debug5_uVoltqFinalRef', self.basic_para["gac_nidec"]["uint16_frame_num"], 2, -2048, 1],
                    [23, [], 'debug5_iDcCur', self.basic_para["gac_nidec"]["uint16_frame_num"], 2, -2048, 1],
                    [24, [], 'debug5_ResFaultFlag', self.basic_para["gac_nidec"]["uint16_frame_num"], 2, 0, 1],
                    [25, [], 'debug5_stTsc', self.basic_para["gac_nidec"]["uint16_frame_num"], 2, 0, 1],
                    [26, [], 'debug5_IGBTSt_UT', self.basic_para["gac_nidec"]["uint16_frame_num"], 2, 0, 1],
                    [27, [], 'debug5_IGBTSt_UB', self.basic_para["gac_nidec"]["uint16_frame_num"], 2, 0, 1],
                    [28, [], 'debug5_IGBTSt_VT', self.basic_para["gac_nidec"]["uint16_frame_num"], 2, 0, 1],
                    [29, [], 'debug5_IGBTSt_VB', self.basic_para["gac_nidec"]["uint16_frame_num"], 2, 0, 1],
                    [30, [], 'debug5_IGBTSt_WT', self.basic_para["gac_nidec"]["uint16_frame_num"], 2, 0, 1],
                    [31, [], 'debug5_IGBTSt_WB', self.basic_para["gac_nidec"]["uint16_frame_num"], 2, 0, 1],
                    [32, [], 'debug5_FaultData_12Bit_1', self.basic_para["gac_nidec"]["uint16_frame_num"], 2, 0, 1],
                    [33, [], 'debug5_FaultData_16Bit_1', self.basic_para["gac_nidec"]["uint16_frame_num"], 2, 0, 1],
                    [34, [], 'uint16_ResolverFault', 7, 2, 0, 0],
                    [35, [], 'uint16_UpperDrvChipFault', 6, 2, 14, 0],
                    [36, [], 'uint16_BottomDrvChipFault', 6, 2, 26, 0],
                    [37, [], 'uint8_date', 6, 1, 6, 1],
                    [38, [], 'uint32_KeyOnTime', 1, 4, 12, 1],
                    [39, [], 'uint32_KeyOnNumber', 1, 4, 16, 1],
                ],
            "gac_lv":
                [
                    [0, [], 'debug5_sthandletoturnoff', self.basic_para["gac_lv"]["uint8_frame_num"], 1, 0, 1],
                    [1, [], 'debug5_stPWMEna', self.basic_para["gac_lv"]["uint8_frame_num"], 1, 0, 1],
                    [2, [], 'debug5_stASCProt', self.basic_para["gac_lv"]["uint8_frame_num"], 1, 0, 1],
                    [3, [], 'debug5_ms_stMode', self.basic_para["gac_lv"]["uint8_frame_num"], 1, 0, 1],
                    [4, [], 'debug5_sthandletoturnoff1', self.basic_para["gac_lv"]["uint8_frame_num"], 1, 0, 1],
                    [5, [], 'debug5_agRotorPosn', self.basic_para["gac_lv"]["uint16_frame_num"], 2, 0, 1],
                    [6, [], 'debug5_stFaultFlag100us', self.basic_para["gac_lv"]["uint16_frame_num"], 2, 0, 1],
                    [7, [], 'debug5_PWMFreq', self.basic_para["gac_lv"]["uint16_frame_num"], 2, 0, 1],
                    [8, [], 'debug5_uDcVolt', self.basic_para["gac_lv"]["real32_frame_num"], 4, 0, 1],
                    [9, [], 'debug5_uLowVolt', self.basic_para["gac_lv"]["real32_frame_num"], 4, 0, 0.1],
                    [10, [], 'debug5_iCurdFinalRef', self.basic_para["gac_lv"]["real32_frame_num"], 4, -2048, 1],
                    [11, [], 'debug5_iCurqFinalRef', self.basic_para["gac_lv"]["real32_frame_num"], 4, -2048, 1],
                    [12, [], 'debug5_iCurdFb', self.basic_para["gac_lv"]["real32_frame_num"], 4, -2048, 1],
                    [13, [], 'debug5_iCurqFb', self.basic_para["gac_lv"]["real32_frame_num"], 4, -2048, 1],
                    [14, [], 'debug5_iPhaCurU', self.basic_para["gac_lv"]["real32_frame_num"], 4, -2048, 1],
                    [15, [], 'debug5_iPhaCurV', self.basic_para["gac_lv"]["real32_frame_num"], 4, -2048, 1],
                    [16, [], 'debug5_iPhaCurW', self.basic_para["gac_lv"]["real32_frame_num"], 4, -2048, 1],
                    [17, [], 'debug5_uVoltdFinalRef', self.basic_para["gac_lv"]["real32_frame_num"], 4, -2048, 1],
                    [18, [], 'debug5_uVoltqFinalRef', self.basic_para["gac_lv"]["real32_frame_num"], 4, -2048, 1],
                    [19, [], 'debug5_iDcCur', self.basic_para["gac_lv"]["real32_frame_num"], 4, -2048, 1],
                    [20, [], 'uint16_reserved_pga411', 8, 2, 0, 0],  # 8代表8个数据，2代表一个数据2个字节，0代表从第0个字节开始，0代表不需要第740行后的第0行
                    [21, [], 'uint8_date', 6, 1, 0, 2], # 6代表6个数据，1代表一个数据1个字节uint8，0代表从第0个字节开始，0代表不需要第740行后的第2行
                    [22, [], 'uint32_KeyOnTime', 1, 4, 0, 3],
                    [23, [], 'uint32_KeyOnNumber', 1, 4, 4, 3],
                ],
            "gac_hv":
                [
                    [0, [], 'debug5_sthandletoturnoff', self.basic_para["gac_hv"]["uint8_frame_num"], 1, 0, 1],
                    [1, [], 'debug5_stPWMEna', self.basic_para["gac_hv"]["uint8_frame_num"], 1, 0, 1],
                    [2, [], 'debug5_stASCProt', self.basic_para["gac_hv"]["uint8_frame_num"], 1, 0, 1],
                    [3, [], 'debug5_ms_stMode', self.basic_para["gac_hv"]["uint8_frame_num"], 1, 0, 1],
                    [4, [], 'debug5_sthandletoturnoff1', self.basic_para["gac_hv"]["uint8_frame_num"], 1, 0, 1],
                    [5, [], 'debug5_agRotorPosn', self.basic_para["gac_hv"]["uint16_frame_num"], 2, 0, 1],
                    [6, [], 'debug5_stFaultFlag100us', self.basic_para["gac_hv"]["uint16_frame_num"], 2, 0, 1],
                    [7, [], 'debug5_PWMFreq', self.basic_para["gac_hv"]["uint16_frame_num"], 2, 0, 1],
                    [8, [], 'debug5_uDcVolt', self.basic_para["gac_hv"]["real32_frame_num"], 4, 0, 1],
                    [9, [], 'debug5_uLowVolt', self.basic_para["gac_hv"]["real32_frame_num"], 4, 0, 0.1],
                    [10, [], 'debug5_iCurdFinalRef', self.basic_para["gac_hv"]["real32_frame_num"], 4, -2048, 1],
                    [11, [], 'debug5_iCurqFinalRef', self.basic_para["gac_hv"]["real32_frame_num"], 4, -2048, 1],
                    [12, [], 'debug5_iCurdFb', self.basic_para["gac_hv"]["real32_frame_num"], 4, -2048, 1],
                    [13, [], 'debug5_iCurqFb', self.basic_para["gac_hv"]["real32_frame_num"], 4, -2048, 1],
                    [14, [], 'debug5_iPhaCurU', self.basic_para["gac_hv"]["real32_frame_num"], 4, -2048, 1],
                    [15, [], 'debug5_iPhaCurV', self.basic_para["gac_hv"]["real32_frame_num"], 4, -2048, 1],
                    [16, [], 'debug5_iPhaCurW', self.basic_para["gac_hv"]["real32_frame_num"], 4, -2048, 1],
                    [17, [], 'debug5_uVoltdFinalRef', self.basic_para["gac_hv"]["real32_frame_num"], 4, -2048, 1],
                    [18, [], 'debug5_uVoltqFinalRef', self.basic_para["gac_hv"]["real32_frame_num"], 4, -2048, 1],
                    [19, [], 'debug5_iDcCur', self.basic_para["gac_hv"]["real32_frame_num"], 4, -2048, 1],
                    [20, [], 'uint16_reserved_pga411', 8, 2, 0, 0],
                    [21, [], 'uint16_3160', 16, 2, 0, 2],
                ],
            "gac_xof":
                [
                    [0, [], 'debug5_sthandletoturnoff', self.basic_para["gac_hv"]["uint8_frame_num"], 1, 0, 1],
                    [1, [], 'debug5_stPWMEna', self.basic_para["gac_hv"]["uint8_frame_num"], 1, 0, 1],
                    [2, [], 'debug5_stASC', self.basic_para["gac_hv"]["uint8_frame_num"], 1, 0, 1],
                    [3, [], 'debug5_ms_stMode', self.basic_para["gac_hv"]["uint8_frame_num"], 1, 0, 1],
                    [4, [], 'debug5_stDrvCtrlMode', self.basic_para["gac_hv"]["uint8_frame_num"], 1, 0, 1],
                    [5, [], 'debug5_id_stDrvOverVoltFault', self.basic_para["gac_hv"]["uint8_frame_num"], 1, 0, 1],
                    [6, [], 'debug5_id_stDrvOverCutFault', self.basic_para["gac_hv"]["uint8_frame_num"], 1, 0, 1],
                    [7, [], 'debug5_od_stOverVoltSWHandle', self.basic_para["gac_hv"]["uint8_frame_num"], 1, 0, 1],
                    [8, [], 'debug5_od_stOverCurSWHandle', self.basic_para["gac_hv"]["uint8_frame_num"], 1, 0, 1],
                    [9, [], 'debug5_stDrvUpICFault', self.basic_para["gac_hv"]["uint8_frame_num"], 1, 0, 1],
                    [10, [], 'debug5_stDrvBomICFault', self.basic_para["gac_hv"]["uint8_frame_num"], 1, 0, 1],
                    [11, [], 'debug5_stDrvUpIC_RDY_Fault', self.basic_para["gac_hv"]["uint8_frame_num"], 1, 0, 1],
                    [12, [], 'debug5_stDrvBomIC_RDY_Fault', self.basic_para["gac_hv"]["uint8_frame_num"], 1, 0, 1],
                    [13, [], 'debug5_TC277_PHASH_AscFeedBackStateVar', self.basic_para["gac_hv"]["uint8_frame_num"], 1, 0, 1],


                    [14, [], 'debug5_agRotorPosn', self.basic_para["gac_hv"]["uint16_frame_num"], 2, 0, 1],
                    [15, [], 'debug5_stFaultFlag100us', self.basic_para["gac_hv"]["uint16_frame_num"], 2, 0, 1],
                    [16, [], 'debug5_PWMFreq', self.basic_para["gac_hv"]["uint16_frame_num"], 2, 0, 1],
                    [17, [], 'debug5_id_tiTspwmExeTime10ns', self.basic_para["gac_hv"]["uint16_frame_num"], 2, 0, 1],
                    [18, [], 'debug5_stASCDuty', self.basic_para["gac_hv"]["uint16_frame_num"], 2, 0, 1],
                    [19, [], 'debug5_uDcVolt', self.basic_para["gac_hv"]["uint16_frame_num"], 2, 0, 1],
                    [20, [], 'debug5_iPhaCurUArray[0]', self.basic_para["gac_hv"]["uint16_frame_num"], 2, 0, 1],
                    [21, [], 'debug5_iPhaCurVArray[0]', self.basic_para["gac_hv"]["uint16_frame_num"], 2, 0, 1],
                    [22, [], 'debug5_iPhaCurWArray[0]', self.basic_para["gac_hv"]["uint16_frame_num"], 2, 0, 1],
                    [23, [], 'debug5_uVRDC', self.basic_para["gac_hv"]["uint16_frame_num"], 2, 0, 1],
                    [24, [], 'debug5_tiPWMDutyPhaUTFront', self.basic_para["gac_hv"]["uint16_frame_num"], 2, 0, 1],
                    [25, [], 'debug5_tiPWMDutyPhaUTBack', self.basic_para["gac_hv"]["uint16_frame_num"], 2, 0, 1],
                    [26, [], 'debug5_tiPWMDutyPhaUBFront', self.basic_para["gac_hv"]["uint16_frame_num"], 2, 0, 1],
                    [27, [], 'debug5_tiPWMDutyPhaUBBack', self.basic_para["gac_hv"]["uint16_frame_num"], 2, 0, 1],
                    [28, [], 'debug5_tiPWMDutyPhaVTFront', self.basic_para["gac_hv"]["uint16_frame_num"], 2, 0, 1],
                    [29, [], 'debug5_tiPWMDutyPhaVTBack', self.basic_para["gac_hv"]["uint16_frame_num"], 2, 0, 1],
                    [30, [], 'debug5_tiPWMDutyPhaVBFront', self.basic_para["gac_hv"]["uint16_frame_num"], 2, 0, 1],
                    [31, [], 'debug5_tiPWMDutyPhaVBBack', self.basic_para["gac_hv"]["uint16_frame_num"], 2, 0, 1],
                    [32, [], 'debug5_tiPWMDutyPhaWTFront', self.basic_para["gac_hv"]["uint16_frame_num"], 2, 0, 1],
                    [33, [], 'debug5_tiPWMDutyPhaWTBack', self.basic_para["gac_hv"]["uint16_frame_num"], 2, 0, 1],
                    [34, [], 'debug5_tiPWMDutyPhaWBFront', self.basic_para["gac_hv"]["uint16_frame_num"], 2, 0, 1],
                    [35, [], 'debug5_tiPWMDutyPhaWBBack', self.basic_para["gac_hv"]["uint16_frame_num"], 2, 0, 1],
                    [36, [], 'debug5_tiPWMDutyPhaUOffFront', self.basic_para["gac_hv"]["uint16_frame_num"], 2, 0, 1],
                    [37, [], 'debug5_tiPWMDutyPhaVOffFront', self.basic_para["gac_hv"]["uint16_frame_num"], 2, 0, 1],
                    [38, [], 'debug5_tiPWMDutyPhaWOffFront', self.basic_para["gac_hv"]["uint16_frame_num"], 2, 0, 1],

                    [39, [], 'debug5_uDcVolt_woLPF', self.basic_para["gac_hv"]["real32_frame_num"], 4, 0, 1],
                    [40, [], 'debug5_uLowVolt', self.basic_para["gac_hv"]["real32_frame_num"], 4, 0, 0.1],
                    [41, [], 'debug5_iCurdFinalRef', self.basic_para["gac_hv"]["real32_frame_num"], 4, -2048, 1],
                    [42, [], 'debug5_iCurqFinalRef', self.basic_para["gac_hv"]["real32_frame_num"], 4, -2048, 1],
                    [43, [], 'debug5_iCurdFb', self.basic_para["gac_hv"]["real32_frame_num"], 4, -2048, 1],
                    [44, [], 'debug5_iCurqFb', self.basic_para["gac_hv"]["real32_frame_num"], 4, -2048, 1],
                    [45, [], 'debug5_iPhaCurU', self.basic_para["gac_hv"]["real32_frame_num"], 4, -2048, 1],
                    [46, [], 'debug5_iPhaCurV', self.basic_para["gac_hv"]["real32_frame_num"], 4, -2048, 1],
                    [47, [], 'debug5_iPhaCurW', self.basic_para["gac_hv"]["real32_frame_num"], 4, -2048, 1],
                    [48, [], 'debug5_uVoltdFinalRef', self.basic_para["gac_hv"]["real32_frame_num"], 4, -2048, 1],
                    [49, [], 'debug5_uVoltqFinalRef', self.basic_para["gac_hv"]["real32_frame_num"], 4, -2048, 1],
                    [50, [], 'debug5_iDcCur', self.basic_para["gac_hv"]["real32_frame_num"], 4, -2048, 1],
                    [51, [], 'debug5_uDc0Volt', self.basic_para["gac_hv"]["real32_frame_num"], 4, 0, 1],
                    [52, [], 'uint8_date', 6, 1, 0, 0],  # 6代表6个数据，1代表一个数据1个字节uint8，0代表从第0个字节开始，0代表不需要第740行后的第2行
                    [53, [], 'uint32_KeyOnTime', 1, 4, 6, 0],
                    [54, [], 'uint32_KeyOnNumber', 1, 4, 2, 1],
                    [55, [], 'uint8_StoreDataSt', 1, 1, 0, 2],
                    [56, [], 'uint8_SWOSCMode', 1, 1, 1, 2],
                    [57, [], 'uint16_driveBottom', 6, 2, 0, 3],
                    [58, [], 'uint16_driveUpper', 6, 2, 0, 5],
                ],
        }
        self.lost_frame = []  # 丢帧提示功能
        self.zero_num = []
        self.osc_data_list = []
        self.osc_data_rolling = []
        # 处理filepath_result
        self.filepath_result = filePath_choosen
        self.project_result = project_choosen
        self.bigdata_result = bigdata_choosen
        self.signal_name = signal_name

    def real32_to_dec(self, real32_data):
        sign = 1 if ((real32_data & 0x80000000) >> 31) == 0 else -1
        exponent = ((real32_data & 0x7F800000) >> 23) - 127
        mantissa = 1 + (real32_data & 0x007FFFFF) / (2 ** 23)
        real32_to_dec_value = sign * mantissa * 2 ** exponent
        return real32_to_dec_value

    def osc_data_procedure(self):
        # 处理filepath_result
        self.filename = os.path.basename(self.filepath_result).replace(os.path.basename(self.filepath_result)[-4:], '')  # 获取文件名，并去掉后缀
        self.file_format = (self.filepath_result[-4:]).lower()  # 把数据格式名称转换成小写
        #处理project_result
        project_type = ''
        if self.project_result[0] == True:  # gac-nidec项目被选中
            project_type = 'gac_nidec'
        if self.project_result[1] == True:  # gac-lv项目被选中
            project_type = 'gac_lv'
        if self.project_result[2] == True:  # gac-hv项目被选中
            project_type = 'gac_hv'
        if self.project_result[3] == True:
            project_type = 'gac_xof'
        # 1、提取osc数据
        osc_data_info = self.get_osc_data(project_type)
        print('len:' , len(self.osc_data_list))
        if osc_data_info == 'OK':
            # 2、如果osc数据丢帧，填充osc数据，填充数据为‘0’
            self.fill_zero(project_type)
            # 3、解析数据
            self.osc_data_parse(project_type)
            print("parse ok")
            # 保存asc数据
            self.data_to_excel_debug(project_type)
            # 画图
            self.data_to_plot(project_type)

        bigdata_info = ''
        # 处理bigdata_result
        if self.bigdata_result[1] == True:  # bigdata被选中了
            bigdata_info = self.get_bigdata()
            if bigdata_info == 'OK':
                self.data_to_excel_bigdata()
        return osc_data_info, bigdata_info

    def get_bigdata(self):
        try:
            log_file = MDF(self.filepath_result)
            for key_str in self.bigdata_distribution.keys():
                self.bigdata_distribution[key_str] = log_file.get(key_str).samples
                self.bigdata_distribution[key_str] = self.bigdata_distribution[key_str].tolist()  # 转换成list

            paragraphy_num = 0
            RC_vaule = log_file.get(list(self.bigdata_distribution.keys())[0]).samples # 获取RC信号的值的位置
            self.bigdata_distribution['段落符号'] = []
            for i in range(0, len(RC_vaule)):
                if RC_vaule[i] == 1:
                    paragraphy_num +=1
                    self.bigdata_distribution['段落符号'].append('第' + str(paragraphy_num) +'段数据')
                else:
                    self.bigdata_distribution['段落符号'].append(' ')
            # for idx, data in enumerate(insert_num):
            #     for key_str in self.bigdata_distribution.keys():
            #         # self.bigdata_distribution[key_str] = np.insert(self.bigdata_distribution[key_str], insert_num, '华丽的分隔符')
            #         # print(type(self.bigdata_distribution[key_str]))
            #         self.bigdata_distribution[key_str].insert(insert_num[idx] + idx, ' ')  # 在第i个RC信号的位置插入一个空字符用来区分)
            print(self.bigdata_distribution)
            bigdata_info = 'OK'
        except Exception as e:
            print(f'get_bigdata error: {e}')
            bigdata_info = 'NG'

        return bigdata_info

    def get_osc_data(self, project_type):
        try:
            log_file = MDF(self.filepath_result)
            if project_type == 'gac_nidec':
                # Nidec的信号名有DCU_OSC_Signal1.2.....33（1个rolling+ 32个valid-data）
                variable_1 = self.signal_name.replace("*", "1", 1)
                self.osc_data_rolling = log_file.get(variable_1).samples.tolist() #把numpy格式转化为list格式
                for i in range(0, len(self.osc_data_rolling)):
                    temp_string = ""
                    for j in range(2, 34):
                        variable_name = self.signal_name.replace("*", str(j), 1)
                        temp_data = hex(log_file.get(variable_name).samples[i])
                        if len(temp_data) == 3:  # 当获取到的数据为单位数时 比如0xF，需要补0
                            temp_data = '0' + temp_data[-1:]
                        elif len(temp_data) == 4:  # 当获取到的数据为双位数时 0xFF ，不需要在前面补0
                            temp_data = temp_data[-2:]
                        temp_string = temp_string + temp_data
                    self.osc_data_list.append(temp_string)
                print("len of osc_data_list",len(self.osc_data_list))
                osc_data_info = 'OK'
            else: # gac_lv和gac_hv的信号名有DCU_OSC_Signal1.2.....8
                variable_1 = self.signal_name.replace("*", "1", 1)
                length = len(log_file.get(variable_1).samples)
                for i in range(0, length):  # 通过DCU_OSC_Signal1获取实际的帧数
                    temp_string = ""
                    for j in range(1, 9):  # DCU_OSC_Signal1-8
                        variable_name = self.signal_name.replace("*", str(j), 1)
                        temp_data = hex(log_file.get(variable_name).samples[i])
                        if len(temp_data) == 3:
                            temp_data = '0' + temp_data[-1:]
                        elif len(temp_data) == 4:
                            temp_data = temp_data[-2:]
                        temp_string = temp_string + temp_data
                    self.osc_data_list.append(temp_string)
                osc_data_info = 'OK'
        except Exception as e:
            print(f'get_osc_data error: {e}')
            osc_data_info = 'NG'
        return osc_data_info

    def fill_zero(self, project_type):
        self.zero_num = []
        if project_type == 'gac_nidec':
            loop_count = 1
            print(len(self.osc_data_rolling))
            for index in range(0, len(self.osc_data_rolling) - 1):  # 把数据分段
                paragraph_rolling = int(self.osc_data_rolling[index + 1]) - int(
                    self.osc_data_rolling[index])  # 这里要把数据类型转化为int
                # print(paragraph_rolling)
                if paragraph_rolling < 0:  # 如果下一个值比上一个值小，把index作为上一段的结尾，把index +1 作为新段的开始
                    loop_count += 1  # 段落数自加1
            for j in range(loop_count):
                for i in range(self.basic_para[project_type]["data_len"] * j, self.basic_para[project_type]["data_len"] * (j + 1)):
                    try:
                        if self.osc_data_rolling[i] != i % self.basic_para[project_type]["data_len"]:
                            self.osc_data_rolling.insert(i, i % self.basic_para[project_type]["data_len"])
                            self.osc_data_list.insert(i, '0000000000000000000000000000000000000000000000000000000000000000')
                            self.zero_num.append(i)
                    except IndexError:  #超出界限（一般只会出现在尾部需要补0的情况）
                        self.osc_data_rolling.append(i % self.basic_para[project_type]["data_len"])
                        self.osc_data_list.append('0000000000000000000000000000000000000000000000000000000000000000')
                        self.zero_num.append(i)
        elif project_type == "gac_lv" or "gac_hv":
            if len(self.osc_data_list) < self.basic_para[project_type]["data_len"]:
                diff = self.basic_para[project_type]["data_len"] - len(self.osc_data_list)
            else:
                diff = len(self.osc_data_list) % self.basic_para[project_type]["data_len"]
            for i in range(0, diff):
                data_fill = '0000000000000000'
                self.osc_data_list.append(data_fill)


    def osc_data_parse(self, project_type):
        self.cycle_num = int(len(self.osc_data_list) / self.basic_para[project_type]["data_len"])
        print(len(self.osc_data_list), self.basic_para[project_type]["data_len"], self.cycle_num)
        if self.cycle_num >= 20:  # 限定外发数据的个数， 个数太多会卡死
            self.cycle_num = 20
        print(self.cycle_num, 'cycle')
        for c_num in range(0, self.cycle_num):
            print(c_num)
            cyc_num = c_num * self.basic_para[project_type]["data_len"]
            print(cyc_num)
            # 以下是对uint8和uint16以及其他uint的数据解析
            loop_count = cyc_num
            for counter in range(0, self.basic_para[project_type]["len_uint"]):
                self.value_get(project_type, self.zero_num, loop_count, 0, 100,
                               self.distribution_osc_data[project_type][counter][4], counter)
                loop_count += self.distribution_osc_data[project_type][counter][3]
                self.uint_100points_num_total = loop_count
                print(loop_count)
                print(self.distribution_osc_data[project_type][counter][1][c_num * 100: (c_num + 1) * 100],
                      type(self.distribution_osc_data[project_type][counter][1][1]))
                # while len(self.basic_para[project_type]_distribution_osc_data[counter][1]) != (int(c_num) + 1) * 100:
                #     self.basic_para[project_type]_distribution_osc_data[counter][1].append(' ')
            print("parsing for unit part Done")
            # 以下是对其他剩余帧的数据解析
            for counter in range(0, self.basic_para[project_type]["len_other"]):
                counter += self.basic_para[project_type]["len_uint"]
                print(counter)
                self.value_get(project_type, self.zero_num,
                               self.uint_100points_num_total + self.distribution_osc_data[project_type][counter][6],
                               self.distribution_osc_data[project_type][counter][5],
                               self.distribution_osc_data[project_type][counter][3],
                               self.distribution_osc_data[project_type][counter][4], counter)

                while len(self.distribution_osc_data[project_type][counter][1]) != (int(c_num) + 1) * 100:
                    self.distribution_osc_data[project_type][counter][1].append(' ')
                print(self.distribution_osc_data[project_type][counter][1][c_num * 100:(c_num + 1) * 100])
            print('parsing for other data Done')
            print(self.lost_frame)
            if project_type == 'gac_nidec':
                # 补充丢帧lost_frame的SignalName到100个数据，为了兼容pdFrame函数, （只针对第1个byte是rolling值的项目）
                while len(self.lost_frame) != (int(c_num) + 1) * 100:
                    self.lost_frame.append(' ')

        if project_type == 'gac_nidec':
            # 偏置和offset处理  只针对nidec的项目（为了配合大数据外发）
            for counter in range(0, self.basic_para[project_type]["len_uint"]):
                self.distribution_osc_data[project_type][counter][1] = [
                    (self.distribution_osc_data[project_type][counter][5]
                         + item *
                        self.distribution_osc_data[project_type][counter][6])
                        for item in
                        self.distribution_osc_data[project_type][counter][1]]
        else:
                # 对real32的数据类型要进行转换
            for counter in range(0, self.basic_para[project_type]["len_uint"]):
                if self.distribution_osc_data[project_type][counter][4] == 4:
                    self.distribution_osc_data[project_type][counter][1] = [
                        self.real32_to_dec(int(item)) for item in
                        self.distribution_osc_data[project_type][counter][1]]



    def value_get(self, project_type, zero_line, loopCounter_start, start_byte, data_len, data_type, key_index):
        '''loop_counter_end end_byte 分别代表该信号最后一个数据的所在帧数序列和byte序列 比如 第50帧 第23byte
        start_byte 从0开始
        data_len指的是一个信号名的数据长度，比如iPhaCurU的数据长度为100个，最后几帧的数据长度比如ResolverFault长度为7等'''
        byte_total = loopCounter_start * self.basic_para[project_type][
            "byte_num_per_frame"] + start_byte + data_len * data_type
        loopCounter_end = byte_total // self.basic_para[project_type]["byte_num_per_frame"]
        end_byte = byte_total % self.basic_para[project_type]["byte_num_per_frame"]
        diff = loopCounter_end - loopCounter_start

        temp_for_data = '' #用来保存一个信号的所有数据放在这里
        for i in range(loopCounter_start, loopCounter_end + 1):
            if project_type == "gac_nidec": # 只针对有rolling值的项目
                # newly added 20220801 for lost frame mark
                for xxx in zero_line:
                    if xxx == i:
                        self.lost_frame.append(self.distribution_osc_data[project_type][key_index][2])
                # newly added 20220801 for lost frame  mark
            if diff == 0:  # 没有跨帧
                # self.abstract_data(project_type, start_byte, data_len, data_type, i, key_index)
                temp_for_data += (self.osc_data_list[i][start_byte*2:(end_byte+1)*2-1]) # 这里是因为一个byte实际上是两个字符
            elif diff >= 1:  # 有跨帧
                print(loopCounter_start, loopCounter_end)
                if loopCounter_start < i < loopCounter_end:  # 中间帧
                    end_byte_temp = self.basic_para[project_type]["byte_num_per_frame"] # 中间帧全部取出来
                    temp_for_data += (self.osc_data_list[i][0:(end_byte_temp+1)*2-1]) # 这里是因为一个byte实际上是两个字符
                    # self.abstract_data(project_type, 0, self.basic_para[project_type]["byte_num_per_frame"] // data_type, data_type, i, key_index)
                else:  # 首尾帧
                    if i == loopCounter_start:
                        end_byte_temp = self.basic_para[project_type]["byte_num_per_frame"]
                        temp_for_data += (self.osc_data_list[i][start_byte*2:(end_byte_temp+1)*2-1]) # 首帧抽取规则: From start byte To 该帧最后一个数据
                        # self.abstract_data(project_type, start_byte, (self.basic_para[project_type]["byte_num_per_frame"] - start_byte) // data_type,
                        #                    data_type, i, key_index)
                    elif i == loopCounter_end:
                        # print(end_byte, data_type, key_index)
                        end_byte_temp = end_byte
                        temp_for_data += (self.osc_data_list[i][0:(end_byte_temp+1)*2-1])
                        # self.abstract_data(project_type, 0, end_byte // data_type, data_type, i, key_index)
        # 将上面获取到的数据处理
        # 将上面获取到的数据处理
        print(temp_for_data)
        self.parse_data(project_type, temp_for_data, data_type, data_len, key_index)

    def parse_data(self, project_type, temp_for_data, data_type, data_len, key_index):
        for j in range(0, data_len):
            hex_data = ''
            for k in range(data_type, 0, -1):
                hex_data += temp_for_data[2 * (data_type * j + k - 1):2 * (data_type * j + k)]
            data = int(('0x' + hex_data), 16)
            self.distribution_osc_data[project_type][key_index][1].append(data)



    def data_to_excel_debug(self, project_type):
        '''此段代码用于保存excel文件'''

        excel_dict = {}
        for i in range(0, self.basic_para[project_type]["len_all"]):
            excel_dict[self.distribution_osc_data[project_type][i][2]] = self.distribution_osc_data[project_type][i][1]
        if project_type == 'gac_nidec': # 只针对有rolling值的项目
            excel_dict['lost_frame_Signal_Name'] = self.lost_frame

        dataframe = pd.DataFrame(excel_dict)
        file_root = os.getcwd()
        tool_nowday = str(datetime.datetime.now().year) + "_" + str(datetime.datetime.now().month) + "_" + str(
            datetime.datetime.now().day) + "_" + str(datetime.datetime.now().hour) + "_" + str(
            datetime.datetime.now().minute) + "_"
        excel_path = file_root + '/' + str(self.filename) + '_SnapshotData_' + project_type + '_' + str(tool_nowday) + '.xlsx'
        dataframe.to_excel(excel_path)


    def data_to_excel_bigdata(self):
        '''此段代码用于保存excel文件'''
        excel_dict = {}
        for idx, key_str in enumerate(self.bigdata_distribution.keys()):
            excel_dict[key_str] = self.bigdata_distribution[key_str]


        dataframe = pd.DataFrame(excel_dict)
        file_root = os.getcwd()
        tool_nowday = str(datetime.datetime.now().year) + "_" + str(datetime.datetime.now().month) + "_" + str(
            datetime.datetime.now().day) + "_" + str(datetime.datetime.now().hour) + "_" + str(
            datetime.datetime.now().minute) + "_"
        csv_path = file_root + '/' + str(self.filename) + '_Bigdata_Nidec' + str(tool_nowday) + '.xlsx'
        dataframe.to_excel(csv_path)


    def data_to_plot(self, project_type):
        # 解决matplotlib无法显示中文问题
        font = {'family': 'MicroSoft YaHei',
                'weight': '6',
                'size': '10'}
        mpl.rc('font', **font)
        tool_nowday = str(datetime.datetime.now().year) + "_" + str(datetime.datetime.now().month) + "_" + str(
            datetime.datetime.now().day)
        # cyc_num = 0
        # if c_type == 'canfd_nidec':
        #     # cyc_num = int(len(self.osc_data_list) / self.canfd_nidec_data_len)

        for index in range(0, self.cycle_num):
            plt.figure(figsize=(12, 6.5))
            plt.suptitle(' " ' + str(self.filename) + ' " ' + '_SnapshotData_' + str(tool_nowday) + '-第' +
                         str(index+1) + '组快照数据' + '--共' + str(self.cycle_num) + '组快照数据', fontsize=14, x=0.5, y=0.95)
            for j in range(len(self.plot_list_from_distribution[project_type])):
                plt.subplot(4, 2, j+1)
                for k in range(len(self.plot_list_from_distribution[project_type][j][0])):
                    data_temp = self.plot_list_from_distribution[project_type][j][0][k]
                    if project_type == "gac_nidec" and self.distribution_osc_data[project_type][data_temp][2] in self.lost_frame[index * 100:(index + 1) * 100]:
                        linestyle = '-.'
                    else:
                        linestyle = '-'
                    plt.plot(self.distribution_osc_data[project_type][data_temp][1][index * 100:(index + 1) * 100],
                             label=self.distribution_osc_data[project_type][data_temp][2],
                             linestyle=linestyle)
                plt.ylabel(self.plot_list_from_distribution[project_type][j][1])
                plt.legend(loc='upper left')
                plt.grid()
        plt.show()



