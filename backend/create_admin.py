from app import create_app, db
from app.models import AdminUser
import os

app = create_app()
app.app_context().push()

def create_admin_user(email, password):
    admin = AdminUser.query.filter_by(email=email).first()
    if admin:
        print(f"Admin user with email {email} already exists.")
    else:
        new_admin = AdminUser(email=email)
        new_admin.set_password(password)
        db.session.add(new_admin)
        db.session.commit()
        print(f"Admin user {email} created successfully.")

if __name__ == '__main__':
    admin_email = os.environ.get('ADMIN_EMAIL') or 'admin@example.com'
    admin_password = os.environ.get('ADMIN_PASSWORD') or 'adminpassword'
    
    create_admin_user(admin_email, admin_password)
