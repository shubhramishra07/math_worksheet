from flask import Flask, request, jsonify, send_file, render_template
import io
from fpdf import FPDF
from grammar import generate_json
from worksheet_generator import create_worksheet_from_json

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate-worksheet', methods=['POST'])
def generate_worksheet():
    data = request.json
    standard = data.get('standard')
    themes = data.get('themes', '')
    theme_list = [theme.strip() for theme in themes.split(',') if theme.strip()]
    num_problems = int(data.get('numProblems'))
    json_file_path = generate_json(standard, num_problems, theme_list)
    print(json_file_path)
    create_worksheet_from_json(json_file_path) 

    return jsonify({"pdf_url": "/download-worksheet"}), 200

@app.route('/download-worksheet', methods=['GET'])
def download_worksheet():
    pdf_path = 'Math_Worksheet.pdf' 
    return send_file(pdf_path, as_attachment=False, mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)
