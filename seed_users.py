from mainapp import db
from mainapp.models import User
from werkzeug.security import generate_password_hash

def add_user_if_not_exists(username, password, role):
    if not User.query.filter_by(username=username).first():
        user = User(username=username, password=generate_password_hash(password), role=role)
        db.session.add(user)

add_user_if_not_exists('admin', 'admin123', 'admin')
add_user_if_not_exists('viewer', 'viewer123', 'viewer')

db.session.commit()
print("Users created if they didn't already exist.")
