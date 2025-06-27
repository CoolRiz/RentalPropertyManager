
from flask import Blueprint, render_template, request, redirect, url_for, flash  # Import necessary Flask modules
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from mainapp.models import User
from mainapp import db   # Import Flask app and database instance
from mainapp.models import Property, Tenant, Rent  # Import models
from datetime import datetime
from flask import send_file
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime, timedelta
from flask_login import current_user


app_routes = Blueprint('app_routes', __name__)

@app_routes.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("app_routes.dashboard"))
    return redirect(url_for("app_routes.login"))


# Route for the home page (optional — can be updated to show dashboard)
@app_routes.route("/")
@login_required
def home():    
    return render_template("home.html")  # Load a template (can be replaced with dashboard)


# Login route to show login form and authenticate user
@app_routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)  # Log the user in
            flash("Login successful!")
            return redirect(url_for("app_routes.dashboard"))
        else:
            flash("Invalid username or password.")
    return render_template("login.html")

# Logout route to log out the current user
@app_routes.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("login"))

# Protect dashboard route
@app_routes.route("/dashboard")
@login_required
def dashboard():
    # Your dashboard logic here
    return render_template("dashboard.html")


# --------------------
# Add Property Route
# --------------------

@app_routes.route("/add-property", methods=["GET", "POST"])
@login_required
def add_property():
    if request.method == "POST":
        # Extract form data submitted by user
        name = request.form["name"]
        address = request.form["address"]
        property_type = request.form["property_type"]
        size_sqft = request.form["size_sqft"]
        amenities = request.form["amenities"]

        # Create new property object
        prop = Property(
            name=name,
            address=address,
            property_type=property_type,
            size_sqft=size_sqft,
            amenities=amenities
        )

        # Save to database
        db.session.add(prop)
        db.session.commit()
        flash("Property added successfully!")  # Show success message
        return redirect(url_for("home"))  # Redirect to home page

    return render_template("add_property.html")  # Show the add property form

# --------------------
# Add Tenant Route
# --------------------


@app_routes.route("/add-tenant", methods=["GET", "POST"])
@login_required
def add_tenant():
    properties = Property.query.all()  # Fetch all properties to populate the dropdown
    if request.method == "POST":
        # Create a new Tenant object with form data
        tenant = Tenant(
            name=request.form["name"],
            contact=request.form["contact"],
            business_type=request.form["business_type"],

            lease_start=datetime.strptime(request.form["lease_start"], "%Y-%m-%d").date(),
            lease_end=datetime.strptime(request.form["lease_end"], "%Y-%m-%d").date(),
#           lease_start=request.form["lease_start"],
#           lease_end=request.form["lease_end"],
            rent=request.form["rent"],
            deposit=request.form["deposit"],
            property_id=request.form["property_id"]  # Link to selected property
        )

        db.session.add(tenant)  # Add the tenant to the session
        db.session.commit()  # Save changes to the database
        flash("Tenant added successfully!")  # Flash success message
        return redirect(url_for("list_tenants"))  # Redirect to tenant listing
    return render_template("add_tenant.html", properties=properties)  # Show the form

# --------------------
# List All Tenants Route
# --------------------

@app_routes.route("/tenants")
@login_required
def list_tenants():
    tenants = Tenant.query.all()  # Fetch all tenants from the database
    return render_template("tenants.html", tenants=tenants)  # Render the list



# --------------------
# Route to view all properties
# --------------------
@app_routes.route("/properties")
@login_required
def list_properties():
    properties = Property.query.all()  # Fetch all properties from the database
    return render_template("properties.html", properties=properties)  # Pass the list to the template

# --------------------
# Edit Tenant Route
# --------------------
@app_routes.route("/edit-tenant/<int:tenant_id>", methods=["GET", "POST"])
@login_required
def edit_tenant(tenant_id):
    tenant_obj = Tenant.query.get_or_404(tenant_id)  # Fetch tenent or return 404 if not found
    properties = Property.query.all()  # Fetch all properties for dropdown
    
    if request.method == "POST":
        # Update tenant fields from form
        tenant_obj.name = request.form["name"]
        tenant_obj.contact = request.form["contact"]
        tenant_obj.business_type = request.form["business_type"]

        tenant_obj.lease_start = datetime.strptime(request.form["lease_start"], "%Y-%m-%d").date(),
        tenant_obj.lease_end = datetime.strptime(request.form["lease_end"], "%Y-%m-%d").date(),

#        tenant_obj.lease_start = request.form["lease_start"]
#        tenant_obj.lease_end = request.form["lease_end"]

        tenant_obj.rent = request.form["rent"]
        tenant_obj.deposit = request.form["deposit"]
        tenant_obj.property_id = request.form["property_id"]

        db.session.commit()  # Save changes to DB
        flash("Tenant updated successfully!")
        return redirect(url_for("list_tenants"))  # Redirect to list

    return render_template("edit_tenant.html", tenant=tenant_obj, properties=properties)  # Show edit form

# --------------------
# Edit Property Route
# --------------------
@app_routes.route("/edit-property/<int:property_id>", methods=["GET", "POST"])
@login_required
def edit_property(property_id):
    property_obj = Property.query.get_or_404(property_id)  # Fetch property or return 404 if not found

    if request.method == "POST":
        # Update property fields from form
        property_obj.name = request.form["name"]
        property_obj.address = request.form["address"]
        property_obj.property_type = request.form["property_type"]
        property_obj.size_sqft = request.form["size_sqft"]
        property_obj.amenities = request.form["amenities"]

        db.session.commit()  # Save changes to DB
        flash("Property updated successfully!")
        return redirect(url_for("list_properties"))  # Redirect to list

    return render_template("edit_property.html", property=property_obj)  # Show edit form


# --------------------
# Delete Property Route
# --------------------
@app_routes.route("/delete-property/<int:property_id>", methods=["POST"])
@login_required
def delete_property(property_id):
    property_obj = Property.query.get_or_404(property_id)  # Fetch property or 404
    db.session.delete(property_obj)  # Delete from DB
    db.session.commit()
    flash("Property deleted successfully!")
    return redirect(url_for("list_properties"))  # Go back to list

# --------------------
# Delete Tenant Route
# --------------------
@app_routes.route("/delete-tenant/<int:tenant_id>", methods=["POST"])
@login_required
def delete_tenant(tenant_id):
    tenant_obj = Tenant.query.get_or_404(tenant_id)
    db.session.delete(tenant_obj)
    db.session.commit()
    flash("Tenant deleted successfully!")
    return redirect(url_for("list_tenants"))


# --------------------
# Add Rent Payment Route
# --------------------
@app_routes.route("/add-rent", methods=["GET", "POST"])
@login_required
def add_rent():
    tenants = Tenant.query.all()  # Get all tenants for dropdown

    if request.method == "POST":
        try:
            # Convert payment_date string into a Python date object
            payment_date = datetime.strptime(request.form["payment_date"], "%Y-%m-%d").date()

            # Create new Rent object with submitted form data
            rent = Rent(
                tenant_id=request.form["tenant_id"],
                month=request.form["month"],
                year=request.form["year"],
                amount_paid=request.form["amount"],
                payment_date=payment_date,
                remarks=request.form.get("remarks")  # Optional field
            )

            # Add and commit the rent record to the database
            db.session.add(rent)
            db.session.commit()

            flash("Rent entry added successfully!")  # Show success message
            return redirect(url_for("list_rents"))

        except Exception as e:
            flash(f"Error saving rent: {e}")  # Show error message

    current_year = datetime.now().year  # Get current year
    return render_template("add_rent.html", tenants=tenants, current_year=current_year)  # Render the rent form

# --------------------
# List Rent Records Route
# --------------------
@app_routes.route("/rents")
@login_required
def list_rents():
    rents = Rent.query.all()  # Fetch all rent records
    return render_template("rents.html", rents=rents)  # Show rent records

# --------------------
# Debug/Test Template Route
# --------------------
@app_routes.route("/test")
def test_template():
    return render_template("test.html")  # Used to check template rendering


# --------------------
# Edit Rent Payment Route
# --------------------
@app_routes.route("/edit-rent/<int:rent_id>", methods=["GET", "POST"])
@login_required
def edit_rent(rent_id):
    rent = Rent.query.get_or_404(rent_id)  # Fetch the rent record by ID or return 404
    tenants = Tenant.query.all()  # Fetch tenants to populate dropdown

    if request.method == "POST":
        try:
            # Update the rent record with form values
            rent.tenant_id = request.form["tenant_id"]
            rent.month = request.form["month"]
            rent.year = request.form["year"]
            rent.amount_paid = request.form["amount_paid"]
            rent.payment_date = datetime.strptime(request.form["payment_date"], "%Y-%m-%d").date()
            rent.remarks = request.form.get("remarks")

            db.session.commit()  # Save changes to DB
            flash("Rent record updated successfully!")
            return redirect(url_for("list_rents"))

        except Exception as e:
            flash(f"Error updating rent record: {e}")

    # Render the edit rent form with current values
    return render_template("edit_rent.html", rent=rent, tenants=tenants)



# -------------------------
# Delete Rent Entry Route
# -------------------------
@app_routes.route("/delete-rent/<int:rent_id>", methods=["POST"])
@login_required
def delete_rent(rent_id):
    rent = Rent.query.get_or_404(rent_id)  # Find rent entry or return 404
    try:
        db.session.delete(rent)
        db.session.commit()
        flash("Rent entry deleted successfully!")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting rent entry: {e}")
    return redirect(url_for("list_rents"))


@app_routes.route("/rent-summary", methods=["GET", "POST"])
@login_required
def rent_summary():
    tenants = Tenant.query.all()
    rents = Rent.query

    # Fetch filter values from form
    selected_month = request.form.get("month")
    selected_year = request.form.get("year")
    selected_tenant = request.form.get("tenant_id")

    # Apply filters if submitted
    if request.method == "POST":
        if selected_month:
            rents = rents.filter_by(month=selected_month)
        if selected_year:
            rents = rents.filter_by(year=selected_year)
        if selected_tenant:
            rents = rents.filter_by(tenant_id=selected_tenant)

    rents = rents.all()
    total_amount = sum([r.amount_paid for r in rents])

    return render_template("rent_summary.html", tenants=tenants, rents=rents,
                           selected_month=selected_month,
                           selected_year=selected_year,
                           selected_tenant=selected_tenant,
                           total_amount=total_amount)

# --------------------
# Route: Export Rent Summary to PDF
# --------------------
@app_routes.route("/export-rent-summary", methods=["GET"])
@login_required
def export_rent_summary_pdf():
    rents = Rent.query
    if request.form.get("month"):
        rents = rents.filter_by(month=request.form.get("month"))
    if request.form.get("year"):
        rents = rents.filter_by(year=request.form.get("year"))
    if request.form.get("tenant_id"):
        rents = rents.filter_by(tenant_id=request.form.get("tenant_id"))

    rents = rents.all()

    # Create PDF
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle("Rent Summary Report")

    pdf.drawString(30, 750, "Rent Summary Report")
    y = 720
    pdf.drawString(30, y, "Tenant")
    pdf.drawString(150, y, "Month")
    pdf.drawString(210, y, "Year")
    pdf.drawString(270, y, "Amount")
    pdf.drawString(340, y, "Paid On")
    y -= 20

    for r in rents:
        pdf.drawString(30, y, r.tenant.name)
        pdf.drawString(150, y, r.month)
        pdf.drawString(210, y, str(r.year))
        pdf.drawString(270, y, str(r.amount_paid))
        pdf.drawString(340, y, r.payment_date.strftime("%Y-%m-%d"))
        y -= 20
        if y < 50:
            pdf.showPage()
            y = 750

    pdf.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="Rent_Summary_Report.pdf", mimetype="application/pdf")
"""
@app_routes.route("/dashboard")
def dashboard():
    total_properties = Property.query.count()
    total_tenants = Tenant.query.count()

    # Get current month/year
    now = datetime.now()
    current_month = now.month
    current_year = now.year

    # Total rent collected this month
    rents_this_month = Rent.query.filter_by(month=current_month, year=current_year).all()
    total_rent_collected = sum(r.amount_paid for r in rents_this_month)

    # Tenants with no rent this month
    tenant_ids_paid = [r.tenant_id for r in rents_this_month]
    pending_rent_tenants = Tenant.query.filter(~Tenant.id.in_(tenant_ids_paid)).all()

    # Leases expiring in next 30 days
    upcoming_expiry = datetime.now().date() + timedelta(days=30)
    lease_expiry_soon = Tenant.query.filter(Tenant.lease_end <= upcoming_expiry).all()

    return render_template(
        "dashboard.html",
        total_properties=total_properties,
        total_tenants=total_tenants,
        total_rent_collected=total_rent_collected,
        pending_rent_tenants=pending_rent_tenants,
        lease_expiry_soon=lease_expiry_soon
    )
"""
@app_routes.route('/due-rents')
@login_required
def due_rents():
    current_month = datetime.now().strftime('%B')
    current_year = datetime.now().year

    # Get all tenants
    tenants = Tenant.query.all()

    due_rent_tenants = []

    for tenant in tenants:
        # Check if rent for this tenant for current month/year exists
        rent_paid = Rent.query.filter_by(
            tenant_id=tenant.id,
            month=current_month,
            year=current_year
        ).first()

        if not rent_paid:
            due_rent_tenants.append(tenant)

    return render_template('due_rents.html', tenants=due_rent_tenants,
                           current_month=current_month, current_year=current_year)


@app_routes.route('/lease-expiry-alerts')
@login_required
def lease_expiry_alerts():
    today = datetime.now().date()
    upcoming_expiry = today + timedelta(days=30)

    # Query tenants whose lease_end is within next 30 days
    tenants_expiring = Tenant.query.filter(
        Tenant.lease_end >= today,
        Tenant.lease_end <= upcoming_expiry
    ).all()

    return render_template('lease_expiry_alerts.html', tenants=tenants_expiring,
                           today=today, upcoming_expiry=upcoming_expiry)



