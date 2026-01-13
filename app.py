import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # allow your static site to call this API

SYSTEM_PROMPT = """You are Archana, an AI assistant for Paramount Project Endeavors Pvt. Ltd.
You answer concisely and professionally.
If a question is about construction, fit-outs, rollouts, or the company, answer in detail.
If you don't know, say you are not sure instead of making things up."""

# --------------------------------------------------------------------
# STRUCTURED KNOWLEDGE BASE
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

# Regions and typical cities (aligned loosely with your frontend map)
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
    # The PDF mentions >25 management staff; we summarise as a group
]

HEADCOUNT_SUMMARY = (
    "Paramount employs more than 25 skilled management and engineering professionals, "
    "supporting its project delivery across sectors and regions."
)

# --------------------------------------------------------------------
# HELPER FUNCTIONS
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


# --------------------------------------------------------------------
# MAIN REPLY FUNCTION
# --------------------------------------------------------------------


def generate_archana_reply(user_message: str) -> str:
    text = (user_message or "").lower().strip()
    if not text:
        return (
            "Namaste, I am Archana, your AI assistant for Paramount Project "
            "Endeavors Pvt. Ltd. How can I help you today?"
        )

    # 1) Greetings / small talk
    if contains_any(text, ["hello", "hi ", "hi,", "hey", "good morning", "good evening"]):
        return (
            "Hello, this is Archana from Paramount Project Endeavors Pvt. Ltd. "
            "How can I support your project today?"
        )

    if "who are you" in text or "what are you" in text or "archana" in text:
        return (
            "I am Archana, an AI assistant for Paramount Project Endeavors Pvt. Ltd., "
            "helping you understand our services, rollout capabilities, project footprint and team."
        )

    # 2) Company identity and registration
    if contains_any(text, ["company name", "legal name", "full name"]):
        return (
            "The full legal name is Paramount Project Endeavors Private Limited "
            "(Paramount Project Endeavors Pvt. Ltd.)."
        )

    if "cin" in text or "registration number" in text or "company identification" in text:
        return (
            "Paramount Project Endeavors Private Limited is registered in India under "
            "CIN U74999MH2013PTC240009."
        )

    if contains_any(text, ["when were you incorporated", "when were you founded", "when did you start"]):
        return (
            "Paramount Project Endeavors Pvt. Ltd. has over a decade of operational experience, "
            "built on the practical site and management experience of its directors and core team."
        )

    # 3) Services / what the company does
    if (
        "what do you do" in text
        or "what does paramount" in text
        or "what does the company do" in text
        or "core business" in text
    ):
        return (
            "Paramount provides professional turnkey solutions for interior fit‑outs and project rollouts. "
            "We combine technical expertise and strong site management to take projects from concept and "
            "design through to successful implementation, with a focus on quality, timelines and coordination."
        )

    if contains_any(text, ["services", "scope of work", "capabilities", "what you offer"]):
        return (
            "Key services include project planning, interior works, civil works, MEP works including HVAC, "
            "and allied packages. Paramount coordinates drawings, BOQs, vendors and approvals, and manages "
            "end‑to‑end delivery within agreed time, cost and quality parameters."
        )

    if "strategy" in text or "how do you deliver" in text or "approach" in text or "process" in text:
        return (
            "The delivery strategy is to emphasise quality and service through well‑qualified engineers and "
            "technicians, systematic coordination and clear planning. We follow a professional approach from "
            "initial site meetings through project completion so that milestones, quality checks and handovers "
            "stay on track."
        )

    # 4) Sectors / verticals
    if contains_any(text, ["sectors", "verticals", "industries", "which sectors"]):
        return (
            "Paramount works across retail stores, quick‑service restaurants (QSR), architectural restaurants "
            "and bars, hotels, corporate offices and high‑end residences. In addition, the team has experience "
            "with multiplexes, fitness centres and other specialised interior projects."
        )

    # Sector‑specific questions
    if "retail" in text:
        return list_sector_projects("retail")

    if "qsr" in text or "quick service" in text:
        return list_sector_projects("qsr")

    if contains_any(text, ["restaurant", "restro", "bar", "f&b"]):
        return list_sector_projects("restaurants")

    if "hotel" in text or "hospitality" in text:
        return list_sector_projects("hospitality")

    if "office" in text or "corporate" in text or "workspace" in text:
        return list_sector_projects("offices")

    if "residence" in text or "bungalow" in text or "apartment" in text or "home interiors" in text:
        return list_sector_projects("residences")

    # 5) Brands
    brand_key = detect_brand(text)
    if brand_key:
        return describe_brand(brand_key)

    if contains_any(text, ["which brands", "list your brands", "client brands", "who have you worked for"]):
        brand_names = sorted({b.title() for b in BRANDS.keys()})
        sample = ", ".join(brand_names[:15])
        return (
            f"Paramount has delivered projects for brands such as {sample}, and others across retail, "
            "QSR, hospitality and corporate formats."
        )

    # 6) Locations / cities / regions
    if contains_any(text, ["cities", "locations", "where do you work", "pan india", "pan-india"]):
        parts = [
            "Paramount manages projects across India, with strong presence in West, North, South and East regions.",
            describe_region("west"),
            describe_region("north"),
            describe_region("south"),
            describe_region("east"),
        ]
        return " ".join(p for p in parts if p)

    region = detect_region(text)
    if region:
        return describe_region(region)

    # 7) Timelines / schedule / budget
    if "timeline" in text or "how long" in text or "duration" in text or "schedule" in text:
        return (
            "Typical single‑site restaurant or retail fit‑outs are executed in roughly 6–10 weeks, depending on "
            "scope, mall approvals and site conditions. Larger hotel or multi‑floor projects can run longer, "
            "but Paramount sequences civil, interiors and MEP so that activities run in parallel wherever possible."
        )

    if "cost" in text or "budget" in text or "rates" in text or "pricing" in text:
        return (
            "Exact pricing depends on city, scope, specifications and services. Paramount normally works against "
            "drawings and BOQs or a defined scope, and can support value‑engineering while maintaining brand "
            "standards. For a directional estimate, it is best to share basic drawings and a brief via the "
            "website contact form."
        )

    # 8) How to engage / next steps
    if contains_any(text, ["how do i start", "engage you", "start a project", "next step", "rfp", "tender"]):
        return (
            "To start, you can share basic project details – location, approximate area, format "
            "(retail, QSR, office, hotel or residence) and any available drawings or BOQ. "
            "Paramount will then review the scope, outline timelines and suggest a delivery "
            "approach aligned to your rollout or opening plan."
        )

    # 9) Team / staff / directors
    if "team" in text or "staff" in text or "who works" in text:
        return team_overview()

    if "directors" in text or "management" in text or "promoters" in text:
        return (
            "The company is led by full‑time directors including Pradeep Singh and Aalok Mishra, "
            "both BE Civil engineers from Mumbai University. Pradeep Singh oversees on‑site project "
            "work from feasibility to handover, while Aalok Mishra leads contracts, BOQs and billing. "
            f"{HEADCOUNT_SUMMARY}"
        )

    # 10) Contact details
    if "contact" in text or "phone" in text or "email" in text or "office address" in text:
        return (
            "You can reach Paramount at the Mumbai head office: 13A, 3rd Floor, Ajay Apartments, "
            "Next to Ruia Hall, Anand Road, Malad West, Mumbai – 400064, phone +91‑22‑2881 2177, "
            "mobile +91 9920479027, email info@ppepl.co.in. The North office is at Plot No. 70/60, "
            "Upper Ground Floor, Mangolpuri, New Delhi – 110085. You can also use the contact form "
            "on the website to share project details."
        )

    # 11) Website / profile
    if "website" in text or "profile" in text or "company profile" in text:
        return (
            "You can explore the live profile, map and sample works at "
            "https://esingh16.github.io/Paramount-Projects-Endeavors-Pvt.-Ltd/ "
            "and request the detailed PDF company profile for internal reference."
        )

    # 12) Fallback
    return (
        "Archana here. I may not have full context for that question, but you can ask me about "
        "Paramount's services, rollout capabilities, focus sectors, project examples, city coverage, "
        "team or how to get in touch for a new project."
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
