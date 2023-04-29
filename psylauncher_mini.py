from switchframe import *
import customtkinter as ctk
import os

# App information and defaults
VERSION = 1.2
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class App(ctk.CTk):
    def __init__(self):
        # Initialize inherited properties
        super().__init__()
        self.title(f"PsyLauncher Mini v{VERSION}")

        # Build Frames (from .txt files in PROGRAMS folder
        self.frames = []
        for filename in os.listdir(os.getcwd() + "\\PROGRAMS"):
            self.frames.append(SwitchFrame(filename, master=self))

        # If there are no .txt files, build new empty frame
        if len(self.frames) == 0:
            self.frames.append(SwitchFrame(None, master=self))

        # Set selected frame to first frame in list
        self.selected_frame = ctk.StringVar(value=self.frames[0].name)

        # Build Combobox
        self.combobox = self.build_combobox()
        self.combobox.pack(padx=10, pady=5)

        # Pack Frame
        self.cur_frame = SwitchFrame(self.selected_frame.get() + ".txt", master=self)
        self.update_frame(self.selected_frame)

    def build_combobox(self):
        # Get list of options from built frames
        values = []
        for i, _ in enumerate(self.frames):
            values.append(self.frames[i].name)

        # Add new frame option
        values.append("--Add New--")

        return ctk.CTkComboBox(master=self, values=values, variable=self.selected_frame, command=self.update_frame)

    def update_frame(self, selected_frame):
        # Remove current frame from app
        self.cur_frame.pack_forget()

        # If selected frame from combobox is new frame option, build new frame, and add to end of list, before add new option
        if selected_frame == "--Add New--":
            self.frames.append(self.add_new_frame())
            values = self.combobox.cget("values")
            values.insert(-2, self.frames[-1].name)
            self.combobox.configure(values=values)
            self.combobox.set(self.frames[-1].name)
            self.cur_frame = self.frames[-1]

        # Set current frame to frame selected from combobox
        for i in range(len(self.frames)):
            if selected_frame == self.frames[i].name:
                self.cur_frame = self.frames[i]

        # Pack current frame
        self.cur_frame.pack(padx=10, pady=5)

    def add_new_frame(self):
        # Prompt user for new frame name
        dialog = ctk.CTkInputDialog(text="Enter Name of New Collection:", title="New Collection").get_input()

        # Build empty frame with name from user
        return SwitchFrame(dialog, master=self)


if __name__ == '__main__':
    app = App()
    app.after(10, lambda: setWinStyle(app))
    app.mainloop()
