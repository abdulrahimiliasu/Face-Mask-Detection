from smtplib import SMTP, SMTPAuthenticationError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import datetime as dt


class Notification:

    def __init__(self, email, password):
        """
        Initializes an object of Notification with user email and password
        :param email: email to be sent from
        :param password: password of email account
        """
        self.email = email
        self.password = password

    def prepare_and_send_email(self, to_email, time, smtp_server, attachment="last_capture.png"):
        """
        Prepare message body of the notification and also attaches offender image
        :param to_email: email address to send notification to
        :param time: current date and time
        :param smtp_server: smtp_server of the user email
        :param attachment: image to attach to notification
        :return: True if successful and False otherwise
        """
        try:
            msg = MIMEMultipart('related')
            msg['Subject'] = 'Notification From Face Mask Detection Software'
            msg['From'] = self.email
            msg['To'] = to_email
            msg.preamble = 'This is a notification alert !'

            msg_alternative = MIMEMultipart('alternative')
            msg.attach(msg_alternative)
            msg_body = MIMEText(f"This Email was sent from Face Mask Detection Software to Notify this email"
                                f"address that a person was detected NOT wearing mask at {time}. "
                                f"Image of the offender can be found by seeing the software.")
            msg_alternative.attach(msg_body)

            msg_body = MIMEText(f'<b><h3>ALERT!, Detected Person/People NOT wearing mask</h3><br> '
                                f'<i>The Image below contains detected face/faces not wearing mask</i></br>'
                                f'</b><br><img src="cid:image1"><br><br><b>{time}</b></br>'
                                f'You received this because your email was used to notify you using the '
                                f'Face Mask Detection Software.', 'html')
            msg_alternative.attach(msg_body)

            fp = open(f"captures/{attachment}", 'rb')
            msg_image = MIMEImage(fp.read())
            fp.close()

            msg_image.add_header('Content-ID', '<image1>')
            msg.attach(msg_image)

            with SMTP(smtp_server) as request:
                request.starttls()
                request.login(user=self.email, password=self.password)
                request.sendmail(from_addr=self.email, to_addrs=to_email,
                                 msg=msg.as_string())
        except TypeError:
            return False
        except SMTPAuthenticationError:
            return False
        else:
            return True

    @staticmethod
    def notify(image="last_capture.png", show_messagebox=True):
        """
        sends an email notification from the details provided on the interface fields, triggered only when send
        button is pressed
        """
        from view.interface import Interface
        from tkinter import messagebox
        date = dt.datetime.now().strftime("DATE: %m/%d/%Y, TIME: %H:%M:%S")
        notifier = Notification(email=Interface.from_email_ent.get(), password=Interface.from_password_ent.get())
        if notifier.prepare_and_send_email(to_email=Interface.to_email_ent.get(),
                                           time=date,
                                           smtp_server=Interface.smtp_label.get().split(':')[1],
                                           attachment=image):
            Interface.update_message_info_text(f'Notification was successful'
                                               f'\nat {date}', fg_color='#4CAF50')
            if show_messagebox:
                messagebox.showwarning(title="Notification Sent",
                                       message="Notification Was Successfully Sent")
        else:
            Interface.update_message_info_text(f"Notification Failed"
                                               f"\nat {date}"
                                               f"\nPlease check credentials and try again!")
            if show_messagebox:
                messagebox.showwarning(title="Notification Error",
                                       message="Email could not be sent,"
                                               " please check the sender's email and password then "
                                               "try again !")
