import requests
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QInputDialog, QTextBrowser, qApp, QMessageBox
import sys
import re
import os

class NeteaseMusicDownloader(QWidget):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        }
    
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.resize(600, 480)
        self.setWindowTitle('网易云歌单下载器')

        # 歌单地址输入按钮
        self.url_buttton = QPushButton('输入歌单网址',self)
        self.url_buttton.setGeometry(40, 50, 100, 30)
        self.url_buttton.clicked.connect(self.inputUrl)

        # 歌单名显示框
        self.list_title_display = QTextBrowser(self)
        self.list_title_display.setGeometry(150, 50, 400, 30)
        self.list_title_display.setStyleSheet('QLabel{background:white;border:1px solid grey;}')

        # 运行按钮
        self.start_button = QPushButton('开始下载', self)
        self.start_button.setGeometry(40, 90, 511, 35)
        self.start_button.clicked.connect(self.downloadMusic)

        # 运行状态显示框
        self.running_display = QTextBrowser(self)
        self.running_display.setGeometry(40, 150, 511, 300)
        self.running_display.setStyleSheet('QLabel{background:white;border:1px solid grey;}')
 
     
        self.show()
        

    # url输入框
    def inputUrl(self):
        self.listID, ok = QInputDialog.getText(self, '输入歌单地址', '歌单地址:')
        if ok:
            self.listID = re.findall(r'\d+', self.listID)[-1]
            self.getMusicList()

    # 爬取歌单信息
    def getMusicList(self):
        url = 'https://music.163.com/playlist?id=' + str(self.listID)
        response = requests.session().get(url, headers=self.headers).content
        soup = BeautifulSoup(response, 'lxml')
        self.title = soup.find('h2', {'class': "f-ff2 f-brk"}).string
        self.list_title_display.setText('歌单名称: '+self.title)
        music = soup.find('ul', {'class': 'f-hide'})
        self.songs = music.find_all('a')
        
    # 音乐下载
    def downloadMusic(self):
        is_path_exist = os.path.exists(self.title)
        if not is_path_exist:
            os.makedirs(self.title)
        for song in self.songs:
            name = song.text
            id = re.findall(r'\d+', str(song['href']))[-1]

            self.running_display.append('    正在下载:' + name + '...')
            QApplication.processEvents()
            try:
                url = 'https://music.163.com/song/media/outer/url?id=' + str(id) + '.mp3'
                data = requests.get(url, headers=self.headers)
                data.raise_for_status()
                with open(self.title + '/' + name + '.mp3', 'wb') as song:
                    song.write(data.content)
                self.running_display.append('下载成功!!!!')
            except:
                self.running_display.append('下载失败....')
        
        # 弹出成功提示
        self.finishMeassage()

    def finishMeassage(self):
        QMessageBox.about(self, '', '下载完成')
        self.list_title_display.clear()
        self.running_display.clear()
       
if __name__ == '__main__':
    app = QApplication(sys.argv)
    musicdownloader = NeteaseMusicDownloader()
    sys.exit(app.exec_())
