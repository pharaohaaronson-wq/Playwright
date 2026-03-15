from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright

app = Flask(__name__)

def run_task(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(url)

        title = page.title()

        browser.close()

        return title


@app.route("/")
def home():
    return "Automation bot running"


@app.route("/run", methods=["POST"])
def run():
    data = request.json
    url = data.get("url")

    result = run_task(url)

    return jsonify({
        "status": "success",
        "result": result
    })


@app.route("/ping")
def ping():
    return "pong"
