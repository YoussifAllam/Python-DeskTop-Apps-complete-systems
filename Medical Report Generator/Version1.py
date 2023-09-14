from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
# from PyQt5.QtWidgets import QWidget
from PyQt5 import uic
from os import path
import sys
import os
from  time import sleep
# import PdfReader
import PyPDF2
from datetime import datetime
import pandas as pd
from pdf2image import convert_from_path, convert_from_bytes
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError
)
import easyocr
import Ui 

#FORM_CLASS,_ = uic.loadUiType(path.join(path.dirname(__file__),'Ui.ui'))


class Mainapp(QMainWindow, Ui.Ui_Frame):
    #QWidget
    bool_task_ended = False
    problems = []
    patient_names_dict = {'Name': [], 'MRN': [],'problems':[]}
    Folderpath = ''
    test = 0
    def __init__(self, parent=None):
        super(Mainapp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.Browse_btn_2.setVisible(False)
        self.run_browse_btn()
        self.run_open_btn()
        self.setWindowTitle( "Medical Report Generator" )
        self.setFixedSize( 603, 477)


    def run_browse_btn(self):
        self.Browse_btn.clicked.connect(self.Handel_Browse_Btn)
        #date = line[28]
        
    def Handel_Browse_Btn(self):
        save_place = QFileDialog.getExistingDirectory(self, 'Select folder')
        self.path_lineEdit.setText(save_place)
        Mainapp.Folderpath = save_place
        pdfs_names = self.get_namesof_pdf_fiels(save_place)
        txt=''
        patient_names =[]
        patient_MRNs =[]
        problems_Lists = []
        for i in range (len(pdfs_names)):
            #print(pdfs_names[i] )
            sleep(2)
            self.label_2.setText(f'Done {i} of {len(pdfs_names)}')
            QApplication.processEvents()
            sleep(1)
            
            patient_name , patient_MRN ,  problems_List = self.extract_pdf_to_txt(pdfs_names[i] ,save_place )
            self.check_if_fileMRN_isSame_PatiantMRN(pdfs_names[i] ,patient_MRN )
            #print(patient_names,patient_MRNs)
            patient_names.append( patient_name)
            patient_MRNs .append(  str(patient_MRN).replace('SAO2.','').strip('0'))
            problems_Lists .append(  problems_List)
        
        self.add_to_dict(patient_names , patient_MRNs ,  problems_Lists )
        self.write_resualts_in_excel()
        self.label_2.setText('finshed')
        QMessageBox.information(self, "i" , " Done  "  )
        Mainapp.bool_task_ended = True 
        
        self.label_2.setText(f'Done {len(pdfs_names)} of {len(pdfs_names)}')
        QApplication.processEvents()
        sleep(1)
        self.Browse_btn_2.setVisible(True)
        QApplication.processEvents()    
        
    # def test_func(self):
    #     for i in range(1):
    #         sleep(2)
    #         self.label_2.setText(f'Done {i+1} of {10}')
    #         QApplication.processEvents()
    #         Mainapp.bool_task_ended = True
    #         self.Browse_btn_2.setVisible(True)
    #         QApplication.processEvents()
            
    def check_patiant_MR(self , txt_lines :str ,Patient_No  ,page_num):
        index = txt_lines.find('Patient No') or txt_lines.find('Hospital No') or txt_lines.find('MRN') or txt_lines.find('MR')
        if index != -1:
            if str(Patient_No) not in str(txt_lines)[index : index+80] :
                return True , page_num
            
            else: return False ,page_num
        else :return None , None
        
    def check_patiant_name(self , txt_lines :str ,name  ,page_num):
        index = str(txt_lines).find('Patient Name')
        if index != -1:
            if str(name) not in str(txt_lines)[index : index+60].replace(',','') :            
                return True , page_num
            
            else: return False , page_num
        else :return None , None
            
    def cheack(self , txt ,i,name ,MRN ):
        txt = str(txt)
        test_name ,page_name = self.check_patiant_name(txt, name ,i)
        test_MRN ,page_MRN= self.check_patiant_MR(txt , MRN ,i )
        if test_name == True and test_MRN ==True and (test_name != None and test_MRN != None) :
            Mainapp.problems.append(f'there is problem in Patient Name at page {page_name}')
            Mainapp.problems.append(f'there is problem in Patient MRN at page {page_MRN}')
            
        elif test_name == True and test_MRN == False :  
            pass
             
            
    def check_if_fileMRN_isSame_PatiantMRN(self ,pdfName , PatiantMRN :str   ):
        
        PatiantMRN = PatiantMRN.replace('SAO2.','').strip('0')
        if str(PatiantMRN) not in str(pdfName):
            Mainapp.problems.append(f'patient MRN does not match with pdf name')     
    
    def check_Q1004(self,txt ):
        index = txt.find("Q1004")
        if index != -1:
            index2 = txt.find("Sputum")
            if  index2 == -1:
                Mainapp.problems.append('Sputum C/S not found')
            else:
                pass
                #print('Sputum founded at',index2)   
                #print('Sputum founded at',index2)        
   
    def run_open_btn(self):    
        self.Browse_btn_2.clicked.connect(self.Open_BTN)
        
    def Open_BTN(self )   :
        if Mainapp.bool_task_ended == True : 
            self.open_excel_sheet()
            self.Browse_btn_2.setVisible(False)
        else : 
            QMessageBox.information(self, "i" , " Please Wait until the process ended "  )
    
    def write_resualts_in_excel(self):
        df = pd.DataFrame(Mainapp.patient_names_dict)
        try:
             df.to_excel(f'{Mainapp.Folderpath}\my_excel_sheet.xlsx')
        except:
            QMessageBox.information(self, "i" , " There is Excel file with the same name in folder please delete it "  )

    def open_excel_sheet(self):
        os.startfile(f'{Mainapp.Folderpath}\my_excel_sheet.xlsx')
        
    
    def getdate(self , report_date):
            curr_month = self.GetDate_from_comboBox()
            self.calc_ifThis_curr_month(report_date  , curr_month)
            
        #print(boolean_test_date)
        
    def convert_str_to_date(self , str_date):
        realdate = datetime.strptime(str_date, "%d-%b-%Y")
        return realdate.date()
    
    def calc_ifThis_curr_month(self , date , curr_month) :
        
        report_date = self.convert_str_to_date(date)
        splited_date = str(report_date).split('-')
        print(splited_date[1] ,'===',curr_month,'====',report_date)
        if  int(splited_date[1]) == int(curr_month):
            print("same month")
        else:
            if 'The Discharge Date does not match with your chosen month' not in Mainapp.problems:
                Mainapp.problems.append('The Discharge Date does not match with your chosen month')
        
    def get_namesof_pdf_fiels(self , folder_path):
        pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
        pdf_names = []
        for pdf_file in pdf_files:
            pdf_names.append(pdf_file)
        return pdf_names
        
    def check_Approved(self , txt_lines :str ):
        indix = str(txt_lines).find('Visa Type')
        if indix != -1:
            if 'APPROVED' not in txt_lines [indix : indix+30] and 'Approved' not in txt_lines [indix : indix+80]  :
                #print(str(txt_lines )[indix : indix+80])
                Mainapp.problems.append(f'the Patient is not APPROVED')
            else:
                indix2 = txt_lines.find('Visa Remarks')
                if indix2 != -1:
                    indix3 = txt_lines.find(' Approved for 0 days')
                    if indix3 != -1:
                        Mainapp.problems.append(f'the Patient is not APPROVED')
                    # num_of_days =  txt_lines[indix2+10:indix2+12]
                    # if int(num_of_days.split()) <= 0:
                    #     Mainapp.problems.append(f'Maximum Number Of Days Approved: 0')

    def check_if_LABORATORY_isFound(self,txt_lines):
        indix = txt_lines.find('LABORATORY DEPARTMENT')
        if indix == -1:   
            Mainapp.problems.append(f'LABORATORY DEPARTMENT page does not found')
    
    def GetDate_from_comboBox(self):
        m = self.comboBox.currentText()
        if m == 'January' : return 1
        elif m == 'February' : return 2
        elif m == 'March' :return 3
        elif m == 'April':return 4
        elif m == 'May':return 5
        elif m == 'June':return 6
        elif m == 'July':return 7
        elif m == 'August':return 8
        elif m == 'September':return 9
        elif m == 'October' :return 10
        elif m == 'November':return 11
        elif m == 'December':return 12
        else:
            print("not found date")
        
    def extract_pdf_to_txt(self,pdf_name, folder_path):
        curr_path = path.join(path.dirname(__file__))
        print('\n',curr_path,"===============================",'\n')
        images = convert_from_path(f'{folder_path}\{pdf_name}', 500, poppler_path=r'C:\Program Files\poppler-21.10.0\Library\bin')
        # g:\BRMAGA\python\UI projects\Project\poppler-21.10.0\Library\bin
        # G:\BRMAGA\python\UI projects\Project\poppler-21.10.0\Library\bin
        images_number=len(images)
        
        for i in range(images_number):
            if i == 0 or  i == 1 or  i == 2 or i == images_number-1 or  i == images_number-2 or  i == images_number-3 or i == images_number-4 :  
              images[i].save('page'+str(i)+'.jpg','JPEG')
            
        scrapped =[]
        reader = easyocr.Reader(['en']) 
        images_number=len(images)
        
        for i in range(images_number):
            if i == 0  or  i == images_number-1 or  i == images_number-2 or  i == images_number-3 or i == images_number-4 :  
                page_txt = reader.readtext('page'+str(i)+'.jpg', detail = 0)
                scrapped.append(reader.readtext('page'+str(i)+'.jpg', detail = 0))
                #print(page_txt)
                if i == 0:
                    patient_name , patient_MRN ,Discharge_date = self.getdata(scrapped)
                   # print('\n','1111',patient_name ,'====',patient_MRN ,'====', Discharge_date,'\n')
                self.getdate(Discharge_date)
                    
                self.cheack(page_txt , i+1 ,patient_name , patient_MRN )  
                
                  
            if i == 1 :
                self.extract_pdf_to_txt_way1(pdf_name,folder_path,patient_name , patient_MRN ,Discharge_date)
                    
            
        scrapped = str(scrapped)    
        self.check_Q1004(scrapped)
        self.check_Approved(scrapped)   
        self.check_if_LABORATORY_isFound(scrapped)
        
        return patient_name , patient_MRN ,  Mainapp.problems
     
    
    def extract_pdf_to_txt_way1(self,pdf_name, folder_path,patient_name,patient_MRN,discharge_date):
        pdfFileObj = open(f'{folder_path}\{pdf_name}', 'rb')
        pdfReader = PyPDF2.PdfReader(pdfFileObj)
        pdf_txt = ''
        Mainapp.problems = []
        for page_num in range(len(pdfReader.pages)):
            if page_num == 0:
                continue
            if page_num == 1 or page_num == 2:
                print('way1')
                page = pdfReader.pages[page_num]
                page_txt = page.extract_text()
                self.cheack(page_txt , page_num+1 ,patient_name , patient_MRN )
            else:
                return
        
    def getdata (self,s):
        Patient_Name , Patient_MRN , Discharge_Time ='','',''
        name_index = s[0].index("Patient Name")
        if name_index != -1:
            Patient_Name = (str(s[0][name_index+1]).replace(',',''))
            
        
        MRN_index = s[0].index("Patient No.")
        if MRN_index != -1:
            Patient_MRN = (str(s[0][MRN_index+1]).replace('SA02.',''))
              
        
        Discharge_Time_index = s[0].index("Discharge Date")
        if Discharge_Time_index != -1:
            Discharge_Time = s[0][Discharge_Time_index+1]
        
        #_______________________
        if  Patient_Name == '':
            Patient_Name = str(s[0][18]).replace(',','')
            
        if Patient_MRN == '':
            Patient_MRN = str(s[0][11]).replace('SA02.','')
            
        if Discharge_Time ==s:
            Discharge_Time = str(s[0][26])
            
        #print(Patient_Name ,'====',Patient_Name ,'====', )  
        return Patient_Name ,Patient_MRN, Discharge_Time   
        
    def add_to_dict(self,names,MRNs ,problems_Lists):    
        #print(names ,MRNs, problems_Lists)
        Mainapp.patient_names_dict['Name'] = names
        Mainapp.patient_names_dict['MRN'] = MRNs
        Mainapp.patient_names_dict['problems'] = problems_Lists
        #print(Mainapp.patient_names_dict)
        
        

def main():
    app = QApplication(sys.argv)
    window = Mainapp()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
    