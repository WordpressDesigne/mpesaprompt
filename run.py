#!/usr/bin/env python
"""
M-Pesa STK Push SaaS - Main Application Entry Point
"""
import os
from app import create_app, db
from app.models import User, Business, Transaction, Customer, Wallet
from flask_migrate import Migrate

# Create the Flask application instance
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    """Make shell context available in the Flask shell.
    
    This allows you to access these objects directly in the shell.
    """
    return dict(
        app=app,
        db=db,
        User=User,
        Business=Business,
        Transaction=Transaction,
        Customer=Customer,
        Wallet=Wallet
    )

@app.cli.command()
def test():
    ""Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

if __name__ == '__main__':
    # Run the Flask development server
    app.run(host='0.0.0.0', port=5000, debug=True)
