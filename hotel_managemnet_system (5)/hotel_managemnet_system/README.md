# Hotel Management System

A comprehensive customer-oriented hotel management system built with Flask and MySQL. This system allows customers to browse rooms, make reservations, provide feedback, and manage their bookings.

## Features

- **User Authentication**: Register, login, and account management
- **Room Management**: Browse different room types with detailed information
- **Booking System**: Check availability, make reservations, and process payments
- **Customer Dashboard**: View reservations, bookings, and payment history
- **Feedback System**: Leave reviews and ratings for previous stays
- **Discount Management**: Apply discount codes to bookings

## Screenshots

*Not available in this version. Screenshots will be added after deployment.*

## Installation

### Prerequisites
- Python 3.8 or higher
- MySQL Server
- Pip (Python package manager)

### Setting up the Database
1. Install MySQL Server
2. Create a database named `HotelManagement`
3. Run the provided SQL script to set up the schema and initial data:
   ```
   mysql -u root -p HotelManagement < database_setup.sql
   ```

### Setting up the Application
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/hotel-management-system.git
   cd hotel-management-system
   ```

2. Create and activate a virtual environment (recommended):
   ```
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Configure the database connection:
   
   Open `app.py` and update the database URI:
   ```python
   app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/HotelManagement'
   ```
   Replace `username` and `password` with your MySQL credentials.

5. Create sample images:
   
   Place room images in the `static/images/` directory with the following naming convention:
   - `room_1.jpg`, `room_2.jpg`, etc. for room type thumbnails
   - `room_details_1.jpg`, `room_details_2.jpg`, etc. for room detail images
   - `hero.jpg` for the homepage hero image
   - `page-banner.jpg` for page banner backgrounds

## Running the Application

1. Initialize the database (this is already handled in the app's `init_db` function):
   ```
   python app.py
   ```

2. Access the application in your web browser:
   ```
   http://localhost:5000
   ```

## Usage

1. **Register an Account**: Create a new user account
2. **Browse Rooms**: View different room types and their details
3. **Make a Reservation**: Select dates, provide guest information, and complete the booking
4. **Dashboard**: Access your reservations, bookings, and payment information
5. **Submit Feedback**: Rate and comment on your previous stays

## Admin Features

1. **Admin Login**: Use admin credentials (email: admin@hotel.com, password: admin123)
2. **Manage Rooms**: Add, edit, or remove room listings
3. **Manage Bookings**: View, confirm, or cancel bookings
4. **Manage Users**: View and manage user accounts
5. **Manage Feedback**: View and respond to user feedback

## Technologies Used

- **Backend**: Flask, SQLAlchemy
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Database**: MySQL
- **Authentication**: Flask-Login

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For any questions or suggestions, please contact [your email address].

## Acknowledgements

- Bootstrap 5 for the UI components
- Font Awesome for the icons
- Placeholder.com for placeholder images 