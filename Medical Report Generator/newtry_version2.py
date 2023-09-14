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

import Ui_ver2

#FORM_CLASS,_ = uic.loadUiType(path.join(path.dirname(__file__),'Ui_ver2.ui'))


class Mainapp(QMainWindow, Ui_ver2.Ui_Frame):
    #QWidget
    bool_task_ended = False
    Check_Name = []
    Check_MRN = []
    Check_Sputum = []
    Check_Total_cost = []
    Check_Approved = []
    Check_LABORATORY = []
    Check_PdfName_Patient_MRN = []
    Cheack_Discharge_Date = []
    excel_file_path = ''
    problems= []
    
    patient_names_dict = {'Name': [] , 'MRN': [] ,'Check Name':[] , 'Check MRN':[] , 'Check Sputum':[] , 'Check Approved':[] , 'Check Discharge Date':[] ,
                          'Check LABORATORY is Found':[] ,'Check if Pdf Name is Match with Patiant MRN':[]   }
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
        self.Excel_path_Browse_btn.clicked.connect(self.Handel_Browse_excell_file_Btn)


        
    def run_browse_btn(self):
        self.Browse_btn.clicked.connect(self.Handel_Browse_Btn)
        #date = line[28]
    
    def Handel_Browse_excell_file_Btn(self):
        excel_file_path =QFileDialog.getOpenFileName(self, 'Open file', '', 'Excel Files (*.xlsx *.xlsm *.sxc *.ods *.csv *.tsv)')
        print(excel_file_path[0] , '===========')
        self.Excel_path_lineEdit.setText(excel_file_path[0])
          
    def Handel_Browse_Btn(self):
        if self.comboBox.currentText() == '':
            QMessageBox.information(self, 'i','You should Choose Month First. ')
            return
        
        if self.Excel_path_lineEdit.text() == '':
            QMessageBox.information(self, 'i','You should enter Excel file path First.')
            return
        
        save_place = QFileDialog.getExistingDirectory(self, 'Select folder')
        self.path_lineEdit.setText(save_place)
        
        excel_file_path = self.Excel_path_lineEdit.text()
        num_OF_Unique_Patient_names = self.read_excel_data(excel_file_path)
        
        Mainapp.Folderpath = save_place
        pdfs_names = self.get_namesof_pdf_fiels(save_place)
        
        if len(pdfs_names) != num_OF_Unique_Patient_names : 
             QMessageBox.information(self, 'i','Number of Patients does not match number of pdf files . ')
             return

        patient_names =[]
        patient_MRNs =[]
        problems_Lists = []
        for i in range (len(pdfs_names)):
            #print(pdfs_names[i] )
            sleep(2)
            self.label_2.setText(f'Done {i} of {len(pdfs_names)}')
            QApplication.processEvents()
            sleep(1)
            
            patient_name , patient_MRN ,  problems_List = self.extract_pdf_to_txt(pdfs_names[i] ,save_place  , i)
            self.check_if_fileMRN_isSame_PatiantMRN(pdfs_names[i] ,patient_MRN )
            #print(patient_names,patient_MRNs)
            patient_names.append( patient_name)
            patient_MRNs .append(  str(patient_MRN).replace('SAO2.','').strip('0'))
            problems_Lists .append(  problems_List)
        
        self.add_to_dict(patient_names , patient_MRNs ,  problems_Lists )
        self.write_resualts_in_excel()
        self.label_2.setText('finshed')
        Mainapp.bool_task_ended = True 
        
        self.label_2.setText(f'Done {len(pdfs_names)} of {len(pdfs_names)}')
        QApplication.processEvents()
        sleep(1)
        self.Browse_btn_2.setVisible(True)
        QApplication.processEvents()    
        QMessageBox.information(self, 'i','Done ')
        
    def read_excel_data(self, excel_file_path):
        df = pd.read_excel(excel_file_path)
        data_list =  df.dropna().values.tolist()
        new = [ i[0] for i in data_list]
        return len(set(new))
               
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
            
    def cheack(self , txt ,i,name ,MRN ,pdf_num ):
        txt = str(txt)
        test_name ,page_name = self.check_patiant_name(txt, name ,i)
        test_MRN ,page_MRN= self.check_patiant_MR(txt , MRN ,i )
        if test_name == True and test_MRN ==True and (test_name != None and test_MRN != None) :
            Mainapp.Check_Name.append(f'there is problem in Patient Name at page {page_name}')
            Mainapp.Check_MRN.append(f'there is problem in Patient MRN at page {page_MRN}')
            
        elif test_name == True and test_MRN == False  and f'Done{pdf_num}' not in Mainapp.Check_Name and f'Done{pdf_num}' not in Mainapp.Check_MRN :  
            Mainapp.Check_Name.append(f'Done{pdf_num}')
            Mainapp.Check_MRN.append(f'Done{pdf_num}')
            
        elif test_name == False and test_MRN == False  and f'Done{pdf_num}' not in Mainapp.Check_Name and f'Done{pdf_num}' not in Mainapp.Check_MRN :
            Mainapp.Check_Name.append(f'Done{pdf_num}')
            Mainapp.Check_MRN.append(f'Done{pdf_num}')
                              
    def check_if_fileMRN_isSame_PatiantMRN(self ,pdfName , PatiantMRN :str   ):
        PatiantMRN = PatiantMRN.replace('SAO2.','').strip('0')
        if str(PatiantMRN) not in str(pdfName):
            Mainapp.Check_PdfName_Patient_MRN.append(f'patient MRN does not match with pdf name') 
        else:     Mainapp.Check_PdfName_Patient_MRN.append('Done') 
               
    def check_Q1004(self,txt ):
        index = txt.find("Q1004")
        if index != -1:
            index2 = txt.find("Sputum")
            if  index2 == -1:
                Mainapp.Check_Sputum.append('Sputum C/S not found')
            else:
                Mainapp.Check_Sputum.append('Done')
                #print('Sputum founded at',index2)   
                #print('Sputum founded at',index2)        
   
    def run_open_btn(self):    
        self.Browse_btn_2.clicked.connect(self.Open_BTN)
        
    def Open_BTN(self )   :
        if Mainapp.bool_task_ended == True : 
            self.open_excel_sheet()
            self.Browse_btn_2.setVisible(False)
        else : 
            error_dialog = QErrorMessage()
            error_dialog.showMessage('Please Wait until the process ended ')
            error_dialog.exec()
    
    def write_resualts_in_excel(self):
        df = pd.DataFrame(Mainapp.patient_names_dict)
        try:
             df.to_excel(f'{Mainapp.Folderpath}\my_excel_sheet.xlsx')
        except:
           
            error_dialog = QErrorMessage()
            error_dialog.showMessage('There is Excel file with the same name in folder please delete it ')
            error_dialog.exec()

    def open_excel_sheet(self):
        os.startfile(f'{Mainapp.Folderpath}\my_excel_sheet.xlsx')
        
    def getdate(self , report_date , pdf_num):
            curr_month = self.GetDate_from_comboBox()
            self.calc_ifThis_curr_month(report_date  , curr_month,pdf_num)
            
        #print(boolean_test_date)
        
    def convert_str_to_date(self , str_date):
        realdate = datetime.strptime(str_date, "%d-%b-%Y")
        return realdate.date()
    
    def calc_ifThis_curr_month(self , date , curr_month,pdf_num) :
        
        report_date = self.convert_str_to_date(date)
        splited_date = str(report_date).split('-')
        print(splited_date[1] ,'===',curr_month,'====',report_date)
        if  int(splited_date[1]) == int(curr_month):
            if f'Done{pdf_num}' not in Mainapp.Cheack_Discharge_Date:
                Mainapp.Cheack_Discharge_Date.append(f'Done{pdf_num}')
        else:
            if f'The Discharge Date does not match with your chosen month in pdf num{pdf_num}' not in Mainapp.Cheack_Discharge_Date:
                Mainapp.Cheack_Discharge_Date.append(f'The Discharge Date does not match with your chosen month in pdf num{pdf_num}')
        
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
                Mainapp.Check_Approved.append('The Patient is not APPROVED')
                
            else:
                indix2 = txt_lines.find('Visa Remarks')
                
                if indix2 != -1:
                    
                    indix3 = txt_lines.find(' Approved for 0 days')
                    if indix3 != -1:
                        Mainapp.Check_Approved.append('The Patient is not APPROVED')
                    else : Mainapp.Check_Approved.append('Done')
                    
                else : Mainapp.Check_Approved.append('Done')
                
        else : Mainapp.Check_Approved.append('The Patient is not APPROVED')
                    
    def check_if_LABORATORY_isFound(self,txt_lines):
        indix = txt_lines.find('LABORATORY DEPARTMENT')
        if indix == -1:   
            Mainapp.Check_LABORATORY.append(f'LABORATORY DEPARTMENT page does not found')
        else : Mainapp.Check_LABORATORY.append('Done')
    
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
        
    def extract_pdf_to_txt(self,pdf_name, folder_path ,pdf_num):
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
                self.getdate(Discharge_date ,pdf_num)
                    
                self.cheack(page_txt , i+1 ,patient_name , patient_MRN , pdf_num)  
                
                  
            if i == 1 :
                self.extract_pdf_to_txt_way1(pdf_name,folder_path,patient_name , patient_MRN ,Discharge_date,pdf_num)
                    
            
        scrapped = str(scrapped)    
        self.check_Q1004(scrapped)
        self.check_Approved(scrapped)   
        self.check_if_LABORATORY_isFound(scrapped)
        
        return patient_name , patient_MRN ,  Mainapp.problems
     
    def extract_pdf_to_txt_way1(self,pdf_name, folder_path,patient_name,patient_MRN,discharge_date,pdf_num):
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
                self.cheack(page_txt , page_num+1 ,patient_name , patient_MRN  ,pdf_num)
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
        Mainapp.patient_names_dict['Check Name'] = Mainapp.Check_Name
        Mainapp.patient_names_dict['Check MRN'] = Mainapp.Check_MRN
        Mainapp.patient_names_dict['Check Sputum'] = Mainapp.Check_Sputum
        # Mainapp.patient_names_dict['Check Total Cost'] = Mainapp.Check_Total_cost
        Mainapp.patient_names_dict['Check Approved'] = Mainapp.Check_Approved
        Mainapp.patient_names_dict['Check Discharge Date'] = Mainapp.Cheack_Discharge_Date
        Mainapp.patient_names_dict['Check LABORATORY is Found'] = Mainapp.Check_LABORATORY
        Mainapp.patient_names_dict['Check if Pdf Name is Match with Patiant MRN'] = Mainapp.Check_PdfName_Patient_MRN
        #print('\n',Mainapp.patient_names_dict,'\n')

        
        

def main():
    app = QApplication(sys.argv)
    window = Mainapp()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
    