# $LAN=PYTHON3$

'''
Project     : Voronoi Diagram using divide and conquer
Author	    : 羅鈞煌
Student ID  : M093040040
Last update : 2020/11/30
'''

from tkinter import filedialog, messagebox, ttk
import tkinter as tk
import ctypes, re, math, os, time, copy, random

#點
class Point():
	def __init__(self, x, y):
		self.x = x
		self.y = y

	def get_point(self):
		return self.x, self.y

#邊
class Edge():
	def __init__(self, x1, y1, x2, y2, Point1 = None, Point2 = None, A = None, B = None, C = None):
		self.x1 = int(x1)
		self.y1 = int(y1)
		self.x2 = int(x2)
		self.y2 = int(y2)

		#方程式
		self.A = A
		self.B = B
		self.C = C

		#組成線的兩點(求垂直平分線的兩點)
		self.point1 = Point1
		self.point2 = Point2

	#回傳目前邊的兩點
	def get_point(self):
		return self.x1, self.y1, self.x2, self.y2

	#回傳組成這條線的兩點(求中垂線)
	def get_2_points(self):
		return self.point1.x, self.point1.y, self.point2.x, self.point2.y

	#回傳方程式 (A * x + B * y + C)
	def get_equations(self):
		return self.A, self.B, self.C

	#回傳組成這條線組成的兩點，目前點的另一個點
	def another_point(self, p):
		if(p.x == self.point1.x and p.y == self.point1.y):
			return self.point2
		else:
			return self.point1

	#更新Edge的兩點
	def Update_edge(self, x1, y1, x2, y2):
		self.x1 = int(x1)
		self.y1 = int(y1)
		self.x2 = int(x2)
		self.y2 = int(y2)
'''
Save Step By Step
Use Full Binary Tree
Data : Voronoi, Convex, HyperPlane, length

'''
class Node():
	def __init__(self):
		self.left = None
		self.right = None
		self.Voronoi = None
		self.Convex = None
		self.HP = None

	def Update_Information(self, Voronoi, Convex, HP, length):
		self.Voronoi = Voronoi
		self.Convex = Convex
		self.HP = HP
		self.length = length


#邊界大小
class Frame():
	'''
	(x, y)
	.---------
	|    x    |
	|		  |
	|y		  |
	|		  |
	 ---------.
			(x1, y1)
	'''
	def __init__(self, x, y, x1, y1):
		self.x = x
		self.y = y
		self.x1 = x1
		self.y1 = y1


class UI():#tk.Frame):
	def __init__(self, parent):
		self.parent = parent
		self.init()

	def init(self):
		self.File = False
		self.point = []
		self.edge = []

		screen_width = self.parent.winfo_screenwidth()
		screen_height = self.parent.winfo_screenheight()
		
		x = int(screen_width/2 - 900/2)
		y = int(screen_height/2 - 750/2)
		self.parent.title("Voronoi Diagram M093040040")
		self.parent.geometry("%dx%d+%d+%d" % (900, 750, x, y))

		self.menubar = tk.Menu(self.parent, tearoff = 0)
		self.menubar.add_command(label = "Read Input File", command = self.Read_Input_File)
		self.menubar.add_command(label = "Read Output File", command = self.Read_Output_File)
		self.menubar.add_command(label = "Save Result", command = self.Output_File)
		self.menubar.add_command(label = "Next Data", command = self.Read_Next_Data)
		self.menubar.add_command(label = "Run", command = self.Run)
		self.menubar.add_command(label = "Step by step", command = self.Step_by_step)
		self.menubar.add_command(label = "Clear Canvas", command = self.Clear_Canvas)
		self.parent.config(menu = self.menubar)

		self.frmU = tk.Frame(width = 900, height = 50)
		self.frmD = tk.Frame(width = 900, height = 700)
		self.frmU.grid_propagate(0)
		self.frmD.grid_propagate(0)
		self.frmU.grid(column = 0, row = 0)
		self.frmD.grid(column = 0, row = 1)

		label = tk.Label(self.frmU, text = "Amount : ")
		label.grid(column = 0, row = 0, padx = 10, pady = 10)
		self.entry = tk.Entry(self.frmU)
		self.entry.grid(column = 1, row = 0, padx = 10, pady = 10)
		Btn = tk.Button(self.frmU, text = "Random", command = self.Random_Point)
		Btn.grid(column = 2, row = 0, padx = 10, pady = 10)

		self.Canvas = tk.Canvas(self.frmD, width = 600, height = 600, highlightbackground = "black", highlightthickness = 1)
		self.Canvas.bind("<Button-1>", self.Add_Point)
		self.Canvas.grid(column = 0, row = 0, padx = 30, pady = 30)

		self.Point_Tree = ttk.Treeview(self.frmD, show="tree", columns=('x', 'y'), height = 25)
		self.Point_Tree['show'] = "headings"
		self.Point_Tree.column("x", width = 80, anchor = 'center')
		self.Point_Tree.column("y", width = 80, anchor = 'center')
		self.Point_Tree.heading("x", text = "X")
		self.Point_Tree.heading("y", text = "Y")
		self.Point_Tree.grid(column = 1, row = 0, sticky='ns', padx = 30, pady = 30)
		vsb = ttk.Scrollbar(self.frmD, orient="vertical", command=self.Point_Tree.yview)
		self.Point_Tree.configure(yscrollcommand = vsb.set)
		vsb.grid(column = 2, row = 0, sticky='ns')

		

	def Read_Input_File(self):
		filename = filedialog.askopenfilename(initialdir = "/", title = "Select file", filetypes = (("Text","*.txt"),("all files","*.*")))
		if filename != '':
			self.File = True
			self.Canvas.delete('all')
			self.point = []
			self.edge = []
			self.line = 0
			f = open(filename, 'r', encoding='UTF-8')
			self.lines = f.readlines()
			for l in self.lines:
				if(l[0] == "#" or l[0] == "\n"):
					self.line += 1
					continue
				elif(l[0] == "0"):
					self.File = False
					tk.messagebox.showinfo('info', "No Data")
					break
				else:
					n = int(re.findall('\d+', l)[0])
					self.line += 1
					for i in range(n):
						points = re.findall('\d+', self.lines[self.line])
						points = list(map(int, points))
						points = Point(points[0], points[1])
						self.point.append(points)
						self.line += 1
					break
			self.Draw_point()
			self.step = Node()
			self.isDone = False

	#讀取輸出檔
	def Read_Output_File(self):
		filename = filedialog.askopenfilename(initialdir = "/", title = "Select file", filetypes = (("Text","*.txt"),("all files","*.*")))
		if filename != '':
			self.Canvas.delete('all')
			self.point = []
			self.edge = []
			self.File = False
			f = open(filename, 'r')
			self.lines = f.readlines()

			for line in self.lines:
				if(line[0] == "P"):
					points = re.findall('-?\d+', line[2:])
					points = list(map(int, points))		
					points = Point(points[0], points[1])
					self.point.append(points)
				elif(line[0] == "E"):
					edges = re.findall('-?\d+', line[2:])
					edges = list(map(int, edges))
					edges = Edge(edges[0], edges[1], edges[2], edges[3])
					self.edge.append(edges)

			self.Draw_point()
			self.Draw_line(self.edge)

	def Output_File(self):
		self.edge.sort(key = lambda l: (l.x1, l.y1, l.x2, l.y2))
		file_name = filedialog.asksaveasfilename(confirmoverwrite=False, title="Save the file", initialfile = "output", defaultextension=".txt", filetypes = (("Text","*.txt"),("all files","*.*")))
		if(file_name):
			try:
				f = open(file_name, "w")
			except:
				f = open(file_name, "w")
			for p in self.point:
				f.write("P " + str(p.x) + " " + str(p.y) + "\n")
			for e in self.edge:
				f.write("E " + str(e.x1) + " " + str(e.y1) + " " + str(e.x2) + " " + str(e.y2) + "\n")
			f.close()

	def Read_Next_Data(self):
		#Read Next Data
		if(self.File):
			self.Canvas.delete('all')
			self.menubar.entryconfig("Save Result", state="disabled")
			self.point = []
			self.edge = []
			for l in range(self.line, len(self.lines)):
				if(self.lines[l][0] == "#"):
					self.line += 1
					continue
				elif(self.lines[l][0] == "0"):
					self.File = False
					tk.messagebox.showinfo('info', "No Data")
					break
				else:
					n = int(re.findall('\d+', self.lines[l])[0])
					self.line += 1
					for i in range(n):
						points = re.findall('\d+', self.lines[self.line])
						points = list(map(int, points))
						points = Point(points[0], points[1])
						self.point.append(points)
						self.line += 1
					break

			self.Draw_point()
			self.step = Node()
			self.isDone = False

	#Run
	def Run(self):
		frame = Frame(-10000, -10000, 10000, 10000)
		if(self.isDone == False):
			self.length = 0
			edge, Convex, HP = self.divide_and_conquer(self.point, frame, self.step, 0)
			self.isDone = True
			self.edge = edge
			self.Draw_point()
			self.Draw_Convex(Convex)
			self.Draw_line(edge)
		else:
			self.Draw_point()
			self.Draw_Step_by_step(self.step, 0, 1)

	#Run Step By Step
	def Step_by_step(self):
		frame = Frame(-10000, -10000, 10000, 10000)
		point = copy.deepcopy(self.point)
		if(self.isDone == False):
			self.length = 0
			edge, Convex, HP = self.divide_and_conquer(point, frame, self.step, 0)
			self.isDone = True
			self.edge = edge
		self.Draw_point()
		self.Draw_Step_by_step(self.step, 0)
		self.length -= 1
		time.sleep(0.5)
		

	def Clear_Canvas(self):
		self.point = []
		self.edge = []
		#self.menubar.entryconfig("Run", state="disabled")
		#self.menubar.entryconfig("Step by step", state="disabled")
		
		items = self.Point_Tree.get_children()
		self.Canvas.delete('all')
		[self.Point_Tree.delete(item) for item in items]


	def Add_Point(self, event):
		self.point.append(Point(event.x, event.y))
		self.Draw_point()
		self.step = Node()
		self.isDone = False

	def Draw_point(self):
		self.Canvas.delete('all')
		items = self.Point_Tree.get_children()
		[self.Point_Tree.delete(item) for item in items]
		self.point.sort(key = lambda l: (l.x, l.y))
		for i in range(len(self.point)):
			x = int(self.point[i].x)
			y = int(self.point[i].y)
			x1, y1 = (x - 1.5), (y - 1.5)
			x2, y2 = (x + 1.5), (y + 1.5)
			self.Canvas.create_oval(x1, y1, x2, y2, fill = "red", outline = "red")
			self.Point_Tree.insert('', 'end', text = str(i), value = (str(x), str(y)))

	def Draw_line(self, edge):
		if(len(edge) > 0):
			for e in edge:
				self.Canvas.create_line(e.get_point(), fill = "red")

	def Draw_Split_line(self, edge):
		x0 = int(edge.x1)
		y0 = int(edge.y1)
		x1 = int(edge.x2)
		y1 = int(edge.y2)
		self.Canvas.create_line(x0, y0, x1, y1, fill = "blue")

	def Draw_Convex(self, convex):
		for i in range(len(convex)):
			self.Canvas.create_line(convex[i].x, convex[i].y, convex[(i + 1) % len(convex)].x, convex[(i + 1) % len(convex)].y , fill = "blue", dash = (5, 1))

	#mode = 1， 直接輸出最後結果
	def Draw_Step_by_step(self, node, length, mode = None):
		if(node == None):
			return
		if(mode == 1):
			Voronoi = node.Voronoi
			Convex = node.Convex
			for v in Voronoi:
				self.Canvas.create_line(v.get_point(), fill = "red")
			for i in range(len(Convex)):
				self.Canvas.create_line(Convex[i].x, Convex[i].y, Convex[(i + 1) % len(Convex)].x, Convex[(i + 1) % len(Convex)].y , fill = "blue", dash = (3, 1))

			node.left = None
			node.right = None
			return

		if(node.left == None and node.right == None):
			if(self.length  == 0):
				Voronoi = node.Voronoi
				Convex = node.Convex
				for v in Voronoi:
					self.Canvas.create_line(v.get_point(), fill = "red")
				for i in range(len(Convex)):
					self.Canvas.create_line(Convex[i].x, Convex[i].y, Convex[(i + 1) % len(Convex)].x, Convex[(i + 1) % len(Convex)].y , fill = "blue", dash = (3, 1))

				node.left = None
				node.right = None
				return
			else:
				return

		if(node.left.left == None and node.left.right == None and node.right.left == None and node.right.right == None and self.length - 1 == length):
			Voronoi = node.left.Voronoi
			Convex = node.left.Convex
			for v in Voronoi:
				self.Canvas.create_line(v.get_point(), fill = "red")
			for i in range(len(Convex)):
				self.Canvas.create_line(Convex[i].x, Convex[i].y, Convex[(i + 1) % len(Convex)].x, Convex[(i + 1) % len(Convex)].y , fill = "red", dash = (3, 1))

			Voronoi = node.right.Voronoi
			Convex = node.right.Convex
			for v in Voronoi:
				self.Canvas.create_line(v.get_point(), fill = "green")
			for i in range(len(Convex)):
				self.Canvas.create_line(Convex[i].x, Convex[i].y, Convex[(i + 1) % len(Convex)].x, Convex[(i + 1) % len(Convex)].y , fill = "green", dash = (3, 1))
			
			HP = node.HP
			for h in HP:
				self.Canvas.create_line(h.get_point(), fill = "blue")
			node.left = None
			node.right = None
			return

		if(node.left != None):
			self.Draw_Step_by_step(node.left, length + 1)
		if(node.right != None):
			self.Draw_Step_by_step(node.right, length + 1)

	#隨機生成N個不重複的點
	def Random_Point(self):
		self.Clear_Canvas()
		n = self.entry.get()
		try:
			n = int(n)
		except:
			messagebox.showerror("Error", "請輸入數字")
			return
		point = []
		i = 0
		while(i < n):
			x = random.randint(0, 600)
			y = random.randint(0, 600)
			if([x, y] not in point):
				point.append([x, y])
				i += 1
		for p in point:
			self.point.append(Point(p[0], p[1]))
		self.Draw_point()
		self.step = Node()
		self.isDone = False

	'''
	Point  : All Points
	Frame  : 範圍
	node   : Save Step by Step
	length : Record depth of Tree 
	'''
	def divide_and_conquer(self, Point, frame, node, length):
		#Delete same Point
		S = []
		for p in Point:
			flag = True
			for p1 in S:
				if(p.x == p1.x and p.y == p1.y):
					flag = False
					break
			if(flag):
				S.append(p)
		n = len(S)

		if(n > 1):
			edge = []
			if(n == 2):
				A, B, C = midLine(S[0].x, S[0].y, S[1].x, S[1].y)
				if(A == 0 and B == 0): 
					node.Update_Information([], [], None, length)
					return [], [], None
				
				x_0, y_0, x_1, y_1 = Find_Point(A, B, C, frame)
				edge.append(Edge(round(x_0), round(y_0), round(x_1), round(y_1), S[0], S[1], A, B, C))
				convex = self.Divide_Convex_Hull(S)

				node.Update_Information(edge, convex, None, length)
				return edge, convex, None
			elif(n == 3):
				A = [None] * 3
				B = [None] * 3
				C = [None] * 3
				A[0], B[0], C[0] = midLine(S[0].x, S[0].y, S[1].x, S[1].y)
				A[1], B[1], C[1] = midLine(S[1].x, S[1].y, S[2].x, S[2].y)
				A[2], B[2], C[2] = midLine(S[0].x, S[0].y, S[2].x, S[2].y)
				c_x, c_y = circumcenter(A[0], B[0], C[0], A[1], B[1], C[1])
				O_T_side = Obtuse_triangle(S[0].x, S[0].y, S[1].x, S[1].y, S[2].x, S[2].y)
				if(c_x == None and c_y == None):
					index = 0
					for a, b, c in zip(A[:2], B[:2], C[:2]):
						x_0, y_0, x_1, y_1 = Find_Point(a, b, c, frame)
						if(index == 2):
							edge.append(Edge(round(x_0), round(y_0), round(x_1), round(y_1), S[index - 2], S[index], a, b, c))
						else:
							edge.append(Edge(round(x_0), round(y_0), round(x_1), round(y_1), S[index], S[index + 1], a, b, c))
						index += 1 
				else:
					index = 0
					for a, b, c in zip(A, B, C):
						if(a == 0): #水平
							if(c_x > S[index].x): #向上
								x = frame.x
								y = -(a * frame.x + c) / b
							else:							#向下
								x = frame.x1
								y = -(a * frame.x1 + c) / b
						elif(b == 0): #垂直
							if(c_y > S[index].y):	#向左
								x = -(b * frame.y + c) / a
								y = frame.y
							else:							#向右
								x = -(b * frame.y1 + c) / a
								y = frame.y1
						else:
							if(index == 2):
								line_A, line_B, line_C = Line(S[index - 2].x, S[index - 2].y, S[index].x, S[index].y)
							else:
								line_A, line_B, line_C = Line(S[index].x, S[index].y, S[index + 1].x, S[index + 1].y)
							direction = line_A * c_x + line_B * c_y + line_C
							
							#找範圍內的兩交點
							x_0, y_0, x_1, y_1 = Find_Point(a, b, c, frame)
							if(direction == 0):
								if(index == 0):
									direction = line_A * S[index + 2].x + line_B * S[index + 2].y + line_C
								elif(index == 1):
									direction = line_A * S[index - 1].x + line_B * S[index - 1].y + line_C
								elif(index == 2):
									direction = line_A * S[index - 1].x + line_B * S[index - 1].y + line_C
					
							if(direction > 0):
								#判斷是否為鈍角三角形最長的邊
								if(O_T_side == index):
									if((line_A * x_0 + line_B * y_0 + line_C) >= 0):
										x = x_0
										y = y_0
									else:
										x = x_1
										y = y_1
								else:
									if((line_A * x_0 + line_B * y_0 + line_C) <= 0):
										x = x_0
										y = y_0
									else:
										x = x_1
										y = y_1
							else:
								#判斷是否為鈍角三角形最長的邊
								if(O_T_side == index):
									if((line_A * x_0 + line_B * y_0 + line_C) <= 0):
										x = x_0
										y = y_0
									else:
										x = x_1
										y = y_1
								else:
									if((line_A * x_0 + line_B * y_0 + line_C) >= 0):
										x = x_0
										y = y_0
									else:
										x = x_1
										y = y_1
						if(index == 2):
							edge.append(Edge(round(c_x), round(c_y), round(x), round(y), S[index - 2], S[index], a, b, c))
						else:
							edge.append(Edge(round(c_x), round(c_y), round(x), round(y), S[index], S[index + 1], a, b, c))
						index += 1
				convex = self.Divide_Convex_Hull(S)

				node.Update_Information(edge, convex, None, length)
				return edge, convex, None

			#大於3點 -> divide and conquer
			else:
				if(length + 1 > self.length):
					self.length = length + 1
				if(n % 2 != 0):
					mid_index = int(n / 2) + 1
					Sl = S[0 : mid_index]
					Sr = S[mid_index : n]
				else:
					mid_index = int(n / 2)
					Sl = S[0 : mid_index]
					Sr = S[mid_index : n]
				
				node.left = Node()
				node.right = Node()
				EdgeL, convex_L, HP_L = self.divide_and_conquer(Sl, frame, node.left, length + 1)
				EdgeR, convex_R, HP_R = self.divide_and_conquer(Sr, frame, node.right, length + 1)

				#Save VD, Convex Hull, HP in node
				node.left.Update_Information(EdgeL, convex_L, HP_L, length + 1)
				node.right.Update_Information(EdgeR, convex_R, HP_R, length + 1)
				
				#Merge tow VD
				Voronoi, Convex, HP = self.Merge(Sl, Sr, EdgeL, EdgeR)
				node.Update_Information(Voronoi, Convex, HP, length)
				
				return Voronoi, Convex, HP
					

		#No point(point <= 1)
		else:
			node.Update_Information([], [], [], length)
			return [], [], []
			

	'''
	Sr = right part of point, Sl = left part of point.
	Er = Voronoi of right, El = Voronoi of left
	mode == 1 -> step by step
	'''
	def Merge(self, Sl, Sr, El, Er):
		Sl = copy.deepcopy(Sl)
		Sr = copy.deepcopy(Sr)
		El = copy.deepcopy(El)
		Er = copy.deepcopy(Er)

		'''
		print("\nMerge : ")
		print("\nSl")
		for p1 in Sl:
			print(p1.x, p1.y)
		print("Sr")
		for p2 in Sr:
			print(p2.x, p2.y)
		'''

		#Find Sl and Sr Convex Hull
		Convex_L = self.Convex_Hull(Sl, El)
		Convex_R = self.Convex_Hull(Sr, Er)

		#Find upper & lower tangent
		Upper_C_S = self.Upper_Common_Support(Convex_L, Convex_R)
		Lower_C_S = self.Lower_Common_Support(Convex_L, Convex_R)

		HP = []
		index = 0	#第一條線，從y = -10000 開始

		while(1):			
			#HyperPlane的垂直平分線 方程式
			HP_A, HP_B, HP_C = midLine(Upper_C_S[0].x, Upper_C_S[0].y, Upper_C_S[1].x, Upper_C_S[1].y)
			'''
			if 最上方的交點 < -10000 (y):
				use 最上方交點當起點 
			else 
				從 y = -10000 當起點
			'''
			if(index == 0):
				x_L, y_L = None, None
				edge_L = None
				for e in El:
					x1_L, y1_L = Find_intersection_point(HP_A, HP_B, HP_C, e)
					if(x1_L != None):
						if(x_L == None):
							x_L, y_L = x1_L, y1_L
							edge_L = e
						elif(y1_L < y_L):
							x_L, y_L = x1_L, y1_L
							edge_L = e

				x_R, y_R = None, None
				edge_R = None
				for e in Er:
					x1_R, y1_R = Find_intersection_point(HP_A, HP_B, HP_C, e)
					if(x1_R != None):
						if(x_R == None):
							x_R, y_R = x1_R, y1_R
							edge_R = e
						elif(y1_R < y_R):
							x_R, y_R = x1_R, y1_R
							edge_R = e
				if(y_L != None and y_R != None):
					if(y_L < y_R and y_L <= -10000):
						prev_x, prev_y = x_L, y_L
						p = edge_L.another_point(Upper_C_S[0])
						Upper_C_S = [p, Upper_C_S[1]]
						HP_A, HP_B, HP_C = midLine(Upper_C_S[0].x, Upper_C_S[0].y, Upper_C_S[1].x, Upper_C_S[1].y)
					elif(y_L > y_R and y_R <= -10000):
						prev_x, prev_y = x_R, y_R
						q = edge_R.another_point(Upper_C_S[1])
						Upper_C_S = [Upper_C_S[0], q]
						HP_A, HP_B, HP_C = midLine(Upper_C_S[0].x, Upper_C_S[0].y, Upper_C_S[1].x, Upper_C_S[1].y)
					else:
						x_0, y_0, x_1, y_1 = Find_Point(HP_A, HP_B, HP_C, Frame(-10000, -10000, 10000, 10000))
						if(y_0 > y_1):
							prev_x, prev_y = x_1, y_1
						else:
							prev_x, prev_y = x_0, y_0
				else:
					x_0, y_0, x_1, y_1 = Find_Point(HP_A, HP_B, HP_C, Frame(-10000, -10000, 10000, 10000))
					if(y_0 > y_1):
						prev_x, prev_y = x_1, y_1
					else:
						prev_x, prev_y = x_0, y_0

			#找左邊和右邊最上方的交點，但不能回頭(> prev_y)
			x_L, y_L = None, None
			edge_L = None
			for e in El:
				x1_L, y1_L = Find_intersection_point(HP_A, HP_B, HP_C, e)
				if(x1_L != None):
					if(x1_L != prev_x or y1_L != prev_y):
						if(y1_L >= prev_y and x_L == None):
							x_L, y_L = x1_L, y1_L
							edge_L = e
						elif(y1_L >= prev_y and y1_L < y_L):
							x_L, y_L = x1_L, y1_L
							edge_L = e

			x_R, y_R = None, None
			edge_R = None
			for e in Er:
				x1_R, y1_R = Find_intersection_point(HP_A, HP_B, HP_C, e)
				if(x1_R != None):
					if(x1_R != prev_x or y1_R != prev_y):
						if(y1_R >= prev_y and x_R == None):
							x_R, y_R = x1_R, y1_R
							edge_R = e
						elif(y1_R >= prev_y and y1_R < y_R):
							x_R, y_R = x1_R, y1_R
							edge_R = e
			'''
			If Upper == Lower:
				如果有交點，HP到交點
				如果沒有，投射到y = 10000
			else:
				如果左邊先碰到, 表示HL左邊的點要往下，透過交點的線段來判斷下一個點的位置
				左邊就相反
			'''
			if(Upper_C_S[0].x == Lower_C_S[0].x and Upper_C_S[0].y == Lower_C_S[0].y and Upper_C_S[1].x == Lower_C_S[1].x and Upper_C_S[1].y == Lower_C_S[1].y):
				x_0, y_0, x_1, y_1 = Find_Point(HP_A, HP_B, HP_C, Frame(-10000, -10000, 10000, 10000))
				if(y_0 > y_1):
					x, y = x_0, y_0
				else:
					x, y = x_1, y_1
				if(y_L == None and y_R == None):
					if(y_0 > y_1):
						HP.append(Edge(prev_x, prev_y, x_0, y_0, Upper_C_S[0], Upper_C_S[1], HP_A, HP_B, HP_C))
					elif(y_0 < y_1):
						HP.append(Edge(prev_x, prev_y, x_1, y_1, Upper_C_S[0], Upper_C_S[1], HP_A, HP_B, HP_C))
					else:
						A, B, C = Line(Upper_C_S[0].x, Upper_C_S[0].y, Upper_C_S[1].x, Upper_C_S[1].y)
						if(A * prev_x + B * prev_y + C > 0):
							if(A * x_0 + B * y_0 + C < 0):
								HP.append(Edge(prev_x, prev_y, x_0, y_0, Upper_C_S[0], Upper_C_S[1], HP_A, HP_B, HP_C))
							elif(A * x_1 + B * y_1 + C < 0):
								HP.append(Edge(prev_x, prev_y, x_1, y_1, Upper_C_S[0], Upper_C_S[1], HP_A, HP_B, HP_C))
						elif(A * prev_x + B * prev_y + C < 0):
							if(A * x_0 + B * y_0 + C > 0):
								HP.append(Edge(prev_x, prev_y, x_0, y_0, Upper_C_S[0], Upper_C_S[1], HP_A, HP_B, HP_C))
							elif(A * x_1 + B * y_1 + C > 0):
								HP.append(Edge(prev_x, prev_y, x_1, y_1, Upper_C_S[0], Upper_C_S[1], HP_A, HP_B, HP_C))
				elif(x_L == x_R and y_L == y_R):
					HP.append(Edge(prev_x, prev_y, x, y, Upper_C_S[0], Upper_C_S[1], HP_A, HP_B, HP_C))
				elif(y_L == None):
					HP.append(Edge(prev_x, prev_y, x, y, Upper_C_S[0], Upper_C_S[1], HP_A, HP_B, HP_C))
				elif(y_R == None):
					HP.append(Edge(prev_x, prev_y, x, y, Upper_C_S[0], Upper_C_S[1], HP_A, HP_B, HP_C))
				else:
					if(y_L > y_R):
						HP.append(Edge(prev_x, prev_y, x, y, Upper_C_S[0], Upper_C_S[1], HP_A, HP_B, HP_C))
					elif(y_L < y_R):
						HP.append(Edge(prev_x, prev_y, x, y, Upper_C_S[0], Upper_C_S[1], HP_A, HP_B, HP_C))
				
				#Upper == Lower -> 結束
				break
			
			else:
				#沒有交點
				if(y_L == None and y_R == None):
					x_0, y_0, x_1, y_1 = Find_Point(HP_A, HP_B, HP_C, Frame(-10000, -10000, 10000, 10000))
					if(HP_A * prev_x + HP_B * prev_y + HP_C == 0):
						if(y_0 > y_1):
							x_R, y_R = x_0, y_0
						else:
							x_R, y_R = x_1, y_1
						HP.append(Edge(prev_x, prev_y, x_R, y_R, Upper_C_S[0], Upper_C_S[1], HP_A, HP_B, HP_C))
						prev_x, prev_y = x_R, y_R
					else:
						if(y_0 > y_1):
							prev_x, prev_y = x_0, y_0
						else:
							prev_x, prev_y = x_1, y_1
						x_L, y_L = None, None
						edge_L = None
						for e in El:
							x1_L, y1_L = Find_intersection_point(HP_A, HP_B, HP_C, e)
							if(x1_L != None):
								if(x1_L != prev_x or y1_L != prev_y):
									if(x_L == None):
										x_L, y_L = x1_L, y1_L
										edge_L = e
									elif(y1_L < y_L):
										x_L, y_L = x1_L, y1_L
										edge_L = e

						x_R, y_R = None, None
						edge_R
						for e in Er:
							x1_R, y1_R = Find_intersection_point(HP_A, HP_B, HP_C, e)
							if(x1_R != None):
								if(x1_R != prev_x or y1_R != prev_y):
									if(x_R == None):
										x_R, y_R = x1_R, y1_R
										edge_R = e
									elif(y1_R < y_R):
										x_R, y_R = x1_R, y1_R
										edge_R = e

						if(y_L == None):
							HP.append(Edge(prev_x, prev_y, x_R, y_R, Upper_C_S[0], Upper_C_S[1], HP_A, HP_B, HP_C))
							prev_x = x_R
							prev_y = y_R
							q = edge_R.another_point(Upper_C_S[1])
							Upper_C_S = [Upper_C_S[0], q]
						elif(y_R == None):
							HP.append(Edge(prev_x, prev_y, x_L, y_L, Upper_C_S[0], Upper_C_S[1], HP_A, HP_B, HP_C))
							prev_x = x_L
							prev_y = y_L
							p = edge_L.another_point(Upper_C_S[0])
							Upper_C_S = [p, Upper_C_S[1]]
						else:
							if(y_L > y_R):
								HP.append(Edge(prev_x, prev_y, x_R, y_R, Upper_C_S[0], Upper_C_S[1], HP_A, HP_B, HP_C))
								prev_x = x_R
								prev_y = y_R
								q = edge_R.another_point(Upper_C_S[1])
								Upper_C_S = [Upper_C_S[0], q]
							elif(y_L < y_R):
								HP.append(Edge(prev_x, prev_y, x_R, y_R, Upper_C_S[0], Upper_C_S[1], HP_A, HP_B, HP_C))
								prev_x = x_L
								prev_y = y_L
								p = edge_L.another_point(Upper_C_S[0])
								Upper_C_S = [p, Upper_C_S[1]]
							else:
								HP.append(Edge(x_L, y_L, x_R, y_R, Upper_C_S[0], Upper_C_S[1], HP_A, HP_B, HP_C))
								x = (Upper_C_S[0].x + Upper_C_S[1].x) / 2
								y = (Upper_C_S[0].y + Upper_C_S[1].y) / 2
								d1 = length(Point(x, y), Point(x_L, y_L))
								d2 = length(Point(x, y), Point(x_R, y_R))
								if(d1 < d2):
									prev_x = x_L
									prev_y = y_L
									p = edge_L.another_point(Upper_C_S[0])
									Upper_C_S = [p, Upper_C_S[1]]
								elif(d1 > d2):
									prev_x = x_R
									prev_y = y_R
									q = edge_R.another_point(Upper_C_S[1])
									Upper_C_S = [Upper_C_S[0], q]
								else:
									p = edge_L.another_point(Upper_C_S[0])
									q = edge_R.another_point(Upper_C_S[1])
									Upper_C_S = [p, q]
					if(prev_y >= 10000):
						Upper_C_S = Lower_C_S

				#兩交點y相同，找離上一個交點較近的
				elif(y_L == y_R):
					if(x_L == x_R):
						HP.append(Edge(prev_x, prev_y, x_R, y_R, Upper_C_S[0], Upper_C_S[1], HP_A, HP_B, HP_C))					
						prev_x = x_R
						prev_y = y_R
						p = edge_L.another_point(Upper_C_S[0])
						q = edge_R.another_point(Upper_C_S[1])
						Upper_C_S = [p, q]
					else:
						if(length(Point(prev_x, prev_y), Point(x_L, y_L)) < length(Point(prev_x, prev_y), Point(x_R, y_R))):
							HP.append(Edge(prev_x, prev_y, x_L, y_L, Upper_C_S[0], Upper_C_S[1], HP_A, HP_B, HP_C))
							prev_x = x_L
							prev_y = y_L
							p = edge_L.another_point(Upper_C_S[0])
							Upper_C_S = [p, Upper_C_S[1]]
						else:
							HP.append(Edge(prev_x, prev_y, x_R, y_R, Upper_C_S[0], Upper_C_S[1], HP_A, HP_B, HP_C))					
							prev_x = x_R
							prev_y = y_R
							q = edge_R.another_point(Upper_C_S[1])
							Upper_C_S = [Upper_C_S[0], q]
				#左邊沒交點
				elif(y_L == None):
					HP.append(Edge(prev_x, prev_y, x_R, y_R, Upper_C_S[0], Upper_C_S[1], HP_A, HP_B, HP_C))					
					prev_x = x_R
					prev_y = y_R
					q = edge_R.another_point(Upper_C_S[1])
					Upper_C_S = [Upper_C_S[0], q]
				#右邊沒交點
				elif(y_R == None):
					HP.append(Edge(prev_x, prev_y, x_L, y_L, Upper_C_S[0], Upper_C_S[1], HP_A, HP_B, HP_C))					
					prev_x = x_L
					prev_y = y_L
					p = edge_L.another_point(Upper_C_S[0])
					Upper_C_S = [p, Upper_C_S[1]]
				else:
					#右邊交點較高
					if(y_L > y_R):
						HP.append(Edge(prev_x, prev_y, x_R, y_R, Upper_C_S[0], Upper_C_S[1], HP_A, HP_B, HP_C))
						prev_x = x_R
						prev_y = y_R
						q = edge_R.another_point(Upper_C_S[1])
						Upper_C_S = [Upper_C_S[0], q]
					#左邊交點較高
					elif(y_L < y_R):
						HP.append(Edge(prev_x, prev_y, x_L, y_L, Upper_C_S[0], Upper_C_S[1], HP_A, HP_B, HP_C))
						prev_x = x_L
						prev_y = y_L
						p = edge_L.another_point(Upper_C_S[0])
						Upper_C_S = [p, Upper_C_S[1]]
			index = 1

		'''
		左邊的VD，消除在HP右邊的
		右邊的VD，消除在HP左邊的
		Step 1 : 找有無交點
		Step 2 : 有交點較讓超過交點的線段Update 目前的兩點
				 沒有交點就判斷是否是在HP的右(左)邊
				 如果是，讓兩點都等於0, 0，之後再消除
		'''
		for l in El:
			All_Right = False
			for e in HP:
				A, B, C = e.get_equations()
				x, y = Find_cross(l, e)
				x1, y1, x2, y2 = l.get_point()
				if(x == None and y == None):
					if((A * x1 + B * y1 + C > 0) and (A * x2 + B * y2 + C > 0) and All_Right == False):
						All_Right = True
				elif(A * x1 + B * y1 + C > 0):
					l.Update_edge(x, y, x2, y2)
					All_Right = (x, y)
				elif(A * x2 + B * y2 + C > 0):
					l.Update_edge(x1, y1, x, y)	
					All_Right = (x, y)
			if(All_Right == True):
				count = 0
				x1, y1, x2, y2 = l.get_point()
				for e in HP:
					e_x1, e_y1, e_x2, e_y2 = e.get_point()
					A, B, C = e.get_equations()
					min_y = min(e_y1, e_y2)
					max_y = max(e_y1, e_y2)
					if(min_y <= y1 <= max_y and (A * x1 + B * y1 + C > 0)):
						count += 1
					if(min_y <= y2 <= max_y and (A * x2 + B * y2 + C > 0)):
						count += 1
				if(count >= 2):
					l.Update_edge(0, 0, 0, 0)
		
		for r in Er:
			All_Left = False
			for e in HP:
				A, B, C = e.get_equations()
				x, y = Find_cross(r, e)
				x1, y1, x2, y2 = r.get_point()
				if(x == None and y == None):
					if((A * x1 + B * y1 + C < 0) and (A * x2 + B * y2 + C < 0) and All_Left == False):
						All_Left = True
				elif(A * x1 + B * y1 + C < 0):
					r.Update_edge(x, y, x2, y2)
					All_Left = (x, y)
				elif(A * x2 + B * y2 + C < 0):
					r.Update_edge(x1, y1, x, y)	
					All_Left = (x, y)			
			if(All_Left == True):
				count = 0
				x1, y1, x2, y2 = r.get_point()
				for e in HP:
					e_x1, e_y1, e_x2, e_y2 = e.get_point()
					A, B, C = e.get_equations()
					min_y = min(e_y1, e_y2)
					max_y = max(e_y1, e_y2)
					if(min_y <= y1 <= max_y and (A * x1 + B * y1 + C < 0)):
						count += 1
					if(min_y <= y2 <= max_y and (A * x2 + B * y2 + C < 0)):
						count += 1
				if(count >= 2):
					r.Update_edge(0, 0, 0, 0)


		Total_Voronoi = HP + Er + El
		Voronoi = []
		for e in Total_Voronoi:
			if(e.get_point() != (0, 0, 0, 0)):
				Voronoi.append(e)
		
		#Merge 整個的Convex Hull
		Convex = self.merge_convex_hull(Convex_L, Convex_R)
		
		return Voronoi, Convex, HP

	'''
	Find Convex Hull
	use divide and conquer
	'''
	def Convex_Hull(self, S, E):
		convex = self.Divide_Convex_Hull(S)
		
		#回傳Convex hull
		return convex

	def Divide_Convex_Hull(self, P):
		n = len(P)
		#如果少於5，直接暴力破解(Jarvis March)
		if(n <= 5):
			return self.brute_convex_hull(P)

		d = int(n / 2)
		Pl = P[0:d]
		Pr = P[d:n]
		convex_L = self.Divide_Convex_Hull(Pl)
		convex_R = self.Divide_Convex_Hull(Pr)
		return self.merge_convex_hull(convex_L, convex_R)
	'''
	Convex Hull by Jarvis March
	從最左邊的點開始，順時針找最外圍的一點(窮舉所有點)
	時間複雜度：O(MN), M = 所有點的數目, N = Convex Hull 點的數目
	'''
	def brute_convex_hull(self, P):
		#start point, 最左的點
		a = min(P, key = lambda p : p.x)
		start = P.index(a)
		#Save Convex result
		convex = []
		convex.append(P[start])

		current_p = start
		while(1):
			next_p = (current_p + 1) % len(P)
			for i in range(len(P)):
				if(i == current_p):
					continue
				d = direction(P[current_p], P[i], P[next_p])
				if(d > 0):
					next_p = i
				elif(d == 0 and length(P[current_p], P[i]) < length(P[current_p], P[next_p]) and P[i] not in convex):
					nex_p = i
			current_p = next_p
			if(current_p == start):
				break
			convex.append(P[current_p])

		return convex

	def merge_convex_hull(self, Pl, Pr):
		'''
		Convex Hull 是順時針
		所以找到Upper & Lower Common Support後
		左邊的從Lower 到 Upper
		右邊的從Upper 到 Lower
		'''

		Upper_C_S = self.Upper_Common_Support(Pl, Pr)
		Lower_C_S = self.Lower_Common_Support(Pl, Pr)
    
		Upper_l = Pl.index(Upper_C_S[0])
		Upper_r = Pr.index(Upper_C_S[1])
		Lower_l = Pl.index(Lower_C_S[0])
		Lower_r = Pr.index(Lower_C_S[1])
    
		convex = []
		start = Lower_l
		convex.append(Pl[Lower_l])
		while(start != Upper_l):
			start = (start + 1) % len(Pl)
			convex.append(Pl[start])
    
		start = Upper_r
		convex.append(Pr[Upper_r])
		while(start != Lower_r):
			start = (start + 1) % len(Pr)
			convex.append(Pr[start])
        
		return convex

	#Find Upper Common Support (upper tangent)
	def Upper_Common_Support(self, Pl, Pr):
		#u is the largest x in Pl
		u = Pl.index(max(Pl, key = lambda p : p.x))
		#v is the smallest x in Pr
		v = Pr.index(min(Pr, key = lambda p : p.x))

		'''
		左邊往順時針轉
		右邊往逆時針轉
		'''
		flag = False
		while(not flag):
			flag = True
			while(direction(Pr[v], Pl[u], Pl[(u + len(Pl) - 1) % len(Pl)]) > 0):
				u = (u + len(Pl) - 1) % len(Pl)
			if(direction(Pr[v], Pl[u], Pl[(u + len(Pl) - 1) % len(Pl)]) == 0 and length(Pr[v], Pl[u]) > length(Pr[v], Pl[(u + len(Pl) - 1) % len(Pl)])):
				u = (u + len(Pl) - 1) % len(Pl)
			
			while(direction(Pl[u], Pr[v], Pr[(v + 1) % len(Pr)]) < 0):
				v = (v + 1) % len(Pr)
				flag = False
			if(direction(Pl[u], Pr[v], Pr[(v + 1) % len(Pr)]) == 0 and length(Pl[u], Pr[v]) > length(Pl[u], Pr[(v + 1) % len(Pr)])):
				v = (v + 1) % len(Pr)
				flag = False

		return [Pl[u], Pr[v]]

	#Find Lower Common Support (lower tangent)
	def Lower_Common_Support(self, Pl, Pr):
		#u is the largest x in Pl
		u = Pl.index(max(Pl, key = lambda p : p.x))
		#v is the smallest x in Pr
		v = Pr.index(min(Pr, key = lambda p : p.x))

		'''
		左邊往逆時針轉
		右邊往順時針轉
		'''

		flag = False
		while(not flag):
			flag = True
			while(direction(Pl[u], Pr[v], Pr[(v + len(Pr) - 1) % len(Pr)]) > 0):
				v = (v + len(Pr) - 1) % len(Pr)
			if(direction(Pl[u], Pr[v], Pr[(v + 1) % len(Pr)]) == 0 and length(Pr[u], Pl[v]) > length(Pr[u], Pl[(v + 1) % len(Pr)])):
				v = (v + 1) % len(Pr)
			
			while(direction(Pr[v], Pl[u], Pl[(u + 1) % len(Pl)]) < 0):
				u = (u + 1) % len(Pl)
				flag = False
			if(direction(Pr[v], Pl[u], Pl[(u + len(Pl) - 1) % len(Pl)]) == 0 and length(Pr[v], Pl[u]) > length(Pr[v], Pl[(u + len(Pl) - 1) % len(Pl)])):
				u = (u + len(Pl) - 1) % len(Pl)
				flag = False

		return [Pl[u], Pr[v]]



#求垂直平分線
def midLine(x1, y1, x2, y2):
	A = 2 * (x2 - x1)
	B = 2 * (y2 - y1)
	C = x1 ** 2 - x2 ** 2 + y1 ** 2 - y2 ** 2
	return A, B, C

#求兩點的直線方程式
#AX + BY + C = 0
def Line(x1, y1, x2, y2):
	A = y2 - y1
	B = x1 - x2
	C = x2 * y1 - x1 * y2
	return A, B, C

#求三角形外心
def circumcenter(A1, B1, C1, A2, B2, C2):
	C1 = -C1
	C2 = -C2
	#Cramer's rule
	if((A1 == 0 and A2 == 0) or (B1 == 0 and B2 == 0) or (A1 * B2) - (A2 * B1) == 0): return None, None
	x = ((C1 * B2) - (C2 * B1)) / ((A1 * B2) - (A2 * B1))
	y = ((A1 * C2) - (A2 * C1)) / ((A1 * B2) - (A2 * B1))
	return x, y

#是否為鈍角三角形
#return witch index is the long side
def Obtuse_triangle(x0, y0, x1, y1, x2, y2):
	edge = [None] * 3
	edge[0] = math.sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2) #0, 1
	edge[1] = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2) #1, 2
	edge[2] = math.sqrt((x0 - x2) ** 2 + (y0 - y2) ** 2) #0, 2
	max_edge = edge.index(max(edge))
	if(max_edge == 0):
		if(edge[1] * edge[1] + edge[2] * edge[2] < edge[0] * edge[0]):
			return 0
		else:
			return -1
	elif(max_edge == 1):
		if(edge[0] * edge[0] + edge[2] * edge[2] < edge[1] * edge[1]):
			return 1
		else:
			return -1
	elif(max_edge == 2):
		if(edge[0] * edge[0] + edge[1] * edge[1] < edge[2] * edge[2]):
			return 2
		else:
			return -1

#找與邊界的交點
def Find_Point(a, b, c, frame):
	if(b == 0):
		x_0 = -(b * frame.y + c) / a
		y_0 = frame.y
		x_1 = -(b * frame.y1 + c) / a
		y_1 = frame.y1
	elif(a == 0):
		x_0 = frame.x
		y_0 = -(a * frame.x + c) / b
		x_1 = frame.x1
		y_1 = -(a * frame.x1 + c) / b
	else:
		if(frame.x <= -(b * frame.y + c) / a <= frame.x1):
			x_0 = -(b * frame.y + c) / a
			y_0 = frame.y

			if(frame.x <= -(b * frame.y1 + c) / a <= frame.x1):
				x_1 = -(b * frame.y1 + c) / a
				y_1 = frame.y1
			elif(frame.y <= -(a * frame.x + c) / b <= frame.y1):
				x_1 = frame.x
				y_1 = -(a * frame.x + c) / b
			elif(frame.y <= -(a * frame.x1 + c) / b <= frame.y1):
				x_1 = frame.x1
				y_1 = -(a * frame.x1 + c) / b
		elif(frame.x <= -(b * frame.y1 + c) / a <= frame.x1):
			x_0 = -(b * frame.y1 + c) / a
			y_0 = frame.y1

			if(frame.y <= -(a * frame.x + c) / b <= frame.y1):
				x_1 = frame.x
				y_1 = -(a * frame.x + c) / b
			elif(frame.y <= -(a * frame.x1 + c) / b <= frame.y1):
				x_1 = frame.x1
				y_1 = -(a * frame.x1 + c) / b
		elif(frame.y <= -(a * frame.x + c) / b <= frame.y1):
			x_0 = frame.x
			y_0 = -(a * frame.x + c) / b
			x_1 = frame.x1
			y_1 = -(a * frame.x1 + c) / b
	return x_0, y_0, x_1, y_1

#三點比較叉積 OA, OB
'''
|A.x - O.x, A.y - O.y|
|B.x - O.x, B.y - O.y|

-> ((A.x - O.x) * (B.y - O.y)) - ((A.y - O.y) * (B.x - O.x))
如果 > 0 OA 在 OB 右邊
'''
def direction(O, A, B):
	#> 0, OA 到 OB 是逆時針
	return ((A.x - O.x) * (B.y - O.y)) - ((A.y - O.y) * (B.x - O.x))

#求兩點距離
def length(A, B):
	return ((A.x - B.x) ** 2) + ((A.y - B.y) ** 2)

#找兩線交點
#可以超出Frame
def Find_intersection_point(A1, B1, C1, edge):
	A2, B2, C2 = edge.get_equations()

	if((A1 * B2 - A2 * B1) == 0):
		return None, None
	x = round((C2 * B1 - C1 * B2) / (A1 * B2 - A2 * B1))
	y = round((C1 * A2 - C2 * A1) / (A1 * B2 - A2 * B1))

	x1, y1, x2, y2 = edge.get_point()
	min_x = min(x1, x2)
	max_x = max(x1, x2)
	min_y = min(y1, y2)
	max_y = max(y1, y2)

	if(min_x <= -10000 and min_x > x or max_x >= 10000 and max_x < x or max_y >= 10000 and max_y < y or min_y <= -10000 and min_y > y):
		return x, y

	if(min_x <= x <= max_x and min_y <= y <= max_y):
		return x, y
	else:
		return None, None

#找兩線段的交點(必須在範圍內)
def Find_cross(edge1, edge2):
	A1, B1, C1 = edge1.get_equations()
	A2, B2, C2 = edge2.get_equations()

	if((A1 * B2 - A2 * B1) == 0):
		return None, None
	x = round((C2 * B1 - C1 * B2) / (A1 * B2 - A2 * B1))
	y = round((C1 * A2 - C2 * A1) / (A1 * B2 - A2 * B1))

	x1, y1, x2, y2 = edge1.get_point()
	min_x1 = min(x1, x2)
	max_x1 = max(x1, x2)
	min_y1 = min(y1, y2)
	max_y1 = max(y1, y2)

	x1, y1, x2, y2 = edge2.get_point()
	min_x2 = min(x1, x2)
	max_x2 = max(x1, x2)
	min_y2 = min(y1, y2)
	max_y2 = max(y1, y2)

	if(min_x1 <= x <= max_x1 and min_y1 <= y <= max_y1 and min_x2 <= x <= max_x2 and min_y2 <= y <= max_y2):
		return x, y
	else:
		return None, None


	
def main():
	path, filename = os.path.split(os.path.abspath(__file__))
	myappid = 'mycompany.myproduct.subproduct.version' # arbitrary string
	ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
	app = tk.Tk()
	try:
		app.iconphoto(False, tk.PhotoImage(file=path + '\icon.png'))
	except:
		pass
	ui = UI(app)
	app.mainloop()

if __name__ == '__main__':
	main()  