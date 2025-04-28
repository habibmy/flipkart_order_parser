from io import BytesIO
import PyPDF2
from flask import Flask, render_template, request, redirect, session, make_response, send_file, send_from_directory
import requests
import os
from dotenv import load_dotenv
load_dotenv()
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

app = Flask(__name__)

ALLOWED_EXTENSIONS = set(['pdf','PDF'])

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/show_pdf', methods=['GET', 'POST'])
def show_pdf():
    if request.method == 'POST':
        send_data = request.files['send_data']
        if send_data and allowed_file(send_data.filename):
            
            output_pdf = PyPDF2.PdfWriter()

            pdf  = PyPDF2.PdfReader(send_data)
            pdf2  = PyPDF2.PdfReader(send_data)

            numPages = len(pdf.pages)

            for i in range(numPages):

                shipping_label = pdf.pages[i]
                invoice = pdf2.pages[i]
                shipping_label.cropbox.lower_left=(185,458)
                shipping_label.cropbox.upper_right = (410,820)
                
                invoice.cropbox.lower_left=(0,78)
                invoice.cropbox.upper_right = (800,455)


                output_pdf.add_page(shipping_label)

                output_pdf.add_page(invoice)

            #this works
            # outputStream = open(r"output.pdf", "wb")
            # output_pdf.write(outputStream)

            outfile = BytesIO()
            output_pdf.write(outfile)
            outfile.seek(0)

             # Extract data using your parser
            send_data.stream.seek(0)
            from parser import extract_details_from_pdf
            extracted_data = extract_details_from_pdf(send_data.stream)

            # Send to webhook (use environment variable for URL)
            try:
                print(extracted_data)
                response = requests.post(
                    WEBHOOK_URL, 
                    json=extracted_data,
                    timeout=3
                )
                if response.status_code == 200:
                    print("Webhook push successful")
                else:
                    print("Webhook push failed with status code:", response.status_code)
            except Exception as e:
                print("Webhook push failed:", e)

            output_filename = send_data.filename +'-output.pdf'

            return send_file(outfile,mimetype='application/pdf',download_name=output_filename, as_attachment=True)

            # return render_template('pdf.html', result=result)

@app.route('/manifest.json')
def manifest():
    return send_from_directory(app.static_folder, 'manifest.json')


@app.route('/sw.js')
def service_worker():
    response = make_response(send_from_directory(app.static_folder, 'sw.js'))
    response.headers['Cache-Control'] = 'no-cache'
    return response

@app.route('/ads.txt')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])

if __name__ == '__main__':
    app.debug = True
    app.run()