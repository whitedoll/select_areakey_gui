import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import threading, time, json
import pyautogui
from pynput import mouse
import cv2, numpy, imutils, keyboard

class ClickMeButton:
    def __init__(self, size, master, button_name):
        self.master = master
        self.button_name = button_name
        self.shortcut = None
        self.size = size
        self.set_img = None
        self.create_widgets()

    def create_widgets(self):
        self.frame = tk.Frame(self.master)
        self.frame.pack(side="left")
        self.button = tk.Button(self.frame, text=self.button_name, command=self.get_shortcut)
        self.button.pack()

        # Add a label to show the image
        self.image_label = tk.Label(self.frame)
        self.image_label.pack()

    def button_callback(self):
        print("Button Clicked {}".format(self.button_name))

    def get_shortcut(self):
        self.button.config(text="Press a key for shortcut...")
        self.button.bind("<KeyPress>", self.save_shortcut)
        self.button.focus_set()

    def save_shortcut(self, event):
        self.shortcut = event.char
        modifier = ""
        # print(type(event.keysym))
        if event.state & 0x0004:  # Check if Ctrl key is pressed
            modifier += "Control-"
        elif event.state & 0x0001:  # Check if Shift key is pressed
            modifier += "Shift-"
        elif event.state & 0x20000:  # Check if Alt key is pressed
            modifier += "Alt-"

        self.shortcut = f"{modifier}{self.shortcut}"
        self.button.config(text=f"{self.shortcut}")
        root.unbind('<KeyPress>')
        
    def set_shortcut(self, shortcut):
        self.shortcut = shortcut
        self.button.unbind("<KeyPress>")
        self.button.bind("<%s>" % shortcut, lambda event=None: self.button_callback(shortcut))
        self.button_name = f"({shortcut})"
        self.button.config(text=shortcut)
       
    def load_image(self, file_path, button):
        self.image_path = file_path
        image = Image.open(file_path)
        for index, i in enumerate(app.buttons):
            if button == i:
                resize_percentage = app.percent_size  # persentage resize value
                # img resize process and save
                new_width = int(image.width * (resize_percentage / 100))
                new_height = int(image.height * (resize_percentage / 100))
                new_size = (new_width, new_height)
                resized_image = image.resize(new_size)
                app.save_imgs[index] = resized_image
       
        self.set_img = image
        image = image.resize((self.size, self.size))
        # Update the label of the clicked button with the loaded image
        photo = ImageTk.PhotoImage(image)
        self.image_label.config(image=photo)
        self.image_label.photo = photo
        
class ClickRunButton:
    def __init__(self, size, master, button_name):
        self.run_master = master
        self.button_name = button_name
        self.shortcut = None
        self.size = size
        self.set_img = None
        self.create_widgets()

    def create_widgets(self):
        print('create_widgets')
        self.run_frame = tk.Frame(self.run_master)
        self.run_frame.pack(side="left")
        # add run button
        self.button = tk.Button(self.run_frame, text=self.button_name, command=self.get_shortcut)
        self.button.pack()
        
        # Add a label to show the select_rect
        self.rect_label = tk.Label(self.run_frame)
        self.rect_label.pack()

    def button_callback(self):
        print("Button Clicked {}".format(self.button_name))

    def get_shortcut(self):
        self.button.config(text="Press a key for shortcut...")
        self.button.bind("<KeyPress>", self.save_shortcut)
        self.button.focus_set()

    def save_shortcut(self, event):
        self.shortcut = event.char
        modifier = ""
        # print(type(event.keysym))
        if event.state & 0x0004:  # Check if Ctrl key is pressed
            modifier += "Control-"
        elif event.state & 0x0001:  # Check if Shift key is pressed
            modifier += "Shift-"
        elif event.state & 0x20000:  # Check if Alt key is pressed
            modifier += "Alt-"

        self.shortcut = f"{modifier}{self.shortcut}"
        self.button.config(text=f"{self.shortcut}")
        root.unbind('<KeyPress>')
        
    def set_shortcut(self, shortcut):
        self.shortcut = shortcut
        self.button.unbind("<KeyPress>")
        self.button.bind("<%s>" % shortcut, lambda event=None: self.button_callback(shortcut))
        self.button_name = f"({shortcut})"
        self.button.config(text=shortcut)
        
    def load_rect(self, region, button):
        for index, i in enumerate(app.run_buttons):
            if button == i:
                print(region)
                app.save_rect[index] = region
                self.rect_region = region

class CustomFrame(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.config(bg="gray", width=100, height=100)
        self.grid_propagate(False)

class App:
    def __init__(self, master):
        self.master = master
        
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.dragging = False
        self.listener = None
        self.select_img = None
        self.select_rect = None
        self.th = None
        self.th_running = False
        self.process = False
        
        self.create_widgets()
        self.create_menu()
        
        self.buttons = []
        self.run_buttons = []
        self.save_imgs = []
        self.save_rect = []
        self.short_key = []
        self.run_short_key = []
        self.settings = {}
        
        self.button_counter = 0
        self.run_button_counter = 0
        self.size = 40
        self.percent_size = 75
        self.click_count = 0
        self.master.bind("<Key>", self.key_handler)
        self.stop_event = threading.Event()
        # self.run_script()
        
    def reset_frame(self):
        print('Destroy')
        
        if self.th_running == True:
            print(self.stop_event.set())
            self.stop_event.set()
            self.th_running = False

        self.button_container.destroy()
        self.add_button.destroy()
        
        self.run_button_container.destroy()
        self.run_frame.destroy()
        self.add_run_button.destroy()

        for button in self.buttons:
            
            button.frame.destroy()
            
        # print(self.run_buttons)
        for run_button in self.run_buttons:
            run_button.run_frame.destroy()
            
        self.buttons = []
        self.run_buttons = []
        self.save_rect = []
        self.run_short_key = []
        self.save_imgs = []
        self.short_key = []
        self.button_counter = 0
        self.run_button_counter = 0
        self.create_widgets()
        
    def create_menu(self):
        self.menu_bar = tk.Menu(self.master)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Save Settings", command=self.save_settings)
        self.file_menu.add_command(label="Load Settings", command=self.load_settings_file)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.menu_bar.add_cascade(label="Reset", command=self.reset_frame)
        # Create an Options submenu
        self.options_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Options", menu=self.options_menu)

        # Create a spinbox in the Options submenu
        self.options_menu.add_command(label="Set Value", command=self.set_value)

        self.master.config(menu=self.menu_bar)
        
    # image persentage menu   
    def set_value(self): 
        # Create a top-level window to hold the spinbox
        self.top = tk.Toplevel(self.master)

        # Create a spinbox and a button in the top-level window
        self.spinbox_var = tk.IntVar()
        self.spinbox_var.set(str(self.percent_size))
        self.spinbox = tk.Spinbox(self.top, from_=0, to=100, textvariable=self.spinbox_var)
        self.spinbox.pack()

        ok_button = tk.Button(self.top, text="OK", command=self.ok_button_callback)
        ok_button.pack()

    # image persentage menu callback
    def ok_button_callback(self):
        # Get the value of the spinbox and print it
        self.percent_size = self.spinbox_var.get()
        print("Value set to", self.percent_size)

        # Destroy the top-level window
        self.top.destroy()

    # create_widgets
    def create_widgets(self):
        self.add_button = tk.Button(self.master, text="+", command=self.create_new_button) # make shortkey and img
        self.add_button.pack(side="left")
        
        self.button_container = tk.Frame(self.master, width=100)
        self.button_container.pack(side="left")
        
        # make select region and runkey 
        self.run_frame = tk.Frame(self.master)
        self.run_frame.pack(side="left")
        self.add_run_button = tk.Button(self.run_frame, text="■", command=self.create_new_run_button)
        self.add_run_button.pack(side="bottom")
        self.run_button_container = tk.Frame(self.run_frame)
        self.run_button_container.pack(side="bottom")
        
        self.frame_count = 0
        self.run_frame_count = 0
        
    # ===========================================================================================
    # mouse click event and make select region 
    
    def start_dragging(self, button):
        self.dragging = True
        self.select_rect = button
        if self.th_running == True: # thread running check
            print(self.stop_event.set())
            self.stop_event.set()
            self.th_running = False
        
        self.listener = mouse.Listener(on_click=self.on_button_press, on_move=self.on_button_move)
        self.listener.start()
        
    def on_button_press(self, x, y, button, pressed):
        if pressed:
            self.click_count += 1
            if self.dragging and self.click_count % 2 == 1: # mouse one click event start
                self.start_x = x
                self.start_y = y

                # create a transparent window 
                if not hasattr(self, 'transparent_window'):
                    self.transparent_window = tk.Toplevel(self.master)
                    self.transparent_window.wm_attributes("-transparentcolor", "#f0f0f0")
                    self.transparent_window.wm_attributes('-topmost', 1)
                    self.transparent_window.geometry(f"+{self.start_x}+{self.start_y}")
                    self.transparent_window.overrideredirect(True)
                    self.transparent_window.lift()

                    self.canvas = tk.Canvas(self.transparent_window, bg='#f0f0f0', bd=0, highlightthickness=0)
                    self.canvas.pack(fill=tk.BOTH, expand=tk.YES)

        if self.dragging and self.click_count % 2 == 0: # mouse two click event stop
            self.save_image()
            
    def on_button_move(self, x, y):
        if self.dragging and self.start_x is not None and self.start_y is not None:
            self.end_x = x
            self.end_y = y
            width = abs(self.end_x - self.start_x)
            height = abs(self.end_y - self.start_y)
            self.transparent_window.geometry(f"{width}x{height}+{min(self.start_x, self.end_x)}+{min(self.start_y, self.end_y)}")

            # Transparent window border options
            self.canvas.config(width=width, height=height)
            self.canvas.delete("all")
            self.canvas.create_rectangle(0, 0, width, height, outline='red', width=4)

    def save_image(self):
        self.dragging = False
        self.listener.stop()
        self.listener = None

        if self.start_x is not None and self.start_y is not None and self.end_x is not None and self.end_y is not None:
            x1, y1, x2, y2 = min(self.start_x, self.end_x), min(self.start_y, self.end_y), max(self.start_x, self.end_x), max(self.start_y, self.end_y)
            print(x1, y1, x2, y2)
            
            # save region area info
            for index, i in enumerate(self.run_buttons):
                if self.select_rect == i:
                    self.save_rect[index] = [x1, y1, x2, y2]
                    self.rect_xy = self.save_rect
                    i.rect_region = [x1, y1, x2, y2]
            
            ## region area to img
            image = pyautogui.screenshot(region=(x1, y1, x2 - x1, y2 - y1))
            self.select_img = image
            # thread start
            self.run_script()
        
            # delete region area info
            self.transparent_window.destroy()
            del self.transparent_window
            del self.canvas
            self.select_rect = None
            self.start_x = None
            self.start_y = None
            self.end_x = None
            self.end_y = None
            
    # ===========================================================================================

    def create_new_button(self):
        row, col = divmod(self.frame_count, 3) # grid
        button_frame = tk.Frame(self.button_container)
        button_frame.grid(row=row, column=col, padx=5, pady=5)
        
        # Add a shortkey button
        new_button = ClickMeButton(self.size, button_frame, "Click Me {}".format(self.button_counter))
        self.button_counter += 1
        self.buttons.append(new_button)
        self.save_imgs.append(self.button_counter)
        self.short_key.append(self.button_counter)

        # Add a label to show the image
        new_button.image_label = tk.Label(button_frame)
        new_button.image_label.pack()
        
        # Add a button to load an image
        load_button = tk.Button(button_frame, text="Load Im", command=lambda button=new_button: self.load_image(button))
        load_button.pack()
        
        self.frame_count += 1
        
    def create_new_run_button(self):
        if self.th_running == True:
            print(self.stop_event.set())
            self.stop_event.set()
            self.th_running = False

        # Add a shortkey button
        run_button_frame = tk.Frame(self.run_button_container)
        new_run_button = ClickRunButton(self.size, run_button_frame, "Click Run {}".format(self.run_button_counter))
        self.run_button_counter += 1
        self.run_buttons.append(new_run_button)
        self.save_rect.append(new_run_button)
        
        # Add a label to show the image
        new_run_button.rect_label = tk.Label(run_button_frame)
        self.run_short_key.append(new_run_button.rect_label)
        new_run_button.rect_label.pack()
        
        # Add a button to load an image self.start_dragging
        load_button = tk.Button(run_button_frame, text="Load Re", command=lambda button=new_run_button: self.load_rect(button))
        load_button.pack()

        run_button_frame.pack()  # Add this line to pack the frame to the container
        self.run_frame_count += 1
    
    # start mouse event callback function
    def load_rect(self, button):
        print('app load_rect')
        self.start_dragging(button)
        
    def create_img_button(self):
        button_frame = tk.Frame(self.master)
        button_frame.pack(side="bottom")

        # Add a label to show the image
        self.image_label = tk.Label(button_frame)
        self.image_label.pack()

    def load_image(self, button):
        file_path = filedialog.askopenfilename()
        if file_path:
            image = Image.open(file_path)
            for index, i in enumerate(self.buttons):
                if button == i:
                    resize_percentage = self.percent_size  # persentage resize value
                    # img resize process and save
                    new_width = int(image.width * (resize_percentage / 100))
                    new_height = int(image.height * (resize_percentage / 100))
                    new_size = (new_width, new_height)
                    resized_image = image.resize(new_size)
                    self.save_imgs[index] = resized_image

            image = image.resize((self.size, self.size))
            photo = ImageTk.PhotoImage(image)
            # Update the label of the clicked button with the loaded image
            button.image_label.config(image=photo)
            button.image_label.photo = photo
            button.image_path = file_path
    
    def save_settings(self): # save settings
        self.settings = {}
        for i, button in enumerate(self.buttons):
            print(button.shortcut)
            print(button.image_path)
            button_info = {
                "image_path": button.image_path,
                "shortcut": button.shortcut,
            }
            self.settings[f"button_{i}"] = button_info

        with open("settings.json", "w") as f:
            json.dump(self.settings, f, indent=2)
            
        for i, button in enumerate(self.run_buttons):
            print(button.shortcut)
            print(button.rect_region)
            button_info = {
                "rect_region": button.rect_region,
                "shortcut": button.shortcut,
            }
            self.settings[f"run_{i}"] = button_info
            
        with open("settings.json", "w") as f:
            json.dump(self.settings, f, indent=2)
            
    def load_settings_file(self):
        file_path = filedialog.askopenfilename()
        if self.buttons != [] and self.run_buttons != []:
            self.reset_frame()
        if file_path:
            self.load_settings(file_path)
                    
    def load_settings(self, file_path):
        with open(file_path, 'r') as f:
            settings = json.load(f)
                    
         # Load additional frames
        num_buttons = len(settings.keys())
        button_data = {}
        run_data = {}

        for key, value in settings.items():
            if key.startswith('button'):
                button_data[key] = value
            if key.startswith('run'):
                run_data[key] = value

        for i in range(self.button_counter, len(button_data)):
            self.create_new_button()
            button_setting = settings['button_' + str(i)]
            if 'shortcut' in button_setting:
                self.buttons[i].set_shortcut(button_setting['shortcut'])
            if 'image_path' in button_setting:
                self.buttons[i].load_image(button_setting['image_path'], self.buttons[i])
        
        for i in range(self.run_button_counter, len(run_data)):
            self.create_new_run_button()
            button_setting = settings['run_' + str(i)]
            if 'shortcut' in button_setting:
                self.run_buttons[i].set_shortcut(button_setting['shortcut'])
            if 'rect_region' in button_setting:
                self.run_buttons[i].load_rect(button_setting['rect_region'], self.run_buttons[i])

        self.run_script()
        
    def key_handler(self, event):
        for button in self.buttons:
            if button.shortcut == event.char:
                button.button_callback()
    
    def run_script(self):     
        if self.th_running:
            return  # Do not start a new thread if one is already running
        
        print('thread run')
        self.stop_event.clear()
        self.th = threading.Thread(target=script, args=(self.master, self.stop_event,), daemon=True)
        self.th.start()
        self.th_running = True

            
class script:
    def __init__(self, master, event) -> None:
        self.stop_event = event
        self.master = master
        self.photo_datas = [None] * len(app.save_rect)
        self.start()
    
    # Template size conversion and image comparison
    def template_scale(self, image, template):
        find_ok = False
        for scale in numpy.linspace(0.8, 1.2, 20)[::-1]:
            # Comparing only when the image size is large
            if image.shape[1] > template.shape[1] and image.shape[0] > template.shape[0]:
                resized = imutils.resize(template, width = int(template.shape[1] * scale))
                res = cv2.matchTemplate(image, resized, cv2.TM_CCOEFF_NORMED)

                threshold = 0.7
                loc = numpy.where(res >= threshold)
                if len(list(zip(*loc[::-1]))) > 0:
                    find_ok = True
                    break

        return find_ok
    
    def start(self):
        loop_pre_time = time.time()
        pre_time = time.time()
        print(app.save_rect)
        for index, value in enumerate(app.save_rect): # region area first time reflected
            if type(app.run_buttons[index].shortcut) == type('str') and type(value) == type([]):
                image = pyautogui.screenshot(region=(value[0], value[1], 
                                                    value[2] - value[0], value[3] - value[1]))

                self.photo_datas[index] = ImageTk.PhotoImage(image)
                app.run_short_key[index].config(image=self.photo_datas[index])
        
        while not self.stop_event.is_set(): # thread running 
            pre_time = time.time()
            for index, value in enumerate(app.save_rect):
                # Condition satisfied when all keys for the region area
                if type(app.run_buttons[index].shortcut) == type('str') and type(value) == type([]):
                    ## region area to img
                    image = pyautogui.screenshot(region=(value[0], value[1], 
                                                        value[2] - value[0], value[3] - value[1]))
                    
                    if time.time() - loop_pre_time > 120: # update region img 120sec
                        self.photo_datas[index] = ImageTk.PhotoImage(image)
                        app.run_short_key[index].config(image=self.photo_datas[index])
                        print(time.time()-pre_time)
                        loop_pre_time = time.time()
                    
                    if not keyboard.is_pressed('ctrl'):
                        if keyboard.is_pressed(str(app.run_buttons[index].shortcut)):
                            for index, img in enumerate(app.save_imgs):

                                screenshot_up_np = cv2.cvtColor(numpy.array(image), cv2.COLOR_RGB2GRAY)
                                pil_image_up = cv2.cvtColor(numpy.array(img), cv2.COLOR_RGB2GRAY)
                                # comparison template and img
                                if self.template_scale(screenshot_up_np, pil_image_up):
                                    if str(app.buttons[index].shortcut).find('Control') >= 0:
                                        key = str(app.buttons[index].shortcut).replace('Control-', '')
                                        pyautogui.hotkey('ctrl', key)
                                    else:
                                        pyautogui.press(str(app.buttons[index].shortcut))
            
            if self.stop_event.is_set():
                app.th_running = False
                break

            time.sleep(0.001)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
