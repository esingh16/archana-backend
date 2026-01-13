import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI  # NEW

app = Flask(__name__)
CORS(app)  # allow your static site to call this API

# OpenAI client (reads OPENAI_API_KEY from environment)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))

SYSTEM_PROMPT = """You are Archana, an AI assistant for Paramount Project Endeavors Pvt. Ltd.
You answer concisely and professionally.
You focus on Paramount's services, projects, brands, cities, team, and how to engage.
If a question is not related to Paramount or construction/fit-outs, politely say it is outside your scope.
Use the structured company data provided to you as reliable context, and don't invent facts.
"""

# --------------------------------------------------------------------
# STRUCTURED KNOWLEDGE BASE (same as before)
# --------------------------------------------------------------------

# Core sectors and what Paramount does there
SECTORS = {
    "retail": {
        "description": (
            "Retail formats including big-box wholesale, value retail and electronics stores. "
            "Typical scopes cover civil works, interiors, MEP, signage coordination and rollouts."
        ),
        "examples": [
            "Booker India wholesale stores (around 30,000 sq.ft. in the West)",
            "Mr DIY outlets across pan‑India",
            "Tata Croma stores in West and South India (around 10,000 sq.ft.)",
        ],
    },
    "qsr": {
        "description": (
            "Quick Service Restaurant (QSR) and café formats, often high‑repeat rollouts with tight timelines "
            "in malls and high‑street locations."
        ),
        "examples": [
            "Burger King outlets pan‑India (around 2,500 sq.ft.)",
            "Punjab Grill and YouMee restaurants pan‑India",
            "McDonald's and Domino's outlets across multiple cities",
            "KFC restaurants in West and South India (around 4,500 sq.ft.)",
        ],
    },
    "restaurants": {
        "description": (
            "Architectural restaurants and bars where brand experience and detailing are critical, "
            "with bespoke interiors and services integration."
        ),
        "examples": [
            "Burma Burma (around 2,500 sq.ft., pan‑India)",
            "Talli Turmeric (about 4,500 sq.ft. in West India)",
            "Family Tree vegetarian restaurant in Mulund, Mumbai (about 2,500–3,100 sq.ft.)",
            "Izumi and other premium F&B formats in Mumbai",
        ],
    },
    "hospitality": {
        "description": (
            "Business hotels and hospitality projects with full interior, services and common area coordination."
        ),
        "examples": [
            "Ginger hotel in Mumbai (around 75,500 sq.ft.)",
            "Accor hotel project in Gujarat (around 55,000 sq.ft.)",
        ],
    },
    "offices": {
        "description": (
            "Corporate offices with open workspaces, meeting rooms, cabins and support areas."
        ),
        "examples": [
            "Nokia Siemens office (around 7,100 sq.ft. in North India)",
            "Trafigura India office (around 7,000 sq.ft. in West India)",
        ],
    },
    "residences": {
        "description": (
            "High‑end residences and bungalows with complete interior and services packages."
        ),
        "examples": [
            "Multiple residences and bungalows in Mumbai and suburbs, "
            "including apartments at Lodha One World and others.",
        ],
    },
}

# Brand-level mapping
BRANDS = {
    "burger king": {
        "sector": "qsr",
        "typical_area": "around 2,500 sq.ft. per outlet",
        "footprint": "pan‑India across North, West, South and East cities",
    },
    "kfc": {
        "sector": "qsr",
        "typical_area": "around 4,500 sq.ft. for flagship outlets",
        "footprint": "West and South India, including Aurangabad and other cities",
    },
    "mcdonald's": {
        "sector": "qsr",
        "typical_area": "around 2,000 sq.ft. per outlet",
        "footprint": "pan‑India in key urban centres",
    },
    "domino's": {
        "sector": "qsr",
        "typical_area": "around 1,500 sq.ft. per store",
        "footprint": "North and other regions via multi‑city rollouts",
    },
    "punjab grill": {
        "sector": "qsr",
        "typical_area": "around 3,000 sq.ft.",
        "footprint": "pan‑India",
    },
    "youmee": {
        "sector": "qsr",
        "typical_area": "around 2,000 sq.ft.",
        "footprint": "pan‑India in malls and high streets",
    },
    "mr diy": {
        "sector": "retail",
        "typical_area": "around 10,000 sq.ft.",
        "footprint": "pan‑India value retail stores",
    },
    "booker": {
        "sector": "retail",
        "typical_area": "around 30,000 sq.ft.",
        "footprint": "wholesale formats in West India",
    },
    "tata croma": {
        "sector": "retail",
        "typical_area": "around 10,000 sq.ft.",
        "footprint": "West and South India",
    },
    "croma": {
        "sector": "retail",
        "typical_area": "around 10,000 sq.ft.",
        "footprint": "West and South India",
    },
    "burma burma": {
        "sector": "restaurants",
        "typical_area": "around 2,500 sq.ft.",
        "footprint": "pan‑India restaurant‑tea room formats",
    },
    "talli turmeric": {
        "sector": "restaurants",
        "typical_area": "around 4,500 sq.ft.",
        "footprint": "West India (for example, Atria Mall, Mumbai)",
    },
    "izumi": {
        "sector": "restaurants",
        "typical_area": "around 2,000–2,100 sq.ft.",
        "footprint": "Mumbai and West India",
    },
    "family tree": {
        "sector": "restaurants",
        "typical_area": "around 2,500–3,100 sq.ft.",
        "footprint": "Mulund, Mumbai and similar urban locations",
    },
    "cinepolis": {
        "sector": "hospitality",
        "typical_area": "around 25,500 sq.ft. multiplexes",
        "footprint": "South India",
    },
    "anytime fitness": {
        "sector": "hospitality",
        "typical_area": "around 7,500 sq.ft.",
        "footprint": "North and West India",
    },
    "ginger": {
        "sector": "hospitality",
        "typical_area": "around 75,500 sq.ft.",
        "footprint": "Mumbai",
    },
    "accor": {
        "sector": "hospitality",
        "typical_area": "around 55,000 sq.ft.",
        "footprint": "Gujarat",
    },
}

# Regions and typical cities
REGIONS = {
    "west": [
        "Mumbai",
        "Pune",
        "Nagpur",
        "Goa",
        "Surat",
        "Vadodara",
        "Rajkot",
        "Jamnagar",
        "Aurangabad",
        "Ankleshwar",
    ],
    "north": [
        "New Delhi",
        "Delhi",
        "Lucknow",
        "Kanpur",
        "Prayagraj",
        "Jaipur",
        "Gurgaon",
        "Noida",
        "Ghaziabad",
        "Amritsar",
    ],
    "south": [
        "Chennai",
        "Bangalore",
        "Hyderabad",
        "Hubli",
        "Mangalore",
        "Kochi",
    ],
    "east": [
        "Kolkata",
        "Guwahati",
        "Siliguri",
        "Ranchi",
        "Patna",
        "Gangtok",
    ],
}

# Team / leadership info
TEAM = [
    {
        "name": "Pradeep Singh",
        "role": "Director – Business & Project Management",
        "background": "BE Civil, Mumbai University; responsible for onsite project work from feasibility to final handover.",
    },
    {
        "name": "Aalok Mishra",
        "role": "Director – Contracts & Finance",
        "background": "BE Civil, Mumbai University; leads BOQ finalisation, contracts and billing processes.",
    },
]

HEADCOUNT_SUMMARY = (
    "Paramount employs more than 25 skilled management and engineering professionals, "
    "supporting its project delivery across sectors and regions."
)

# --------------------------------------------------------------------
# HELPER FUNCTIONS (unchanged)
# --------------------------------------------------------------------


def contains_any(text: str, keywords) -> bool:
    return any(k in text for k in keywords)


def detect_region(text: str):
    for region, cities in REGIONS.items():
        if region in text:
            return region
        for c in cities:
            if c.lower() in text:
                return region
    return None


def detect_brand(text: str):
    for brand_key in BRANDS.keys():
        if brand_key in text:
            return brand_key
    return None


def describe_region(region: str) -> str:
    cities = REGIONS.get(region, [])
    if not cities:
        return ""
    city_list = ", ".join(cities[:8])
    region_label = region.capitalize()
    return (
        f"In the {region_label} region, Paramount has delivered projects in cities such as "
        f"{city_list}, with additional locations depending on brand rollout plans."
    )


def describe_brand(brand_key: str) -> str:
    info = BRANDS.get(brand_key)
    if not info:
        return ""
    sector = info["sector"]
    sector_desc = SECTORS.get(sector, {}).get("description", "")
    lines = [
        f"Paramount has executed projects for {brand_key.title()}.",
        f"Typical outlet area is {info['typical_area']}.",
        f"The footprint includes {info['footprint']}.",
    ]
    if sector_desc:
        lines.append(f"This falls under our {sector} sector: {sector_desc}")
    return " ".join(lines)


def list_sector_projects(sector_key: str) -> str:
    sector = SECTORS.get(sector_key)
    if not sector:
        return ""
    examples = "; ".join(sector["examples"])
    return (
        f"In {sector_key.upper()} formats, Paramount focuses on: {sector['description']} "
        f"Representative projects include {examples}."
    )


def team_overview() -> str:
    parts = []
    for member in TEAM:
        parts.append(
            f"{member['name']} – {member['role']}. {member['background']}"
        )
    parts.append(HEADCOUNT_SUMMARY)
    return " ".join(parts)


# Build a compact textual context from the structured data for the LLM
def build_structured_context() -> str:
    lines = []

    # Sectors
    for key, val in SECTORS.items():
        lines.append(f"Sector {key}: {val['description']}")
        lines.append("Examples: " + "; ".join(val["examples"]))

    # Brands
    for key, val in BRANDS.items():
        lines.append(
            f"Brand {key}: sector={val['sector']}, typical_area={val['typical_area']}, "
            f"footprint={val['footprint']}"
        )

    # Regions
    for region, cities in REGIONS.items():
        lines.append(f"Region {region}: cities such as {', '.join(cities)}")

    # Team
    lines.append("Team: " + team_overview())

    return "\n".join(lines)


STRUCTURED_CONTEXT = build_structured_context()


# --------------------------------------------------------------------
# MAIN REPLY FUNCTION – NOW LLM-BASED
# --------------------------------------------------------------------


def generate_archana_reply(user_message: str) -> str:
    text = (user_message or "").strip()
    if not text:
        return (
            "Namaste, I am Archana, your AI assistant for Paramount Project "
            "Endeavors Pvt. Ltd. How can I help you today?"
        )

    # Lightweight intent hints for brands/regions to help the model
    lower = text.lower()
    hints = []
    brand_key = detect_brand(lower)
    if brand_key:
        hints.append("User is asking about brand: " + brand_key)
    region = detect_region(lower)
    if region:
        hints.append("User is asking about region: " + region)

    hint_text = "\n".join(hints) if hints else "No specific brand/region detected."

    try:
        completion = client.chat.completions.create(
            model="gpt-4.1-mini",
            temperature=0.2,
            max_tokens=400,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "system",
                    "content": (
                        "Structured company data for Paramount Project Endeavors Pvt. Ltd:\n"
                        + STRUCTURED_CONTEXT
                    ),
                },
                {
                    "role": "system",
                    "content": "Helper hints: " + hint_text,
                },
                {"role": "user", "content": text},
            ],
        )
        reply = completion.choices[0].message.content.strip()
        if not reply:
            return (
                "Archana here. I could not generate a detailed response just now; "
                "please try asking your question again in a moment."
            )
        return reply
    except Exception:
        return (
            "Archana here. I am temporarily unavailable due to a backend error. "
            "Please try again after some time."
        )


# --------------------------------------------------------------------
# ROUTES
# --------------------------------------------------------------------


@app.route("/")
def health():
    return jsonify({"status": "ok", "assistant": "Archana"})


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")
    reply = generate_archana_reply(message)
    return jsonify({"assistant_name": "Archana", "reply": reply})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
