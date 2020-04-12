#!/usr/bin/env python3

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog as fd
from tkinter import simpledialog as sd
import os
import shutil
import json
import bin_log_analyzer
import datetime

class DataStore:
	def __init__(self):
		self._dataStore = ".e4e_flight_info.json"
		if not os.path.isfile(self._dataStore):
			with open(self._dataStore, 'w') as dataFile:
				data = {}
				data['airframes'] = []
				data['pilots'] = []
				dataFile.write(json.dumps(data))
		with open(self._dataStore) as dataFile:
			raw_data = dataFile.readline()
			data = json.loads(raw_data)
		self._airframes = [Aircraft.fromDictionary(d) for d in data['airframes']]
		self._pilots = [Pilot.fromDictionary(d) for d in data['pilots']]

	def getPilots(self):
		return self._pilots

	def setPilots(self, pilots):
		assert(isinstance(pilots, list))
		assert(all(isinstance(pilot, Pilot) for pilot in pilots))
		self._pilots = pilots
		self.write()

	def getAircraft(self):
		return self._airframes

	def setAircraft(self, acfts):
		assert(isinstance(acfts, list))
		assert(all(isinstance(acft, Aircraft) for acft in acfts))
		self._airframes = acfts
		self.write()

	def write(self):
		with open(self._dataStore, 'w') as dataFile:
			data = {}
			data['airframes'] = [airframe.toDict() for airframe in self._airframes]
			data['pilots'] = [pilot.toDict() for pilot in self._pilots]
			dataFile.write(json.dumps(data))

class Aircraft:
	def __init__(self, nickname, faaId = ""):
		assert(nickname is not None)
		assert(isinstance(faaId, str))
		self._nickname = nickname
		self._id = faaId

	@classmethod
	def fromDictionary(cls, d):
		assert('nickname' in d)
		assert('id' in d)
		assert(isinstance(d['nickname'], str))
		assert(isinstance(d['id'], str))
		return cls(d['nickname'], d['id'])

	def getId(self):
		return self._id

	def setId(self, faaId):
		assert(isinstance(faaId, str))
		self._id = faaId

	def getName(self):
		return self._nickname

	def setId(self, name):
		assert(isinstance(name, str))
		self._nickname = name

	def toDict(self):
		return {'nickname': self._nickname, 'id': self._id}

	def __str__(self):
		return "(%s: %s)" % (self._nickname, self._id)

class Pilot:
	def __init__(self, name, cert = None):
		assert(name is not None)
		assert(isinstance(name, str))
		if cert is not None:
			assert(isinstance(cert, int))
		self._name = name
		self._cert = cert

	@classmethod
	def fromDictionary(cls, d):
		assert('name' in d)
		assert('cert' in d)
		assert(isinstance(d['name'], str))
		assert(isinstance(d['cert'], int) or d['cert'] is None)
		return cls(d['name'], d['cert'])

	def getName(self):
		return self._name

	def getCert(self):
		return self._cert

	def setCert(self, certNumber):
		assert(isinstance(certNumber, int))
		self._cert = certNumber

	def toDict(self):
		retval = {}
		retval['name'] = self._name
		retval['cert'] = self._cert
		return retval

	def __str__(self):
		if self._cert is not None:
			return "(%s: %d)" % (self._name, self._cert)
		else:
			return "(%s: N/A)" % (self._name)

class PilotInfoEdit(tk.Toplevel):
	def __init__(self, parent, data):
		tk.Toplevel.__init__(self, parent)
		self.transient(parent)
		self.title("Edit Pilots")
		self.parent = parent
		self.data = data
		body = tk.Frame(self)

		pilots = self.data.getPilots()
		self.pilotFrame = tk.Frame(body)
		self.pilotFrame.pack()

		self.numPilots = 0

		addButton = tk.Button(body, text="Add", command=self.addPilot)
		self.initial_focus = addButton
		for pilot in pilots:
			label = tk.Label(self.pilotFrame, text=pilot.getName())
			entry = tk.Entry(self.pilotFrame)
			entry.insert(0, pilot.getCert())
			if self.numPilots == 0:
				self.initial_focus = entry
			removeButton = tk.Button(self.pilotFrame, text="Remove", 
				command = lambda c=self.numPilots :self.removePilot(c))
			label.grid(row = self.numPilots, column = 1)
			entry.grid(row = self.numPilots, column = 2)
			removeButton.grid(row = self.numPilots, column = 3)
			self.numPilots += 1

		addButton.pack()

		body.pack(padx = 5, pady = 5)

		box = tk.Frame(self)

		w = tk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
		w.pack(side=tk.LEFT, padx=5, pady=5)
		w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
		w.pack(side=tk.LEFT, padx=5, pady=5)

		self.bind("<Return>", self.ok)
		self.bind("<Escape>", self.cancel)

		box.pack()

		self.grab_set()

		self.protocol("WM_DELETE_WINDOW", self.cancel)

		self.geometry("+%d+%d" % (parent.winfo_rootx() + 50,
			parent.winfo_rooty() + 50))

		self.initial_focus.focus_set()

		self.wait_window(self)

	def removePilot(self, id):
		print("Deleting row %d" % id)
		widgetsToDestroy = []
		for widget in self.pilotFrame.grid_slaves():
			if widget.grid_info()['row'] == id:
				widget.grid_forget()
			elif widget.grid_info()['row'] > id:
				column = widget.grid_info()['column']
				row = widget.grid_info()['row'] - 1
				widget.grid(row=row, column=column)
		for widget in widgetsToDestroy:
			widget.destroy()
		self.numPilots -= 1
		self.pilotFrame.update()

	def addPilot(self):
		pilotName = sd.askstring("Add Pilot", "Pilot Name", parent=self)
		if pilotName is '':
			return

		label = tk.Label(self.pilotFrame, text=pilotName)
		entry = tk.Entry(self.pilotFrame)
		removeButton = tk.Button(self.pilotFrame, text="Remove",
			command = lambda:self.removePilot(pilot.getName()))

		label.grid(row = self.numPilots, column = 1)
		entry.grid(row = self.numPilots, column = 2)
		removeButton.grid(row = self.numPilots, column = 3)
		self.numPilots += 1


	def ok(self, event=None):
		if not self.validate():
			self.initial_focus.focus_set()
			return

		self.withdraw()
		self.update_idletasks()

		self.apply()
		
		self.cancel()

	def cancel(self, event=None):

		# put focus back to the parent window
		self.parent.focus_set()
		self.destroy()

	def validate(self):
		names = [""] * self.numPilots
		ids = [None] * self.numPilots

		retval = True

		for widget in self.pilotFrame.grid_slaves():
			idx = widget.grid_info()['row']
			if isinstance(widget, tk.Label):
				names[idx] = widget.cget("text")
			elif isinstance(widget, tk.Entry):
				s = widget.get()
				if s != '':
					ids[idx] = int(s)
					if ids[idx] < 0:
						widget.config(bg='red')
						retval = False

		return retval


	def apply(self):
		names = [""] * self.numPilots
		ids = [None] * self.numPilots

		retval = True

		for widget in self.pilotFrame.grid_slaves():
			idx = widget.grid_info()['row']
			if isinstance(widget, tk.Label):
				name = widget.cget("text")
				names[idx] = name
			elif isinstance(widget, tk.Entry):
				s = widget.get()
				if s != '':
					ids[idx] = int(s)
		
		pilots = []
		for i in range(self.numPilots):
			pilot = Pilot(names[i], ids[i])
			pilots.append(pilot)
		self.data.setPilots(pilots)

class ACFTInfoEdit(tk.Toplevel):
	def __init__(self, parent, data):
		tk.Toplevel.__init__(self, parent)
		self.transient(parent)
		self.title("Edit Aircraft")
		self.parent = parent
		self.data = data
		body = tk.Frame(self)

		acfts = self.data.getAircraft()
		self.acftFrame = tk.Frame(body)
		self.acftFrame.pack()

		self.numACFT = 0

		addButton = tk.Button(body, text="Add", command=self.addAircraft)
		self.initial_focus = addButton
		for acft in acfts:
			label = tk.Label(self.acftFrame, text=acft.getName())
			entry = tk.Entry(self.acftFrame)
			entry.insert(0, acft.getId())
			if self.numACFT == 0:
				self.initial_focus = entry
			removeButton = tk.Button(self.acftFrame, text="Remove", 
				command = lambda c=self.numACFT:self.removeAircraft(c))
			label.grid(row = self.numACFT, column = 1)
			entry.grid(row = self.numACFT, column = 2)
			removeButton.grid(row = self.numACFT, column = 3)
			self.numACFT += 1

		addButton.pack()

		body.pack(padx = 5, pady = 5)

		box = tk.Frame(self)

		w = tk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
		w.pack(side=tk.LEFT, padx=5, pady=5)
		w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
		w.pack(side=tk.LEFT, padx=5, pady=5)

		self.bind("<Return>", self.ok)
		self.bind("<Escape>", self.cancel)

		box.pack()

		self.grab_set()

		self.protocol("WM_DELETE_WINDOW", self.cancel)

		self.geometry("+%d+%d" % (parent.winfo_rootx() + 50,
			parent.winfo_rooty() + 50))

		self.initial_focus.focus_set()

		self.wait_window(self)

	def removeAircraft(self, id):
		print("Deleting row %d" % id)
		widgetsToDestroy = []
		for widget in self.acftFrame.grid_slaves():
			if widget.grid_info()['row'] == id:
				widget.grid_forget()
			elif widget.grid_info()['row'] > id:
				column = widget.grid_info()['column']
				row = widget.grid_info()['row'] - 1
				widget.grid(row=row, column=column)
		for widget in widgetsToDestroy:
			widget.destroy()
		self.numACFT -= 1
		self.acftFrame.update()

	def addAircraft(self):
		acftName = sd.askstring("Add Aircraft", "Aircraft Nickname", parent=self)
		if acftName is '':
			return

		label = tk.Label(self.acftFrame, text=acftName)
		entry = tk.Entry(self.acftFrame)
		removeButton = tk.Button(self.acftFrame, text="Remove",
			command = lambda:self.removePilot(acft.getName()))

		label.grid(row = self.numACFT, column = 1)
		entry.grid(row = self.numACFT, column = 2)
		removeButton.grid(row = self.numACFT, column = 3)
		self.numACFT += 1


	def ok(self, event=None):
		if not self.validate():
			self.initial_focus.focus_set()
			return

		self.withdraw()
		self.update_idletasks()

		self.apply()
		
		self.cancel()

	def cancel(self, event=None):

		# put focus back to the parent window
		self.parent.focus_set()
		self.destroy()

	def validate(self):
		names = [""] * self.numACFT
		ids = [None] * self.numACFT

		retval = True

		for widget in self.acftFrame.grid_slaves():
			idx = widget.grid_info()['row']
			if isinstance(widget, tk.Label):
				names[idx] = widget.cget("text")
			elif isinstance(widget, tk.Entry):
				s = widget.get()
				if s != '':
					ids[idx] = s

		return retval


	def apply(self):
		names = [""] * self.numACFT
		ids = [None] * self.numACFT

		retval = True

		for widget in self.acftFrame.grid_slaves():
			idx = widget.grid_info()['row']
			if isinstance(widget, tk.Label):
				names[idx] = widget.cget("text")
			elif isinstance(widget, tk.Entry):
				s = widget.get()
				ids[idx] = s

		acfts = []
		for i in range(self.numACFT):
			acft = Aircraft(names[i], ids[i])
			acfts.append(acft)
		self.data.setAircraft(acfts)

class LogInfoGui(tk.Toplevel):
	def __init__(self, parent, data, logs, logPath):
		tk.Toplevel.__init__(self, parent)
		self.transient(parent)
		self.title("Flight Info")
		self.parent = parent
		assert(isinstance(data, DataStore))
		self.data = data
		assert(isinstance(logs, list))
		self.logs = logs
		assert(isinstance(logPath, str))
		self.logPath = logPath
		body = tk.Frame(self)
		# make internals

		pilotEntryLabel = tk.Label(body, text="Pilot Name: ")
		pilotEntryLabel.grid(row = 0, column = 0)

		pilots = self.data.getPilots()
		self.pilotVar = tk.StringVar(body)
		if len(pilots) == 0:
			d = PilotInfoEdit(self, self.data)
			pilots = self.data.getPilots()
		self.pilotVar.set(pilots[0])
		self.selectedPilot = pilots[0]

		self.pilotEntry = tk.OptionMenu(body, self.pilotVar, pilots[0], 
			command=self.setPilot)

		menu = self.pilotEntry['menu']
		menu.delete(0, "end")
		for pilot in pilots:
			menu.add_command(label=pilot, command=tk._setit(self.pilotVar, pilot))

		self.pilotEntry.grid(row = 0, column = 1)

		editPilots = tk.Button(body, text='Edit', command=self.editPilots)
		editPilots.grid(row = 0, column = 2)

		tk.Label(body, text='Aircraft: ').grid(row=1, column=0)

		acfts = self.data.getAircraft()
		self.acftVar = tk.StringVar(body)
		if len(acfts) == 0:
			d = ACFTInfoEdit(self, self.data)
			acfts = self.data.getAircraft()
		self.acftVar.set(acfts[0])
		self.selectedAcft = acfts[0]
		self.acftEntry = tk.OptionMenu(body, self.acftVar, acfts[0],
			command=self.setAcft)

		menu = self.acftEntry['menu']
		menu.delete(0, "end")
		for acft in acfts:
			menu.add_command(label=acft, command=tk._setit(self.acftVar, acft))

		self.acftEntry.grid(row=1, column=1)

		editAcft = tk.Button(body, text='Edit', command=self.editAcft)
		editAcft.grid(row=1, column=2)

		self.initial_focus = self.pilotEntry
		body.pack(padx = 5, pady = 5)
		self.buttonbox()
		self.grab_set()

		self.protocol("WM_DELETE_WINDOW", self.cancel)

		self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
			parent.winfo_rooty()+50))

		self.initial_focus.focus_set()

		self.wait_window(self)

	def setAcft(self, value):
		self.acftVar.set(value)
		self.selectedAcft = value

	def editAcft(self):
		d = ACFTInfoEdit(self, self.data)
		menu = self.acftEntry['menu']
		menu.delete(0, 'end')
		for acft in self.data.getAircraft():
			menu.add_command(label=acft, command=tk._setit(self.acftVar, acft))

	def setPilot(self, value):
		self.pilotVar.set(value)
		self.selectedPilot = value

	def editPilots(self):
		d = PilotInfoEdit(self, self.data)
		menu = self.pilotEntry['menu']
		menu.delete(0, 'end')
		for pilot in self.data.getPilots():
			menu.add_command(label=pilot, command=tk._setit(self.pilotVar, pilot))

	def buttonbox(self):
		# add standard button box. override if you don't want the
		# standard buttons

		box = tk.Frame(self)

		w = tk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
		w.pack(side=tk.LEFT, padx=5, pady=5)
		w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
		w.pack(side=tk.LEFT, padx=5, pady=5)

		self.bind("<Return>", self.ok)
		self.bind("<Escape>", self.cancel)

		box.pack()

	def ok(self, event=None):
		self.withdraw()
		self.update_idletasks()
		self.apply()
		self.cancel()

	def cancel(self, event=None):

		# put focus back to the parent window
		self.parent.focus_set()
		self.destroy()

	def apply(self):
		mavlogs = []
		for log in self.logs:
			mavlog = bin_log_analyzer.mavLog(log, self.selectedPilot.getName(),
				self.selectedPilot.getCert(), str(self.selectedAcft))
			mavlog.analyze()
			date = mavlog.takeoff_date
			if date is None:
				new_dir = os.path.join(self.logPath, 'no_date')
			else:
				new_dir = os.path.join(self.logPath, '%04d.%02d.%02d' % 
					(date.year, date.month, date.day))
			if not os.path.isdir(new_dir):
				os.mkdir(new_dir)
			shutil.move(log, os.path.join(new_dir, os.path.basename(log)))

			mavlogs.append(mavlog)
			mavlog.generate_report(os.path.join(new_dir, 
				os.path.basename(mavlog.report_fname)))

class LogAnalyzerGui:
	"""Log Analyzer Gui"""
	def __init__(self, logPath):
		self.logPath = logPath
		self._Data = DataStore()
		
		self.root = tk.Tk()
		self.root.title("E4E ArduPilot Log Manager")

		self.centerFrame = tk.Frame(self.root)

		self.logView = ttk.Treeview(self.centerFrame)
		self.logView.bind("<ButtonRelease-1>", self.selectNode)
		self.loadLogTree()
		self.logDisplay = tk.LabelFrame(self.centerFrame)

		tk.Label(self.logDisplay, justify="left", text='Pilot:')\
			.grid(row=0, column=0, sticky=tk.E)
		tk.Label(self.logDisplay, justify="left", text='Pilot Certificate:')\
			.grid(row=1, column=0, sticky=tk.E)
		tk.Label(self.logDisplay, justify="left", text='Aircraft Registration:')\
			.grid(row=2, column=0, sticky=tk.E)
		tk.Label(self.logDisplay, justify="left", text='Flight Operations Area:')\
			.grid(row=3, column=0, sticky=tk.E)
		tk.Label(self.logDisplay, justify="left", text='Time In Air:')\
			.grid(row=4, column=0, sticky=tk.E)
		tk.Label(self.logDisplay, justify="left", text='Battery Consumption:')\
			.grid(row=5, column=0, sticky=tk.E)
		tk.Label(self.logDisplay, justify="left", text='Flight Modes:')\
			.grid(row=6, column=0, sticky=tk.E)
		tk.Label(self.logDisplay, justify="left", text='Errors:')\
			.grid(row=7, column=0, sticky=tk.E)
		tk.Label(self.logDisplay, justify="left", text='Takeoffs:')\
			.grid(row=8, column=0, sticky=tk.E)

		self.logVars = {}
		self.logVars['pilotName'] = tk.StringVar(self.logDisplay)
		self.logVars['pilotCert'] = tk.StringVar(self.logDisplay)
		self.logVars['Aircraft'] = tk.StringVar(self.logDisplay)
		self.logVars['OpsArea'] = tk.StringVar(self.logDisplay)
		self.logVars['AirTime'] = tk.StringVar(self.logDisplay)
		self.logVars['Consumption'] = tk.StringVar(self.logDisplay)
		self.logVars['numTakeoffs'] = tk.StringVar(self.logDisplay)
		self.logVars['flightModes'] = tk.StringVar(self.logDisplay)
		self.logVars['Errors'] = tk.StringVar(self.logDisplay)
		self.logVars['Takeoffs'] = tk.StringVar(self.logDisplay)

		tk.Entry(self.logDisplay, state=tk.DISABLED, 
			textvariable=self.logVars['pilotName']).grid(row=0, column=1)
		tk.Entry(self.logDisplay, state=tk.DISABLED, 
			textvariable=self.logVars['pilotCert']).grid(row=1, column=1)
		tk.Entry(self.logDisplay, state=tk.DISABLED, 
			textvariable=self.logVars['Aircraft']).grid(row=2, column=1)
		tk.Entry(self.logDisplay, state=tk.DISABLED, 
			textvariable=self.logVars['OpsArea']).grid(row=3, column=1)
		tk.Entry(self.logDisplay, state=tk.DISABLED, 
			textvariable=self.logVars['AirTime']).grid(row=4, column=1)
		tk.Entry(self.logDisplay, state=tk.DISABLED, 
			textvariable=self.logVars['Consumption']).grid(row=5, column=1)
		tk.Entry(self.logDisplay, state=tk.DISABLED, 
			textvariable=self.logVars['flightModes']).grid(row=6, column=1)
		tk.Entry(self.logDisplay, state=tk.DISABLED, 
			textvariable=self.logVars['Errors']).grid(row=7, column=1)
		tk.Entry(self.logDisplay, state=tk.DISABLED, 
			textvariable=self.logVars['numTakeoffs']).grid(row=8, column=1)


		self.logDisplay.pack(side=tk.RIGHT, fill=tk.BOTH)
		self.logView.pack(side=tk.RIGHT, fill=tk.BOTH, expand=1)

		self.buttonFrame = tk.Frame(self.root)
		self.loadLogButton = tk.Button(self.buttonFrame, 
			text="Load Logs", command=self.loadLogs)
		self.editPilotButton = tk.Button(self.buttonFrame, 
			text='Edit Pilots', command=self.editPilots)
		self.editAircraftButton = tk.Button(self.buttonFrame, 
			text='Edit Aircraft', command=self.editAircraft)

		self.centerFrame.pack(fill=tk.BOTH, expand=1)
		self.loadLogButton.pack(side=tk.LEFT)
		self.editPilotButton.pack(side=tk.LEFT)
		self.editAircraftButton.pack(side=tk.LEFT)
		self.buttonFrame.pack()

	def loadLogTree(self):
		self.logView.delete(*self.logView.get_children())
		root_node = self.logView.insert('', 'end', text=self.logPath, 
			open=True, value=self.logPath)
		self.loadDirectory(root_node, self.logPath)

	def editPilots(self):
		d = PilotInfoEdit(self.root, self._Data)

	def editAircraft(self):
		d = ACFTInfoEdit(self.root, self._Data)

	def loadLogs(self):
		logs = fd.askopenfilenames(initialdir='~',
			title='Select Logs',
			filetypes = [("Dataflash Logs", "*.BIN *.bin")])
		if logs == () or logs == "":
			return
		logs = list(logs)

		copiedLogs = []

		# Copy to logs folder
		for log in logs:
			dest = os.path.join(self.logPath, os.path.basename(log))
			shutil.copy2(log, dest)
			copiedLogs.append(dest)
		d = LogInfoGui(self.root, self._Data, copiedLogs, self.logPath)
		self.loadLogTree()

	def selectNode(self, event):
		curItem = self.logView.focus()
		# print(self.logView.item(curItem)['values'])
		nodeType = self.logView.item(curItem)['values'][1]
		value = self.logView.item(curItem)['values'][0]
		self.logVars['pilotName'].set('')
		self.logVars['pilotCert'].set('')
		self.logVars['Aircraft'].set('')
		self.logVars['OpsArea'].set('')
		self.logVars['AirTime'].set('')
		self.logVars['Consumption'].set('')
		self.logVars['numTakeoffs'].set('')
		self.logVars['flightModes'].set('')
		self.logVars['Errors'].set('')
		if nodeType == 'apm' or nodeType == 'dir':
			if value != "None":
				rpt = logReport(value)
				self.logVars['pilotName'].set(rpt.pilotName)
				self.logVars['pilotCert'].set(rpt.pilotCert)
				self.logVars['Aircraft'].set(rpt.aircraft)
				self.logVars['OpsArea'].set(rpt.opsArea)
				self.logVars['AirTime'].set(rpt.AirTime)
				self.logVars['Consumption'].set(rpt.consumption)
				self.logVars['numTakeoffs'].set(rpt.numTakeoffs)
				self.logVars['flightModes'].set(rpt.flightModes)
				self.logVars['Errors'].set(rpt.numErrors)
				return

		pass

	def loadDirectory(self, parent, path):
		for p in sorted(os.listdir(path)):
			abspath = os.path.join(path, p)
			isdir = os.path.isdir(abspath)
			if os.path.isdir(abspath):
				if p != 'no_date':
					date = datetime.datetime.strptime(p[:10], '%Y.%m.%d')
					val = os.path.join(path, p, "%s.rpt" % (date.date().isoformat()))
					if not os.path.isfile(val):
						val = None
					old = self.logView.insert(parent, 'end', text=p, open=False,
						value=[val, 'dir'])
				else:
					old = self.logView.insert(parent, 'end', text=p, open=False,
						value=[None, 'no-date'])
				self.loadDirectory(old, abspath)
			elif os.path.splitext(p)[1].lower() == '.bin':
				val = os.path.splitext(abspath)[0] + '.rpt'
				old = self.logView.insert(parent, 'end', text=p, open=False, 
					value=[val, 'apm'])

	def run(self):
		self.root.mainloop()

class logReport:
	def __init__(self, reportPath):
		assert(os.path.isfile(reportPath))
		self.pilotName = ""
		self.pilotCert = ""
		self.aircraft = ""
		self.opsArea = ""
		self.AirTime = ""
		self.numTakeoffs = 0
		self.takeoffs = []
		self.flightModes = ""
		self.numErrors = 0
		self.Errors = []
		self.consumption = ""
		with open(reportPath) as report:
			for line in report:
				try:
					key = line.split(':')[0].strip()
					value = line.split(':')[1].strip()
				except IndexError as e:
					print(e)
					print(line)
				if key == 'Pilot':
					self.pilotName = value
				elif key == 'Certificate #':
					self.pilotCert = value
				elif key == 'Aircraft Registration':
					self.aircraft = value
				elif key == 'Flight Operations Area':
					self.opsArea = value
				elif key == 'Time In Air':
					self.AirTime = value
				elif key == 'Takeoffs':
					self.numTakeoffs = int(value)
					self.takeoffs = [''] * self.numTakeoffs
					for i in range(self.numTakeoffs):
						line = next(report)
						self.takeoffs[i] = line.strip()
				elif key == 'Flight Modes':
					self.flightModes = value
				elif key == 'Errors':
					if value == 'None':
						value = 0
					self.numErrors = int(value)
					self.Errors = [""] * self.numErrors
					for i in range(self.numErrors):
						line = next(report)
						self.Errors[i] = line.strip()
				elif key == 'Consumed':
					self.consumption = value

def main():
	logPath = os.path.abspath('logs')
	root = LogAnalyzerGui(logPath)

	root.run()

if __name__ == '__main__':
	main()