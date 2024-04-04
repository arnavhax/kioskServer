from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import cups
import requests
from zipfile import ZipFile
import os

app = Flask(__name__)
CORS(app)
UPLOAD_DIRECTORY = 'user_uploads'
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

CLOUD_SERVER_URL = 'http://127.0.0.1:3000'  # Replace with your cloud server URL


@app.route('/test')
def test():
	pdf_name="pdf-test.pdf"
	conn=cups.Connection()
	printer=conn.getPrinters()
	print(printer)
	selected_printer=list(printer.keys())[0]
	double_sided=False
	copies=2
	options={
			'multiple-document-handling':'separate-documents-collated-copies' if double_sided else 'single_document',
		'copies': str(copies)	
		}
		
	conn.printFile(selected_printer,pdf_name,"",options )
	
	return f"PRINTING SERVER IS WORKING: PRINTER :{printer}"

@app.route('/print',methods=['POST'])
def print_route():

	#checking for pdf
	
	if 'pdf' not in request.files:
		return jsonify({'error':'No file received'}),400
		
	#checking for options
	
	if(request.form.get('double_page')):
		double_page=request.form.get('double_page')
	else:
		double_page=False
	
	if(request.form.get('copies')):
		copies=request.form.get('copies')
	else:
		copies=1
	##end options
	
	pdf_file=request.file['pdf']
	
	if pdf_file and pdf_file.filename.endswith('.pdf'):
	#connection with printer
		conn=cups.Connection()
		printer=conn.getPrinters()
		selected_printer=list(printer.keys())[0]
		
		options={
			'multiple-document-handling':'separate-documents-collated-copies' if double_sided else 'single_document',
		'copies': str(copies)	
		}
		
		conn.printFile(selected_printer,pdf_file,"",options )
	return jsonify({"status":"Done"}),200

@app.route('/startSession', methods=['POST'])
def start_session():
    return jsonify({'message': 'Session started successfully.'}), 200

@app.route('/endSession', methods=['GET'])
def end_session():
    # Trigger end session route in the cloud server
    cloud_end_session_response = requests.get(f'{CLOUD_SERVER_URL}/endSession')

    if cloud_end_session_response.status_code == 200:
        # Call the function to delete uploaded files
        return jsonify({'message': 'Session ended successfully. Uploaded files deleted.'}), 200
    else:
        return jsonify({'error': 'Failed to end session in the cloud server.'}), 500

@app.route('/download', methods=['GET'])
def download_files():
    # Fetch files from the cloud server
    cloud_download_response = requests.get(f'{CLOUD_SERVER_URL}/download')

    # Check if the cloud server responded with files
    if cloud_download_response.status_code == 200:
        files_data = cloud_download_response.json()
        return jsonify(files_data), 200
    else:
        return jsonify({'error': 'Failed to download files from cloud server.'}), 500

if __name__ == '__main__':
    app.run(debug=True)
