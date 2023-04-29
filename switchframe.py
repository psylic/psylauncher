from tkinter import filedialog
from tkinter.messagebox import askyesno
from functools import partial
from PIL import Image
import customtkinter as ctk
import ctypes as ct
import os


# Parse .txt file for list of programs
def get_programs(path: str):
    programs = {}
    with open(path) as f:
        for line in f:
            name, program = line.split(' = ')
            programs.update({name: [program.strip(), ctk.BooleanVar(value=False)]})
    return programs


# Function for removing resize buttons from title bar (used in Mini Launcher, and FrameManager)
# (NOTE: Windows Defender will flag program as malicious, I assume it's due to something from this function)
# Copied from: https://stackoverflow.com/questions/2969870/removing-minimize-maximize-buttons-in-tkinter/72664499#72664499
def setWinStyle(root):
    set_window_pos = ct.windll.user32.SetWindowPos
    set_window_long = ct.windll.user32.SetWindowLongPtrW
    get_window_long = ct.windll.user32.GetWindowLongPtrW
    get_parent = ct.windll.user32.GetParent

    # Identifiers
    gwl_style = -16

    ws_minimizebox = 131072
    ws_maximizebox = 65536

    swp_nozorder = 4
    swp_nomove = 2
    swp_nosize = 1
    swp_framechanged = 32

    hwnd = get_parent(root.winfo_id())

    old_style = get_window_long(hwnd, gwl_style) # Get the style

    new_style = old_style & ~ ws_maximizebox & ~ ws_minimizebox # New style, without max/min buttons

    set_window_long(hwnd, gwl_style, new_style) # Apply the new style

    set_window_pos(hwnd, 0, 0, 0, 0, 0, swp_nomove | swp_nosize | swp_nozorder | swp_framechanged)     # Updates


class SwitchFrame(ctk.CTkFrame):
    def __init__(self, programfile, master, **kwargs):
        # Initialize inherited properties
        super().__init__(master, **kwargs)

        if programfile is not None:
            # If programfile is a file that exists already
            if '.txt' in programfile:
                self.program_path = os.getcwd() + f"\\PROGRAMS\\{programfile}"
                self.programs = get_programs(self.program_path)

            # Else (if programfile is just name (new frame, name from user input))
            # Make empty .txt file from name, build empty program
            else:
                programfile = programfile + '.txt'
                self.program_path = os.getcwd() + f"\\PROGRAMS\\{programfile}"
                f = open(self.program_path, 'w')
                f.close()
                self.programs = {"Empty": ["Empty", ctk.BooleanVar(value=False)]}

        # Failsafe else, make empty .txt file, and empty program
        else:
            programfile = 'Empty.txt'
            self.program_path = os.getcwd() + f"\\PROGRAMS\\{programfile}"
            f = open(self.program_path, 'w')
            f.close()
            self.programs = {"Empty": ["Empty", ctk.BooleanVar(value=False)]}

        # Initialize variables
        self.switches = []
        self.manager = None
        self.name, _ = programfile.split('.txt')

        # Set tkinter grid properties
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)

        # Manager Button
        self.manager_img = ctk.CTkImage(light_image=Image.open(os.getcwd() + "\\ASSETS\\cogwheel.png"))
        self.manager_img_size = self.manager_img.cget("size")
        self.manager_btn = ctk.CTkButton(master=self, height=self.manager_img_size[0], width=self.manager_img_size[1], fg_color="transparent", text="", image=self.manager_img, command=self.open_manager)
        self.manager_btn.grid(row=0, column=0)

        # Delete Button
        self.delete_img = ctk.CTkImage(light_image=Image.open(os.getcwd() + "\\ASSETS\\delete_icon.png"))
        self.delete_img_size = self.delete_img.cget("size")
        self.delete_btn = ctk.CTkButton(master=self, height=self.delete_img_size[0], width=self.delete_img_size[1], fg_color="transparent", text="", image=self.delete_img, command=self.delete_frame)
        self.delete_btn.grid(row=0, column=2)

        # Name Label
        self.name_label = ctk.CTkLabel(master=self, text=self.name)
        self.name_label.grid(row=0, column=1)

        # Run Button
        self.run_img = ctk.CTkImage(light_image=Image.open(os.getcwd() + "\\ASSETS\\play.png"))
        self.run_btn = ctk.CTkButton(master=self, text=f"Start {self.name}", image=self.run_img, command=self.run_programs)

        # Update
        self.update_all()

    def run_programs(self):
        # Check all programs in frame, if run bool is true, open program from program_path
        for _, name in enumerate(self.programs):
            if self.programs[name][1].get():
                os.startfile(self.programs[name][0])

    def build_switches(self):
        # For programs in list, create a switch and connect run bool to switch
        for count, name in enumerate(self.programs):
            self.switches.append(ctk.CTkSwitch(master=self, text=name, variable=self.programs[name][1], onvalue=True, offvalue=False))

            # Add new switch to grid
            self.switches[count].grid(row=count+1, column=1, pady=5)

    def update_all(self):
        # Destroy all switches in frame
        for i in range(len(self.switches)):
            self.switches[i].destroy()

        # Remove run button from display
        self.run_btn.grid_forget()

        # Build new switches
        self.switches = []
        self.programs = get_programs(self.program_path)
        self.build_switches()

        # Grid run button to bottom of frame
        self.run_btn.grid(row=len(self.switches)+2, column=0, columnspan=3)

    def open_manager(self):
        # If manager frame does not exist
        if self.manager is None or not self.manager.winfo_exists():
            # Build new manager frame
            self.manager = FrameManager(self)

            # Remove resize buttons from title bar
            self.manager.after(10, lambda: setWinStyle(self.manager))

            # Bring manager to foreground
            self.manager.after(15, self.manager.focus)

        # Else (manager already exists)
        else:
            # Bring manager to foreground
            self.manager.focus()

    def delete_frame(self):
        # Prompt user to delete frame (deletes text file this frame was created from)
        answer = askyesno(title=f"Delete {self.name}", message=f"Are you sure you want to delete {self.name}?")
        if answer:
            os.remove(self.program_path)
            self.destroy()


class FrameManager(ctk.CTkToplevel):
    def __init__(self, parent: SwitchFrame, *args, **kwargs):
        # Initialize inherited properties
        super().__init__(*args, **kwargs)

        # Initialize and set variables
        self.parent = parent
        self.title(f"{self.parent.name} Configure")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.remove_img = ctk.CTkImage(light_image=Image.open(os.getcwd() + "\\ASSETS\\delete_icon.png"))
        self.browse_img = ctk.CTkImage(light_image=Image.open(os.getcwd() + "\\ASSETS\\folder_icon.png"))
        self.remove_img_size = self.remove_img.cget("size")
        self.browse_img_size = self.browse_img.cget("size")

        # Labels
        self.name_label = ctk.CTkLabel(master=self, text="Name")
        self.name_label.grid(row=0, column=0)
        self.path_label = ctk.CTkLabel(master=self, text="Programs")
        self.path_label.grid(row=0, column=1)

        # Build Name and Path Entries, and buttons
        self.name_entries = []
        self.path_entries = []
        self.browse_btns = []
        self.remove_btns = []
        for i, name in enumerate(self.parent.programs):
            name_entry = ctk.CTkEntry(master=self, width=100, textvariable=ctk.StringVar(value=name))
            path_entry = ctk.CTkEntry(master=self, width=200, textvariable=ctk.StringVar(value=self.parent.programs[name][0]))
            self.name_entries.append(name_entry)
            self.path_entries.append(path_entry)
            self.browse_btns.append(ctk.CTkButton(master=self, fg_color="transparent", text="", image=self.browse_img, width=self.browse_img_size[0], height=self.browse_img_size[1], command=partial(self.path_browse, i)))
            self.remove_btns.append(ctk.CTkButton(master=self, fg_color="transparent", text="", image=self.remove_img, width=self.remove_img_size[0], height=self.remove_img_size[1], command=partial(self.remove_program,i)))

        # Save Button
        self.save_btn = ctk.CTkButton(master=self, text="Save", command=self.save_programs)

        # Add New Button
        self.new_btn = ctk.CTkButton(master=self, text="Add New", command=self.add_program)

        self.update_all()

    def update_all(self):
        # Add all widgets to grid, associating each row with a new program entry
        for i in range(len(self.name_entries)):
            self.name_entries[i].grid(row=i+1, column=0, padx=5, pady=5)
            self.path_entries[i].grid(row=i+1, column=1, padx=5, pady=5)
            self.browse_btns[i].grid(row=i+1, column=2, padx=0, pady=5)
            self.remove_btns[i].grid(row=i+1, column=3, padx=0, pady=5)

        # Add buttons to bottom of grid
        self.new_btn.grid(row=len(self.name_entries) + 2, column=0, columnspan=4)
        self.save_btn.grid(row=len(self.name_entries) + 3, column=0, columnspan=4)

    def save_programs(self):
        # Save programs entries to .txt file associated with frame
        with open(self.parent.program_path, 'w') as f:
            programs = []
            for i in range(len(self.name_entries)):
                programs.append(f"{self.name_entries[i].get()} = {self.path_entries[i].get()}\n")
            f.writelines(programs)

    def add_program(self):
        # Add new program entry to frame
        length = len(self.name_entries)
        self.name_entries.append(ctk.CTkEntry(master=self, width=100, textvariable=ctk.StringVar(value=f"New Name")))
        self.path_entries.append(ctk.CTkEntry(master=self, width=200, textvariable=ctk.StringVar(value=f"\"New Path\"")))
        self.browse_btns.append(ctk.CTkButton(master=self, fg_color="transparent", text="", image=self.browse_img, width=self.browse_img_size[0], height=self.remove_img_size[0], command=partial(self.path_browse, length)))
        self.remove_btns.append(ctk.CTkButton(master=self, fg_color="transparent", text="", image=self.remove_img, width=self.remove_img_size[0], height=self.remove_img_size[0], command=partial(self.remove_program, length)))

        # Update frame with new entry
        self.update_all()

    def remove_program(self, index: int):
        # Remove program entry (name entry, path entry, add button, remove button)
        # Destroy tkinter object, then remove from list used to create tkinter objects
        self.name_entries[index].destroy()
        self.name_entries.pop(index)
        self.path_entries[index].destroy()
        self.path_entries.pop(index)
        self.remove_btns[index].destroy()
        self.remove_btns.pop(index)
        self.browse_btns[index].destroy()
        self.browse_btns.pop(index)

        # Update button commands with new indexes
        for i in range(len(self.remove_btns)):
            self.remove_btns[i].configure(command=partial(self.remove_program, i))
            self.browse_btns[i].configure(command=partial(self.path_browse, i))

        # Update frame
        self.update_all()

    def path_browse(self, index: int):
        # Prompt user with file explorer
        filetypes = [('Executable files', '*.exe'),
                     ('All files', '*.*')]
        path = f"\"{filedialog.askopenfilename(title='Select a File', initialdir='/', filetypes=filetypes)}\""

        # If no new file selected, set entry text to previous entry text
        if path != "\"\"":
            self.path_entries[index].configure(textvariable=ctk.StringVar(value=path))

        # Bring framemanager to foreground
        self.focus()

    def on_closing(self):
        # Updates parent frame with new inputs
        self.parent.update_all()

        # Destroy framemanager object
        self.destroy()


# For testing
if __name__ == '__main__':
    ROWS = 1
    COLUMNS = 1

    WIDTH = COLUMNS * 200
    HEIGHT = ROWS * 300

    root = ctk.CTk()
    root.title("switchframe, framemanager")
    root.geometry(f"{WIDTH}x{HEIGHT}")

    frame = SwitchFrame("Sites.txt", master=root)
    frame.pack(padx=10, pady=10)

    root.mainloop()
