from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright

app = Flask(__name__)

@app.route("/")
def home():
    return "Playwright bot running"

@app.route("/task", methods=["POST"])
def run_task():
    data = request.json
    url = data.get("url")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)

        title = page.title()

        browser.close()

    return jsonify({
        "status": "success",
        "title": title
    })
