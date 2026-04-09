import requests
import random
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

FOURSQUARE_KEY = "FHPFAEY4KVHW34ZAS4XM3CX1MV1TUKPDEHLI1SND5BFP5CEB"

@app.route("/")
def index():
    return "MCA Agency Leads Finder API is running!"

@app.route("/search")
def search():
    term = request.args.get("term", "barbershop")
    city = request.args.get("city", "Compton, CA")

    headers = {
        "Authorization": FOURSQUARE_KEY,
        "accept": "application/json"
    }

    params = {
        "query": term,
        "near": city,
        "limit": 50,
        "fields": "name,location,tel,website"
    }

    response = requests.get(
        "https://api.foursquare.com/v3/places/search",
        headers=headers,
        params=params
    )

    data = response.json()
    businesses = data.get("results", [])

    leads = []
    for biz in businesses:
        website = biz.get("website", "")
        if website and website.strip() != "":
            continue

        phone = biz.get("tel", "")
        if not phone or phone.strip() == "":
            continue

        location = biz.get("location", {})
        address_parts = [
            location.get("address", ""),
            location.get("locality", ""),
            location.get("region", ""),
            location.get("postcode", "")
        ]
        address = ", ".join(p for p in address_parts if p)

        leads.append({
            "name": biz.get("name", ""),
            "phone": phone,
            "address": address
        })

    return jsonify({"total_checked": len(businesses), "leads": leads})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
