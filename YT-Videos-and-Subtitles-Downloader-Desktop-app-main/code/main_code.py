from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
from os import *
import sys
import re
from downloder_Ui import Ui_Form
from pytube import *

# import files that have important methods 
import downloder as do


class Mainapp(QMainWindow, Ui_Form):
    
    def __init__(self, parent=None):
        super(Mainapp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.Handel_UI()
        self.Handel_Buttons()
    

    def Handle_progress(self,stream, chunk, bytes_remaining):
      if stream != None:
       global progressBar
       total_size = stream.filesize
       bytes_downloaded = total_size - int(bytes_remaining)
       pct_completed = bytes_downloaded / total_size * 100
       self.progressBar.setValue(int(pct_completed))
       #? QApplication.processEvents()
        

    def Handel_UI(self):
        self.setWindowTitle( "T.D.S Downloder" )
        self.setFixedSize( 392 , 574 )
        


    def Handel_Buttons(self):
        #* start button
        self.B_start.clicked.connect(self.Download)
        #* Browse button
        self.Btn_BROWSE.clicked.connect(self.Handel_Btn_Browse)


    def Handel_Btn_Browse(self):
        save_place = QFileDialog.getExistingDirectory(self, 'Select folder')
        self.LINE_PATH.setText(save_place)


    

        
    def shutdown(self):  
        # Shutdown the computer after 30 seconds
        system("shutdown /s /t 30")
        

    def rest_values(self):
         self.LINE_url.clear()
         self.LINE_PATH.clear()
         self.check_subtitle.setChecked(False)
         self.check_trans.setChecked(False)
         self.check_audio.setChecked(False)
         self.check_shut.setChecked(False)
         self.lcdNumber_1.display(0)
         self.lcdNumber_2.display(0)
         self.progressBar.setValue(0)


    def get_data(self):
        url = self.LINE_url.text()
        save_location = self.LINE_PATH.text()
        resolution = self.c_quality.currentText()

        if self.check_subtitle.isChecked():
            subtitle_pre = True
        else:
            subtitle_pre = False 

        if self.check_audio.isChecked():
            QMessageBox.warning(self, "i" , "من فضلك لا تستخدم البرنامج في تنزيل الأغاني والموسيقي , تذكر انها محرمه")
            audio_pre = True
        else:
            audio_pre = False 
        return  url , save_location , resolution , subtitle_pre , audio_pre






    def Download(self):
        url , save_location , resolution , subtitle_pre , audio_pre = self.get_data()
        try:
           self.update_lcd_number( 1 , 1 )
           self.download_sigle( url , save_location , resolution , subtitle_pre , audio_pre)
           self.lcdNumber_1.display(1)
           self.lcdNumber_2.display(1)
           self.rest_values()
           QMessageBox.information(self, "i" , "Download Completed ") 
           if self.check_shut.isChecked():
               QMessageBox.warning(self, "i" ,'The Computer will shutdown after 30 seconds')
               self.shutdown()

        except Exception: # if there is a problem have been done when download single vedio 
            # like if the url is not for single vedio
           try:
                #? QMessageBox.information(self, "i" , "playlist") 
                n_vedios = do.get_number_of_Vedios(url)
                self.lcdNumber_1.display(n_vedios)
                self.update_lcd_number( n1 = n_vedios , n2 = None )
                self.download_playlist( url , save_location , resolution , subtitle_pre , audio_pre , 1 )
                
                QMessageBox.information(self, "i" , "Download Completed ")
                self.rest_values() 
                

                if self.check_shut.isChecked():
                  QMessageBox.warning(self, "i" ,'the computer will shutdown after 30 seconds')
                  self.shutdown()

           except:
                QMessageBox.warning(self, "i" , " Downloading failed "  )

               
        #todo self.progressBar_4.setvValue(0)
 
    
    def update_lcd_number(self , n2 , n1):
        if n1  != None:
            self.lcdNumber_1.display(n1)
        if n2  != None:
            self.lcdNumber_2.display(n2)


    def download_playlist( self , Link , Path , resolution_of_vedios , subtitle_pre , audio_pre , n ) :
     playlist = Playlist( Link )   
     DOWNLOAD_PATH = r'{}'.format( Path )
     playlist._video_regex = re.compile( r"\"url\":\"(/watch\?v=[\w-]*)" )  

     for video in playlist.videos:
        video_id = do.get_video_id(video.watch_url)
        for i in ( '\\' , ':' , '*' , '\"' , '>' , '<' , '?' , '|' , ' ' ,  '^' , '.' ):
            video.title = video.title.replace(i,"_")
        if subtitle_pre == True:
              do.download_transcript( video_id , DOWNLOAD_PATH , video.title )
        
        if audio_pre:
             do.download_audio( video.watch_url, DOWNLOAD_PATH ) 

        else:
            yt= YouTube(video.watch_url )
            streams = yt.streams
            if not do.is_res_found( streams , resolution_of_vedios ):
                resolution_of_vedios = yt.streams.get_highest_resolution()
            
            do.s_download(video , resolution_of_vedios , Path )
            n = n+1
            self.update_lcd_number( n2 = n , n1 = None)
            #self.rest_values()
            QApplication.processEvents()
            
            
    def download_sigle(self , Link , Path , resolution_of_vedios  , trans_per , audio_pre):
       #? self.down_single_thread.start()
       
       yt = YouTube( Link )
       #? , on_progress_callback = self.Handle_progress
       yt.video_id
       streams = yt.streams
    
       video_id = do.get_video_id(yt.watch_url)
    
       for i in ( '\\' , ':' , '*' , '\"' , '>' , '<' , '?' , '|' , ' ' ,  '^' , '.' ):
            yt.title = yt.title.replace(i,"_")

       if trans_per == True:
              do.download_transcript( video_id , Path , yt.title )

       if audio_pre:
             do.download_audio( yt.watch_url , Path ) 
       else:
    
          if not do.is_res_found( streams , resolution_of_vedios ):
              resolution_of_vedios = yt.streams.get_highest_resolution()
          video_stream = yt.streams.filter( res = resolution_of_vedios , file_extension = 'mp4' ).first()
          video_stream.download( Path , filename = yt.title+".mp4" ) 
   


def main():
    app = QApplication(sys.argv)
    window = Mainapp()
    window.show()
#    app.thread()
    app.exec_()
    


if __name__ == "__main__":

    main()
