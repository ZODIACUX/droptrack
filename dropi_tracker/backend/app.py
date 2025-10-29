from flask import Flask, request, render_template, redirect, url_for, flash
import os
import json
from werkzeug.utils import secure_filename
from utils import csv_parser, interrapidisimo_tracker
from utils.dropi_api_client import DropiAPIClient

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__, template_folder='../frontend', static_folder='../frontend/static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key') # Use env var in production

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'csv_file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['csv_file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Ensure the upload folder exists
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        tracking_numbers = csv_parser.parse_csv(filepath)

        # Now, track the packages using the tracker utility
        tracking_results = interrapidisimo_tracker.track_packages(tracking_numbers)

        # Format the results for the dashboard template
        trackings = []
        for number, details in tracking_results.items():
            trackings.append({
                "number": number,
                "status": details.get('last_event', details.get('status', 'N/A'))
            })

        return render_template('dashboard.html', trackings=trackings)

    return redirect(url_for('index'))

@app.route('/settings')
def settings():
    return render_template('settings.html')


@app.route('/sync')
def sync_with_dropi():
    try:
        client = DropiAPIClient()
        tracking_numbers = client.get_tracking_numbers()

        if not tracking_numbers:
            flash('No se encontraron guías en Dropi o las órdenes aún no han sido despachadas.')
            return redirect(url_for('index'))

        # Track the packages using the existing tracker utility
        tracking_results = interrapidisimo_tracker.track_packages(tracking_numbers)

        # Format the results for the dashboard template
        trackings = []
        for number, details in tracking_results.items():
            trackings.append({
                "number": number,
                "status": details.get('last_event', details.get('status', 'N/A'))
            })

        return render_template('dashboard.html', trackings=trackings)

    except Exception as e:
        flash(f'Error al sincronizar con Dropi: {e}')
        return redirect(url_for('index'))


if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
