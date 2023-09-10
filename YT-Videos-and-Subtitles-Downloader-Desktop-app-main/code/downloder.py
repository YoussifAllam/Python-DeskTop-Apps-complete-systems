import re
from pytube import *
from youtube_transcript_api import YouTubeTranscriptApi as yt
from youtube_transcript_api.formatters import SRTFormatter
import os
import http.client

#from  main  import *




def download_playlist( Link , Path , resolution_of_vedios , subtitle_pre , audio_pre) :
   invalid_vedios=[]
   playlist = Playlist( Link )   
   
   DOWNLOAD_PATH = r'{}'.format( Path )
   
   playlist._video_regex = re.compile( r"\"url\":\"(/watch\?v=[\w-]*)" )  
   for video in playlist.videos:
        video_id = get_video_id(video.watch_url)
        for i in ( '\\' , ':' , '*' , '\"' , '>' , '<' , '?' , '|' , ' ' ,  '^' , '.' ):
            video.title = video.title.replace(i,"_")
        if subtitle_pre == True:
              download_transcript( video_id , DOWNLOAD_PATH , video.title )
        
        if audio_pre:
           download_audio( video.watch_url, DOWNLOAD_PATH ) 
        else:
            yt= YouTube(video.watch_url)
            streams = yt.streams
            if not is_res_found( streams , resolution_of_vedios ):
                resolution_of_vedios = yt.streams.get_highest_resolution()
            
            video.streams.\
            filter( type = 'video' , progressive = True , file_extension = 'mp4' ,  res = resolution_of_vedios ).\
            order_by( 'resolution' ).\
            desc().\
            first().\
            download( DOWNLOAD_PATH )
       
        
  
   return invalid_vedios


def get_number_of_Vedios(URL):
    playlist = Playlist( URL )
    return len(playlist.videos)


def s_download(video ,resolution_of_vedios , DOWNLOAD_PATH ):
        invalid_vedios=[]
        try:
            video.streams.\
            filter( type = 'video' , progressive = True , file_extension = 'mp4' ,  res = resolution_of_vedios ).\
            order_by( 'resolution' ).\
            desc().\
            first().\
            download( DOWNLOAD_PATH )
        except AttributeError:
            invalid_vedios += str(video.watch_url)
            
        except http.client.IncompleteRead as e:
            invalid_vedios += str(video.watch_url)
            

def is_res_found(streams , resolution_of_vedios):
   bool=False
   for stream in streams:
     if stream.resolution == resolution_of_vedios:
        bool =True
        return bool
   else:
       bool =False
       return bool


def get_video_id(url):
  video_id = url.split("=")[-1]
  return video_id


def download_transcript( video_id , trans_path , filename ):
   transcript = yt.get_transcript( video_id , languages = ['en'] )
   formatter = SRTFormatter()

   STR_formatted = formatter.format_transcript( transcript )
   new_file_name = trans_path+r"\{}.srt".format( filename )
   old = trans_path + "\\aaa.srt"

   filepath = os.path.join( trans_path , old )
   
   with open( filepath , 'w', encoding = 'utf-8' ) as STR_file :
       STR_file.write( STR_formatted )

   os.rename(  old , new_file_name )
   

def download_sigle(Link , Path , resolution_of_vedios  , trans_per , audio_pre):
    yt = YouTube(Link)
    yt.video_id
    streams = yt.streams
    
    video_id = get_video_id(yt.watch_url)
    
    for i in ( '\\' , ':' , '*' , '\"' , '>' , '<' , '?' , '|' , ' ' ,  '^' , '.' ):
            yt.title = yt.title.replace(i,"_")

    if trans_per == True:
              download_transcript( video_id , Path , yt.title )

    if audio_pre:
             download_audio( yt.watch_url , Path ) 
    else:
    
       if not is_res_found( streams , resolution_of_vedios ):
              resolution_of_vedios = yt.streams.get_highest_resolution()
       video_stream = yt.streams.filter( res = resolution_of_vedios , file_extension = 'mp4' ).first()
       video_stream.download( Path , filename = yt.title+".mp4" )
    

def download_audio(link, download_path):
    yt = YouTube(link)
    streams = yt.streams
    audio_streams = streams.filter(only_audio=True)
    audio_stream = audio_streams[0]
    audio_stream.download(download_path , filename = yt.title+'.mp3')


def get_size_ofvedios( video_link , resolution_of_vedios ):

    video = YouTube(video_link)
    #video_size = video.streams.filter( res = resolution_of_vedios , file_extension = 'mp4' ).filesize()
   # video_size = video.streams.get_highest_resolution().filesize / (1024*1024)
    video_size = video.streams.get_by_itag(17).filesize / (1024*1024)
    #stream = yt.streams.get_by_resolution(resolution_of_vedios)
    print(video_size)
    






  