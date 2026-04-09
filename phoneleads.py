import requests
import random
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

YELP_KEY = "vNXs85Q0Dpm2C7_8CoXiqczM_lFH10nhKu3PKeW-88sgHha1abWLQSH_l1hoiehaOI9rN-tF_AWRAhdz_yU7h7qrWajNlI3xyvegyBNks3-bJVOrT3hmQujS4N7VaXYx"

@app.route("/")
def index():
    return "MCA Agency Leads Finder API is running!"

@app.route("/search")
def search():
    term = request.args.get("term", "barbershop")
    city = request.args.get("city", "Compton, CA")
    offset = random.randint(0, 40)

    yelp_headers = {"Authorization": f"Bearer {YELP_KEY}"}
    params = {
        "term": term,
        "location": city,
        "limit": 50,
        "offset": offset
    }
    response = requests.get("https://api.yelp.com/v3/businesses/search", headers=yelp_headers, params=params)
    businesses = response.json().get("businesses", [])

    leads = []
    for biz in businesses:
        biz_id = biz.get("id")
        detail_response = requests.get(
            f"https://api.yelp.com/v3/businesses/{biz_id}",
            headers=yelp_headers
        ).json()

        website = detail_response.get("website", "")
        if website and website.strip() != "":
            continue

        phone = detail_response.get("display_phone", "")
        if not phone or phone.strip() == "":
            continue

        leads.append({
            "name": detail_response.get("name", ""),
            "phone": phone,
            "address": ", ".join(detail_response["location"].get("display_address", []))
        })

    return jsonify({"total_checked": len(businesses), "leads": leads})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
