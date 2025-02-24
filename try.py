from flask import Flask, request, render_template, redirect, url_for
import firebase_admin
from firebase_admin import credentials, db
import datetime
import os

app = Flask(__name__)

# Firebase setup
firebase_cred_path = 'E:/projects/linuxtraining/mlm-leaf-disease-detection-firebase-adminsdk-depno-7c5ba0e6e8.json'
if not firebase_admin._apps:
    if os.path.exists(firebase_cred_path):
        try:
            cred = credentials.Certificate(firebase_cred_path)
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://mlm-leaf-disease-detection-default-rtdb.asia-southeast1.firebasedatabase.app'
            })
        except Exception as e:
            print(f"Error initializing Firebase: {e}")
    else:
        print(f"Firebase credentials file not found: {firebase_cred_path}")

# Disease labels based on ID mapping
labels = ['Health', 'Miner', 'Rust', 'Phoma', 'Cercospora']

# Disease descriptions
diseases = {
    "rust": "Rust disease is caused by Hemileia vastatrix and affects coffee leaves.",
    "phoma": "Phoma leaf spot causes brown lesions on leaves, often due to fungi.",
    "miner": "Leaf miner damages coffee leaves by creating trails due to larval feeding.",
    "health": "The plant is healthy.",
    "cercospora": "Cercospora leaf spot causes brown spots on leaves, often due to fungi."
}

@app.route("/", methods=["GET", "POST"])
def index():
    disease_info = None
    disease_name = None
    humidity = "N/A"
    rainfall = "N/A"
    temperature = "N/A"
    harvesting_condition = "N/A"

    if request.method == "POST":
        data_source = request.form.get("data_source")
        if data_source == "firebase":
            # Fetch disease ID from Firebase
            disease_id = db.reference("/disease/id").get()

            # Convert ID to disease name
            if isinstance(disease_id, int) and 0 <= disease_id < len(labels):
                disease_name = labels[disease_id]
            else:
                disease_name = "Unknown"

            # Get disease description
            disease_info = diseases.get(disease_name.lower(), "Disease not found.")
        
        elif data_source == "user_input":
            disease_name = request.form.get("disease_name")
            if disease_name:
                disease_info = diseases.get(disease_name.lower(), "Disease not found.")

        # Fetch climate data from Firebase
        climate_data = db.reference("/data").get() or {}
        humidity = climate_data.get("humidity", "N/A")
        rainfall = "Yes" if climate_data.get("rain", 0) == 1 else "No"
        temperature = climate_data.get("temperature", "N/A")

        try:
            # Update harvesting condition based on climate data
            harvesting_condition = determine_harvesting_condition(rainfall, float(humidity), float(temperature))
        except ValueError as e:
            print(f"Error converting climate data to float: {e}")
            harvesting_condition = "Error in climate data"

    # Fetch coffee market data
    coffee_market_info = get_coffee_market_info()

    # Government schemes data
    government_schemes = {
        "15th Finance Commission": "The Coffee Board offers various schemes under the 15th Finance Commission. [3]",
        "MTF Schemes": "The Coffee Board offers various MTF schemes. [4]",
        "Modalities of Implementation Support Schemes": "The Coffee Board provides modalities for implementation support schemes. [5]",
        "Rainfall Insurance Scheme for Coffee Growers (RISC)": "The Coffee Board offers a rainfall insurance scheme for coffee growers. [6]"
    }

    return render_template("index.html", disease_info=disease_info, disease_name=disease_name,
                           humidity=humidity, rainfall=rainfall, temperature=temperature,
                           harvesting_condition=harvesting_condition, coffee_market_info=coffee_market_info,
                           government_schemes=government_schemes, current_date=datetime.datetime.now().strftime("%B %d, %Y"))

@app.route("/submit_climate_data", methods=["POST"])
def submit_climate_data():
    rain = int(request.form.get("rain"))
    humidity = request.form.get("humidity")
    temperature = request.form.get("temperature")
    
    # Update harvesting condition based on climate data
    harvesting_condition = determine_harvesting_condition("Yes" if rain == 1 else "No", float(humidity), float(temperature))
    
    return redirect(url_for('index'))

def determine_harvesting_condition(rain, humidity, temperature):
    if rain == "No":
        return "Dry weather - Ideal for coffee harvesting."
    if 15 <= temperature <= 25 and 50 <= humidity <= 70:
        return "Optimal harvesting conditions."
    elif temperature < 15:
        return "Too cold for optimal harvesting."
    elif temperature > 25:
        return "Too hot for optimal harvesting."
    elif humidity < 50:
        return "Humidity too low for optimal harvesting."
    elif humidity > 70:
        return "Humidity too high for optimal harvesting."
    else:
        return "Conditions not ideal for harvesting."

def get_coffee_market_info():
    # Simulate fetching the latest coffee market data
    coffee_market_info = """
    <ul>
        <li>As of today, the coffee market in Kerala is experiencing notable price fluctuations:</li>
        <li><strong>Current Prices:</strong></li>
        <ul>
            <li>Average Price: ₹31,250 per Quintal</li>
            <li>Lowest Price: ₹23,100 per Quintal</li>
            <li>Highest Price: ₹46,000 per Quintal</li>
        </ul>
        <li><strong>Market-Specific Rates:</strong></li>
        <ul>
            <li>Mananthavady: ₹27,800 per Quintal</li>
            <li>Pulpally: ₹23,200 per Quintal</li>
            <li>Kattappana: ₹46,000 per Quintal</li>
            <li>Thodupuzha: ₹28,000 per Quintal</li>
            <li>Sultan Bathery: ₹28,000 per Quintal</li>
            <li>Kalpetta: ₹27,200 per Quintal</li>
        </ul>
    </ul>
    """
    return coffee_market_info

if __name__ == "__main__":
    app.run(debug=True)
