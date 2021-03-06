import editor
from   objc_util import *
import ui

@on_main_thread
def test(tv):
	import console
	import re
	import ui
	tv.find = console.input_alert('text or regex to search', '', tv.find, hide_cancel_button=True)
	txt = tv.find

	for sv in tv.subviews():
		if 'SUIButton_PY3' in str(sv._get_objc_classname()):
			sv.removeFromSuperview()
	if txt == '':
		return
	t = str(tv.text())
	#print('search',txt,'in',t)
	#for m in re.finditer('(?i)'+txt, t):
	for m in re.finditer(txt, t):
		st,en = m.span()
		p1 = tv.positionFromPosition_offset_(tv.beginningOfDocument(), st)
		p2 = tv.positionFromPosition_offset_(tv.beginningOfDocument(), en)
		rge = tv.textRangeFromPosition_toPosition_(p1,p2)
		rect = tv.firstRectForRange_(rge)	# CGRect
		x,y = rect.origin.x,rect.origin.y
		w,h = rect.size.width,rect.size.height
		#print(x,y,w,h)
		l = ui.Button()
		l.frame = (x,y,w,h)
		if '|' not in txt:
			l.background_color = (1,0,0,0.2)
		else:
			# search multiple strings
			wrds = txt.split('|')
			idx = wrds.index(t[st:en])
			cols = [(1,0,0,0.2), (0,1,0,0.2), (0,0,1,0.2), (1,1,0,0.2), (1,0,1,0.2), (0,1,1,0.2)]
			col = cols[idx % len(cols)]
			l.background_color = col
		l.corner_radius = 4
		l.border_width = 1
		tv.addSubview_(l)

def key_pressed(sender):
		import ui
		from objc_util import ObjCClass
		tv = sender.objc_instance.firstResponder()	# associated TextView
		# get actual cursor position					
		cursor = tv.offsetFromPosition_toPosition_(tv.beginningOfDocument(), tv.selectedTextRange().start())
		
		if sender.name == 'left':	
			if cursor == 0:
				return												# already first character
			cursor = cursor - 1							
		elif sender.name == 'right':	
			if cursor == (len(str(tv.text()))-1):
				return												# already after last character
			cursor = cursor + 1		
		elif sender.name == 'down':			
			# surely not correct because not tested in limit cases,
			# just to show for topic https://forum.omz-software.com/topic/6408/defining-a-line-up-line-down-keyboard-function
			# count position in line
			c = str(tv.text()).rfind('\n',0,cursor)	# begin of current line
			p = cursor - c
			e = str(tv.text()).find('\n',cursor)		# end   of current line
			cursor = e + 1													# begin of next line
			e = str(tv.text()).find('\n',cursor)		# end   of next line
			cursor = cursor + min(p-1,e-cursor)
		elif sender.name == 'next word':
			t = str(tv.text())[cursor+1:]	
			for i in range(0,len(t)):
				# search 1st separator
				if t[i] in ' _.\n\t':
					# search 1st not separator
					ch_found = False
					for j in range(i+1,len(t)):
						if t[j] not in ' _.\n\t':
							ch_found = True
							cursor = cursor + 1 + j
							break
					if ch_found:
						break
		elif sender.name == 'delete':						
			# delete at right = delete at left of next character
			if cursor == (len(str(tv.text()))-1):
				return												# already after last character
			cursor_position = tv.positionFromPosition_offset_(tv.beginningOfDocument(), cursor+1)
			tv.selectedTextRange = tv.textRangeFromPosition_toPosition_(cursor_position, cursor_position)
			tv.deleteBackward()							
		elif sender.name == 'find':
			test(tv)
		else:
			# normal key
			tv.insertText_(sender.title)	
			return
		# set cursor
		cursor_position = tv.positionFromPosition_offset_(tv.beginningOfDocument(), cursor)
		tv.selectedTextRange = tv.textRangeFromPosition_toPosition_(cursor_position, cursor_position)	

class MyView(ui.View):
	def __init__(self, pad, *args, **kwargs):
		#super().__init__(self, *args, **kwargs)	
		self.width = ui.get_screen_size()[0]			# width of keyboard = screen
		self.background_color = 'lightgray'#(0,1,0,0.2)
		self.h_button = 32	
		self.pad = pad

		#================================================ for the fun begin		
		# cable for road
		self.road = ui.Label()
		self.road.frame = (0,40,self.width,1)
		self.road.border_width = 1
		self.road.border_color = 'green'
		self.road.flex = 'W'
		self.add_subview(self.road)
		
		# cable for tramway
		self.line = ui.Label()
		self.line.frame = (0,12,self.width,1)
		self.line.border_width = 1
		self.line.border_color = 'gray'
		self.line.flex = 'W'
		self.line.hidden = True
		self.add_subview(self.line)
		
		# moving emoji behind buttons
		self.moving = ui.Button()
		self.moving.font = ('<system>',self.h_button-4)
		self.moving.frame = (0,10,self.h_button,self.h_button)
		self.moving.icons = ['emj:Delivery_Truck', 'emj:Car_1','emj:Car_2', 'emj:Bus', 'emj:Police_Car', 'emj:Railway_Car','emj:Speedboat']
		self.moving.action = self.fun
		self.moving.index = 0
		self.add_subview(self.moving)
		self.update_interval = 0.06
		#================================================ for the fun end
		
		# build buttons
		for pad_elem in self.pad:
			if pad_elem['key'] in ('nul', 'new row'):		#  free space or new row
				continue
			button = ui.Button()									# Button for user functionnality
			button.name = pad_elem['key']
			button.background_color = 'white'			# or any other color
			button.tint_color = 'black'
			button.corner_radius = 5		
			button.font = ('<system>',self.h_button - 8)
			button.title = ''
			if 'title' in pad_elem:
				button.title = pad_elem['title']
			elif 'icon' in pad_elem:
				button.image = ui.Image.named(pad_elem['icon']).with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
			else:
				button.title = pad_elem['key']

			button.action = key_pressed
			retain_global(button) # see https://forum.omz-software.com/topic/4653/button-action-not-called-when-view-is-added-to-native-view
			self.add_subview(button)	
		self.layout()		

	#================================================ for the fun begin		
	def fun(self,sender):	
			self.update_interval = 0.06 - self.update_interval
			
	def update(self):
		import ui
		x = self.moving.x - 5
		if x < -self.moving.width:
			x = ui.get_screen_size()[0]
			self.moving.index = self.moving.index+1
			if self.moving.index == len(self.moving.icons):
				self.moving.index = 0
			emoji = self.moving.icons[self.moving.index]
			self.moving.image = ui.Image.named(emoji).with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
			self.line.hidden = not (emoji == 'emj:Railway_Car')
			self.road.border_color = 'blue' if emoji == 'emj:Speedboat' else 'green'
		self.moving.x = x
		#================================================ for the fun end

	def layout(self):
		import ui
		#print('layout')
		# supports changing orientation
		#print(ui.get_screen_size())
		dx = 8
		dy = 2
		x0 = 15
		y0 = 10
		dx_middle = 25 
		y = y0
		x = x0
		w_button = (ui.get_screen_size()[0] - 2*x0 - 17*dx - dx_middle)/18
		for pad_elem in self.pad:
			nw = pad_elem.get('width', 1)
			wb = w_button*nw + dx*(nw-1)
			if (x + wb + dx) > self.width:
				y = y + self.h_button + dy
				x = x0
			if pad_elem['key'] == 'nul':					# let free space	
				x = x + wb + dx	
				continue
			elif pad_elem['key'] == 'new row':		# new row
				y = y + self.h_button + dy
				x = x0
				continue
			button = self[pad_elem['key']]
			xb = x + dx_middle if (x+wb) > self.width/2 else x
			button.frame = (xb,y,wb,self.h_button)
			if button.title != '':
				font_size = self.h_button - 8
				while True:
					d = ui.measure_string(button.title,font=(button.font[0],font_size))[0]+4
					if d <= wb:
						break
					font_size = font_size - 1			
			button.font = (button.font[0],font_size)
			x = x + wb + dx
		self.height = y + self.h_button + dy	
	
@on_main_thread	
def AddButtonsToPythonistaKeyboard(pad=None):
	if not pad:
		pad = [
		{'key':'next word','width':2},
		{'key':'find','icon':'iob:ios7_search_32'},
		{'key':'nul'},
		{'key':'>'},
#		{'key':'new row'},
		{'key':'nul'},
		{'key':'nul'},
		{'key':'#'},
		{'key':'nul'},
		{'key':'"'},
		{'key':'nul'},
		{'key':'left','icon':'iob:arrow_left_a_32'},
		{'key':'right','icon':'iob:arrow_right_a_32'},
		{'key':'down','icon':'iob:arrow_down_a_32'},
		{'key':'\\'},
		{'key':'nul'},
		{'key':'delete','title':'Del'}]
		
	ev = editor._get_editor_tab().editorView()
	tv = ev.textView()
	#print(tv._get_objc_classname())
	#print(dir(tv))
	
	# create ui.View for InputAccessoryView above keyboard
	v = MyView(pad)												# view above keyboard
	vo = ObjCInstance(v)									# get ObjectiveC object of v
	retain_global(v) # see https://forum.omz-software.com/topic/4653/button-action-not-called-when-view-is-added-to-native-view
	tv.setInputAccessoryView_(vo)	# attach accessory to textview
	tv.find = ''

if __name__ == '__main__':	
	AddButtonsToPythonistaKeyboard()
