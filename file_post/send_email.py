import smtplib
from email.mime.text import MIMEText
from email.header import Header
from config.read import configs

class SMTP(object):
    def __init__(self):
        """

        :param sender:xxxxxx@qq.com
        :param receivers:email of receivers
        :param host:"smtp.qq.com"
        :param user:xxxxxx@qq.com
        :param password:
        """

        self.sender = configs.email['sender']
        self.host = configs.email['host']
        self.user = configs.email['user']
        self.password = configs.email['password']
    def send_email_(self, *, msg:str, email:str)-> bool:
        try:
            msg = msg
            self.receivers = [email]
            if type(msg) is not str:
                raise Exception("msg must be str")

            self.message = MIMEText(msg, "html", "utf-8")
            self.message["Form"] = Header(configs.email['from'], "utf-8")
            self.message["Subject"] = Header(configs.email['subject'], "utf-8")
            smtp_obj = smtplib.SMTP()
            smtp_obj.connect(self.host, 25)
            smtp_obj.login(self.user, self.password)
            smtp_obj.sendmail(self.sender, self.receivers, self.message.as_string())
            print("Email send success")
            return True
        except smtplib.SMTPException:
            print("Email send error")
            return False



