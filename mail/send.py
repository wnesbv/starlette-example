
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from db_config.settings import settings


async def send_mail(self):

    msg = MIMEMultipart()
    message = str(self)

    password = settings.MAIL_PASSWORD
    msg["From"] = settings.FROM
    msg["To"] = settings.TO_MAIL
    msg["Subject"] = "Subscription"

    msg.attach(MIMEText(message, "plain"))

    server = smtplib.SMTP("smtp.gmail.com: 587")

    server.starttls()

    server.login(msg["From"], password)

    server.sendmail(msg["From"], msg["To"], msg.as_string())

    server.quit()
