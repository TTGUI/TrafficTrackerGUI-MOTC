
from .ui_BaseManager import BaseManager

class DisplayinfoManager(BaseManager):
    """本類別處理 Displayinfo 的文字、功能綁定、功能函數"""
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        
        self.initText()     # 初始化按鈕文字
        self.bind_buttons() # 綁定按鈕與槽

    def initText(self):
        self.main_window._window.ForwardPage_btn.setText('<<== Page')
        self.main_window._window.NextPage_btn.setText('Page ==>>')
        self.main_window._window.Back_btn.setText('▲ Back')
        self.main_window._window.Next_btn.setText('▼ Next')

    def bind_buttons(self):
        self.main_window._window.ForwardPage_btn.clicked.connect(self.forwardPage)
        self.main_window._window.NextPage_btn.clicked.connect(self.nextPage)
        self.main_window._window.Back_btn.clicked.connect(self.back)
        self.main_window._window.Next_btn.clicked.connect(self.next)

    def forwardPage(self):
        if self.main_window.scheduleType == 'edit' : # 在Schedule 編輯模式
            if self.main_window.page > 0:
                self.main_window.page = self.main_window.page -1
                self.main_window.currentScheduleIndex = self.main_window.page * self.main_window.pageLen
            elif self.main_window.page == 0 :
                self.main_window.currentScheduleIndex = 0
            self.displayInfo(3)
        elif self.main_window.currentStep == 9 and self.main_window.TIVPmode == 3 : # 在TIVP Realtime 模式
            if self.main_window.page > 0:
                self.main_window.page = self.main_window.page -1
                self.main_window.currentIssueIndex = self.main_window.page * self.main_window.pageLen
            elif self.main_window.page == 0 :
                self.main_window.currentIssueIndex = 0
            self.displayInfo(4)
        else:                                                                      # 在Step 0 模式
            if self.main_window.page > 0:
                self.main_window.page = self.main_window.page -1
                self.main_window.currentVideoIndex = self.main_window.page * self.main_window.pageLen
            elif self.main_window.page == 0 :
                self.main_window.currentVideoIndex = 0
            self.displayInfo(1)
            self.main_window.PlayerManager.load()

    def nextPage(self):
        if self.main_window.scheduleType  == 'edit' : # 在Schedule 編輯模式
            if self.main_window.page < int((len(self.main_window.ScheduleList)-1) / self.main_window.pageLen ):
                self.main_window.page = self.main_window.page + 1
                self.main_window.currentScheduleIndex = self.main_window.page * self.main_window.pageLen
            self.displayInfo(3)
        elif self.main_window.currentStep == 9 and self.main_window.TIVPmode == 3 : # 在TIVP Realtime 模式          

            if self.main_window.page < int((len(self.main_window.TIVIsampleList)-1) / self.main_window.pageLen ):
                self.main_window.page = self.main_window.page + 1
                self.main_window.currentIssueIndex = self.main_window.page * self.main_window.pageLen
            self.displayInfo(4)
        else:                                                                       # 在Step 0 模式
            if self.main_window.page < int((self.main_window.videoLen-1) / self.main_window.pageLen ):
                self.main_window.page = self.main_window.page + 1
                self.main_window.currentVideoIndex = self.main_window.page * self.main_window.pageLen
            self.displayInfo(1)
            self.main_window.PlayerManager.load()

    def back(self):
        if self.main_window.scheduleType == 'edit' : # 在Schedule 編輯模式
            if self.main_window.currentScheduleIndex > 0 :
                self.main_window.currentScheduleIndex = self.main_window.currentScheduleIndex - 1
                
                self.displayInfo(3)
        elif self.main_window.currentStep == 9 and self.main_window.TIVPmode == 3 : # 在TIVP Realtime 模式
            if self.main_window.currentIssueIndex > 0 :
                self.main_window.currentIssueIndex -= 1
            self.displayInfo(4)  
        elif self.main_window.currentVideoIndex > 0 : # 在Step 0 模式
            self.main_window.currentVideoIndex = self.main_window.currentVideoIndex - 1
            self.displayInfo(2) 
            self.main_window.PlayerManager.load()

    def next(self):
        if self.main_window.scheduleType == 'edit' : # 在Schedule 編輯模式
            if self.main_window.currentScheduleIndex < len(self.main_window.ScheduleList) - 1 :
                self.main_window.currentScheduleIndex = self.main_window.currentScheduleIndex + 1
                
                self.displayInfo(3)
        elif self.main_window.currentStep == 9 and self.main_window.TIVPmode == 3 : # 在TIVP Realtime 模式
            if self.main_window.currentIssueIndex < len(self.main_window.TIVIsampleList) - 1:
                self.main_window.currentIssueIndex += 1
            self.displayInfo(4)
        elif self.main_window.currentVideoIndex < self.main_window.videoLen - 1 : # 在Step 0 模式
            self.main_window.currentVideoIndex = self.main_window.currentVideoIndex + 1
            self.displayInfo(2) 
            self.main_window.PlayerManager.load()

