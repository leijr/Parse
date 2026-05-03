import sys
import os
import platform
import SnapshotTools_V42
from PySide6.QtWidgets import QMessageBox
import ReadDBCNew_readlines
import CRC_v1
from DBC_EXCEL import DBCtoEXCEL
from DBC_CANIN_CANOUT import DBC_CANIN, DBC_CANOUT
import pandas as pd

# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////
from modules import *
from widgets import *
os.environ["QT_FONT_DPI"] = "96" # FIX Problem for High DPI and Scale above 100%

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.dbc_result = {}
        self.current_signal_lst = []
        self.current_id_lst = []
        self.current_result = {}
        self.filepath_asc = ''
        self.output_result = []

        self.dbc_result_caninout = {}
        self.ecu_tx_list = []
        self.fileName_dbc = ""
        self.fileName_canin = ""
        self.fileName_canout = ""
        self.canout_sheetname_list = []
        self.canin_sheetname_list = []


        # USE CUSTOM TITLE BAR | USE AS "False" FOR MAC OR LINUX
        # ///////////////////////////////////////////////////////////////
        Settings.ENABLE_CUSTOM_TITLE_BAR = True

        # APP NAME
        # ///////////////////////////////////////////////////////////////
        title = "DCUTestGroup - General-Tools"
        description = "Convenient Tools for DCU - SnapShot Tools & CRC Tools etc."
        # APPLY TEXTS
        self.setWindowTitle(title)
        self.ui.titleRightInfo.setText(description)

        # TOGGLE MENU
        # ///////////////////////////////////////////////////////////////
        self.ui.toggleButton.clicked.connect(lambda: UIFunctions.toggleMenu(self, True))

        # SET UI DEFINITIONS
        # ///////////////////////////////////////////////////////////////
        UIFunctions.uiDefinitions(self)

        # # QTableWidget PARAMETERS
        # # ///////////////////////////////////////////////////////////////
        # self.ui.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # BUTTONS CLICK
        # ///////////////////////////////////////////////////////////////

        # LEFT MENUS
        self.ui.btn_home.clicked.connect(self._switch_page)
        self.ui.btn_snapshot.clicked.connect(self._switch_page)
        self.ui.btn_crc.clicked.connect(self._switch_page)
        self.ui.btn_caninout.clicked.connect(self._switch_page)

        # SNAPSHOT TOOLS
        self.ui.pushButton_mdffile.clicked.connect(self.mdf_file)
        self.ui.pushButton_snapshot_start.clicked.connect(self.mdf_parse)

        # CRC TOOLS
        self.ui.dbc_btn.clicked.connect(self._on_dbc_file_select)
        self.ui.comboBox_canid.currentTextChanged.connect(self.canid_change)
        self.ui.pushButton_add.clicked.connect(self._on_add_signal)
        self.ui.pushButton_delete.clicked.connect(self._on_delete_signal)
        self.ui.pushButton_asc.clicked.connect(self._on_asc_file_select)
        self.ui.pushButton_start.clicked.connect(self._on_start_crc)

        # CAN INOUT TOOLS
        self.ui.btn_dbc_caninout.clicked.connect(self._on_dbc_caninout_select)
        self.ui.btn_canin_cainout.clicked.connect(self._on_canin_select)
        self.ui.btn_canout_caninout.clicked.connect(self._on_canout_select)
        self.ui.btn_start_parse_caninout.clicked.connect(self._on_start_caninout_parse)


        self.show()

        # SET CUSTOM THEME
        # ///////////////////////////////////////////////////////////////
        # ///////////////////////////////////////////////////////////////
        # 路径冻结，防止打包成exe后路径错乱
        if getattr(sys, 'frozen', False):
            absPath = os.path.dirname(os.path.abspath(sys.executable))
        elif __file__:
            absPath = os.path.dirname(os.path.abspath(__file__))
        useCustomTheme = False
        self.useCustomTheme = useCustomTheme
        self.absPath = absPath
        themeFile = os.path.abspath(os.path.join(absPath, "themes", "py_dracula_light.qss"))

        # SET THEME AND HACKS
        if useCustomTheme:
            # LOAD AND APPLY STYLE
            UIFunctions.theme(self, themeFile, True)

            # SET HACKS
            AppFunctions.setThemeHack(self)

        # SET HOME PAGE AND SELECT MENU
        # ///////////////////////////////////////////////////////////////
        self.ui.stackedWidget.setCurrentWidget(self.ui.home)
        self.ui.btn_home.setStyleSheet(UIFunctions.selectMenu(self.ui.btn_home.styleSheet()))


    # NAVIGATION: page switch helper
    # ///////////////////////////////////////////////////////////////
    _PAGE_WIDGET_MAP = {
        "btn_home": "home",
        "btn_snapshot": "snapshot_widget",
        "btn_crc": "crc_page",
        "btn_caninout": "caninout_page",
    }

    def _switch_page(self):
        btn = self.sender()
        btnName = btn.objectName()
        page_name = self._PAGE_WIDGET_MAP[btnName]
        self.ui.stackedWidget.setCurrentWidget(getattr(self.ui, page_name))
        UIFunctions.resetStyle(self, btnName)
        btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

    def _on_theme_toggle(self):
        if self.useCustomTheme:
            themeFile = os.path.abspath(os.path.join(self.absPath, "themes/py_dracula_dark.qss"))
            UIFunctions.theme(self, themeFile, True)
            AppFunctions.setThemeHack(self)
            self.useCustomTheme = False
        else:
            themeFile = os.path.abspath(os.path.join(self.absPath, "themes/py_dracula_light.qss"))
            UIFunctions.theme(self, themeFile, True)
            AppFunctions.setThemeHack(self)
            self.useCustomTheme = True

    def _on_dbc_file_select(self):
        self.ui.dbc_filepath.clear()
        fileName_choose, _ = QFileDialog.getOpenFileName(self, '选取dbc文件', '.',
                                                         'dbc文件(*.dbc)')
        print(fileName_choose)
        if fileName_choose == "":
            QMessageBox.warning(self, 'warning', '请选择dbc文件!!')
        else:
            self.ui.listWidget_result.clear()
            self.ui.dbc_filepath.append(fileName_choose)
            self.dbc_result = ReadDBCNew_readlines.readDBC(fileName_choose)
            self.canid_list = [i for i in self.dbc_result]
            self.ui.comboBox_canid.addItems(self.canid_list)

    def _on_add_signal(self):
        self.ui.listWidget_result.addItem(
            self.ui.comboBox_canid.currentText() + '.' + self.ui.listWidget_signal.currentItem().text())

    def _on_delete_signal(self):
        self.ui.listWidget_result.takeItem(self.ui.listWidget_result.currentRow())

    def _on_asc_file_select(self):
        self.ui.asc_filepath.clear()
        fileName_choose, _ = QFileDialog.getOpenFileName(self, '选取asc文件', '.',
                                                         'dbc文件(*.asc)')
        print(fileName_choose)
        self.filepath_asc = fileName_choose
        if fileName_choose == "":
            QMessageBox.warning(self, 'warning', '请选择asc文件!!')
        else:
            self.ui.asc_filepath.append(fileName_choose)

    def _on_start_crc(self):
        canfd_check = self.ui.radioButton_canfd.isChecked()
        can_check = self.ui.radioButton_can.isChecked()

        if self.filepath_asc == "":
            QMessageBox.warning(self, 'warning', '请先选择asc文件!!')
            return

        if (not canfd_check) and (not can_check):
            QMessageBox.warning(self, 'warning', '请选择can的类型')
            return

        can_type = 1 if canfd_check else 2
        warning_num = self.id_list_check(can_type)
        if warning_num != 0:
            return

        crc_model = CRC_v1.CRC_calculation(self.current_id_lst, self.filepath_asc, can_type)
        output_result = crc_model.crc_data_procedure()
        print(output_result)
        msg = ''
        for i in output_result:
            msg += '   ' + i + '  \n  '
        QMessageBox.information(self, 'result', msg)

    def _on_dbc_caninout_select(self):
        self.ui.dbc_file_caninout.clear()
        self.fileName_dbc, _ = QFileDialog.getOpenFileName(self, '选取dbc文件', '.',
                                                         'dbc文件(*.dbc)')
        print(self.fileName_dbc)
        if self.fileName_dbc == "":
            QMessageBox.warning(self, 'warning', '请选择dbc文件!!')
        else:
            self.ui.dbc_file_caninout.append(self.fileName_dbc)
            self.dbc_result_caninout = ReadDBCNew_readlines.readDBC(self.fileName_dbc)
            self.ecu_tx_list = [self.dbc_result_caninout[i]['txecu'] for i in self.dbc_result_caninout]
            self.ecu_tx_list = list(set(self.ecu_tx_list))
            self.ui.dbc_combox.addItems(self.ecu_tx_list)

    def _on_canin_select(self):
        self.ui.canin_caninout.clear()
        self.fileName_canin, _ = QFileDialog.getOpenFileName(self, '选取canin对应的excel接口文件', '.',
                                                         'excel文件(*.xlsx)')
        self.ui.canin_caninout.append(self.fileName_canin)
        self.canin_sheetname_list = pd.ExcelFile(self.fileName_canin).sheet_names
        self.canin_sheetname_list = list(set(self.canin_sheetname_list))
        self.ui.canin_combox.addItems(self.canin_sheetname_list)

    def _on_canout_select(self):
        self.ui.canout_caninout.clear()
        self.fileName_canout, _ = QFileDialog.getOpenFileName(self, '选取canout对应的excel接口文件', '.',
                                                         'excel文件(*.xlsx)')
        print(self.fileName_canout)
        self.ui.canout_caninout.append(self.fileName_canout)
        self.canout_sheetname_list = pd.ExcelFile(self.fileName_canout).sheet_names
        self.ui.canout_combox.addItems(self.canout_sheetname_list)

    def _on_start_caninout_parse(self):
        if self.fileName_dbc == "":
            QMessageBox.warning(self, 'warning', '请先选择dbc文件!!')
            return

        self.ui.caninout_text_area.clear()
        DBC_SAVE_filename = os.getcwd() + '/' + 'DBC_SAVE' + '.xlsx'
        CANIN_SAVE_filename = os.getcwd() + '/' + 'CANIN_SAVE' + '.xlsx'
        CANOUT_SAVE_filename = os.getcwd() + '/' + 'CANOUT_SAVE' + '.xlsx'

        ECU_Name = self.ui.dbc_combox.currentText()
        DBCtoEXCEL(self.fileName_dbc, DBC_SAVE_filename, ECU_Name)
        self.ui.caninout_text_area.append('DBC文件解析完成，保存在' + DBC_SAVE_filename + '\n')

        if self.fileName_canin != "" and self.fileName_canout == "":
            CANIN_sheetname = self.ui.canin_combox.currentText()
            DBC_CANIN(self.fileName_canin, DBC_SAVE_filename, CANIN_sheetname, CANIN_SAVE_filename)
            self.ui.caninout_text_area.append('CANIN文件解析完成，保存在' + CANIN_SAVE_filename + '\n')

        elif self.fileName_canin == "" and self.fileName_canout != "":
            CANOUT_sheetname = self.ui.canout_combox.currentText()
            DBC_CANOUT(self.fileName_canout, DBC_SAVE_filename, CANOUT_sheetname, CANOUT_SAVE_filename)
            self.ui.caninout_text_area.append('CANOUT文件解析完成，保存在' + CANOUT_SAVE_filename + '\n')

        elif self.fileName_canin != "" and self.fileName_canout != "":
            CANIN_sheetname = self.ui.canin_combox.currentText()
            CANOUT_sheetname = self.ui.canout_combox.currentText()
            DBC_CANIN(self.fileName_canin, DBC_SAVE_filename, CANIN_sheetname, CANIN_SAVE_filename)
            self.ui.caninout_text_area.append('CANIN文件解析完成，保存在' + CANIN_SAVE_filename + '\n')
            DBC_CANOUT(self.fileName_canout, DBC_SAVE_filename, CANOUT_sheetname, CANOUT_SAVE_filename)
            self.ui.caninout_text_area.append('CANOUT文件解析完成，保存在' + CANOUT_SAVE_filename + '\n')


    def canid_change(self):
        self.ui.listWidget_signal.clear()
        self.ui.listWidget_signal.addItems([j for j in self.dbc_result[self.ui.comboBox_canid.currentText()]['signal'].keys()])

    def id_list_check(self, can_type):
        self.current_id_lst = []
        warning_num = 0

        itemsTextList = [self.ui.listWidget_result.item(i).text() for i in range(self.ui.listWidget_result.count())]
        for item in itemsTextList:
            msg_name = item.split('.')[0]
            signal_name = item.split('.')[1]  #
            # 前提是canfd默认是前两个byte为checksum，can默认是最后一个byte为checksum！！！
            # print(self.dbc_result[msg_name]['signal'][signal_name]['byteorder'])
            print(can_type)
            if can_type == 1:
                if self.dbc_result[msg_name]['signal'][signal_name]['byteorder'] == '0':  # motorola
                    if self.dbc_result[msg_name]['signal'][signal_name]['endbit'] == '7' and \
                            self.dbc_result[msg_name]['signal'][signal_name]['siglen'] == '16' and self.dbc_result[msg_name]['msglen'] == '64':
                        self.current_id_lst.append(self.dbc_result[msg_name]['id'])
                    else:
                        QMessageBox.warning(self, 'warning', msg_name + '.' + signal_name + '是CheckSum/CRC信号吗？')
                        warning_num += 1
                else: #intel
                    if self.dbc_result[msg_name]['signal'][signal_name]['endbit'] == '0' and \
                            self.dbc_result[msg_name]['signal'][signal_name]['siglen'] == '16' and self.dbc_result[msg_name]['msglen'] == '64':
                        self.current_id_lst.append(self.dbc_result[msg_name]['id'])
                    else:
                        QMessageBox.warning(self, 'warning', msg_name + '.' + signal_name + '是CheckSum/CRC信号吗？')
                        warning_num += 1
            elif can_type == 2:
                if self.dbc_result[msg_name]['signal'][signal_name]['byteorder'] == '0':  # motorola
                    if self.dbc_result[msg_name]['signal'][signal_name]['endbit'] == '63' and \
                            self.dbc_result[msg_name]['signal'][signal_name]['siglen'] == '8' and \
                            self.dbc_result[msg_name]['msglen'] == '8':
                        self.current_id_lst.append(self.dbc_result[msg_name]['id'])
                    else:
                        QMessageBox.warning(self, 'warning', msg_name + '.' + signal_name + '是CheckSum/CRC信号吗？')
                        warning_num += 1
                else:  # intel
                    print(self.dbc_result[msg_name]['signal'][signal_name]['endbit'])
                    print(self.dbc_result[msg_name]['signal'][signal_name]['siglen'])
                    print(self.dbc_result[msg_name]['msglen'])
                    if self.dbc_result[msg_name]['signal'][signal_name]['endbit'] == '56' and \
                            self.dbc_result[msg_name]['signal'][signal_name]['siglen'] == '8' and \
                            self.dbc_result[msg_name]['msglen'] == '8':
                        self.current_id_lst.append(self.dbc_result[msg_name]['id'])
                    else:
                        QMessageBox.warning(self, 'warning', msg_name + '.' + signal_name + '是CheckSum/CRC信号吗？')
                        warning_num += 1
        self.current_id_lst = list(set(self.current_id_lst)) # 去重
        self.current_id_lst = [hex(int(i))[2:] for i in self.current_id_lst] # 转换为十六进制并去掉0x

        print(self.current_id_lst)
        return warning_num

    def mdf_file(self):

        self.ui.textBrowser.clear()
        fileName_choose, _ = QFileDialog.getOpenFileName(self, '选取快照数据文件', '.',
                                                         '数据文件(*.mdf *.dat *.mf4)')  # 设置文件扩展名过滤,用双分号间隔
        print(fileName_choose)
        if fileName_choose == "":
            QMessageBox.warning(self, 'warning', '请选择解析文件!!')
        else:
            self.ui.textBrowser.append(fileName_choose)

            gac_nidec_check = self.ui.gac_nidec_radiobtn.isChecked()
            gac_lv_check = self.ui.gac_lv_radiobtn.isChecked()
            gac_hv_check = self.ui.gac_hv_radiobtn.isChecked()
            gac_xof_check = self.ui.gac_xof_radiobtn.isChecked()

            project_check_status = [gac_nidec_check, gac_lv_check, gac_hv_check, gac_xof_check]

            bigdataIsNot_check = self.ui.bigdata0_radiobtn.isChecked()
            bigdataIs_check = self.ui.bigdata1_radiobtn.isChecked()


            bigdata_check_status = [bigdataIsNot_check, bigdataIs_check]
            # print(project_check_status, bigdata_check_status)
            # 把选择结果输出到text-browser
            idx = project_check_status.index(True)
            output_text_project=  ['A02项目被选择', 'XOF项目被选择', 'X3T项目被选择', 'XOF项目被选择']
            self.ui.textBrowser.append(output_text_project[idx])
            idx = bigdata_check_status.index(True)
            output_text_bigdata = ['大数据解析没有被选择', '大数据解析被选择']
            self.ui.textBrowser.append(output_text_bigdata[idx])
        self.output_result = [fileName_choose, project_check_status, bigdata_check_status]  # 输出上位机

    def mdf_parse(self):
        if self.output_result[0] == "":
            QMessageBox.warning(self, 'warning', '请先选择解析文件!!')
        else:
            if self.ui.lineEdit_SignalName.text() == "":
                signal_name = 'DCU_OSC_Signal*'
            else:
                signal_name = self.ui.lineEdit_SignalName.text()
            if '*' not in signal_name:
                QMessageBox.warning(self, 'warning', '请输入正确的带有*号的信号名字！！')
            else:
                SnapShot_cls = SnapshotTools_V42.SnapShot(self.output_result[0], self.output_result[1],
                                                          self.output_result[2], signal_name)
                osc_data_info, bigdata_info = SnapShot_cls.osc_data_procedure()
                if osc_data_info == 'NG':
                    QMessageBox.warning(self, 'warning', '待解析数据中不包含debug外发数据')
                else:
                    self.ui.textBrowser.append('debug外发数据解析完成！！')
                if self.output_result[2][1] == True:
                    if bigdata_info == 'NG':
                        QMessageBox.warning(self, 'warning', '待解析数据中不包含bigdata数据')
                    else:
                        self.ui.textBrowser.append('bigdata数据解析完成！！')


    # RESIZE EVENTS
    # ///////////////////////////////////////////////////////////////
    def resizeEvent(self, event):
        # Update Size Grips
        UIFunctions.resize_grips(self)

    # MOUSE CLICK EVENTS
    # ///////////////////////////////////////////////////////////////
    def mousePressEvent(self, event):
        # SET DRAG POS WINDOW
        self.dragPos = event.globalPos()

        # PRINT MOUSE EVENTS
        if event.buttons() == Qt.LeftButton:
            print('Mouse click: LEFT CLICK')
        if event.buttons() == Qt.RightButton:
            print('Mouse click: RIGHT CLICK')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.ico"))
    window = MainWindow()
    sys.exit(app.exec())
