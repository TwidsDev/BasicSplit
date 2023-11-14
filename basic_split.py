import tkinter as tk
from tkinter import messagebox, filedialog, colorchooser, PhotoImage
import time
import pickle
import configparser
import os
import platform  # Added platform module

class TimerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("BasicSplit")
        self.master.resizable(False, False)  # Disable maximize button, enable minimize button

        self.is_running = False
        self.start_time = None
        self.split_times = []
        self.loaded_split_file = None  # Added variable to keep track of loaded split file

        # Initialize entry widgets as None
        self.start_entry = None
        self.stop_entry = None
        self.reset_entry = None
        self.split_entry = None
        self.background_entry = None

        self.load_config()  # Load the settings from the config file

        self.label = tk.Label(master, text="0:00.00", font=("Helvetica", 36))
        self.label.pack(pady=10)

        self.split_listbox = tk.Listbox(master, height=5, selectmode=tk.BROWSE)
        self.split_listbox.pack(pady=10)

        self.start_stop_button = tk.Button(master, text="Start", command=self.toggle_timer)
        self.start_stop_button.pack(side=tk.TOP, fill=tk.X, padx=20, pady=5)

        self.reset_button = tk.Button(master, text="Reset", command=self.reset_timer)
        self.reset_button.pack(side=tk.TOP, fill=tk.X, padx=20, pady=5)

        self.split_button = tk.Button(master, text="Split", command=self.split_timer)
        self.split_button.pack(side=tk.TOP, fill=tk.X, padx=20, pady=5)

        self.compare_button = tk.Button(master, text="Compare", command=self.compare_splits)
        self.compare_button.pack(side=tk.TOP, fill=tk.X, padx=20, pady=5)

        # Create an icon if it exists (you can replace 'icon.png' with the path to your icon file)
        try:
            self.icon = PhotoImage(file='icon.png')
        except tk.TclError:
            # Handle the case where the icon file is not found or not a valid image
            self.icon = None

        # Check the operating system
        self.is_macos = platform.system() == 'Darwin'
        self.is_windows = platform.system() == 'Windows'
        self.is_linux = platform.system() == 'Linux'
        self.version_num = 0.1

        self.create_menu()

        # Apply settings on window creation
        self.apply_settings()

    def open_link(self, url):
        import webbrowser
        webbrowser.open(url)

    def load_config(self):
        self.config = configparser.ConfigParser()

        # Create a default config if not exists
        if not os.path.exists('config.ini'):
            self.config['Settings'] = {
                'StartHotkey': 's',
                'StopHotkey': 'x',
                'ResetHotkey': 'r',
                'SplitHotkey': 'space',
                'AlwaysOnTop': 'yes',
                'BackgroundColor': ''
            }
            with open('config.ini', 'w') as configfile:
                self.config.write(configfile)

        # Load the config file
        self.config.read('config.ini')

    def save_config(self):
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)

    def apply_settings(self):
        # Apply hotkeys
        if self.start_entry:
            self.start_entry.delete(0, tk.END)
            self.start_entry.insert(0, self.config.get('Settings', 'StartHotkey'))

        if self.stop_entry:
            self.stop_entry.delete(0, tk.END)
            self.stop_entry.insert(0, self.config.get('Settings', 'StopHotkey'))

        if self.reset_entry:
            self.reset_entry.delete(0, tk.END)
            self.reset_entry.insert(0, self.config.get('Settings', 'ResetHotkey'))

        if self.split_entry:
            self.split_entry.delete(0, tk.END)
            self.split_entry.insert(0, self.config.get('Settings', 'SplitHotkey'))

        # Apply Always On Top
        always_on_top_var = tk.BooleanVar()
        always_on_top_var.set(self.config.getboolean('Settings', 'AlwaysOnTop'))
        self.master.wm_attributes("-topmost", always_on_top_var.get())

        # Apply Background Color
        background_color = self.config.get('Settings', 'BackgroundColor')
        self.master.configure(bg=background_color)

    def create_menu(self):
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="About", command=self.show_about_window)
        file_menu.add_separator()
        file_menu.add_command(label="New", command=self.new_splits)
        file_menu.add_command(label="Save", command=self.save_splits)
        file_menu.add_command(label="Compare", command=self.compare_splits)
        file_menu.add_separator()
        file_menu.add_command(label="Settings", command=self.open_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Close", command=self.close_app)

    def show_about_window(self):
        about_window = tk.Toplevel(self.master)
        about_window.title("About BasicSplit")

        # Set window attributes for macOS
        about_window.attributes('-topmost', True)

        # Set icon if it exists
        if hasattr(self, 'icon') and self.icon:
            about_window.iconphoto(True, self.icon)

        # Create and place widgets in the about window
        if hasattr(self, 'icon') and self.icon:
            icon_label = tk.Label(about_window, image=self.icon)
            icon_label.grid(row=0, column=0, padx=10, pady=10, rowspan=3)

        title_label = tk.Label(about_window, text="BasicSplit", font=("Helvetica", 16, "bold"))
        title_label.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)

        version_label_text = f"Version {self.version_num} (OS: {platform.system()})"
        version_label = tk.Label(about_window, text=version_label_text)
        version_label.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)

        about_text = "This is a simple time splitting application created with Python to be cross platform.\n\n" \
        "This is an open source project by "
        about_label = tk.Label(about_window, text=about_text, wraplength=300, justify=tk.LEFT)
        about_label.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)
        twids_link = tk.Label(about_window, text="@TwidsDev", fg="blue", cursor="hand2")
        twids_link.grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)
        twids_link.bind("<Button-1>", lambda e: self.open_link("https://twitter.com/TwidsDev"))
        github_link = tk.Label(about_window, text="GitHub", fg="blue", cursor="hand2")
        github_link.grid(row=3, column=2, padx=10, pady=5, sticky=tk.W)
        github_link.bind("<Button-1>", lambda e: self.open_link("https://github.com/TwidsDev/BasicSplit/"))


    def open_settings(self):
        settings_window = tk.Toplevel(self.master)
        settings_window.title("Settings")
        settings_window.wm_attributes('-topmost', True)  # Keep settings window on top

        start_label = tk.Label(settings_window, text="Start Hotkey:")
        start_label.grid(row=0, column=0, sticky=tk.E, padx=10, pady=5)
        self.start_entry = tk.Entry(settings_window)
        self.start_entry.grid(row=0, column=1, padx=10, pady=5)
        self.start_entry.bind("<Key>", lambda event: self.bind_hotkey(event, self.start_entry, 'StartHotkey'))

        stop_label = tk.Label(settings_window, text="Stop Hotkey:")
        stop_label.grid(row=1, column=0, sticky=tk.E, padx=10, pady=5)
        self.stop_entry = tk.Entry(settings_window)
        self.stop_entry.grid(row=1, column=1, padx=10, pady=5)
        self.stop_entry.bind("<Key>", lambda event: self.bind_hotkey(event, self.stop_entry, 'StopHotkey'))

        reset_label = tk.Label(settings_window, text="Reset Hotkey:")
        reset_label.grid(row=2, column=0, sticky=tk.E, padx=10, pady=5)
        self.reset_entry = tk.Entry(settings_window)
        self.reset_entry.grid(row=2, column=1, padx=10, pady=5)
        self.reset_entry.bind("<Key>", lambda event: self.bind_hotkey(event, self.reset_entry, 'ResetHotkey'))

        split_label = tk.Label(settings_window, text="Split Hotkey:")
        split_label.grid(row=3, column=0, sticky=tk.E, padx=10, pady=5)
        self.split_entry = tk.Entry(settings_window)
        self.split_entry.grid(row=3, column=1, padx=10, pady=5)
        self.split_entry.bind("<Key>", lambda event: self.bind_hotkey(event, self.split_entry, 'SplitHotkey'))

        always_on_top_var = tk.BooleanVar()
        always_on_top_check = tk.Checkbutton(settings_window, text="Window Always On Top", variable=always_on_top_var)
        always_on_top_check.grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky=tk.W)
        always_on_top_check.bind("<Button-1>", lambda event: self.toggle_always_on_top(always_on_top_var))

        background_label = tk.Label(settings_window, text="Background Colour:")
        background_label.grid(row=5, column=0, sticky=tk.E, padx=10, pady=5)
        self.background_entry = tk.Entry(settings_window)
        self.background_entry.grid(row=5, column=1, padx=10, pady=5)
        self.background_entry.bind("<Button-1>", self.pick_color)

        save_button = tk.Button(settings_window, text="Save", command=lambda: self.save_settings(settings_window))
        save_button.grid(row=6, column=0, pady=10, sticky=tk.E)

        cancel_button = tk.Button(settings_window, text="Cancel", command=settings_window.destroy)
        cancel_button.grid(row=6, column=1, pady=10, sticky=tk.W)

        # Set initial values based on config
        self.start_entry.insert(0, self.config.get('Settings', 'StartHotkey'))
        self.stop_entry.insert(0, self.config.get('Settings', 'StopHotkey'))
        self.reset_entry.insert(0, self.config.get('Settings', 'ResetHotkey'))
        self.split_entry.insert(0, self.config.get('Settings', 'SplitHotkey'))
        always_on_top_var.set(self.config.getboolean('Settings', 'AlwaysOnTop'))
        self.background_entry.insert(0, self.config.get('Settings', 'BackgroundColor'))

    def save_settings(self, settings_window):
        # Save hotkeys to the config file
        self.config.set('Settings', 'StartHotkey', self.start_entry.get())
        self.config.set('Settings', 'StopHotkey', self.stop_entry.get())
        self.config.set('Settings', 'ResetHotkey', self.reset_entry.get())
        self.config.set('Settings', 'SplitHotkey', self.split_entry.get())

        # Save Always On Top setting
        always_on_top_value = 'yes' if self.master.attributes('-topmost') else 'no'
        self.config.set('Settings', 'AlwaysOnTop', always_on_top_value)

        # Save Background Color setting
        self.config.set('Settings', 'BackgroundColor', self.background_entry.get())

        # Apply settings to the main window
        self.apply_settings()

        # Save the updated config to the file
        self.save_config()

        # Close the settings window
        settings_window.destroy()


    def toggle_always_on_top(self, always_on_top_var):
        always_on_top_value = 'yes' if always_on_top_var.get() else 'no'
        self.master.attributes("-topmost", always_on_top_var.get())
        self.config.set('Settings', 'AlwaysOnTop', always_on_top_value)

    def bind_hotkey(self, event, entry_widget, setting_name):
        entry_widget.delete(0, tk.END)
        hotkey = event.keysym
        entry_widget.insert(0, hotkey)
        # Update the config setting immediately
        self.config.set('Settings', setting_name, hotkey)

    def pick_color(self, event):
        color = colorchooser.askcolor()[1]
        if color:
            self.background_entry.delete(0, tk.END)
            self.background_entry.insert(0, color)
            # Update the config setting immediately
            self.config.set('Settings', 'BackgroundColor', color)

    def toggle_timer(self):
        if not self.is_running:
            self.start_timer()
            self.start_stop_button.config(text="Stop")
        else:
            self.stop_timer()
            self.start_stop_button.config(text="Start")

    def start_timer(self):
        if not self.is_running:
            self.is_running = True
            self.start_time = time.time()
            self.update_timer()

    def stop_timer(self):
        if self.is_running:
            self.is_running = False

    def reset_timer(self):
        self.is_running = False
        self.label.config(text="0:00.00")
        self.split_times = []
        self.update_split_list()

    def split_timer(self):
        if self.is_running:
            elapsed_time = time.time() - self.start_time
            self.split_times.append(elapsed_time)
            self.update_split_list()

    def update_timer(self):
        if self.is_running:
            elapsed_time = time.time() - self.start_time
            formatted_time = self.format_time(elapsed_time)
            self.label.config(text=formatted_time)
            self.master.after(100, self.update_timer)

    def format_time(self, elapsed_time):
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        milliseconds = int((elapsed_time % 1) * 100)
        return f"{minutes}:{seconds:02}.{milliseconds:02}"

    def update_split_list(self):
        self.split_listbox.delete(0, tk.END)
        for i, split_time in enumerate(self.split_times, start=1):
            formatted_split_time = self.format_time(split_time)
            color = 'green' if self.loaded_split_file and i <= len(self.loaded_split_file) and split_time < self.loaded_split_file[i-1] else 'red'
            self.split_listbox.insert(tk.END, f"Split {i}: {formatted_split_time}")
            self.split_listbox.itemconfig(tk.END, {'fg': color})

    def new_splits(self):
        result = messagebox.askyesno("New Splits", "Do you want to start a new set of splits?")
        if result:
            self.reset_timer()

    def save_splits(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".split", filetypes=[("Split files", "*.split")])
        if file_path:
            with open(file_path, "wb") as file:
                pickle.dump(self.split_times, file)

    def compare_splits(self):
        file_path = filedialog.askopenfilename(filetypes=[("Split files", "*.split")])
        if file_path:
            with open(file_path, "rb") as file:
                self.loaded_split_file = pickle.load(file)
                self.update_split_list()
                messagebox.showinfo("Comparison Result", "Splits loaded for comparison.")

    def close_app(self):
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TimerApp(root)
    root.mainloop()
