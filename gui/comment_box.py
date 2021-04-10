import tkinter as tk
import tkinter.scrolledtext as tks
import tkinter.ttk as ttk
import tkinter.filedialog as tkf



class CommentBox(tk.Frame):
	def __init__(self, master):
		master = tk.Toplevel(master)
		super().__init__(master)
		self.setup()
		self.result = False


	def setup(self):
		self.master.title("Comment")
		self.style = ttk.Style();
		self.style.theme_use("default")
		self.pack(fill=tk.BOTH, expand=True)

		self.input_text = tks.ScrolledText(self)
		self.input_text["height"] = 8;
		self.input_text.pack(fill=tk.BOTH, side=tk.TOP, expand=True)

		self.apply_button = tk.Button(self)
		self.apply_button["text"] = "Apply"
		self.apply_button["width"] = 8;
		self.apply_button["command"] = self.apply_button_click
		self.apply_button.pack(side=tk.LEFT, padx=5, pady=5)

		self.cancel_button = tk.Button(self)
		self.cancel_button["text"] = "Cancel"
		self.cancel_button["width"] = 8;
		self.cancel_button["command"] = self.cancel_button_click
		self.cancel_button.pack(side=tk.LEFT, padx=5, pady=5)


	def apply_button_click(self):
		self.result = self.input_text.get(1.0, tk.END)
		self.master.destroy()


	def cancel_button_click(self):
		self.master.destroy()