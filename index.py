from flask import Flask, flash, request, redirect, url_for, render_template
import smtplib
import os
from werkzeug.utils import secure_filename
import tensorflow as tf
import keras
import tensorflow.keras as tfk
import keras_preprocessing
import PIL
import numpy as np

BATCHSIZE = 32


UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

vector = []


@app.route("/")
def index():
    return render_template('index.html', title="Detectam flori")


def upload_form():
    return render_template('index.html')


@app.route('/', methods=['POST','GET'])
def upload_image():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('Nu a fost selectat niciun fisier.')
            return redirect(request.url)
        if (allowed_file(file.filename) == False):
            
            return render_template('index.html')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #return redirect(url_for('download_file', name=filename))
            #flower_names = list(training_set.class_indices.keys())
            with open('flori.txt') as f:
                flower_names = f.read().splitlines()
            conv_neural_network = tf.keras.models.load_model('conv_neural_network_last_attempt')
            conv_neural_network.load_weights('conv_neural_network_last_attempt/variables/variables')
            from keras_preprocessing import image
            test_img = image.load_img('static/uploads/%s' % (filename), target_size=(64,64))
            test_img = image.img_to_array(test_img)
            test_img = np.expand_dims(test_img, axis=0)
            res = conv_neural_network.predict(test_img)
            max = res.argmax(1)[0]
            rez = flower_names[max]
            return render_template('succes.html', title="Analiza finalizata", rezultat = rez, fisier = "static/uploads/" + filename)
    return ''



@app.route('/contact')
def contact():
    return render_template("contact.html", title="Contact")


@app.route('/succes', methods=['POST', 'GET'])
def success():
    return render_template("succes.html", title="Analiza finalizata")

@app.route('/flori')
def flori():
    return render_template("flori.html", title="Lista flori")


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
