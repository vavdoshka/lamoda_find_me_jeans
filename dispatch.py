from gmail import GMail, Message
import json
import os

def dispatch_email_via_gmail(msg):
    config = json.load(open(os.path.join(os.getcwd(), "config.json")))
    gmail = GMail(config['mailFrom'], config['mailPassword'])
    msg = Message("Latest News From Find Me Jeans", to=config['mailTo'], text=msg)
    gmail.send(msg)
