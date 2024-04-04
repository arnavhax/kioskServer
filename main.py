from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import cups
import requests
from io import BytesIO
from zipfile import ZipFile
import os
import base64
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
def download():
    try:
        # Make a request to the original Flask application's /download route
        download_response = requests.get(f'{CLOUD_SERVER_URL}/download')

        # Check if the request was successful
        if download_response.status_code != 200:
            return jsonify({'error': 'Failed to download files from the server.'}), download_response.status_code

        # Extract files from the zip archive
        with ZipFile(BytesIO(download_response.content), 'r') as zip_file:
            # Extract PDF files from the zip archive
            pdf_files = [name for name in zip_file.namelist() if name.endswith('.pdf')]

            # Read the content of each PDF file
            pdf_contents = {}
            for pdf_file in pdf_files:
                with zip_file.open(pdf_file) as f:
                    # Encode binary data to base64
                    encoded_data = base64.b64encode(f.read()).decode('utf-8')
                    pdf_contents[pdf_file] = encoded_data

        # Return the extracted PDF contents as JSON data
        return jsonify(pdf_contents)
    except Exception as e:
        return jsonify({'error': f'Error extracting and returning files: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
