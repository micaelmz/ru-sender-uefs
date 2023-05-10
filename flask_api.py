from flask import Flask, request


app = Flask(__name__)

# Twilio API
@app.route('/message', methods=['POST'])
def reply():
    pass