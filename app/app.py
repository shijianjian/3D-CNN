"""
MicroService for 3D point cloud CNN
"""

import os
from pyntcloud import PyntCloud
from flask import Flask, json, render_template, send_from_directory, request, redirect
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
from cnn.util.dbscan import dbscan_labels, find_cluster_points
from cnn.util.process_pointcloud import norm_point


APP = Flask(__name__)
CORS(APP)
APP.config['CORS_HEADERS'] = 'Content-Type'
APP.config['supports_credentials'] = 'True'

@APP.after_request
def after_request(response):
    """
    Response headers.
    """
    # response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


APP_STATIC_PATH = os.path.join(os.getcwd(), 'angular', 'dist')
APP.static_folder = APP_STATIC_PATH
APP.template_folder = APP_STATIC_PATH

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = set(['pts', 'md'])
APP.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@APP.route('/', methods=['GET'])
@cross_origin()
def index():
    """
    Index Page.
    """
    return render_template('index.html')


@APP.route('/<path:path>')
@cross_origin()
def send_js(path):
    """
    Service static resources
    """
    return send_from_directory(APP_STATIC_PATH, path)


@APP.route('/cluster', methods=['GET', 'POST'])
@cross_origin()
def cluster_point_cloud():
    """
    Output point cloud cluster according to the configuration.
    """
    my_point_cloud = PyntCloud.from_file(os.path.join(os.getcwd(), 'ttt2.pts'), sep=" ", header=0, names=["x", "y", "z"])
    normalized_cloud = norm_point(my_point_cloud.xyz)
    labels = dbscan_labels(normalized_cloud, 0.02, 10, algorithm='ball_tree')
    cluster = find_cluster_points(normalized_cloud, labels)
 
    response = APP.response_class(
        response=json.dumps(cluster),
        status=200,
        mimetype='application/json'
    )
    return response


@APP.route('/upload', methods=['GET', 'POST', 'OPTIONS'])
@cross_origin()
def upload_file():
    """
    Upload point cloud file.
    """
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            print('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            os.makedirs(APP.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(os.path.join(APP.config['UPLOAD_FOLDER'], filename))
            return "File uploaded"

    return index()


def allowed_file(filename):
    """
    Filter files according to file extensions.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == "__main__":
    APP.run()
   