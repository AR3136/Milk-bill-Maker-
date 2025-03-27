import os
from flask import Flask, request, jsonify, render_template
import pandas as pd
import re
import difflib  # For fuzzy matching
import pywhatkit as kit
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Upload folder configuration
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"xlsx"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)
        return jsonify({"message": "File uploaded successfully", "filepath": filepath})

    return jsonify({"error": "Invalid file format"}), 400


@app.route("/calculate", methods=["POST"])
def calculate_bill():
    try:
        data = request.json
        filepath = data.get("filepath")
        customer_name = data.get("customer_name").strip().lower()

        if not os.path.exists(filepath):
            return jsonify({"error": "File not found"}), 400

        df = pd.read_excel(filepath)
        df.columns = [re.sub(r"\s+", " ", col.strip().lower()) for col in df.columns]

        # Extract milk rates
        try:
            rate_cow = float(df["rate cow"].iloc[0])
            rate_buffalo = float(df["rate buffalo"].iloc[0])
        except KeyError:
            return jsonify({"error": "Missing 'Rate Cow' or 'Rate Buffalo' column"}), 400

        # Function for fuzzy column matching
        def find_best_match(target, options):
            match = difflib.get_close_matches(target, options, n=1, cutoff=0.7)
            return match[0] if match else None

        customer_cow_column = find_best_match(f"{customer_name} cow", df.columns)
        customer_buffalo_column = find_best_match(f"{customer_name} buffalo", df.columns)

        if not customer_cow_column and not customer_buffalo_column:
            return jsonify({"error": f"No records found for customer '{customer_name}'"}), 404

        df.fillna(0, inplace=True)

        # Calculate milk totals
        cow_milk_total = float(df[customer_cow_column].sum()) if customer_cow_column else 0
        buffalo_milk_total = float(df[customer_buffalo_column].sum()) if customer_buffalo_column else 0
        total_bill = (cow_milk_total * rate_cow) + (buffalo_milk_total * rate_buffalo)

        # Return formatted JSON response
        return jsonify({
            "customer_name": customer_name.capitalize(),
            "cow_milk": round(cow_milk_total, 2),
            "buffalo_milk": round(buffalo_milk_total, 2),
            "total_bill": round(total_bill, 2)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/send_whatsapp", methods=["POST"])
def send_whatsapp():
    try:
        data = request.json
        phone_number = data.get("phone_number")
        message = data.get("message")

        if not phone_number.startswith("+91") or not phone_number[1:].isdigit():
            return jsonify({"error": "Invalid phone number format"}), 400

        kit.sendwhatmsg_instantly(phone_number, message, 15, True, 15)
        return jsonify({"message": "WhatsApp message sent successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
