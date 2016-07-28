#!/usr/bin/env python

# This file is part of Openplotter.
# Copyright (C) 2015 by sailoog <https://github.com/sailoog/openplotter>
#
# Openplotter is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# any later version.
# Openplotter is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Openplotter. If not, see <http://www.gnu.org/licenses/>.

import wx, sys, socket, threading, time
from classes.datastream import DataStream
from classes.paths import Paths
from classes.conf import Conf
from classes.language import Language

class MyFrame(wx.Frame):
		
		def __init__(self):
			Quelle='127.0.0.1' # Adresse des eigenen Rechners
			Port=55560
			 
			self.e_udp_sock = socket.socket( socket.AF_INET,  socket.SOCK_DGRAM ) #s.o.
			self.e_udp_sock.bind( (Quelle,Port) )

			self.ttimer=100
			
			self.home=Paths().home
			self.currentpath=Paths().currentpath
			self.conf=Conf()
			
			Language(self.conf.get('GENERAL','lang'))

			list_N2K_txt=[]
			self.list_N2K=[]
			with open(self.home+'/.config/openplotter/classes/N2K_PGN.csv') as f:
				list_N2K_txt = [x.strip('\n\r').split(',') for x in f.readlines()]
			
			for ii in list_N2K_txt:
				pgn=int(ii[0])
				self.list_N2K.append([pgn,ii[1]])
			
			Buf_ = (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)
			self.Buffer = bytearray(Buf_)
			self.Zustand=6
			self.list_iter=[]

			wx.Frame.__init__(self, None, title='diagnostic N2K output', size=(650,435))
			self.Bind(wx.EVT_CLOSE, self.OnClose)
			
			self.timer = wx.Timer(self)
			self.Bind(wx.EVT_TIMER, self.timer_act, self.timer)
						
			self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
			
			self.icon = wx.Icon(self.currentpath+'/openplotter.ico', wx.BITMAP_TYPE_ICO)
			self.SetIcon(self.icon)

			self.list = wx.ListCtrl(self, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER, size=(540, 370), pos=(5, 5))
			self.list.InsertColumn(0, _('PGN'), wx.LIST_FORMAT_RIGHT, width=62)
			self.list.InsertColumn(1, _('SRC'), wx.LIST_FORMAT_RIGHT, width=38)
			self.list.InsertColumn(2, _('DST'), wx.LIST_FORMAT_RIGHT, width=38)
			self.list.InsertColumn(3, _('Name'), width=180)
			self.list.InsertColumn(4, _('Interval'), wx.LIST_FORMAT_RIGHT, width=45)
			self.list.InsertColumn(5, _('Data'), width=350)

			self.sort_PGN_b =wx.Button(self, label=_('Sort PGN'), pos=(555, 160))
			self.Bind(wx.EVT_BUTTON, self.sort_PGN, self.sort_PGN_b)

			self.sort_SRC_b =wx.Button(self, label=_('Sort SRC'), pos=(555, 200))
			self.Bind(wx.EVT_BUTTON, self.sort_SRC, self.sort_SRC_b)

			self.CreateStatusBar()

			self.Show(True)

			self.status=''
			self.data=[]
			self.baudc=0
			self.baud=0

			self.timer.Start(self.ttimer)
			
		def timer_act(self, event):		
			data1, addr = self.e_udp_sock.recvfrom( 1024 )
			# Die Puffergroesse muss immer eine Potenz
			# von 2 sein
			data=bytearray(data1)
			if data[7]+9==len(data):
				self.output(data)				
			
		def sort_PGN(self, e):
			self.timer.Stop()
			self.list_iter.sort()
			self.list.DeleteAllItems()
			self.init2()
			self.timer.Start(self.ttimer)

		def sort_SRC(self, e):
			self.timer.Stop()
			self.list.DeleteAllItems()

			list_new=[]
			for i in sorted(self.list_iter, key=lambda item: (item[1], item[0])):
				list_new.append(i)
			self.list_iter=list_new
			self.init2()
			self.timer.Start(self.ttimer)
			
		def init2(self):
			index=0		
			for i in self.list_iter:
				self.list.InsertStringItem(index, str(i[0]))
				self.list.SetStringItem(index, 1, str(i[1]))
				self.list.SetStringItem(index, 2, str(i[2]))
				self.list.SetStringItem(index, 3, str(i[3]))
				self.list.SetStringItem(index, 4, str(i[4]))
				self.list.SetStringItem(index, 5, '')
				index+=1
								
		def OnClose(self, event):
			self.timer.Stop()
			self.Destroy()

		def output(self,data):
			k = 0
			Buffer=bytearray(data)
			if Buffer[0] == 0x94:				
				nPriority = Buffer[2]
				lPGN=Buffer[3]+Buffer[4]*256+Buffer[5]*256*256
				nDestAddr = Buffer[6];
				nSrcAddr = 'own'
				length = Buffer[7];

				datap=''
				data=0
				for i in range(8,8+length):
					data=data+Buffer[i];
					datap+=' '+('0'+hex(Buffer[i])[2:])[-2:]
					
				#print lPGN, nSrcAddr, nDestAddr, datap
				
				exist=0
				index=0
				tt=time.time()
				for i in self.list_iter:
					if nSrcAddr==i[1]:
						if lPGN==i[0]:
							td=round(i[4]*0.3+0.7*(tt-i[5]),1)
							self.list_iter[index][4]=td
							self.list_iter[index][5]=tt							
							self.list.SetStringItem(index,4,str(td))
							self.list.SetStringItem(index,5,str(datap))
							self.Update()
							exist=1
					index+=1						
				if exist==0:				
					self.list.InsertStringItem(index, str(lPGN))
					self.list.SetStringItem(index, 1, str(nSrcAddr))
					self.list.SetStringItem(index, 2, str(nDestAddr))
					for ii in self.list_N2K:
						if lPGN==ii[0]:
							self.list.SetStringItem(index, 3, ii[1])
					self.list.SetStringItem(index, 4, 'X')
					self.list.SetStringItem(index, 5, datap)
					self.list_iter.append([lPGN,nSrcAddr,nDestAddr,self.list.GetItem(index, 3).GetText(),0,tt])
										
app = wx.App()
MyFrame().Show()
app.MainLoop()