from flask import Flask, request, render_template
import os
from investement_prediction import StartupInvestmentPredictor

app = Flask(__name__)
UPLOAD_FOLDER = 'data'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the data folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        # Handle file upload
        if 'file' not in request.files:
            return "No file part", 400
        file = request.files['file']
        if file.filename == '':
            return "No file selected", 400
        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'cleaned_data.csv')
            file.save(file_path)

            # Initialize predictor
            predictor = StartupInvestmentPredictor(file_path)
            predictor.load_and_preprocess_data()
            model_performance, top_indices = predictor.train_models()

            # Pass results to results template
            return render_template("result.html", results=model_performance, top_indices=top_indices)

    return render_template("upload.html")

@app.route("/results", methods=["GET"])
def results():
    return "Results will be shown here."

if __name__ == "__main__":
    app.run(debug=True)
