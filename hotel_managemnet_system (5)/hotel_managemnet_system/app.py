import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session # type: ignore
from flask_sqlalchemy import SQLAlchemy # type: ignore
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user # type: ignore
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash # type: ignore
import json
from sqlalchemy import inspect # type: ignore
from decimal import Decimal

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hotelmanagement123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Khamlesh%401234@localhost/HotelManagementNew'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models based on SQL schema
class RoomType(db.Model):
    __tablename__ = 'Room_Type'
    Room_Type_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Type_Name = db.Column(db.String(50), nullable=False)
    Description = db.Column(db.Text)
    Base_Price = db.Column(db.Numeric(10, 2), nullable=False)
    Max_Occupancy = db.Column(db.Integer, nullable=False)
    Bed_Type = db.Column(db.String(50))
    Extra_Bed_Charge = db.Column(db.Numeric(10, 2), default=0.00)
    rooms = db.relationship('Room', backref='room_type', lazy=True)
    amenities = db.relationship('Amenity', backref='room_type', lazy=True)

class Amenity(db.Model):
    __tablename__ = 'Amenities'
    Amenity_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Amenity_Name = db.Column(db.String(100))
    Description = db.Column(db.Text)
    Availability_Status = db.Column(db.Enum('Available', 'Unavailable'))
    Cost = db.Column(db.Numeric(10, 2))
    Room_Type_ID = db.Column(db.Integer, db.ForeignKey('Room_Type.Room_Type_ID'))
    Last_Maintenance_Date = db.Column(db.Date)

class Room(db.Model):
    __tablename__ = 'Rooms'
    Room_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Room_Number = db.Column(db.String(10), unique=True, nullable=False)
    Room_Type_ID = db.Column(db.Integer, db.ForeignKey('Room_Type.Room_Type_ID'), nullable=False)
    Status = db.Column(db.Enum('Available', 'Occupied', 'Maintenance'), default='Available')
    Price_Per_Night = db.Column(db.Numeric(10, 2), nullable=False)
    Floor_Number = db.Column(db.Integer)
    Capacity = db.Column(db.Integer, nullable=False)
    reservations = db.relationship('Reservation', backref='room', lazy=True)
    bookings = db.relationship('Booking', backref='room', lazy=True)
    maintenance = db.relationship('Maintenance', backref='room', lazy=True)

class Customer(db.Model, UserMixin):
    __tablename__ = 'Customer'
    Customer_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    First_Name = db.Column(db.String(50), nullable=False)
    Last_Name = db.Column(db.String(50), nullable=False)
    Contact_Number = db.Column(db.String(15), nullable=False)
    Email = db.Column(db.String(100), unique=True)
    Address = db.Column(db.Text)
    Membership_Status = db.Column(db.String(20), default='Regular')
    Password = db.Column(db.String(255))  # Added for user authentication
    reservations = db.relationship('Reservation', backref='customer', lazy=True)
    bookings = db.relationship('Booking', backref='customer', lazy=True)
    feedback = db.relationship('Feedback', backref='customer', lazy=True)
    event_bookings = db.relationship('EventBooking', backref='customer', lazy=True)
    
    def get_id(self):
        return str(self.Customer_ID)

class Reservation(db.Model):
    __tablename__ = 'Reservation'
    Reservation_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Customer_ID = db.Column(db.Integer, db.ForeignKey('Customer.Customer_ID'), nullable=False)
    Room_ID = db.Column(db.Integer, db.ForeignKey('Rooms.Room_ID'), nullable=True)
    Check_In_Date = db.Column(db.Date, nullable=False)
    Check_Out_Date = db.Column(db.Date, nullable=False)
    Total_Cost = db.Column(db.Numeric(10, 2), nullable=False)
    Status = db.Column(db.Enum('Confirmed', 'Canceled', 'Pending'), default='Pending')
    payments = db.relationship('Payment', backref='reservation', lazy=True)
    feedback = db.relationship('Feedback', backref='reservation', lazy=True)

class Payment(db.Model):
    __tablename__ = 'Payment'
    Payment_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Reservation_ID = db.Column(db.Integer, db.ForeignKey('Reservation.Reservation_ID'), nullable=False)
    Payment_Method = db.Column(db.String(50), nullable=False)
    Amount = db.Column(db.Numeric(10, 2), nullable=False)
    Payment_Date = db.Column(db.Date, nullable=False)
    Transaction_Status = db.Column(db.Enum('Successful', 'Failed', 'Pending'), default='Pending')
    Discount_Applied = db.Column(db.Numeric(10, 2), default=0.00)

class Discount(db.Model):
    __tablename__ = 'Discount'
    Discount_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Discount_Code = db.Column(db.String(50), unique=True, nullable=False)
    Description = db.Column(db.Text)
    Discount_Percentage = db.Column(db.Numeric(5, 2), nullable=False)
    Valid_From = db.Column(db.Date, nullable=False)
    Valid_Until = db.Column(db.Date, nullable=False)

class Booking(db.Model):
    __tablename__ = 'Booking'
    Booking_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Customer_ID = db.Column(db.Integer, db.ForeignKey('Customer.Customer_ID'), nullable=False)
    Room_ID = db.Column(db.Integer, db.ForeignKey('Rooms.Room_ID'), nullable=False)
    Booking_Date = db.Column(db.Date, nullable=False)
    Check_In_Date = db.Column(db.Date, nullable=False)
    Check_Out_Date = db.Column(db.Date, nullable=False)
    Booking_Status = db.Column(db.Enum('Confirmed', 'Canceled', 'Pending'), default='Pending')

class Department(db.Model):
    __tablename__ = 'Department'
    Department_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Department_Name = db.Column(db.String(100), nullable=False)
    Contact_Number = db.Column(db.String(15))
    Email = db.Column(db.String(100), unique=True)
    Number_of_Employees = db.Column(db.Integer, default=0)
    Location = db.Column(db.Text)
    staff = db.relationship('Staff', backref='department', lazy=True)

class Staff(db.Model):
    __tablename__ = 'Staff'
    Staff_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    First_Name = db.Column(db.String(50), nullable=False)
    Last_Name = db.Column(db.String(50), nullable=False)
    Department_ID = db.Column(db.Integer, db.ForeignKey('Department.Department_ID'))
    Role_Position = db.Column(db.String(100))
    Contact_Number = db.Column(db.String(15))
    Salary = db.Column(db.Numeric(10, 2), nullable=False)
    services = db.relationship('Service', backref='staff', lazy=True)

class Service(db.Model):
    __tablename__ = 'Services'
    Service_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Service_Name = db.Column(db.String(100), nullable=False)
    Description = db.Column(db.Text)
    Price = db.Column(db.Numeric(10, 2), nullable=False)
    Availability_Status = db.Column(db.Enum('Available', 'Unavailable'), default='Available')
    Duration = db.Column(db.Time)
    Staff_In_Charge = db.Column(db.Integer, db.ForeignKey('Staff.Staff_ID'))

class Maintenance(db.Model):
    __tablename__ = 'Maintenance'
    Maintenance_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Room_ID = db.Column(db.Integer, db.ForeignKey('Rooms.Room_ID'), nullable=False)
    Issue_Reported = db.Column(db.Text, nullable=False)
    Report_Date = db.Column(db.DateTime, default=datetime.now)
    Maintenance_Status = db.Column(db.String(20), default='Pending')
    Technician_Assigned = db.Column(db.String(100), nullable=True)
    Repair_Cost = db.Column(db.Numeric(10, 2), nullable=True)

class Event(db.Model):
    __tablename__ = 'Event'
    Event_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Event_Name = db.Column(db.String(100), nullable=False)
    Description = db.Column(db.Text)
    Event_Date = db.Column(db.Date, nullable=False)
    Location = db.Column(db.Text)
    Organizer_ID = db.Column(db.Integer)
    Expected_Guests = db.Column(db.Integer, nullable=False)
    event_bookings = db.relationship('EventBooking', backref='event', lazy=True)

class EventBooking(db.Model):
    __tablename__ = 'Event_Booking'
    Event_Booking_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Event_ID = db.Column(db.Integer, db.ForeignKey('Event.Event_ID'), nullable=False)
    Customer_ID = db.Column(db.Integer, db.ForeignKey('Customer.Customer_ID'), nullable=False)
    Booking_Date = db.Column(db.Date, nullable=False)
    Total_Cost = db.Column(db.Numeric(10, 2), nullable=False)
    Status = db.Column(db.Enum('Confirmed', 'Canceled', 'Pending'), default='Pending')
    Special_Requests = db.Column(db.Text)

class Feedback(db.Model):
    __tablename__ = 'Feedback'
    Feedback_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Customer_ID = db.Column(db.Integer, db.ForeignKey('Customer.Customer_ID'), nullable=False)
    Reservation_ID = db.Column(db.Integer, db.ForeignKey('Reservation.Reservation_ID'), nullable=False)
    Rating = db.Column(db.Integer)
    Comments = db.Column(db.Text)
    Feedback_Date = db.Column(db.Date, nullable=False)
    Staff_Response = db.Column(db.Text)

@login_manager.user_loader
def load_user(user_id):
    return Customer.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    room_types = RoomType.query.all()
    return render_template('index.html', room_types=room_types)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        contact_number = request.form.get('contact_number')
        
        # Check if passwords match
        if password != password_confirm:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register'))
        
        # Check if user exists
        existing_user = Customer.query.filter_by(Email=email).first()
        if existing_user:
            flash('Email already registered. Please login.', 'warning')
            return redirect(url_for('login'))
        
        # Create new user
        hashed_password = generate_password_hash(password, method='pbkdf2')
        new_customer = Customer(
            First_Name=first_name,
            Last_Name=last_name,
            Email=email,
            Password=hashed_password,
            Contact_Number=contact_number
        )
        
        db.session.add(new_customer)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        customer = Customer.query.filter_by(Email=email).first()
        
        if not customer or not check_password_hash(customer.Password, password):
            flash('Please check your login details and try again.', 'danger')
            return redirect(url_for('login'))
            
        login_user(customer)
        flash('Login successful!', 'success')
        return redirect(url_for('dashboard'))
        
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user's room reservations
    reservations = Reservation.query.filter_by(Customer_ID=current_user.Customer_ID).all()
    
    # Get user's event bookings
    event_bookings = EventBooking.query.filter_by(Customer_ID=current_user.Customer_ID).all()
    
    # Enhance event bookings with event details
    for booking in event_bookings:
        booking.event_details = Event.query.get(booking.Event_ID)
    
    today = datetime.now().date()
    return render_template('dashboard.html', 
                          user=current_user, 
                          reservations=reservations, 
                          event_bookings=event_bookings,
                          today=today)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        contact_number = request.form.get('contact_number')
        address = request.form.get('address')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Verify current password
        if not check_password_hash(current_user.Password, current_password):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('edit_profile'))
        
        # Check if email already exists for another user
        if email != current_user.Email:
            existing_user = Customer.query.filter_by(Email=email).first()
            if existing_user and existing_user.Customer_ID != current_user.Customer_ID:
                flash('Email already in use by another account.', 'danger')
                return redirect(url_for('edit_profile'))
        
        # Update user information
        current_user.First_Name = first_name
        current_user.Last_Name = last_name
        current_user.Email = email
        current_user.Contact_Number = contact_number
        current_user.Address = address
        
        # Handle password change if requested
        if new_password:
            if new_password != confirm_password:
                flash('New passwords do not match.', 'danger')
                return redirect(url_for('edit_profile'))
            
            # Update password
            current_user.Password = generate_password_hash(new_password, method='pbkdf2')
            flash('Password updated successfully!', 'success')
        
        try:
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
            return redirect(url_for('edit_profile'))
    
    return render_template('edit_profile.html', user=current_user)

@app.route('/rooms')
def rooms():
    room_types = RoomType.query.all()
    now = datetime.now()
    return render_template('rooms.html', room_types=room_types, now=now)

@app.route('/room_details/<int:room_type_id>')
def room_details(room_type_id):
    room_type = RoomType.query.get_or_404(room_type_id)
    amenities = Amenity.query.filter_by(Room_Type_ID=room_type_id).all()
    available_rooms = Room.query.filter_by(Room_Type_ID=room_type_id, Status='Available').all()
    return render_template('room_details.html', room_type=room_type, amenities=amenities, available_rooms=available_rooms)

@app.route('/book-room/<int:room_id>', methods=['GET', 'POST'])
@login_required
def book_room(room_id):
    room = Room.query.get_or_404(room_id)
    room_type = RoomType.query.get(room.Room_Type_ID)
    
    # Get parameters from URL
    check_in = request.args.get('check_in', '')
    check_out = request.args.get('check_out', '')
    guests = request.args.get('guests', '1')
    discount_code = request.args.get('discount', '')
    
    # Calculate total nights and price
    total_nights = 0
    total_price = 0
    discount_amount = 0
    discount_percentage = 0
    
    if check_in and check_out:
        check_in_date = datetime.strptime(check_in, '%Y-%m-%d')
        check_out_date = datetime.strptime(check_out, '%Y-%m-%d')
        total_nights = (check_out_date - check_in_date).days
        total_price = room_type.Base_Price * total_nights
        
        # Apply discount if provided
        if discount_code:
            discount_code = discount_code.upper()
            is_weekend = has_weekend_stay(check_in_date, check_out_date)
            
            if discount_code == 'SUMMER2023':
                discount_percentage = 15
            elif discount_code == 'WELCOME10':
                discount_percentage = 10
            elif discount_code == 'FAMILY25' and room_type.Type_Name == 'Family':
                discount_percentage = 25
            elif discount_code == 'WEEKEND15' and is_weekend:
                discount_percentage = 15
            elif discount_code == 'EARLYBIRD':
                # Check if booking is at least 30 days in advance
                days_until_checkin = (check_in_date - datetime.now()).days
                if days_until_checkin >= 30:
                    discount_percentage = 20
            elif discount_code == 'LOYALTY20':
                discount_percentage = 20
                
            if discount_percentage > 0:
                discount_amount = total_price * (Decimal(str(discount_percentage)) / Decimal('100'))
                total_price = total_price - discount_amount
    
    if request.method == 'POST':
        try:
            check_in_date = datetime.strptime(request.form.get('check_in_date'), '%Y-%m-%d')
            check_out_date = datetime.strptime(request.form.get('check_out_date'), '%Y-%m-%d')
            
            # Calculate the total price if not already calculated
            if total_nights == 0:
                total_nights = (check_out_date - check_in_date).days
                total_price = room.Price_Per_Night * total_nights
                
                # Apply discount if present in the form
                discount_code = request.form.get('discount_code', '')
                if discount_code:
                    discount_code = discount_code.upper()
                    is_weekend = has_weekend_stay(check_in_date, check_out_date)
                    
                    if discount_code == 'SUMMER2023':
                        discount_percentage = 15
                    elif discount_code == 'WELCOME10':
                        discount_percentage = 10
                    elif discount_code == 'FAMILY25' and room.room_type.Type_Name == 'Family':
                        discount_percentage = 25
                    elif discount_code == 'WEEKEND15' and is_weekend:
                        discount_percentage = 15
                    elif discount_code == 'EARLYBIRD':
                        # Check if booking is at least 30 days in advance
                        days_until_checkin = (check_in_date - datetime.now()).days
                        if days_until_checkin >= 30:
                            discount_percentage = 20
                    elif discount_code == 'LOYALTY20':
                        discount_percentage = 20
                    
                    if discount_percentage > 0:
                        discount_amount = total_price * (Decimal(str(discount_percentage)) / Decimal('100'))
                        total_price = total_price - discount_amount
                
                # Add taxes (10%)
                tax_amount = total_price * Decimal('0.10')
                total_price += tax_amount
            
            # Process booking
            booking = Booking(
                Room_ID=room.Room_ID,
                Customer_ID=current_user.Customer_ID,
                Booking_Date=datetime.now().date(),
                Check_In_Date=check_in_date,
                Check_Out_Date=check_out_date,
                Booking_Status='Pending'  # Set to Pending until payment is completed
            )
            
            # Create a reservation record
            reservation = Reservation(
                Customer_ID=current_user.Customer_ID,
                Room_ID=room.Room_ID,
                Check_In_Date=check_in_date,
                Check_Out_Date=check_out_date,
                Total_Cost=total_price,
                Status='Pending'  # Set to Pending until payment is completed
            )
            
            # Save booking and reservation to database
            db.session.add(booking)
            db.session.add(reservation)
            db.session.commit()
            
            flash('Room reserved! Please complete your payment.', 'success')
            return redirect(url_for('payment', reservation_id=reservation.Reservation_ID))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
            print(f"Error in booking: {str(e)}")
    
    return render_template('book_room.html', 
                          room=room, 
                          room_type=room_type,
                          check_in=check_in,
                          check_out=check_out,
                          guests=guests,
                          total_nights=total_nights,
                          total_price=total_price,
                          discount_code=discount_code,
                          discount_amount=discount_amount,
                          discount_percentage=discount_percentage)

# Helper function to check if stay includes a weekend
def has_weekend_stay(check_in, check_out):
    current_date = check_in
    while current_date < check_out:
        if current_date.weekday() >= 5:  # 5, 6 are Saturday and Sunday
            return True
        current_date += timedelta(days=1)
    return False

@app.route('/payment/<int:reservation_id>', methods=['GET', 'POST'])
@login_required
def payment(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    
    # Make sure the reservation belongs to the current user
    if reservation.Customer_ID != current_user.Customer_ID:
        flash('You do not have permission to access this reservation.', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        payment_method = request.form.get('payment_method')
        
        # Create payment record
        new_payment = Payment(
            Reservation_ID=reservation_id,
            Payment_Method=payment_method,
            Amount=reservation.Total_Cost,
            Payment_Date=datetime.now().date(),
            Transaction_Status='Successful'
        )
        
        # Update reservation status
        reservation.Status = 'Confirmed'
        
        # Update booking status as well
        booking = Booking.query.filter_by(
            Customer_ID=current_user.Customer_ID,
            Room_ID=reservation.Room_ID,
            Check_In_Date=reservation.Check_In_Date,
            Check_Out_Date=reservation.Check_Out_Date
        ).first()
        
        if booking:
            booking.Booking_Status = 'Confirmed'
        
        # Update room status
        room = Room.query.get(reservation.Room_ID)
        if room:
            room.Status = 'Occupied'
        
        # Commit all changes to database
        try:
            db.session.add(new_payment)
            db.session.commit()
            
            # Handle AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True})
            
            flash(f'Payment successful! Your reservation is confirmed. Reservation ID: #{reservation_id}', 'success')
            return redirect(url_for('payment_success', reservation_id=reservation_id))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
            
            # Handle AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': str(e)})
            
            return redirect(url_for('payment', reservation_id=reservation_id))
    
    # Get today's date to set min date for datepickers
    today = datetime.now().date()
    
    return render_template('payment.html', reservation=reservation, today=today)

@app.route('/payment_success/<int:reservation_id>')
@login_required
def payment_success(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    
    # Make sure the reservation belongs to the current user
    if reservation.Customer_ID != current_user.Customer_ID:
        flash('You do not have permission to access this reservation.', 'danger')
        return redirect(url_for('dashboard'))
    
    return render_template('payment_success.html', reservation=reservation, user=current_user)

@app.route('/submit_feedback/<int:reservation_id>', methods=['GET', 'POST'])
@login_required
def submit_feedback(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    
    if request.method == 'POST':
        rating = int(request.form.get('rating'))
        comments = request.form.get('comments')
        
        new_feedback = Feedback(
            Customer_ID=current_user.Customer_ID,
            Reservation_ID=reservation_id,
            Rating=rating,
            Comments=comments,
            Feedback_Date=datetime.now().date()
        )
        
        db.session.add(new_feedback)
        db.session.commit()
        
        flash('Thank you for your feedback!')
        return redirect(url_for('dashboard'))
    
    return render_template('feedback.html', reservation=reservation)

@app.route('/services')
@login_required
def services():
    all_services = Service.query.filter_by(Availability_Status='Available').all()
    now = datetime.now()
    return render_template('services.html', services=all_services, now=now)

@app.route('/events')
@login_required
def events():
    upcoming_events = Event.query.filter(Event.Event_Date >= datetime.now().date()).all()
    
    # If no upcoming events found, create sample events and save them to the database
    if not upcoming_events:
        today = datetime.now().date()
        sample_events = [
            Event(
                Event_Name='Wine Tasting', 
                Description='Join our sommelier for an evening of exquisite wine tasting featuring premium selections from around the world.',
                Event_Date=today + timedelta(days=7), 
                Location='Hotel Wine Cellar',
                Organizer_ID=1,
                Expected_Guests=30
            ),
            Event(
                Event_Name='Live Music', 
                Description='Enjoy a night of soulful live music with renowned local artists and a special guest performance.',
                Event_Date=today + timedelta(days=14), 
                Location='Main Ballroom',
                Organizer_ID=1,
                Expected_Guests=80
            ),
            Event(
                Event_Name='Cooking Class', 
                Description='Learn to prepare authentic local dishes with our master chef in this interactive cooking session.',
                Event_Date=today + timedelta(days=3), 
                Location='Hotel Kitchen',
                Organizer_ID=1,
                Expected_Guests=20
            ),
            Event(
                Event_Name='Yoga Session', 
                Description='Relax and rejuvenate with our professional yoga instructor in a peaceful poolside setting.',
                Event_Date=today + timedelta(days=10), 
                Location='Pool Deck',
                Organizer_ID=1,
                Expected_Guests=25
            ),
            Event(
                Event_Name='Cultural Dance Night', 
                Description='Experience the rich cultural heritage through traditional dance performances and music.',
                Event_Date=today + timedelta(days=21), 
                Location='Garden Pavilion',
                Organizer_ID=1,
                Expected_Guests=50
            )
        ]
        
        # Save the sample events to the database
        try:
            db.session.add_all(sample_events)
            db.session.commit()
            # Query again to get the events with proper IDs
            upcoming_events = Event.query.filter(Event.Event_Date >= datetime.now().date()).all()
        except Exception as e:
            db.session.rollback()
            print(f"Error adding sample events: {e}")
    
    now = datetime.now()
    return render_template('events.html', events=upcoming_events, now=now)

@app.route('/cancel_reservation/<int:reservation_id>', methods=['POST'])
@login_required
def cancel_reservation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    
    # Make sure the reservation belongs to the current user
    if reservation.Customer_ID != current_user.Customer_ID:
        flash('You do not have permission to cancel this reservation.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Check if reservation is already canceled
    if reservation.Status == 'Canceled':
        flash('This reservation has already been canceled.', 'warning')
        return redirect(url_for('dashboard'))
    
    # Update reservation status
    reservation.Status = 'Canceled'
    
    # Update corresponding booking record
    booking = Booking.query.filter_by(
        Customer_ID=current_user.Customer_ID,
        Room_ID=reservation.Room_ID,
        Check_In_Date=reservation.Check_In_Date,
        Check_Out_Date=reservation.Check_Out_Date
    ).first()
    
    if booking:
        booking.Booking_Status = 'Canceled'
    
    # Update room status back to available if cancellation is made before check-in
    today = datetime.now().date()
    if today < reservation.Check_In_Date:
        room = Room.query.get(reservation.Room_ID)
        if room and room.Status == 'Occupied':
            room.Status = 'Available'
    
    # Commit changes to database
    try:
        db.session.commit()
        flash('Your reservation has been canceled successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
    
    return redirect(url_for('dashboard'))

@app.route('/cancel_event_booking/<int:booking_id>', methods=['POST'])
@login_required
def cancel_event_booking(booking_id):
    event_booking = EventBooking.query.get_or_404(booking_id)
    
    # Make sure the booking belongs to the current user
    if event_booking.Customer_ID != current_user.Customer_ID:
        flash('You do not have permission to cancel this event booking.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Check if booking is already canceled
    if event_booking.Status == 'Canceled':
        flash('This event booking has already been canceled.', 'warning')
        return redirect(url_for('dashboard'))
    
    # Check cancellation policy - 48 hours before event
    event = Event.query.get(event_booking.Event_ID)
    today = datetime.now().date()
    
    if event and (event.Event_Date - today).days < 2:
        flash('Cancellation within 48 hours of the event may incur charges as per our policy.', 'warning')
    
    # Update booking status
    event_booking.Status = 'Canceled'
    
    # Commit changes to database
    try:
        db.session.commit()
        flash('Your event booking has been canceled successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
    
    return redirect(url_for('dashboard'))

@app.route('/book_event/<int:event_id>', methods=['GET', 'POST'])
@login_required
def book_event(event_id):
    try:
        # Get the event from the database
        event = Event.query.get_or_404(event_id)
        
        # Define event prices based on event type
        event_prices = {
            'Wine Tasting': 1500.00,
            'Live Music': 1000.00,
            'Cooking Class': 2000.00,
            'Yoga Session': 800.00,
            'Cultural Dance Night': 1200.00,
            'Cocktail Masterclass': 1800.00,
            'Movie Night Under Stars': 500.00,
            'Art Exhibition': 300.00,
            'Gourmet Food Festival': 2500.00,
            'Salsa Dancing Night': 1200.00
        }
        
        # Get the event price or use a default price of 1000
        event_price = event_prices.get(event.Event_Name, 1000.00)
        
        if request.method == 'POST':
            try:
                # Get form data
                num_attendees = int(request.form.get('num_attendees', 1))
                special_requests = request.form.get('special_requests', '')
                discount_code = request.form.get('discount_code', '').upper()
                payment_method = request.form.get('payment_method')
                
                # Calculate base cost
                base_cost = event_price * num_attendees
                
                # Apply discount if valid
                discount_amount = 0
                if discount_code:
                    if discount_code == 'EVENT20':
                        discount_amount = base_cost * Decimal('0.20')
                    elif discount_code == 'WELCOME10':
                        discount_amount = base_cost * Decimal('0.10')
                    elif discount_code == 'LOYALTY15':
                        discount_amount = base_cost * Decimal('0.15')
                    elif discount_code == 'GROUP30' and num_attendees >= 5:
                        discount_amount = base_cost * Decimal('0.30')
                        
                # Calculate final cost with taxes
                tax_amount = base_cost * Decimal('0.10')
                total_cost = base_cost + tax_amount - discount_amount
                
                # Create event booking
                new_event_booking = EventBooking(
                    Event_ID=event_id,
                    Customer_ID=current_user.Customer_ID,
                    Booking_Date=datetime.now().date(),
                    Total_Cost=total_cost,
                    Status='Confirmed',
                    Special_Requests=special_requests
                )
                
                db.session.add(new_event_booking)
                db.session.commit()
                
                # Flash success message with booking ID
                flash(f'Event booked successfully! Your booking ID is #{new_event_booking.Event_Booking_ID}', 'success')
                
                # Store the booking ID in session for access in the success page
                session['last_event_booking_id'] = new_event_booking.Event_Booking_ID
                
                # Redirect to the event booking success page
                return redirect(url_for('event_booking_success', event_booking_id=new_event_booking.Event_Booking_ID))
            except Exception as e:
                db.session.rollback()
                flash(f'An error occurred while booking the event: {str(e)}', 'danger')
                print(f"Error booking event: {e}")
                # Still render the booking page with the event data
                return render_template('event_booking.html', event=event, event_price=event_price, error=str(e))
        
        # GET request - show the booking form
        return render_template('event_booking.html', event=event, event_price=event_price)
    
    except Exception as e:
        # Handle any errors accessing the event
        print(f"Error accessing event {event_id}: {e}")
        flash(f'Could not load the event details: {str(e)}', 'danger')
        return redirect(url_for('events'))

@app.route('/event_booking_success/<int:event_booking_id>')
@login_required
def event_booking_success(event_booking_id):
    # Get the event booking
    event_booking = EventBooking.query.get_or_404(event_booking_id)
    
    # Make sure the booking belongs to the current user
    if event_booking.Customer_ID != current_user.Customer_ID:
        flash('You do not have permission to access this booking.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get the event details
    event = Event.query.get(event_booking.Event_ID)
    
    return render_template('event_booking_success.html', 
                          event_booking=event_booking, 
                          event=event, 
                          user=current_user)

@app.route('/contact')
def contact():
    departments = Department.query.all()
    now = datetime.now()
    return render_template('contact.html', departments=departments, now=now)

@app.route('/about')
def about():
    return render_template('about.html')

# API endpoints for AJAX requests
@app.route('/api/check_availability', methods=['POST'])
def check_availability():
    data = request.json
    room_type_id = data.get('room_type_id')
    check_in = datetime.strptime(data.get('check_in'), '%Y-%m-%d').date()
    check_out = datetime.strptime(data.get('check_out'), '%Y-%m-%d').date()
    
    # Find all rooms of the specified type
    all_rooms = Room.query.filter_by(Room_Type_ID=room_type_id).all()
    
    # Get the current date to check for expired bookings
    current_date = datetime.now().date()
    
    # Sort rooms into categories (available, booked, pending)
    available_room_data = []
    booked_room_data = []
    pending_room_data = []
    
    for room in all_rooms:
        # Get all reservations for this room
        room_reservations = Reservation.query.filter_by(Room_ID=room.Room_ID).filter(
            Reservation.Status != 'Canceled'
        ).all()
        
        # Check if there are expired reservations that need to be cleared
        expired_reservations = [res for res in room_reservations if res.Check_Out_Date < current_date]
        for expired in expired_reservations:
            # Mark expired reservation as completed or update status as needed
            if expired.Status != 'Completed':
                expired.Status = 'Completed'
        
        # If room status is occupied but all reservations are expired, make it available again
        if room.Status == 'Occupied' and all(res.Check_Out_Date < current_date for res in room_reservations if res.Status != 'Canceled'):
            room.Status = 'Available'
            
        # Check if room has conflicting reservations for the selected dates
        conflicting_reservations = Reservation.query.filter_by(Room_ID=room.Room_ID).filter(
            (Reservation.Check_In_Date <= check_out) & (Reservation.Check_Out_Date >= check_in)
        ).filter(Reservation.Status != 'Canceled').all()
        
        room_data = {
            'id': room.Room_ID,
            'number': room.Room_Number,
            'floor': room.Floor_Number,
            'capacity': room.Capacity
        }
        
        if room.Status != 'Available':
            # Room is in maintenance or already occupied
            booked_room_data.append(room_data)
        elif conflicting_reservations:
            # Room has a reservation during the selected dates
            pending_count = sum(1 for res in conflicting_reservations if res.Status == 'Pending')
            if pending_count > 0:
                pending_room_data.append(room_data)
            else:
                booked_room_data.append(room_data)
        else:
            # Room is available
            available_room_data.append(room_data)
    
    # Commit any status changes
    db.session.commit()
    
    return jsonify({
        'available': len(available_room_data) > 0,
        'room_count': len(available_room_data),
        'available_rooms': available_room_data,
        'booked_rooms': booked_room_data,
        'pending_rooms': pending_room_data
    })

@app.route('/staff')
@login_required
def staff_portal():
    # Check if user is staff or admin (for demo, we'll allow any authenticated user to access)
    # In a real system, you would check staff roles here
    
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    technician_filter = request.args.get('technician', 'all')
    
    # Base query
    base_query = Maintenance.query
    
    # Apply filters
    if status_filter != 'all':
        base_query = base_query.filter(Maintenance.Maintenance_Status == status_filter)
    
    if date_from:
        date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        base_query = base_query.filter(Maintenance.Report_Date >= date_from)
    
    if date_to:
        date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        base_query = base_query.filter(Maintenance.Report_Date <= date_to)
    
    if technician_filter != 'all':
        if technician_filter == 'unassigned':
            base_query = base_query.filter(Maintenance.Technician_Assigned == None)
        else:
            base_query = base_query.filter(Maintenance.Technician_Assigned == technician_filter)
    
    # Get requests based on status
    all_requests = base_query.all()
    pending_requests = [req for req in all_requests if req.Maintenance_Status == 'Pending']
    ongoing_requests = [req for req in all_requests if req.Maintenance_Status == 'Ongoing']
    completed_requests = [req for req in all_requests if req.Maintenance_Status == 'Completed']
    
    # Get maintenance staff (from Staff table with maintenance-related roles)
    maintenance_staff = Staff.query.filter(
        Staff.Role_Position.in_(['Maintenance Technician', 'Plumber', 'Electrician', 'HVAC Specialist', 'Handyman'])
    ).all()
    
    # Get all staff for staff information tab
    all_staff = Staff.query.all()
    
    # Get all departments for the add staff form
    departments = Department.query.all()
    
    # If no maintenance staff found, add some dummy data for demo
    if not maintenance_staff:
        maintenance_roles = [
            {'First_Name': 'Rajesh', 'Last_Name': 'Kumar', 'Role_Position': 'Maintenance Technician', 'Staff_ID': 101, 'Experience': '5 years', 'Specialization': 'General Maintenance'},
            {'First_Name': 'Suresh', 'Last_Name': 'Patel', 'Role_Position': 'Plumber', 'Staff_ID': 102, 'Experience': '8 years', 'Specialization': 'Bathroom Fixtures & Pipelines'},
            {'First_Name': 'Amit', 'Last_Name': 'Sharma', 'Role_Position': 'Electrician', 'Staff_ID': 103, 'Experience': '7 years', 'Specialization': 'Electrical Systems & Wiring'},
            {'First_Name': 'Vijay', 'Last_Name': 'Singh', 'Role_Position': 'HVAC Specialist', 'Staff_ID': 104, 'Experience': '6 years', 'Specialization': 'AC & Heating Systems'},
            {'First_Name': 'Arun', 'Last_Name': 'Verma', 'Role_Position': 'Handyman', 'Staff_ID': 105, 'Experience': '4 years', 'Specialization': 'Furniture & Wood Work'}
        ]
        maintenance_staff = maintenance_roles
    
    today = datetime.now().date()
    
    # Counts for dashboard
    all_count = len(all_requests)
    pending_count = len(pending_requests)
    ongoing_count = len(ongoing_requests)
    completed_count = len(completed_requests)
    
    return render_template('staff.html',
                          all_requests=all_requests,
                          pending_requests=pending_requests,
                          ongoing_requests=ongoing_requests,
                          completed_requests=completed_requests,
                          maintenance_staff=maintenance_staff,
                          all_staff=all_staff,
                          departments=departments,
                          today=today,
                          all_count=all_count,
                          pending_count=pending_count,
                          ongoing_count=ongoing_count,
                          completed_count=completed_count,
                          extract_priority=get_priority_from_text)

@app.route('/get_current_guest/<int:room_id>')
@login_required
def get_current_guest(room_id):
    # Get active reservation for this room
    today = datetime.now().date()
    reservation = Reservation.query.filter(
        Reservation.Room_ID == room_id,
        Reservation.Status == 'Confirmed',
        Reservation.Check_In_Date <= today,
        Reservation.Check_Out_Date >= today
    ).first()
    
    if reservation:
        return Customer.query.get(reservation.Customer_ID)
    return None

@app.route('/assign_maintenance/<int:maintenance_id>', methods=['GET', 'POST'])
@login_required
def assign_maintenance(maintenance_id):
    if request.method == 'POST':
        technician = request.form.get('technician')
        estimated_cost = request.form.get('estimated_cost', 0)
        notes = request.form.get('notes', '')
        
        # Get the maintenance request
        maintenance = Maintenance.query.get_or_404(maintenance_id)
        
        # Update maintenance record
        maintenance.Technician_Assigned = technician
        maintenance.Repair_Cost = float(estimated_cost) if estimated_cost else 0
        maintenance.Maintenance_Status = 'Ongoing'
        
        # Add notes to the issue reported field
        if notes:
            maintenance.Issue_Reported += f"\n\n--- Technician Notes ({datetime.now().strftime('%Y-%m-%d %H:%M')}) ---\n{notes}"
        
        try:
            db.session.commit()
            flash(f'Maintenance request #{maintenance_id} assigned to {technician}', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
        
        return redirect(url_for('staff_portal'))
    
    elif request.method == 'GET':
        # Get the maintenance request details
        maintenance = Maintenance.query.get_or_404(maintenance_id)
        
        # Get maintenance staff (from Staff table with maintenance-related roles)
        maintenance_staff = Staff.query.filter(
            Staff.Role_Position.in_(['Maintenance Technician', 'Plumber', 'Electrician', 'HVAC Specialist', 'Handyman'])
        ).all()
        
        # If no maintenance staff found, add some dummy data for demo
        if not maintenance_staff:
            maintenance_staff = [
                {'First_Name': 'Rajesh', 'Last_Name': 'Kumar', 'Role_Position': 'Maintenance Technician', 'Staff_ID': 101, 'Experience': '5 years', 'Specialization': 'General Maintenance'},
                {'First_Name': 'Suresh', 'Last_Name': 'Patel', 'Role_Position': 'Plumber', 'Staff_ID': 102, 'Experience': '8 years', 'Specialization': 'Bathroom Fixtures & Pipelines'},
                {'First_Name': 'Amit', 'Last_Name': 'Sharma', 'Role_Position': 'Electrician', 'Staff_ID': 103, 'Experience': '7 years', 'Specialization': 'Electrical Systems & Wiring'},
                {'First_Name': 'Vijay', 'Last_Name': 'Singh', 'Role_Position': 'HVAC Specialist', 'Staff_ID': 104, 'Experience': '6 years', 'Specialization': 'AC & Heating Systems'},
                {'First_Name': 'Arun', 'Last_Name': 'Verma', 'Role_Position': 'Handyman', 'Staff_ID': 105, 'Experience': '4 years', 'Specialization': 'Furniture & Wood Work'}
            ]
        
        # Get suggested technician based on issue
        suggested_tech, suggested_name, reason = suggest_technician(maintenance.Issue_Reported, maintenance_staff)
        
        # Calculate average costs for common issues
        issue_costs = {
            'plumbing': 2500.00,  # Basic plumbing fixes in INR
            'electrical': 3000.00,  # Electrical repairs in INR
            'hvac': 5500.00,       # HVAC maintenance in INR
            'furniture': 2000.00,  # Furniture repairs in INR
            'general': 1500.00     # General maintenance in INR
        }
        
        # Estimate cost based on issue type
        estimated_cost = issue_costs['general']  # Default cost
        
        # Determine a more specific cost if possible
        lower_text = maintenance.Issue_Reported.lower() if maintenance.Issue_Reported else ""
        if any(term in lower_text for term in ['leak', 'water', 'pipe', 'drain', 'toilet']):
            estimated_cost = issue_costs['plumbing']
        elif any(term in lower_text for term in ['light', 'power', 'outlet', 'electric']):
            estimated_cost = issue_costs['electrical']
        elif any(term in lower_text for term in ['ac', 'air conditioning', 'heating', 'temperature']):
            estimated_cost = issue_costs['hvac']
        elif any(term in lower_text for term in ['door', 'window', 'furniture', 'cabinet']):
            estimated_cost = issue_costs['furniture']
        
        # Adjust cost based on priority
        priority = get_priority_from_text(maintenance.Issue_Reported)
        if priority == 'Emergency':
            estimated_cost *= 1.5  # 50% premium for emergency service
        elif priority == 'High':
            estimated_cost *= 1.2  # 20% premium for high priority
        
        return render_template('assign_technician.html', 
                            maintenance=maintenance,
                            maintenance_staff=maintenance_staff,
                            suggested_tech=suggested_tech,
                            suggested_name=suggested_name, 
                            reason=reason,
                            estimated_cost=estimated_cost,
                            get_priority=get_priority_from_text)

@app.route('/complete_maintenance/<int:maintenance_id>', methods=['POST'])
@login_required
def complete_maintenance(maintenance_id):
    if request.method == 'POST':
        final_cost = request.form.get('final_cost', 0)
        resolution = request.form.get('resolution', '')
        completion_date_str = request.form.get('completion_date')
        
        # Parse completion date for inclusion in resolution notes
        completion_date = datetime.now().date()
        if completion_date_str:
            try:
                completion_date = datetime.strptime(completion_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        # Get the maintenance request
        maintenance = Maintenance.query.get_or_404(maintenance_id)
        
        # Update maintenance record
        maintenance.Maintenance_Status = 'Completed'
        maintenance.Repair_Cost = float(final_cost) if final_cost else 0
        
        # Add resolution details to the issue reported field
        if resolution:
            maintenance.Issue_Reported += f"\n\n--- Resolution ({completion_date.strftime('%Y-%m-%d')}) ---\n{resolution}"
        
        # Update room status if needed
        if maintenance.room and maintenance.room.Status == 'Maintenance':
            maintenance.room.Status = 'Available'
        
        try:
            db.session.commit()
            flash(f'Maintenance request #{maintenance_id} marked as completed', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
        
        return redirect(url_for('staff_portal'))

@app.route('/add_staff', methods=['POST'])
@login_required
def add_staff():
    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        department_id = request.form.get('department_id') or None  # Handle empty selection
        role_position = request.form.get('role_position')
        contact_number = request.form.get('contact_number')
        salary = request.form.get('salary')
        
        # Create new staff member
        new_staff = Staff(
            First_Name=first_name,
            Last_Name=last_name,
            Department_ID=department_id,
            Role_Position=role_position,
            Contact_Number=contact_number,
            Salary=float(salary)
        )
        
        try:
            db.session.add(new_staff)
            db.session.commit()
            flash(f'Staff member {first_name} {last_name} added successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
        
        return redirect(url_for('staff_portal'))

@app.route('/maintenance_diagnostic')
@login_required
def maintenance_diagnostic():
    try:
        # Check if Maintenance table exists
        exists = False
        try:
            maintenance_count = Maintenance.query.count()
            exists = True
        except:
            exists = False
        
        column_names = []
        model_columns = []
        priority_exists = False
        resolved_date_exists = False
        
        if exists:
            # Get the column names for the Maintenance table from the database engine
            inspector = inspect(db.engine)
            try:
                columns = inspector.get_columns('Maintenance')
                column_names = [column['name'] for column in columns]
                priority_exists = 'Priority' in column_names
                resolved_date_exists = 'Resolved_Date' in column_names
            except:
                column_names = ["Could not inspect table"]
            
            # Now check the model definition
            model_columns = [column.key for column in Maintenance.__table__.columns]
            
            # If columns exist in database but not in model, suggest dropping them
            if priority_exists and 'Priority' not in model_columns:
                flash("The Priority column exists in your database but has been removed from the model. " +
                      "Consider dropping this column to avoid future issues.", "warning")
            
            if resolved_date_exists and 'Resolved_Date' not in model_columns:
                flash("The Resolved_Date column exists in your database but has been removed from the model. " +
                      "Consider dropping this column to avoid future issues.", "warning")
        
        return render_template('diagnostic.html', 
                              table_exists=exists,
                              db_columns=column_names,
                              model_columns=model_columns,
                              priority_exists=priority_exists,
                              resolved_date_exists=resolved_date_exists,
                              match=(set(column_names) == set(model_columns)))
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/drop_column', methods=['POST'])
@login_required
def drop_column():
    column_name = request.form.get('column_name')
    if not column_name:
        flash("No column name provided", "danger")
        return redirect(url_for('maintenance_diagnostic'))
        
    try:
        with db.engine.connect() as conn:
            conn.execute(db.text(f"ALTER TABLE Maintenance DROP COLUMN {column_name}"))
            conn.commit()
        flash(f"{column_name} column has been successfully dropped from the Maintenance table.", "success")
    except Exception as e:
        flash(f"Error dropping {column_name} column: {str(e)}", "danger")
    
    return redirect(url_for('maintenance_diagnostic'))

@app.route('/recreate_maintenance_table', methods=['POST'])
@login_required
def recreate_maintenance_table():
    try:
        # First backup existing data if any
        backup_data = []
        try:
            maintenance_records = Maintenance.query.all()
            for record in maintenance_records:
                backup_data.append({
                    'Room_ID': record.Room_ID,
                    'Issue_Reported': record.Issue_Reported,
                    'Report_Date': record.Report_Date,
                    'Maintenance_Status': record.Maintenance_Status,
                    'Technician_Assigned': record.Technician_Assigned,
                    'Repair_Cost': record.Repair_Cost,
                })
        except Exception as e:
            print(f"Error backing up data: {str(e)}")  # Table might not exist or have different structure

        # Drop the table
        with db.engine.connect() as conn:
            conn.execute(db.text("DROP TABLE IF EXISTS Maintenance"))
            conn.commit()

        # Create the table with correct structure
        db.create_all()
        
        # Restore the data if any
        if backup_data:
            for record in backup_data:
                new_record = Maintenance(**record)
                db.session.add(new_record)
            db.session.commit()
            
        flash("Maintenance table has been successfully recreated with the correct structure.", "success")
    except Exception as e:
        flash(f"Error recreating Maintenance table: {str(e)}", "danger")
    
    return redirect(url_for('maintenance_diagnostic'))

@app.route('/create_maintenance_table')
def create_maintenance_table():
    """Create the Maintenance table with the correct structure."""
    try:
        # Check if table exists
        inspector = inspect(db.engine)
        table_exists = 'Maintenance' in inspector.get_table_names()
        
        if table_exists:
            # Drop the table first if it exists
            with db.engine.connect() as conn:
                conn.execute(db.text("DROP TABLE IF EXISTS Maintenance"))
                conn.commit()
                
        # Create the Maintenance table with the correct structure
        # Define the SQL directly to ensure it matches our model
        with db.engine.connect() as conn:
            conn.execute(db.text("""
                CREATE TABLE Maintenance (
                    Maintenance_ID INT AUTO_INCREMENT PRIMARY KEY,
                    Room_ID INT NOT NULL,
                    Issue_Reported TEXT NOT NULL,
                    Report_Date DATETIME NOT NULL,
                    Maintenance_Status VARCHAR(20) DEFAULT 'Pending',
                    Technician_Assigned VARCHAR(100),
                    Repair_Cost DECIMAL(10, 2),
                    FOREIGN KEY (Room_ID) REFERENCES Rooms(Room_ID)
                )
            """))
            conn.commit()
            
        return "Maintenance table created successfully. You can now submit maintenance requests."
    except Exception as e:
        return f"Error creating Maintenance table: {str(e)}"

@app.route('/schedule_maintenance_completion/<int:maintenance_id>', methods=['POST'])
@login_required
def schedule_maintenance_completion(maintenance_id):
    """Schedule a maintenance request to be automatically completed after a specified time period."""
    if request.method == 'POST':
        hours = int(request.form.get('hours', 24))  # Default to 24 hours if not specified
        notes = request.form.get('notes', '')
        
        # Get the maintenance request
        maintenance = Maintenance.query.get_or_404(maintenance_id)
        
        # Calculate completion time
        completion_time = datetime.now() + timedelta(hours=hours)
        
        # Add scheduling note to the issue reported field
        maintenance.Issue_Reported += f"\n\n--- Auto-Completion Scheduled ({datetime.now().strftime('%Y-%m-%d %H:%M')}) ---\n"
        maintenance.Issue_Reported += f"This maintenance request will be automatically marked as completed on {completion_time.strftime('%Y-%m-%d %H:%M')}.\n"
        
        if notes:
            maintenance.Issue_Reported += f"Notes: {notes}\n"
        
        try:
            # Store the scheduled completion time in the database
            # First, check if Task_Schedule table exists, if not create it
            inspector = inspect(db.engine)
            if 'Task_Schedule' not in inspector.get_table_names():
                with db.engine.connect() as conn:
                    conn.execute(db.text("""
                        CREATE TABLE Task_Schedule (
                            Task_ID INT AUTO_INCREMENT PRIMARY KEY,
                            Maintenance_ID INT NOT NULL,
                            Scheduled_Time DATETIME NOT NULL,
                            Task_Type VARCHAR(50) DEFAULT 'completion',
                            Completed BOOLEAN DEFAULT 0,
                            FOREIGN KEY (Maintenance_ID) REFERENCES Maintenance(Maintenance_ID)
                        )
                    """))
                    conn.commit()
            
            # Insert the scheduled task
            with db.engine.connect() as conn:
                conn.execute(db.text(f"""
                    INSERT INTO Task_Schedule 
                    (Maintenance_ID, Scheduled_Time, Task_Type) 
                    VALUES ({maintenance_id}, '{completion_time.strftime('%Y-%m-%d %H:%M:%S')}', 'completion')
                """))
                conn.commit()
            
            db.session.commit()
            flash(f'Maintenance request #{maintenance_id} scheduled for automatic completion after {hours} hours.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
        
        return redirect(url_for('staff_portal'))

@app.route('/process_scheduled_tasks')
def process_scheduled_tasks():
    """Process all scheduled tasks that are due."""
    try:
        # Check if Task_Schedule table exists
        inspector = inspect(db.engine)
        if 'Task_Schedule' not in inspector.get_table_names():
            return "Task_Schedule table does not exist."
        
        # Get all due tasks
        now = datetime.now()
        due_tasks = []
        
        # Use raw SQL to query the tasks
        with db.engine.connect() as conn:
            result = conn.execute(db.text("""
                SELECT Task_ID, Maintenance_ID, Scheduled_Time, Task_Type 
                FROM Task_Schedule 
                WHERE Scheduled_Time <= NOW() AND Completed = 0
            """))
            due_tasks = [dict(row._mapping) for row in result]
        
        processed_count = 0
        for task in due_tasks:
            # Process task based on type
            if task['Task_Type'] == 'completion':
                # Get the maintenance request
                maintenance = Maintenance.query.get(task['Maintenance_ID'])
                if maintenance and maintenance.Maintenance_Status != 'Completed':
                    # Update maintenance record
                    maintenance.Maintenance_Status = 'Completed'
                    
                    # Add auto-completion note
                    maintenance.Issue_Reported += f"\n\n--- Auto-Completed ({now.strftime('%Y-%m-%d %H:%M')}) ---\n"
                    maintenance.Issue_Reported += "This maintenance request was automatically marked as completed as scheduled."
                    
                    # Update room status if needed
                    if maintenance.room and maintenance.room.Status == 'Maintenance':
                        maintenance.room.Status = 'Available'
                    
                    # Mark task as completed
                    with db.engine.connect() as conn:
                        conn.execute(db.text(f"""
                            UPDATE Task_Schedule SET Completed = 1 
                            WHERE Task_ID = {task['Task_ID']}
                        """))
                        conn.commit()
                    
                    processed_count += 1
        
        db.session.commit()
        return f"Processed {processed_count} scheduled tasks successfully."
    except Exception as e:
        db.session.rollback()
        return f"Error processing scheduled tasks: {str(e)}"

@app.route('/cleanup_expired_bookings')
def cleanup_expired_bookings():
    """
    Check for expired bookings and update room statuses.
    This route can be called manually or scheduled as a daily task.
    """
    try:
        # Get current date
        current_date = datetime.now().date()
        
        # Find all reservations that have ended (check-out date has passed)
        expired_reservations = Reservation.query.filter(
            Reservation.Check_Out_Date < current_date,
            Reservation.Status.in_(['Confirmed', 'Pending'])
        ).all()
        
        updated_count = 0
        rooms_freed = 0
        
        # Update reservation statuses
        for reservation in expired_reservations:
            reservation.Status = 'Completed'
            updated_count += 1
            
            # Find the corresponding booking record
            booking = Booking.query.filter_by(
                Customer_ID=reservation.Customer_ID,
                Room_ID=reservation.Room_ID,
                Check_In_Date=reservation.Check_In_Date,
                Check_Out_Date=reservation.Check_Out_Date
            ).first()
            
            if booking:
                booking.Booking_Status = 'Completed'
            
            # Update room status to available if currently occupied
            room = Room.query.get(reservation.Room_ID)
            if room and room.Status == 'Occupied':
                room.Status = 'Available'
                rooms_freed += 1
        
        # Commit all changes
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f"Cleanup completed. {updated_count} expired bookings processed, {rooms_freed} rooms freed."
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f"Error during cleanup: {str(e)}"
        })

@app.route('/drop_task_schedule')
def drop_task_schedule():
    """
    Drops the Task_Schedule table from the database.
    This route can be used to clean up the database by removing the Task_Schedule table.
    """
    try:
        # Check if Task_Schedule table exists
        inspector = inspect(db.engine)
        if 'Task_Schedule' in inspector.get_table_names():
            # Drop the Task_Schedule table
            with db.engine.connect() as conn:
                conn.execute(db.text("DROP TABLE IF EXISTS Task_Schedule"))
                conn.commit()
            return "Task_Schedule table has been successfully dropped from the database."
        else:
            return "Task_Schedule table does not exist in the database."
    except Exception as e:
        return f"Error dropping Task_Schedule table: {str(e)}"

@app.route('/maintenance')
@login_required
def maintenance():
    """
    Room maintenance request page.
    Allows users to submit maintenance requests for rooms.
    """
    # Get all rooms
    rooms = Room.query.all()
    
    # Check if the user has already submitted maintenance requests
    user_requests = []
    if current_user.is_authenticated:
        # Get reservations for the current user
        user_reservations = Reservation.query.filter_by(Customer_ID=current_user.Customer_ID).all()
        
        # Get room IDs from user's reservations
        reserved_room_ids = [res.Room_ID for res in user_reservations if res.Room_ID is not None]
        
        # Get maintenance requests for rooms reserved by the user
        if reserved_room_ids:
            user_requests = Maintenance.query.filter(Maintenance.Room_ID.in_(reserved_room_ids)).all()
    
    return render_template('maintenance.html', rooms=rooms, user_requests=user_requests)

@app.route('/submit_maintenance', methods=['POST'])
@login_required
def submit_maintenance():
    """
    Handle submission of maintenance requests.
    """
    if request.method == 'POST':
        room_id = request.form.get('room_id')
        issue = request.form.get('issue')
        
        if not room_id or not issue:
            flash('Please select a room and describe the issue.', 'danger')
            return redirect(url_for('maintenance'))
        
        # Create new maintenance request
        new_request = Maintenance(
            Room_ID=room_id,
            Issue_Reported=issue,
            Report_Date=datetime.now(),
            Maintenance_Status='Pending'
        )
        
        try:
            db.session.add(new_request)
            db.session.commit()
            flash('Maintenance request submitted successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
        
        return redirect(url_for('maintenance'))

@app.route('/maintenance_history')
@login_required
def maintenance_history():
    """Displays the maintenance request history for the current user."""
    # Get reservations for the current user
    user_reservations = Reservation.query.filter_by(Customer_ID=current_user.Customer_ID).all()
    reserved_room_ids = [res.Room_ID for res in user_reservations if res.Room_ID is not None]
    
    # Get maintenance requests related to the user's reserved rooms
    user_requests = []
    if reserved_room_ids:
        user_requests = Maintenance.query.filter(Maintenance.Room_ID.in_(reserved_room_ids)) \
            .order_by(Maintenance.Report_Date.desc()).all()
            
    return render_template('maintenance_history.html', requests=user_requests)

def suggest_technician(issue_text, technicians):
    """
    Suggest a technician based on the reported maintenance issue.
    
    Args:
        issue_text (str): The reported maintenance issue text
        technicians (list): List of maintenance staff members
    
    Returns:
        tuple: (technician_id, technician_name, reason_for_suggestion)
    """
    # Convert issue text to lowercase for easier matching
    issue_lower = issue_text.lower() if issue_text else ""
    
    # Define keywords for different types of issues
    plumbing_keywords = ['leak', 'water', 'pipe', 'drain', 'toilet', 'faucet', 'sink', 'shower']
    electrical_keywords = ['light', 'power', 'outlet', 'electric', 'bulb', 'switch', 'circuit', 'fan']
    hvac_keywords = ['ac', 'air conditioning', 'heating', 'temperature', 'hot', 'cold', 'ventilation']
    furniture_keywords = ['door', 'window', 'furniture', 'cabinet', 'chair', 'desk', 'bed', 'drawer']
    
    # Determine issue type based on keywords
    if any(keyword in issue_lower for keyword in plumbing_keywords):
        issue_type = 'Plumbing'
    elif any(keyword in issue_lower for keyword in electrical_keywords):
        issue_type = 'Electrical'
    elif any(keyword in issue_lower for keyword in hvac_keywords):
        issue_type = 'HVAC'
    elif any(keyword in issue_lower for keyword in furniture_keywords):
        issue_type = 'Furniture'
    else:
        issue_type = 'General'
    
    # Find technician with matching specialization
    for tech in technicians:
        # Determine the role_position or specialization field name
        if hasattr(tech, 'Role_Position'):
            role = tech.Role_Position
        else:
            # For dictionary objects
            role = tech.get('Role_Position', '')
        
        # Get technician name
        if hasattr(tech, 'First_Name') and hasattr(tech, 'Last_Name'):
            tech_name = f"{tech.First_Name} {tech.Last_Name}"
        else:
            # For dictionary objects
            first_name = tech.get('First_Name', '')
            last_name = tech.get('Last_Name', '')
            tech_name = f"{first_name} {last_name}"
        
        # Get technician ID
        if hasattr(tech, 'Staff_ID'):
            tech_id = tech.Staff_ID
        else:
            # For dictionary objects
            tech_id = tech.get('Staff_ID', '')
        
        # Match issue type with technician role
        if issue_type == 'Plumbing' and 'Plumber' in role:
            return tech_id, tech_name, f"Plumbing issue detected: {issue_type}"
        elif issue_type == 'Electrical' and 'Electrician' in role:
            return tech_id, tech_name, f"Electrical issue detected: {issue_type}"
        elif issue_type == 'HVAC' and 'HVAC' in role:
            return tech_id, tech_name, f"HVAC issue detected: {issue_type}"
        elif issue_type == 'Furniture' and 'Handyman' in role:
            return tech_id, tech_name, f"Furniture issue detected: {issue_type}"
    
    # If no specialized technician found, suggest a general maintenance technician
    for tech in technicians:
        if hasattr(tech, 'Role_Position'):
            role = tech.Role_Position
        else:
            role = tech.get('Role_Position', '')
        
        if hasattr(tech, 'First_Name') and hasattr(tech, 'Last_Name'):
            tech_name = f"{tech.First_Name} {tech.Last_Name}"
        else:
            first_name = tech.get('First_Name', '')
            last_name = tech.get('Last_Name', '')
            tech_name = f"{first_name} {last_name}"
        
        if hasattr(tech, 'Staff_ID'):
            tech_id = tech.Staff_ID
        else:
            tech_id = tech.get('Staff_ID', '')
        
        if 'Maintenance' in role or 'Technician' in role:
            return tech_id, tech_name, f"General maintenance issue: {issue_type}"
    
    # If no maintenance technician found, return the first technician in the list
    if technicians:
        if hasattr(technicians[0], 'Staff_ID'):
            tech_id = technicians[0].Staff_ID
        else:
            tech_id = technicians[0].get('Staff_ID', '')
        
        if hasattr(technicians[0], 'First_Name') and hasattr(technicians[0], 'Last_Name'):
            tech_name = f"{technicians[0].First_Name} {technicians[0].Last_Name}"
        else:
            first_name = technicians[0].get('First_Name', '')
            last_name = technicians[0].get('Last_Name', '')
            tech_name = f"{first_name} {last_name}"
            
        return tech_id, tech_name, "No specialized technician matched, suggesting default"
    
    # Fallback if no technicians available
    return None, "No technician available", "Please add maintenance staff first"

def get_priority_from_text(issue_text):
    """
    Determine the priority level based on the reported issue text.
    
    Args:
        issue_text (str): The reported maintenance issue
    
    Returns:
        str: Priority level (Emergency, High, Medium, Low)
    """
    if not issue_text:
        return "Low"
    
    # Convert to lowercase for easier matching
    issue_lower = issue_text.lower()
    
    # Emergency keywords
    emergency_keywords = [
        'fire', 'smoke', 'flood', 'flooding', 'leak everywhere', 'no water', 'no electricity',
        'gas', 'emergency', 'danger', 'safety hazard', 'security breach', 'broken window',
        'cannot lock', 'urgent', 'immediate', 'elevator stuck', 'alarm'
    ]
    
    # High priority keywords
    high_keywords = [
        'ac not working', 'no hot water', 'no heating', 'toilet overflow', 'leaking',
        'drainage', 'important', 'priority', 'broken door', 'lock issue', 'electrical issue',
        'power outage', 'not functioning', 'major', 'significant', 'bathroom unusable'
    ]
    
    # Medium priority keywords
    medium_keywords = [
        'maintenance', 'repair', 'fix', 'issue', 'problem', 'not working properly',
        'attention needed', 'check', 'inspect', 'malfunction', 'intermittent',
        'moderate', 'inconvenience'
    ]
    
    # Check for emergency keywords
    for keyword in emergency_keywords:
        if keyword in issue_lower:
            return "Emergency"
    
    # Check for high priority keywords
    for keyword in high_keywords:
        if keyword in issue_lower:
            return "High"
    
    # Check for medium priority keywords
    for keyword in medium_keywords:
        if keyword in issue_lower:
            return "Medium"
    
    # Default priority
    return "Low"

def init_db():
    """Initialize the database by creating all tables."""
    try:
        # Create all tables defined by SQLAlchemy models
        with app.app_context():
            db.create_all()
            print("Database tables created successfully.")
    except Exception as e:
        print(f"Error creating database tables: {str(e)}")

if __name__ == '__main__':
    init_db()
    app.run(debug=True)