import datetime
from io import TextIOWrapper
from typing import List
from pydantic import BaseModel
from  rich import print
from moviepy.editor import VideoFileClip

FORMAT = """{}\n{} --> {}\n{}\n"""

class Subtitles(BaseModel):
    count: int
    start_time: datetime.time
    end_time: datetime.time
    text: str


class subtitles:
    def __init__(self,filename:str):
        self.filename = filename
        self.subtitle :List[Subtitles]= []
        self.segments = -1
        self.video_duration = 0
        self.doIt()

    def doIt(self):
        with open(self.filename, 'r') as f:
            while True:
                self.subtitle.append(self.scrape(f))
                self.segments+=1
                if (self.subtitle[self.segments]==None):
                    self.subtitle.pop()
                    break



    @staticmethod
    def getStartTime(subtitle_time: str):
        temp = subtitle_time.split('-->')[0].replace(",", ":").split(':')
        return datetime.time(int(temp[0]), int(temp[1]), int(temp[2]), int(temp[3]))

    @staticmethod
    def getEndTime(subtitle_time: str):
        temp = subtitle_time.split('-->')[1].replace(",", ":").replace("\n", "").replace(" ", "").split(':')
        return datetime.time(int(temp[0]), int(temp[1]), int(temp[2]), int(temp[3]))

    
    def getStartEndTime(self,subtitle_time: str):
        return (self.getStartTime(subtitle_time=subtitle_time),self.getEndTime(subtitle_time))
    
    @staticmethod
    def readSubtitle(file_ptr):
        sub_text : str = ''
        for line in file_ptr:
            if (line == "\n"):
                break
            sub_text += line
        return sub_text

    def scrape(self,file_ptr: TextIOWrapper):
        line = None
        for line in file_ptr:
            if (line != "\n"):
                break
        if line == None:
                return None

        count = int(line.strip())
        start_time , end_time = self.getStartEndTime(file_ptr.readline())
        text = self.readSubtitle(file_ptr)
        return Subtitles(count=count, start_time=start_time, end_time=end_time,text=text)

    def write(self,filename:str):
        with open(filename, 'w') as file:
            for i in self.subtitle:
                self.write_subtitle(i,file)

    @staticmethod
    def find_offset(time_standard,time_offset):
        date = datetime.date(1, 1, 1)
        datetime1 = datetime.datetime.combine(date, time_standard)
        datetime2 = datetime.datetime.combine(date, time_offset)
        return datetime1 - datetime2


    def write_subtitle(self,obj:Subtitles,offset=datetime.time(),file_ptr:TextIOWrapper=None,count=0,resetNumbers:bool=False):
        s= str(self.find_offset(obj.start_time,offset))
        e =str(self.find_offset(obj.end_time,offset))
        file_ptr.write(FORMAT.format(next(count) if resetNumbers else obj.count ,s[:-6]+s[-3:],e[:-6]+e[-3:],obj.text))


    def split(self,split_time:datetime.time,split_file_1:str,split_file_2:str,resetNumbers:bool=False,reWriteTime:datetime.time=datetime.time()):
        flag= 0
        with open(split_file_1,"w") as file:
            while 1:
                #print(self.subtitle[flag].start_time , split_time)
                if self.subtitle[flag].start_time > split_time:
                    break
                self.write_subtitle(obj=self.subtitle[flag],file_ptr=file)
                flag+=1
        
        count_range =iter(range(1,self.segments-flag+2))
        with open(split_file_2,"w") as file:
                for i in range(flag,self.segments):
                    self.write_subtitle(obj=self.subtitle[i],file_ptr=file,resetNumbers=resetNumbers,count=count_range,offset=split_time)
    @staticmethod
    def getvideoduration(filename):
        return int(VideoFileClip(filename).duration)


    @staticmethod
    def convert(seconds):
        seconds = seconds % (24 * 3600)
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        return datetime.time(hour=hour,minute=minutes,second=seconds)

    def split_by_video(self,filename,split_file_1:str,split_file_2:str,resetNumbers:bool=False):
        split_time = self.convert(self.getvideoduration(filename))
        self.split(split_time,split_file_1,split_file_2,resetNumbers)








