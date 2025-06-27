from mainapp import db  # Import the SQLAlchemy database object from the mainapp package
from datetime import date
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)  # Primary key for each user
    username = db.Column(db.String(50), unique=True, nullable=False)  # Username (unique)
    password = db.Column(db.String(255), nullable=False)  # Hashed password
    role = db.Column(db.String(20), nullable=False)  # User role (Admin, Manager, etc.)

    def __repr__(self):
        return f"<User {self.username}>"
    

# Define the Property model for managing individual properties
class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key for the Property table
    name = db.Column(db.String(100))              # Property name
    address = db.Column(db.String(200))           # Full address of the property
    property_type = db.Column(db.String(50))      # Type: Home or Commercial
    size_sqft = db.Column(db.Integer)             # Size in square feet
    amenities = db.Column(db.String(300))         # Comma-separated list of amenities


# Define the Tenant model for managing tenant information
class Tenant(db.Model):
    id = db.Column(db.Integer, primary_key=True)         # Primary key for the Tenant table
    name = db.Column(db.String(100), nullable=False)                     # Tenant's name
    contact = db.Column(db.String(20), nullable=False)                  # Contact details (phone or email)
    business_type = db.Column(db.String(100), nullable=True)            # Business type (for commercial tenants)
    lease_start = db.Column(db.Date, nullable=True)               # Lease start date
    lease_end = db.Column(db.Date, nullable=True)                 # Lease end date
    rent = db.Column(db.Float, nullable=False)                           # Monthly rent amount
    deposit = db.Column(db.Float, nullable=True)                        # Security deposit

    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)  # Foreign key linked to Property
    property = db.relationship("Property", backref="tenants", lazy=True)



# -----------------------------------------------
# Rent model to track rent payments by tenants
# -----------------------------------------------

class Rent(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique ID

    tenant_id = db.Column(db.Integer, db.ForeignKey('tenant.id'), nullable=False)  # Link to tenant

    month = db.Column(db.String(20), nullable=False)  # e.g., "January"
    year = db.Column(db.Integer, nullable=False)
    
    amount_paid = db.Column(db.Float, nullable=False)  # Amount received
    payment_date = db.Column(db.Date, nullable=False, default=date.today)  # Date of rent payment

    remarks = db.Column(db.String(200))  # Optional notes

    tenant = db.relationship('Tenant', backref=db.backref('rents', lazy=True))



