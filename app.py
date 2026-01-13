import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # allow your static site to call this API

SYSTEM_PROMPT = """You are Archana, an AI assistant for Paramount Project Endeavors Pvt. Ltd.
You answer concisely and professionally.
If a question is about construction, fit-outs, rollouts, or the company, answer in detail.
If you don't know, say you are not sure instead of making things up."""

# ---- RULE-BASED KNOWLEDGE BASE ----
def generate_archana_reply(user_message: str) -> str:
    text = (user_message or "").lower().strip()
    if not text:
        return (
            "Namaste, I am Archana, your AI assistant for Paramount Project "
            "Endeavors Pvt. Ltd. How can I help you today?"
        )

    # 1) Greetings / small talk
    if any(w in text for w in ["hello", "hi ", "hi,", "hey", "good morning", "good evening"]):
        return (
            "Hello, this is Archana from Paramount Project Endeavors Pvt. Ltd. "
            "How can I support your project today?"
        )

    if "who are you" in text or "what are you" in text or "archana" in text:
        return (
            "I am Archana, an AI assistant for Paramount Project Endeavors Pvt. Ltd., "
            "here to help you understand our services, rollout capabilities and project footprint."
        )

    # 2) Company identity / registration
    if "company name" in text or "full name" in text or "legal name" in text:
        return (
            "The full legal name is Paramount Project Endeavors Private Limited "
            "(often written as Paramount Project Endeavors Pvt. Ltd.)."
        )

    if "cin" in text or "company identification" in text or "registration number" in text:
        return (
            "Paramount Project Endeavors Private Limited is registered in India under "
            "CIN U74999MH2013PTC240009."  # from zaubacorp link
        )

    if "when" in text and ("incorporated" in text or "founded" in text or "started" in text):
        return (
            "Paramount Project Endeavors Pvt. Ltd. has over 10 years of practical experience, "
            "with directors who each bring around 20 years of execution and site-management expertise."
        )

    if "directors" in text or "management" in text or "promoters" in text:
        return (
            "The company is led by full‑time directors including Pradeep Singh and Aalok Mishra, "
            "both BE Civil engineers from Mumbai University, supported by a team of more than "
            "25 skilled management personnel."  # from PDF
        )

    # 3) What the company does
    if "what do you do" in text or "what does paramount" in text or "what does the company do" in text:
        return (
            "Paramount provides professional turnkey solutions for projects, combining technical "
            "expertise and strong site management to take projects from concept and design through "
            "to successful implementation. The focus is on quality interior execution and rollout "
            "coordination across retail, QSR, hospitality, offices and residences."
        )

    if "services" in text or "scope of work" in text or "capabilities" in text:
        return (
            "Key services include project designing, interior works, civil works, MEP works including "
            "HVAC, and allied works. The team plans project flow, implements systems and processes, "
            "coordinates multiple stakeholders, and manages end‑to‑end delivery within agreed time, "
            "cost and quality parameters."  # from PDF focus sectors
        )

    if "strategy" in text or "how do you deliver" in text or "approach" in text or "process" in text:
        return (
            "The delivery strategy is to emphasise quality and service, using well‑qualified engineers "
            "and technicians, systematic coordination, and clear planning. Paramount follows a "
            "professional approach from initial site meetings through project completion so that "
            "targets stay on program and quality benchmarks are met."
        )

    # 4) Sectors and project types
    if "sectors" in text or "verticals" in text or "industry" in text:
        return (
            "Paramount focuses on retail stores, quick‑service restaurants (QSR), architectural "
            "restaurant‑bars, hotels, corporate offices and premium residences. The company also "
            "executes multiplexes, fitness centres and other specialised interior projects."
        )

    if "retail" in text or "store" in text or "croma" in text or "mr diy" in text or "booker" in text:
        return (
            "In retail, Paramount has delivered stores such as Booker India wholesale formats, "
            "Mr DIY outlets and Tata Croma electronics stores, typically in the 10,000–30,000 sq.ft. "
            "range across West and South India."
        )

    if "qsr" in text or "quick service" in text or "restaurant" in text or "food" in text:
        return (
            "In quick‑service and restaurant formats, Paramount has executed outlets for Burger King, "
            "Punjab Grill, YouMee, McDonald's, Domino's and KFC, generally between about 1,500 and "
            "4,500 sq.ft., including pan‑India rollouts for several of these brands."
        )

    if "hospitality" in text or "hotel" in text or "ginger" in text or "accor" in text:
        return (
            "In hospitality, Paramount has handled hotel projects such as Ginger Mumbai and Accor in "
            "Gujarat, with built‑up areas around 55,000–75,000 sq.ft., covering full interior and "
            "services coordination."
        )

    if "office" in text or "corporate" in text or "nokia" in text or "trafigura" in text:
        return (
            "For corporate offices, Paramount has delivered projects for clients such as Nokia Siemens "
            "and Trafigura India, with floor plates around 7,000 sq.ft., including partitions, "
            "workstations, conference rooms, ceilings, flooring, electrical and allied works."
        )

    if "residence" in text or "bungalow" in text or "apartment" in text or "home interiors" in text:
        return (
            "Paramount has also executed high‑end residential interiors for bungalows and apartments "
            "in and around Mumbai and its suburbs, handling civil modifications, false ceilings, "
            "carpentry, finishes and services as turnkey packages."
        )

    # 5) Example projects / “best works”
    if "best works" in text or "sample projects" in text or "case studies" in text:
        return (
            "Some highlighted works include Burma Burma, Talli Turmeric, Izumi, Family Tree vegetarian "
            "restaurant, KFC at Nirala Bazaar in Aurangabad, and multiple Croma, Mr DIY and QSR outlets. "
            "Typical restaurant areas range from about 2,000 to 4,500 sq.ft. with build times around "
            "60–70 days for individual outlets."
        )

    if "kfc" in text:
        return (
            "A representative KFC restaurant executed by Paramount was at Nirala Bazaar in Aurangabad, "
            "Maharashtra, with a total area of about 4,500 sq.ft. and a completion time of roughly 70 days."
        )

    if "family tree" in text:
        return (
            "The Family Tree vegetarian restaurant at Mulund, Mumbai, was delivered by Paramount over "
            "approximately 60 days, for a total area of around 2,500–3,100 sq.ft."
        )

    # 6) Locations, pan‑India footprint, brands list
    if "locations" in text or "cities" in text or "where do you work" in text or "pan india" in text:
        return (
            "Paramount manages projects across India, with a strong presence in Mumbai and the West, "
            "North‑India rollouts, and work in South and East regions. The interactive map and clients "
            "directory on the website show detailed city‑wise markers by brand."
        )

    if "brands" in text or "clients" in text or "who have you worked for" in text:
        return (
            "Paramount has delivered projects for brands such as Burger King, KFC, McDonald's, Domino's, "
            "Punjab Grill, YouMee, Mr DIY, Tata Croma, Cinepolis, Anytime Fitness, Burma Burma, Izumi and "
            "others, along with hotel chains, corporate offices and residential clients."
        )

    # 7) How to engage / timelines / process questions
    if "how do i start" in text or "engage" in text or "next step" in text or "rfp" in text or "tender" in text:
        return (
            "You can start by sharing basic project details – location, approximate area, format "
            "(retail, QSR, office, hotel or residence) and any available drawings or BOQ. "
            "Paramount will then review scope, advise on timelines and sequencing, and propose a "
            "delivery approach aligned to your rollout plan."
        )

    if "timeline" in text or "how long" in text or "duration" in text or "schedule" in text:
        return (
            "Typical single‑site restaurant or retail fit‑outs are executed in roughly 60–10 weeks "
            "depending on scope, approvals and site conditions. Larger hospitality or multi‑floor "
            "projects can run longer, but Paramount plans sequencing so civil, interiors and MEP progress "
            "in parallel where possible."
        )

    if "cost" in text or "budget" in text or "rates" in text or "pricing" in text:
        return (
            "Exact pricing depends on city, scope, specifications and services. Paramount usually works "
            "against drawings and BOQs or a defined scope, and can support value‑engineering while "
            "maintaining brand standards. For a directional estimate, it is best to share basic drawings "
            "and a brief via the contact form."
        )

    # 8) Contact details / offices
    if "contact" in text or "phone" in text or "email" in text or "office address" in text:
        return (
            "You can reach Paramount at the Mumbai head office: 13A, 3rd Floor, Ajay Apartments, "
            "Next to Ruia Hall, Anand Road, Malad West, Mumbai – 400064, phone +91‑22‑2881 2177, "
            "mobile +91 9920479027, email info@ppepl.co.in. The North office is at Plot No. 70/60, "
            "Upper Ground Floor, Mangolpuri, New Delhi – 110085."
        )

    # 9) Website / where to see more
    if "website" in text or "profile" in text or "company profile" in text:
        return (
            "You can explore the full company profile and live project map at "
            "https://esingh16.github.io/Paramount-Projects-Endeavors-Pvt.-Ltd/ "
            "and request the detailed PDF profile for reference."
        )

    # 10) Fallback generic answer
    return (
        "Archana here. I may not have full context for that question, but you can ask me about "
        "Paramount's services, rollout capabilities, focus sectors, project examples, city coverage "
        "or how to get in touch for a new project."
    )

# ---- ROUTES ----
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
