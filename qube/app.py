from flask import Flask, render_template, request, redirect, url_for
from views import views

app = Flask(__name__)
app.config['UPLOAD_PATH'] = 'uploads'

app.register_blueprint(views, url_prefix="/spaceship")

if __name__ == '__main__':
    app.run(port=8080)
