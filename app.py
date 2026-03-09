from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/pricing")
def pricing():
    return render_template("pricing.html")

@app.route("/checkout-pro")
def pro():
    return "<h1>Pro plan coming soon</h1>"

@app.route("/checkout-business")
def business():
    return "<h1>Business plan coming soon</h1>"

if __name__ == "__main__":
    app.run(debug=True)