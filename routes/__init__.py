"""
Flask routes package
"""

from routes.auth import auth_bp
from routes.employees import employees_bp
from routes.salary import salary_bp

__all__ = ["auth_bp", "employees_bp", "salary_bp"]
