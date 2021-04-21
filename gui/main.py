import tkinter as tk
import tkinter.scrolledtext as tks
import tkinter.ttk as ttk
import tkinter.filedialog as tkf
import gui.comment_box as cb
import subprocess
import sys
import os
import re
import matplotlib
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, 
    NavigationToolbar2Tk
)
from matplotlib.figure import Figure
from datetime import datetime



class Application(tk.Frame):
	def clear_output(self):
		self.output_text["state"] = tk.NORMAL
		self.output_text.delete(1.0, tk.END)
		self.output_text["state"] = tk.DISABLED


	def append_output(self, line: str):
		self.output_text["state"] = tk.NORMAL
		self.output_text.insert(tk.END, line)
		self.output_text["state"] = tk.DISABLED


	def get_input(self):
		return [s for s in self.input_text.get(1.0, tk.END).splitlines() if s != ""]


	def spawn_process(self, args):
		self.clear_output()
		path = os.path.realpath(__file__) + '/../../dsbs.py'
		process = subprocess.Popen(
			[sys.executable, path] + args + ['-silent'], 
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE
		)
		while process.poll() is None:
			line = process.stdout.readline()
			if not line:
				line = process.stderr.readline()
				if not line:
					continue
			line = line.decode('utf-8')
			self.append_output(line)
		process.wait()
		if process.returncode == 0:
			self.append_output('Success' + "\n")
		else:
			self.append_output(f'Error: {process.returncode}\n')


	def __init__(self):
		super().__init__(tk.Tk())
		self.setup()


	def setup(self):
		self.master.title("DSBS GUI V0.0.0.0")
		self.style = ttk.Style();
		self.style.theme_use("default")
		self.pack(fill=tk.BOTH, expand=True)

		self.setup_input_frame()
		self.setup_control_frame()
		self.setup_output_frame()


	def setup_input_frame(self):
		self.input_frame = tk.Frame(self)
		self.input_frame.pack(side=tk.TOP, fill=tk.X)

		self.input_label = tk.Label(self.input_frame)
		self.input_label["text"] = "Input directories"
		self.input_label.pack(side=tk.TOP)

		self.input_text = tks.ScrolledText(self.input_frame)
		self.input_text["height"] = 8;
		self.input_text.pack(fill=tk.X, side=tk.TOP)

		self.browse_button = tk.Button(self.input_frame)
		self.browse_button["text"] = "Browse"
		self.browse_button["width"] = 8;
		self.browse_button["command"] = self.browse_button_click
		self.browse_button.pack(side="left", padx=5, pady=5)


	def setup_output_frame(self):
		self.output_frame = tk.Frame(self)
		self.output_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

		self.output_label = tk.Label(self.output_frame)
		self.output_label["text"] = "Output"
		self.output_label.pack(side=tk.TOP)

		self.output_text = tks.ScrolledText(self.output_frame)
		self.output_text["state"] = tk.DISABLED
		self.output_text.pack(fill=tk.BOTH, side=tk.TOP, expand=True)


	def setup_control_frame(self):
		self.control_frame = tk.Frame(self)
		self.control_frame.pack(side=tk.BOTTOM, fill=tk.X)

		self.index_button = tk.Button(self.control_frame)
		self.index_button["text"] = "Index"
		self.index_button["width"] = 8
		self.index_button["command"] = self.index_button_click
		self.index_button.pack(side=tk.LEFT, padx=5, pady=5)

		self.log_button = tk.Button(self.control_frame)
		self.log_button["text"] = "Log"
		self.log_button["width"] = 8
		self.log_button["command"] = self.log_button_click
		self.log_button.pack(side=tk.LEFT, padx=5, pady=5)

		self.status_button = tk.Button(self.control_frame)
		self.status_button["text"] = "Status"
		self.status_button["width"] = 8
		self.status_button["command"] = self.status_button_click
		self.status_button.pack(side=tk.LEFT, padx=5, pady=5)

		self.merge_button = tk.Button(self.control_frame)
		self.merge_button["text"] = "Merge"
		self.merge_button["width"] = 8
		self.merge_button["command"] = self.merge_button_click
		self.merge_button.pack(side=tk.LEFT, padx=5, pady=5)

		self.push_button = tk.Button(self.control_frame)
		self.push_button["text"] = "Push"
		self.push_button["width"] = 8
		self.push_button["command"] = self.push_button_click
		self.push_button.pack(side=tk.LEFT, padx=5, pady=5)

		self.clean_button = tk.Button(self.control_frame)
		self.clean_button["text"] = "Clean"
		self.clean_button["width"] = 8
		self.clean_button["command"] = self.clean_button_click
		self.clean_button.pack(side=tk.LEFT, padx=5, pady=5)

		self.graph_button = tk.Button(self.control_frame)
		self.graph_button["text"] = "Graph"
		self.graph_button["width"] = 8
		self.graph_button["command"] = self.graph_button_click
		self.graph_button.pack(side=tk.LEFT, padx=5, pady=5)


	def browse_button_click(self):
		directory = tkf.askdirectory()
		if directory:
			self.input_text.insert(tk.END, directory + "\n")
        

	def index_button_click(self):
		comment = cb.CommentBox(self)
		comment.wait_window()
		msg = comment.result
		if msg:
			for line in self.get_input():
				self.append_output(f"Starting process for \"{line}\"...\n")
				args = ['index', '-i', line];
				if msg != "":
					args += ['-m', msg]
				self.spawn_process(args)


	def log_button_click(self):
		for line in self.get_input():
			self.append_output(f"Starting process for \"{line}\"...\n")
			self.spawn_process(['log', '-i', line])


	def status_button_click(self):
		for line in self.get_input():
			self.append_output(f"Starting process for \"{line}\"...\n")
			self.spawn_process(['status', '-i', line])


	def merge_button_click(self):
		self.spawn_process(['merge'] + self.get_input())


	def push_button_click(self):
		self.spawn_process(['push', '-s', self.get_input()[0]] + self.get_input()[1:])


	def clean_button_click(self):
		self.spawn_process(['clean'] + self.get_input())

	def graph_button_click(self):
		out = self.output_text.get("1.0", tk.END)
		stamps = [
			datetime.strptime(x, '%Y-%m-%d %H:%M:%S') 
			for x in re.findall(r'\[(.+)\]', out)
		]
		
		frame = tk.Frame(tk.Toplevel(self))
		frame.master.title("Indexation history")
		frame.pack(fill=tk.BOTH, expand=True)

		fig = Figure(figsize=(5,4), dpi=100)
		ax = fig.add_subplot(1, 1, 1)
		ax.hist(stamps, 20)
		canvas = FigureCanvasTkAgg(fig, master=frame)
		canvas.get_tk_widget().pack(fill=tk.BOTH, side=tk.TOP, expand=True)






app = Application()
app.mainloop()