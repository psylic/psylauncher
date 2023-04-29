from switchframe import SwitchFrame
import customtkinter as ctk
import os

# App information and defaults
VERSION = 1.2
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


# Get layout properties from LAYOUT.txt file
def get_layout():
    layoutfile = os.getcwd() + "\\LAYOUT.txt"
    layout = {}
    with open(layoutfile) as f:
        for line in f:
            key, value = line.split(' = ')
            layout.update({key: int(value)})
    return layout


class App(ctk.CTk):
    def __init__(self):
        # Initialize inherited properties
        super().__init__()

        # Initiliaze and set variables
        self.LAYOUT = get_layout()
        self.title(f"PsyLauncher v{VERSION}")

        # Set height and width based on number of rows and columns from LAYOUT.txt
        self.HEIGHT = [(self.LAYOUT["ROWS"] * 200) + 200, self.LAYOUT["MIN_HEIGHT"]][(self.LAYOUT["ROWS"] * 200) + 200 < self.LAYOUT["MIN_HEIGHT"]]
        self.WIDTH = [(self.LAYOUT["COLUMNS"] * 150) + 100, self.LAYOUT["MIN_WIDTH"]][(self.LAYOUT["COLUMNS"] * 150) + 100 < self.LAYOUT["MIN_WIDTH"]]
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")

        # Configure Rows and Columns
        for row in range(self.LAYOUT["ROWS"]):
            self.grid_rowconfigure(row, weight=1)
        for col in range(self.LAYOUT["COLUMNS"]):
            self.grid_columnconfigure(col, weight=1)
        self.grid_rowconfigure(self.LAYOUT["ROWS"]+1, weight=1)

        # Build Frames
        self.frames = []
        for filename in os.listdir(os.getcwd() + "\\PROGRAMS"):
            self.frames.append(SwitchFrame(filename, master=self))

        # Build Run All Button
        self.run_btn = ctk.CTkButton(master=self, text="Run All", command=self.run_all)

        # Build Add New Button
        self.add_new_btn = ctk.CTkButton(master=self, text="Add New", command=self.add_new_frame)

        # Show Frames
        self.update_frames()

    def run_all(self):
        # Loop over all switchframes
        for i, _ in enumerate(self.frames):
            # Call switchframe's run button's command
            self.frames[i].run_btn.cget("command")()

    def update_frames(self):
        # Remove all switchframes from grid
        for j in range(len(self.frames)):
            self.frames[j].grid_forget()

        # Add frames to grid, based on (row, column) layout
        i = 0
        for row in range(self.LAYOUT["ROWS"]):
            for col in range(self.LAYOUT["COLUMNS"]):
                if i < len(self.frames):
                    self.frames[i].grid(row=row, column=col)
                i += 1

        # Add run all and add new buttons to bottom of grid
        self.run_btn.grid(row=self.LAYOUT["ROWS"] + 1, column=0, columnspan=self.LAYOUT["COLUMNS"])
        self.add_new_btn.grid(row=self.LAYOUT["ROWS"] + 2, column=0, columnspan=self.LAYOUT["COLUMNS"])

    def add_new_frame(self):
        # Prompt user for new frame name
        dialog = ctk.CTkInputDialog(text="Enter Name of New Collection:", title="New Collection").get_input()

        # Add empty frame to list with name from user
        self.frames.append(SwitchFrame(dialog, master=self))

        # Update app with new frame
        self.update_frames()


if __name__ == '__main__':
    app = App()
    app.mainloop()
