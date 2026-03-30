"""
Salary Calculator Web Application
"""

import os

from dotenv import load_dotenv
from flask import Flask

from routes import auth_bp, employees_bp, salary_bp
from routes.auth import init_login_manager

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "tbrosventures")

init_login_manager(app)
app.register_blueprint(auth_bp)
app.register_blueprint(employees_bp)
app.register_blueprint(salary_bp)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5001)))
