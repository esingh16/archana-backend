import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # allow your static site to call this API

SYSTEM_PROMPT = """You are Archana, an AI assistant for Paramount Project Endeavors Pvt. Ltd.
You answer concisely and professionally.
If a question is about construction, fit-outs, rollouts, or the company, answer in detail.
If you don't know, say you are not sure instead of making things up."""

# ---- SIMPLE RULE-BASED REPLIES (no external API) ----
def generate_archana_reply(user_message: str) -> str:
    text = (user_message or "").lower()

    if not text.strip():
        return "Namaste, I am Archana, your AI assistant. How can I help you today?"

    # a few quick intents
    if "hello" in text or "hi" in text:
        return "Hello, this is Archana. How can I support your project today?"

    if "what do you do" in text or "who are you" in text:
        return (
            "I am Archana, an AI assistant for Paramount Project Endeavors Pvt. Ltd., "
            "helping you understand our services, rollout capabilities and project footprint."
        )

    if "services" in text or "what does paramount" in text:
        return (
            "Paramount manages turnkey interior execution and rollout coordination across India, "
            "including civil works, interiors, MEP services, vendor interfaces, and multicity project management."
        )

    if "contact" in text or "phone" in text or "email" in text:
        return (
            "You can reach Paramount at the Mumbai head office on +91 9920479027 "
            "or by email at info@ppepl.co.in, as listed on the website contact section."
        )

    if "locations" in text or "cities" in text or "clients" in text:
        return (
            "Paramount has delivered projects for brands such as Dr Agarwals Eye Hospital, "
            "Burger King, KFC, Croma, McDonalds, Dominos and others across multiple Indian cities. "
            "You can explore the interactive map and directory on the site for more detail."
        )

    # fallback generic answer
    return (
        "Archana here. I may not have full context for that question, "
        "but you can ask me about Paramount's services, rollout capabilities, "
        "client footprint, or how to get in touch."
    )


@app.route("/")
def health():
    return jsonify({"status": "ok", "assistant": "Archana"})


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")

    reply = generate_archana_reply(message)

    return jsonify({
        "assistant_name": "Archana",
        "reply": reply
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
