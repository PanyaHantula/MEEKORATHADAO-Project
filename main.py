############################################
#           Pyside 6 + Qt Designer         #
############################################
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QPushButton, \
                            QMessageBox, QWidget, QVBoxLayout, QLabel, QLineEdit
from PySide6.QtCore import QThread, QObject, Signal, Slot, QTimer
import datetime
import time
from main_gui import Ui_MainWindow
from DB import Database


class IR_Count_Worker(QObject):
    # PyQt Signals
    IR_Count_ThreadProgress = Signal(int)
    
    @Slot()
    def count(self):
        self.count = 0
        while True:
            self.count += 1
            self.IR_Count_ThreadProgress.emit(self.count)
            time.sleep(2)
    
    def reset(self):
        self.count = 0
        
class PZEM_Worker(QObject):
    # PyQt Signals
    PZEM_ThreadProgress = Signal(int,int)
    @Slot()
    def getPower(self):
        self.Power = 100
        self.Energy = 0
        while True:
            self.Energy += 1
            self.PZEM_ThreadProgress.emit(self.Power,self.Energy)
            time.sleep(10)
            
    def reset(self):
        self.Power = 100
        self.Energy = 0    


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.db = Database()
        self.db.connect_db()
        
        self.setThread()
        self.loadDatabase()
        self.resetData()
        self.setClock()
        
        self.ui.date_select_start.setDate(datetime.datetime.now())
        self.ui.date_select_end.setDate(datetime.datetime.now())
        
        self.ui.btn_update.clicked.connect(self.add_DataToDataBase)
        self.ui.btn_LoadDB.clicked.connect(self.loadDataBaseToResulteTable)
        self.ui.btn_Delete.clicked.connect(self.delete_DataFromDataBase)
        # self.ui.btn_Edit.clicked.connect(self.ShowEditWindows)
        self.ui.btn_Edit.hide()
        
    def setClock(self):
        timer = QTimer(self)
        timer.timeout.connect(self.showTime)
        timer.start(1000)
    
       # method called by timer
    def showTime(self):
        label_time = datetime.datetime.now().strftime("%H:%M")
        self.ui.lbl_Clock.setText(label_time)
        
        dateNow = datetime.datetime.now().strftime("%Y-%m-%d")
        self.ui.lbl_dateNow.setText(dateNow)
            
    def setThread(self):
        # Initialize worker and thread
        # IR Counter
        self.IR_Count_thread = QThread()
        self.IR_Count_thread.setObjectName('IR_Count_thread')   # Create thread 
        self.IR_Count_Worker = IR_Count_Worker()                # Create worker
        self.IR_Count_Worker.moveToThread(self.IR_Count_thread) # move worker to thread 
        self.IR_Count_thread.started.connect(self.IR_Count_Worker.count)     # Connect Thread
        self.IR_Count_Worker.IR_Count_ThreadProgress.connect(self.UpdateTotalCount)     # Connect signals and slots
        self.IR_Count_thread.start()    # Start Thread
        
        # PZEM Power Meter 
        self.PZEM_thread = QThread()
        self.PZEM_thread.setObjectName('PZEM_thread')   # Create thread 
        self.PZEM_Worker = PZEM_Worker()                # Create worker
        self.PZEM_Worker.moveToThread(self.PZEM_thread) # move worker to thread 
        self.PZEM_thread.started.connect(self.PZEM_Worker.getPower)     # Connect Thread
        self.PZEM_Worker.PZEM_ThreadProgress.connect(self.update_PowerEnergy)     # Connect signals and slots
        self.PZEM_thread.start()    # Start Thread
    
    # Call Windows
    # def ShowEditWindows(self,checked):
    #     self.EditWindows = Edit_DB_Window()
    #     self.EditWindows.show()
        
    # Update PowerEnergy
    def update_PowerEnergy(self,power,energy):
        self.ui.lbl_Power.setText(str(power))  
        self.ui.lbl_Energy.setText(str(energy)) 
    
    # Count and cal Preformance      
    def UpdateTotalCount(self,count):
        self.ui.lbl_CountTotal.setText(str(count))
        
        # Cal Preformance
        totalTimeMinute = float((datetime.datetime.now() - self.startTime ).total_seconds()/60)
        if totalTimeMinute > 0:
            Performance = int(self.ui.lbl_CountTotal.text()) / totalTimeMinute
        else:
            Performance = 0
        self.ui.lbl_Preformance.setText("{:.2f}".format(Performance))     
    
    # delete data in DB
    def delete_DataFromDataBase(self):
        timeStampToDelete = self.ui.tw_Resulte_DB.item(self.ui.tw_Resulte_DB.currentIndex().row(),0).text()
        SelectRowToDetete = self.ui.tw_Resulte_DB.currentRow()
        
        dlg = QMessageBox(self)
        dlg.setWindowTitle("ลบข้อมูล")
        dlg.setText("ต้องการลบข้อมูลผู้ใช้งานหรือไม่ ??\n " + timeStampToDelete)
        dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        button = dlg.exec()
        
        if button == QMessageBox.Yes:
            if SelectRowToDetete < 0:
                return
            self.ui.tw_Resulte_DB.removeRow(SelectRowToDetete)
            
            # Delete in DB   
            sql = "DELETE FROM dataLoger WHERE (time = '" + timeStampToDelete + "')"
            resultes = self.db.query(sql)
            print(resultes)
            
            # Refresh Table User
            self.loadDatabase()
            self.loadDataBaseToResulteTable()
    
    # Load data form DB and update to table view        
    def loadDatabase(self):
        sql = "select count(*) from dataLoger"
        resultes = self.db.query(sql)

        # create Table
        self.ui.twDB.setRowCount(resultes[0][0])
        self.ui.twDB.setColumnCount(6)
        
        self.ui.twDB.setHorizontalHeaderItem(0, QTableWidgetItem("เวลาบันทึก"))
        self.ui.twDB.setHorizontalHeaderItem(1, QTableWidgetItem("เวลาเริ่มงาน"))
        self.ui.twDB.setHorizontalHeaderItem(2, QTableWidgetItem("จำนวนทั้งหมดที่ผลิตได้(ชิ้น)"))
        self.ui.twDB.setHorizontalHeaderItem(3, QTableWidgetItem("ความเร็วในการผลิต(ชิ้น/นาที)"))
        self.ui.twDB.setHorizontalHeaderItem(4, QTableWidgetItem("กำลังไฟฟ้า(วัตต์)"))
        self.ui.twDB.setHorizontalHeaderItem(5, QTableWidgetItem("พลังงานไฟฟ้าที่ใช้ไป(หน่วย)"))
        
        # load data in DB
        sql = ("select * from dataLoger")
        resultes = self.db.query(sql)
        tablerow = 0
        for row in resultes:
            self.ui.twDB.setItem(tablerow,0,QTableWidgetItem(str(row[0])))
            self.ui.twDB.setItem(tablerow,1,QTableWidgetItem(str(row[1])))
            self.ui.twDB.setItem(tablerow,2,QTableWidgetItem(str(row[2])))
            self.ui.twDB.setItem(tablerow,3,QTableWidgetItem(str(row[3])))
            self.ui.twDB.setItem(tablerow,4,QTableWidgetItem(str(row[4])))
            self.ui.twDB.setItem(tablerow,5,QTableWidgetItem(str(row[5])))
            tablerow += 1
    
    # Load data form DB and update to table resulteview   
    def loadDataBaseToResulteTable(self):
        self.ui.date_select_end.setDateTime(datetime.datetime.now())
        
        dateStart = self.ui.date_select_start.text()
        dateEnd = self.ui.date_select_end.text()
        
        # count total row with select from DB
        sql = ("SELECT COUNT(*) FROM dataLoger WHERE time BETWEEN '" + dateStart + "' AND '" + dateEnd + "'")
        resultes = self.db.query(sql)

        # create Table
        self.ui.tw_Resulte_DB.setRowCount(resultes[0][0])
        self.ui.tw_Resulte_DB.setColumnCount(6)
        
        self.ui.tw_Resulte_DB.setHorizontalHeaderItem(0, QTableWidgetItem("เวลาบันทึก"))
        self.ui.tw_Resulte_DB.setHorizontalHeaderItem(1, QTableWidgetItem("เวลาเริ่มงาน"))
        self.ui.tw_Resulte_DB.setHorizontalHeaderItem(2, QTableWidgetItem("จำนวนทั้งหมดที่ผลิตได้(ชิ้น)"))
        self.ui.tw_Resulte_DB.setHorizontalHeaderItem(3, QTableWidgetItem("ความเร็วในการผลิต(ชิ้น/นาที)"))
        self.ui.tw_Resulte_DB.setHorizontalHeaderItem(4, QTableWidgetItem("กำลังไฟฟ้า(วัตต์)"))
        self.ui.tw_Resulte_DB.setHorizontalHeaderItem(5, QTableWidgetItem("พลังงานไฟฟ้าที่ใช้ไป(หน่วย)"))
        
        if int(resultes[0][0]) > 0 :
                
            # load data in DB
            #mycursor.execute("select * from dataLoger")
            sql = ("SELECT * FROM dataLoger WHERE time BETWEEN '" + dateStart + "' AND '" + dateEnd + "'")
            resultes = self.db.query(sql)
            tablerow = 0
            for row in resultes:
                self.ui.tw_Resulte_DB.setItem(tablerow,0,QTableWidgetItem(str(row[0])))
                self.ui.tw_Resulte_DB.setItem(tablerow,1,QTableWidgetItem(str(row[1])))
                self.ui.tw_Resulte_DB.setItem(tablerow,2,QTableWidgetItem(str(row[2])))
                self.ui.tw_Resulte_DB.setItem(tablerow,3,QTableWidgetItem(str(row[3])))
                self.ui.tw_Resulte_DB.setItem(tablerow,4,QTableWidgetItem(str(row[4])))
                self.ui.tw_Resulte_DB.setItem(tablerow,5,QTableWidgetItem(str(row[5])))
                tablerow += 1

            # cal resulte 
            totalRowCount = int(tablerow)
            from collections import defaultdict
            output = defaultdict(list)
            for col in range(2,6):
                for row in range(self.ui.tw_Resulte_DB.rowCount()):
                    value = float(self.ui.tw_Resulte_DB.item(row, col).text())
                    output[f'column_{col}'].append(value)

            self.ui.lbl_Resulte_DateStart.setText(dateStart)
            self.ui.lbl_Resulte_DateStart_2.setText(dateEnd)
            self.ui.lbl_Resulte_TotalCount.setText(str(sum(output['column_2'])))
            self.ui.lbl_Resulte_Preformance.setText(str(sum(output['column_3']) / totalRowCount))
            self.ui.lbl_Resulte_power.setText(str(sum(output['column_4']) / totalRowCount))
            self.ui.lbl_Resulte_energy.setText(str(sum(output['column_5']) / totalRowCount))
        
        else:
            # Meassage Box
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Warning")
            dlg.setText("ไม่มีข้อมูล \nโปรดเลือกช่วงวันที่ใหม่อีกครั้ง")
            button = dlg.exec()

    # Record data to data base
    # Include meassage box before accept    
    def add_DataToDataBase(self):
        startTime = self.ui.lbl_StartTime.text()
        CountTotal = self.ui.lbl_CountTotal.text()
        Preformance = self.ui.lbl_Preformance.text()
        Power = self.ui.lbl_Power.text()
        Energy = self.ui.lbl_Energy.text()
        
        dlg = QMessageBox(self)
        dlg.setWindowTitle("ลบข้อมูล")
        dlg.setText("ต้องการบันข้อมูลผู้ใช้งานหรือไม่ ??\n หมายเหตุ: หลังจากกดบันทึกแล้ว ข้อมูลที่หน้าจอจะหายไป")
        dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        button = dlg.exec()
        
        if button == QMessageBox.Yes:
            try:  
                val = (startTime,CountTotal,Preformance,Power,Energy)
                sql = "INSERT INTO dataLoger (start_time, total_product, preformance, power,energy) VALUES " + str(val)
                resultes = self.db.query(sql)
                
                self.loadDatabase()
                self.resetData()

            except:
                print("Error insert data")
            

    # Reset data before add data to data base 
    # reset value in thread 
    def resetData(self):
        
        # Stop Thread befor reset        
        self.startTime = datetime.datetime.now()
        self.ui.lbl_CountTotal.setText("0")
        self.ui.lbl_StartTime.setText(str(self.startTime.strftime("%H:%M:%S")))
        self.ui.lbl_Preformance.setText("0")    
        self.ui.lbl_Power.setText("0")  
        self.ui.lbl_Energy.setText("0") 
        
        # reset value of counter and pzem device
        self.IR_Count_Worker.reset()
        self.PZEM_Worker.reset()
        
if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()    