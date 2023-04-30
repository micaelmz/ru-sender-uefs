from authentication import WhatsAppAuthenticator, EmailAuthenticator

class WhatsAppSender:
    def __init__(self, message):
        self.message = message

    def send(self):
        print(f"Sending WhatsApp message: {self.message}")


class WhatsAppMessage:
    def __init__(self, message):
        self.message = message

    def send(self):
        WhatsAppSender(self.message).send()

class EmailSender:
    def __init__(self, message):
        self.message = message

    def send(self):
        print(f"Sending email message: {self.message}")

class EmailMessage:
    def __init__(self):
        self.html_file = None

