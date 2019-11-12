import os
from flask import Flask, flash, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from mockup import Mockup
import cv2
from prediction import detection

# Manage Folder
UPLOAD_FOLDER = './uploads/'
RESULT_FOLDER = './results_prediction/'

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

# Init Flask
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER

# 16 Mbits limit file update
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


try:
    os.mkdir("output/")
    os.mkdir(UPLOAD_FOLDER)
    os.mkdir(RESULT_FOLDER)
except FileExistsError:
    pass


def allowed_file(filename):
    """
    Check if extensions is allow
    :param filename:
    :return: Boolean
    """

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    """
    Display update page and update submit file
    GET => Display update page for web
    POST => Update submit file (api/web)
    :return: String | Route
    """

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path_to_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path_to_file)

            select = request.form.get("export_type")

            if select == "Svg":
                new_filename = start_prediction_to_svg(path_to_file, filename)
            elif select == "Balsamiq":
                new_filename = start_prediction_to_balsamiq(path_to_file, filename)
            elif select == "Pencil":
                new_filename = start_prediction_to_pencil(path_to_file, filename)
            else:
                new_filename = start_prediction_to_svg(path_to_file, filename)

            return redirect(url_for('send_file',
                                    filename=new_filename))
    return '''

<!doctype html>
<html lang="fr">

    <head>
        <!-- Required meta tags -->
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        
        <!-- Bootstrap CSS -->
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
        
        <title>Ui Detector</title>
    </head>
    
    <body>
        <div class="container mt-5">
            <div class="row">
                <div class="col align-self-center">
                    <div class="card">
                      <div class="card-header">
                        Ui Detector
                      </div>
                      <div class="card-body">
                        <h5 class="card-title">Conversion capture d'écran site web vers Maquette en SVG</h5>
                        <p class="card-text">Sélectionner une image</p>
                        <form method=post enctype=multipart/form-data>
                            <input type=file name=file>
                            <select name="export_type">
                                <option value="">Type d'export</option>
                                <option value="Pencil">Pencil</option>
                                <option value="Balsamiq">Balsamiq</option>
                                <option value="Svg">Svg (Adobe XD)</option>
                            </select>
                            <button type="submit" value=Upload class="btn btn-primary">Conversion</button>
                        </form>
                      </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js" integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous"></script>
        <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>
    </body>
</html>
    
    '''


@app.route('/uploads/<filename>')
def send_file(filename):
    """
    Send file to client
    :param filename:
    :return: File response
    """

    return send_from_directory(app.config['RESULT_FOLDER'], filename, as_attachment=True)


def start_prediction_to_svg(path_image, filename):
    """
    Launch prediction to convert screenshots to SVG
    :param path_image:
    :param filename:
    :return:
    """

    image = cv2.imread(path_image)
    original_image = image.copy()
    detection_results = detection(image)

    filename = filename.split('.')[0]

    mockup = Mockup(filename, original_image, detection_results)
    mockup.translate_raw_results()
    mockup.align_text_elements()
    filename = mockup.create_svg(app.config['RESULT_FOLDER'])

    return filename


def start_prediction_to_balsamiq(path_image, filename):
    """
    Launch prediction to convert screenshots to SVG
    :param path_image:
    :param filename:
    :return:
    """

    image = cv2.imread(path_image)
    original_image = image.copy()
    detection_results = detection(image)

    filename = filename.split('.')[0]

    mockup = Mockup(filename, original_image, detection_results)
    mockup.translate_raw_results()
    mockup.align_text_elements()
    filename = mockup.create_bmml(app.config['RESULT_FOLDER'])

    return filename


def start_prediction_to_pencil(path_image, filename):
    """
    Launch prediction to convert screenshots to SVG
    :param path_image:
    :param filename:
    :return:
    """

    image = cv2.imread(path_image)
    original_image = image.copy()
    detection_results = detection(image)

    filename = filename.split('.')[0]

    mockup = Mockup(filename, original_image, detection_results)
    mockup.translate_raw_results()
    mockup.align_text_elements()
    mockup.create_xml_page()
    filename = mockup.generate_pencil_file(app.config['RESULT_FOLDER'])

    return filename


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=89)
