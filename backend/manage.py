from app import create_app, db
from app.models import Business, APIKeys, Transaction, Customer, Wallet, CommissionLedger, AdminUser

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Business': Business, 'APIKeys': APIKeys, 'Transaction': Transaction, 
            'Customer': Customer, 'Wallet': Wallet, 'CommissionLedger': CommissionLedger, 
            'AdminUser': AdminUser}

if __name__ == '__main__':
    app.run()
