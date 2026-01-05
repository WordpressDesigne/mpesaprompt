import os
import sys
import click
sys.path.append(os.path.dirname(__file__))
from app import create_app, db
from app.models import Business, APIKeys, Transaction, Customer, Wallet, CommissionLedger, AdminUser

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Business': Business, 'APIKeys': APIKeys, 'Transaction': Transaction, 
            'Customer': Customer, 'Wallet': Wallet, 'CommissionLedger': CommissionLedger, 
            'AdminUser': AdminUser}

@app.cli.command("init-db")
def init_db_command():
    """Creates the admin user from environment variables."""
    admin_email = os.environ.get('ADMIN_EMAIL') or 'admin@example.com'
    admin_password = os.environ.get('ADMIN_PASSWORD') or 'adminpassword'
    
    admin = AdminUser.query.filter_by(email=admin_email).first()
    if not admin:
        new_admin = AdminUser(email=admin_email)
        new_admin.set_password(admin_password)
        db.session.add(new_admin)
        db.session.commit()
        click.echo(f"Admin user {admin_email} created successfully.")
    else:
        click.echo(f"Admin user {admin_email} already exists.")

if __name__ == '__main__':
    app.run()
