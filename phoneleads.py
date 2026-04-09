import requests
import random
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

YELP_KEY = "vNXs85Q0Dpm2C7_8CoXiqczM_lFH10nhKu3PKeW-88sgHha1abWLQSH_l1hoiehaOI9rN-tF_AWRAhdz_yU7h7qrWajNlI3xyvegyBNks3-bJVOrT3hmQujS4N7VaXYx"

def google_has_website(business_name, address):
    try:
        query = f"{business_name} {address} official website"
        response = requests.get(
            "https://www.google.com/search",
            params={"q": query},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=5
        )
        text = response.text.lower()
        skip_domains = ["yelp.com", "facebook.com", "instagram.com", "google.com", "yellowpages.com", "mapquest.com"]
        lines = [l for l in text.split() if "http" in l]
        for line in lines:
            if not any(d in line for d in skip_domains):
                return True
        return False
    except:
        return False

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
        detail = requests.get(
            f"https://api.yelp.com/v3/businesses/{biz_id}",
            headers=yelp_headers
        ).json()

        website = detail.get("website", "")
        if website and website.strip() != "":
            continue

        phone = detail.get("phone", "") or detail.get("display_phone", "")
        if not phone or phone.strip() == "":
            continue

        name = detail.get("name", "")
        address = ", ".join(detail["location"].get("display_address", []))

        if google_has_website(name, address):
            continue

        leads.append({
            "name": name,
            "phone": detail.get("display_phone", phone),
            "address": address
        })

    return jsonify({"total_checked": len(businesses), "leads": leads})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
