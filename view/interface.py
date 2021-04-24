from tkinter import Tk, Label, IntVar, Radiobutton, Entry, Button, filedialog, StringVar, PhotoImage, HORIZONTAL,\
    Canvas, ttk, Checkbutton
from tkinter.ttk import Combobox, Progressbar
from control.notification import Notification
import os


GREEN = '#4CAF50'
DEEP_ORANGE = '#FF5722'
RED = '#c62828'
GREY = '#212121'
GREY_LIGHT = '#9E9E9E'
BACKGROUND = '#ECECEC'
BLUE = '#4FC3F7'
BLACK = '#000000'
FONT_LARGE = ("Helvetica", 35, 'bold')
FONT_MEDIUM = ("Helvetica", 20, 'normal')
FONT_SMALL = ("Helvetica", 13, 'normal')


class Interface:

    window = Tk()
    window.config(padx=50, pady=50, bg=BACKGROUND)
    window.minsize(width=1400, height=500)
    window.title("Face Mask Detection Software")

    from_email_ent = Entry(width=20, bd=0, highlightcolor=BLUE)
    from_password_ent = Entry(width=20, show='*', bd=0, highlightcolor=BLUE)
    to_email_ent = Entry(width=20, bd=0, highlightcolor=BLUE)
    smtp_label = StringVar()

    progress_bar = Progressbar(window, orient=HORIZONTAL, length=100, mode='determinate')
    info_text = Label(text="", font=FONT_SMALL, padx=20, pady=20, bg=BACKGROUND, fg=DEEP_ORANGE)
    canvas = Canvas(width=300, height=300, bg=GREY_LIGHT, highlightthickness=0)
    message_info_label = Label(text="", font=FONT_SMALL, padx=5, pady=5, bg=BACKGROUND, fg=DEEP_ORANGE)

    canvas_image = PhotoImage(file='../captures/last_capture.png')
    auto_send_is_on = IntVar()

    def __init__(self):
        # Text
        self.selected_image = 'last_capture.png'
        title = Label(text="Face Mask Detection Software", font=FONT_LARGE, padx=10, pady=10, fg=GREY,
                      bg=BACKGROUND)
        please_choose_text = Label(text="Please Choose Detection Mode", font=FONT_MEDIUM, padx=5, pady=5, bg=BACKGROUND,
                                   fg=BLACK)
        email_setup_text = Label(text="Email Setup", font=FONT_MEDIUM, padx=5, pady=5, bg=BACKGROUND, fg=BLACK)
        from_email_text = Label(text="Sender Email: ", font=FONT_SMALL, padx=5, pady=5, bg=BACKGROUND, fg=BLACK)
        camera_source_text = Label(text="Camera Source: ", font=FONT_SMALL, padx=5, pady=5, bg=BACKGROUND, fg=BLACK)
        space = Label(text="                           ", font=FONT_SMALL, padx=5, pady=5, bg=BACKGROUND, fg=BLACK)
        password_text = Label(text="Password: ", font=FONT_SMALL, padx=5, pady=5, bg=BACKGROUND, fg=BLACK)
        please_upload_text = Label(text="Please Upload or Provide File Directory", font=FONT_SMALL, padx=10, pady=10,
                                   fg=BLACK, bg=BACKGROUND)
        to_email_text = Label(text="Receiver Email: ", font=FONT_SMALL, padx=5, pady=5, bg=BACKGROUND, fg=BLACK)
        target_detection_text = Label(text="Last Detection", font=FONT_MEDIUM, padx=5, pady=5, bg=BACKGROUND,
                                      fg=RED)
        smtp_server_text = Label(text="SMTP Server: ", font=FONT_SMALL, padx=5, pady=5, bg=BACKGROUND, fg=BLACK)

        #
        auto_send = Checkbutton(Interface.window, text="automatically send email", variable=Interface.auto_send_is_on,
                                onvalue=1, offvalue=0, bg=BACKGROUND)

        # Buttons
        send_bttn_image = PhotoImage(file='../buttons/send.png')
        send_bttn = Button(image=send_bttn_image, highlightthickness=0,
                           command=lambda: Notification.notify(image=self.selected_image), font=FONT_MEDIUM,
                           bg=BACKGROUND, relief='raised', bd=0)

        # Radio Buttons
        self.radio_state = IntVar()
        webcam_radio_bttn = Radiobutton(text="Camera", value=0, variable=self.radio_state, command=self.radio_chosen,
                                        anchor='c', bg=BACKGROUND, fg=BLACK)
        image_radio_bttn = Radiobutton(text="Image", value=1, variable=self.radio_state, command=self.radio_chosen,
                                       anchor='c', bg=BACKGROUND, fg=BLACK)
        video_radio_bttn = Radiobutton(text="Video  ", value=2, variable=self.radio_state, command=self.radio_chosen,
                                       anchor='c', bg=BACKGROUND, fg=BLACK)

        # Entries, Buttons and Separator
        self.file_directory_ent = Entry(width=50, bd=0, highlightcolor=BLUE)
        upload_bttn_image = PhotoImage(file='../buttons/upload.png')
        self.upload_bttn = Button(highlightthickness=0, command=self.upload_file,
                                  image=upload_bttn_image, bg=BACKGROUND, state='disabled')
        sep = ttk.Separator(Interface.window, orient='vertical')
        start_bttn_image = PhotoImage(file='../buttons/power.png')
        start_bttn = Button(image=start_bttn_image, highlightthickness=0, command=self.start, font=FONT_MEDIUM,
                            bg=BACKGROUND, relief='groove', bd=0)

        # ComboBox
        smtp_combo = Combobox(Interface.window, width=19, textvariable=Interface.smtp_label)
        smtp_combo['values'] = ('Google:smtp.gmail.com', 'Outlook:smtp.live.com', 'Office365:smtp.office365.com',
                                'Yahoo:smtp.mail.yahoo.com', 'YahooPlus:plus.smtp.mail.yahoo.com',
                                'YahooUK:smtp.mail.yahoo.co.uk', 'Hotmail:smtp.live.com',
                                'AT&T:smtp.att.yahoo.com', 'O2UK:smtp.o2.co.uk')
        camera_src_label = StringVar()
        self.camera_combo = Combobox(Interface.window, width=5, textvariable=camera_src_label)
        self.camera_combo['values'] = ('0', '1', '2', '3')
        self.camera_combo.current(1)
        smtp_combo.current(0)
        browse_detections_bttn = Button(text="Browse Detections", command=self.browse_images, bg=BACKGROUND,
                                        highlightthickness=0)

        # Grid Setup
        title.grid(row=1, column=0, sticky='w', columnspan=3)
        please_choose_text.grid(row=2, column=0, sticky='w')
        self.file_directory_ent.grid(row=7, column=0, columnspan=2, sticky='w')
        please_upload_text.grid(row=6, column=0, sticky='w')
        self.upload_bttn.grid(row=7, column=2)
        sep.grid(row=0, column=7, rowspan=9, sticky='ns', padx=20)
        smtp_server_text.grid(row=5, column=5)
        webcam_radio_bttn.grid(row=3, column=0, sticky='w')
        image_radio_bttn.grid(row=5, column=0, sticky='w')
        video_radio_bttn.grid(row=5, column=1, sticky='w')
        email_setup_text.grid(row=2, column=5)
        camera_source_text.grid(row=3, column=1, sticky='w')
        space.grid(row=3, column=3)
        self.from_email_ent.grid(row=3, column=6)
        password_text.grid(row=4, column=5)
        from_email_text.grid(row=3, column=5)
        smtp_combo.grid(row=5, column=6)
        self.to_email_ent.grid(row=6, column=6)
        self.camera_combo.grid(row=3, column=2)
        to_email_text.grid(row=6, column=5)
        target_detection_text.grid(row=0, column=8, columnspan=2)
        start_bttn.grid(row=8, column=6, columnspan=2, padx=30, pady=30)

        Interface.info_text.grid(row=8, column=0, columnspan=3)
        Interface.from_password_ent.grid(row=4, column=6)
        browse_detections_bttn.grid(row=2, column=8, columnspan=2)
        auto_send.grid(row=3, column=8, columnspan=2)
        Interface.message_info_label.grid(row=4, column=8, columnspan=2, rowspan=2)
        send_bttn.grid(row=6, column=8, columnspan=2)
        Interface.canvas.grid(row=1, column=8, columnspan=2)
        Interface.progress_bar.grid(row=9, column=6, columnspan=2)

        Interface.window.mainloop()

    def radio_chosen(self):
        if self.radio_state.get() == 0:
            self.file_directory_ent.config(state='disabled')
            self.camera_combo.config(state='normal')
            self.upload_bttn.config(state='disabled')
            self.camera_combo.focus()
        else:
            self.file_directory_ent.config(state='normal')
            self.upload_bttn.config(state='normal')
            self.file_directory_ent.focus()
            self.camera_combo.config(state='disabled')

    def upload_file(self):
        self.file_directory_ent.delete(0, 'end')
        directory = filedialog.askopenfilename(title='Select a file to use for detections')
        self.file_directory_ent.focus()
        self.file_directory_ent.insert(0, directory)

    def browse_images(self):
        chosen_image_to_send = filedialog.askopenfilename(initialdir='captures/last_capture.png',
                                                          title='Images of Detections')
        if not chosen_image_to_send == '':
            p = chosen_image_to_send.split('/')
            self.selected_image = p[len(p)-1]
            Interface.canvas_image = PhotoImage(file=f'captures/{self.selected_image}')
            Interface.canvas.create_image(150, 150, image=Interface.canvas_image)

    @staticmethod
    def update_progress_bar(value: int):
        """
        Updates the progress bar level visible on the interface
        :param value: Sets the value of the progress bar (int 0 - 100)
        """
        Interface.progress_bar['value'] = value
        Interface.window.update_idletasks()

    @staticmethod
    def update_info_text(text: str):
        """
        Updates the Info text visible on the interface to a specified string text
        :param text: Sets the text value of info text
        """
        Interface.info_text.config(text=text)
        Interface.window.update_idletasks()
        Interface.window.update()

    @staticmethod
    def update_message_info_text(text: str, fg_color=DEEP_ORANGE):
        """
        Updates the timer text visible on the interface to a specified string text
        :param text: Sets the text value of info text
        :param fg_color: Sets the foreground color of the text
        """
        Interface.message_info_label.config(text=text, fg=fg_color)
        Interface.window.update_idletasks()
        Interface.window.update()

    def start(self):
        """
        Starts detection base on user's choice. Triggered only when start button is clicked
        """
        from control.video_mask_detection import VideoMaskDetection
        Interface.update_progress_bar(10)
        if self.radio_state.get() == 0:
            video = VideoMaskDetection()
            video.start_video_stream(stream_source=int(self.camera_combo.get()))
        elif self.radio_state.get() == 1:
            from control.image_mask_detection import ImageMaskDetection
            image = ImageMaskDetection(image_path=self.file_directory_ent.get())
            image.start_mask_detections()
        elif self.radio_state.get() == 2:
            video = VideoMaskDetection()
            video.start_video_capture(path=self.file_directory_ent.get())
