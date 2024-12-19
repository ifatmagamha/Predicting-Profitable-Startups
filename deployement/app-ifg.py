from flask import Flask, request, render_template
import os
import sys 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from predection import StartupInvestmentPredictor
import tempfile

app = Flask(__name__)
UPLOAD_FOLDER = 'data'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if 'file' not in request.files:
            return "No file part", 400
        file = request.files['file']
        if file.filename == '':
            return "No file selected", 400
        if file:
            with tempfile.TemporaryDirectory() as temp_dir:
                file_path = os.path.join(temp_dir, 'cleaned_data.csv')
                file.save(file_path)

                # Initialize predictor
                predictor = StartupInvestmentPredictor(file_path)
                predictor.load_and_preprocess_data()

                # Train models and retrieve results
                model_performance, top_indices, best_model_name, X_test, y_test = predictor.train_models()

                # Retrieve the DataFrame containing test results for display
                df_test_results = predictor.display_predictions(X_test, y_test, best_model_name)

                # Pass results to results template
                return render_template(
                    "display.html",
                    results=model_performance,
                    top_indices=top_indices,
                    best_model_name=best_model_name,
                    df_test_results=df_test_results.to_dict(orient='records')  # Convert DataFrame to dictionary for Jinja
                )
    return render_template("upload.html")


@app.route("/results", methods=["GET"])
def results():
    return "Results will be shown here."

if __name__ == "__main__":
    app.run(debug=True)
