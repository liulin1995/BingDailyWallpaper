# -*- coding: utf-8 -*-
"""
Created on Thu May  9 09:52:47 2019

@author: liu
"""

import requests
import random
import datetime
import os
import re
import wx
 
class BingPhoto(wx.App):
    def __init__(self, redirect=False, filename=None):
        wx.App.__init__(self, redirect, filename)
        self.frame = wx.Frame(None, title='Daily Bing Photo')
        self.img_folder = './images'
        self.panel = wx.Panel(self.frame)
 
        self.PhotoMaxSize = 1600
        self.now_img = self.pick_one_image()
        self.createWidgets()
        self.frame.Centre()
        self.frame.Show()
 
    def createWidgets(self):
        img = wx.Image(self.now_img)
        img = self.img_scale(img)
        self.imageCtrl = wx.StaticBitmap(self.panel, wx.ID_ANY, 
                                         wx.Bitmap(img))
        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        Item1 = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        Item2 = fileMenu.Append(wx.ID_ANY, 'Fresh', 'Fresh the photo')
        Item3 = fileMenu.Append(wx.ID_ANY, 'PickOne', 'Random pick one photo')
        menubar.Append(fileMenu, '&File')
        self.frame.SetMenuBar(menubar)
        self.frame.SetIcon(wx.Icon('bing.png'))
        self.frame.Bind(wx.EVT_MENU, self.OnQuit, Item1)
        self.frame.Bind(wx.EVT_MENU, self.onFresh, Item2)
        self.frame.Bind(wx.EVT_MENU, self.onPickOne, Item3)
        
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(self.imageCtrl, 0, wx.ALL, 5)
        self.panel.SetSizer(self.mainSizer)
        self.mainSizer.Fit(self.frame)
        self.panel.Layout()
 
    def onFresh(self, e):
        today_filepath = self.if_today_file_exist()
        if today_filepath is None:
            self.download_image()
            today_filepath = self.if_today_file_exist()
            print(today_filepath)
        self.now_img = today_filepath
        img = wx.Image(today_filepath)
        img = self.img_scale(img)
 
        self.imageCtrl.SetBitmap(wx.Bitmap(img))
        self.panel.Refresh()
        
    def onPickOne(self, e):
        choice_img = self.pick_one_image()
        self.now_img = choice_img
        img = wx.Image(choice_img)
        img = self.img_scale(img)
        self.imageCtrl.SetBitmap(wx.Bitmap(img))
        self.panel.Refresh()
        
    def today_filename(self):
        d = datetime.datetime.now()
        name = d.strftime('%Y %m %d')
        return name
    
    def pick_one_image(self):
        if not os.path.exists(self.img_folder):
            os.mkdir(self.img_folder)
        file_paths = os.listdir(self.img_folder)
        img_types = ['.jpg','.png']
        img_paths = [f for f in file_paths for types in img_types if types in f]
        pick_img_path = random.choice(img_paths)
        return os.path.join(self.img_folder,pick_img_path)
        
    
    def if_today_file_exist(self):
        img_types = ['.jpg','.png']
        if not os.path.exists(self.img_folder):
            os.mkdir(self.img_folder)

        today_filenames = [self.today_filename() + i for i in img_types]
        for i in today_filenames:
            i_name = os.path.join(self.img_folder, i)
            if os.path.isfile(i_name):
                return i_name
        else:
            return None
    
    def img_scale(self, img):
        # scale the image, preserving the aspect ratio
        W = img.GetWidth()
        H = img.GetHeight()
        if W > H:
            NewW = self.PhotoMaxSize
            NewH = self.PhotoMaxSize * H / W
        else:
            NewH = self.PhotoMaxSize
            NewW = self.PhotoMaxSize * W / H
        img = img.Scale(NewW,NewH)
        return img
        
    def OnQuit(self, e):
        self.frame.Close()
        
    def download_image(self):
        bing_url = 'https://cn.bing.com'
        headers = {
                "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
                }
        r = requests.get(bing_url,headers=headers)
        if r.status_code == 200:
            print('Successful get the html file')
        else:
            print('Fail to get the html file')
            return 
        r.encoding="utf-8"
        html = r.text
        regex_1 = re.search(r'background-image:url\((.*?)\)', html,re.S)
        img_url = bing_url + regex_1.group(1)[:-7]
        img_type = img_url[-4:]
        img_path = os.path.join(self.img_folder, self.today_filename() + img_type)
        img_file = requests.get(img_url)
        with open(img_path, 'wb') as f:
            f.write(img_file.content)
    
if __name__ == '__main__':
    app = BingPhoto()
    app.MainLoop()