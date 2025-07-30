from TkinterWidgets import TiffViewer as iv
from TkinterWidgets import FlowPlane as  plane
import tkinter as tk

root = tk.Tk()
root.withdraw()  # Hide the root window
toplevel = tk.Toplevel(root,width=800, height=600)
toplevel.iconbitmap('./main.ico')  # Set the icon for the window
toplevel.title("CvFlow")
toplevel.pack_propagate(False)  # Prevent the window from resizing to fit its contents
graphics_frame = plane(toplevel)
graphics_frame.pack(fill=tk.BOTH, expand=True)
root.mainloop() 
 