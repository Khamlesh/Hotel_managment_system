from app import app, db, Staff, Department
from datetime import datetime
import sys

def add_department_if_not_exists(dept_name, contact_number, email, location):
    """Add a department if it doesn't already exist"""
    try:
        dept = Department.query.filter_by(Department_Name=dept_name).first()
        if not dept:
            dept = Department(
                Department_Name=dept_name,
                Contact_Number=contact_number,
                Email=email,
                Number_of_Employees=0,
                Location=location
            )
            db.session.add(dept)
            db.session.commit()
            print(f"Department '{dept_name}' added successfully!")
        else:
            print(f"Department '{dept_name}' already exists.")
        return dept
    except Exception as e:
        db.session.rollback()
        print(f"Error adding department '{dept_name}': {str(e)}")
        return None

def add_staff_member(first_name, last_name, department_id, role_position, contact_number, salary):
    """Add a staff member to the database"""
    try:
        # Check if staff already exists
        existing_staff = Staff.query.filter_by(
            First_Name=first_name, 
            Last_Name=last_name,
            Role_Position=role_position
        ).first()
        
        if existing_staff:
            print(f"Staff member {first_name} {last_name} already exists.")
            return existing_staff
        
        # Create new staff member
        new_staff = Staff(
            First_Name=first_name,
            Last_Name=last_name,
            Department_ID=department_id,
            Role_Position=role_position,
            Contact_Number=contact_number,
            Salary=float(salary)
        )
        
        db.session.add(new_staff)
        db.session.commit()
        print(f"Staff member {first_name} {last_name} added successfully!")
        
        # Update department employee count
        department = Department.query.get(department_id)
        if department:
            department.Number_of_Employees += 1
            db.session.commit()
        
        return new_staff
    except Exception as e:
        db.session.rollback()
        print(f"Error adding staff member {first_name} {last_name}: {str(e)}")
        return None

def add_staff_members():
    """Add multiple staff members to the database"""
    print("Starting to add staff members to the database...")
    try:
        # Verify database connection
        print("Verifying database connection...")
        db.session.execute(db.text("SELECT 1"))
        print("Database connection successful!")
        
        # Add departments
        print("\nAdding departments...")
        maintenance_dept = add_department_if_not_exists(
            "Maintenance",
            "+91 98765 43210",
            "maintenance@hotel.com",
            "Ground Floor, East Wing"
        )
        
        housekeeping_dept = add_department_if_not_exists(
            "Housekeeping",
            "+91 98765 43211",
            "housekeeping@hotel.com",
            "Ground Floor, West Wing"
        )
        
        front_desk_dept = add_department_if_not_exists(
            "Front Desk",
            "+91 98765 43212",
            "frontdesk@hotel.com",
            "Lobby"
        )
        
        management_dept = add_department_if_not_exists(
            "Management",
            "+91 98765 43213",
            "management@hotel.com",
            "First Floor, North Wing"
        )
        
        food_service_dept = add_department_if_not_exists(
            "Food Service",
            "+91 98765 43214",
            "foodservice@hotel.com",
            "Ground Floor, South Wing"
        )
        
        # Check if departments were created successfully
        if not (maintenance_dept and housekeeping_dept and front_desk_dept and 
                management_dept and food_service_dept):
            print("Error: Failed to create one or more departments.")
            return
        
        # Add maintenance staff
        print("\nAdding maintenance staff...")
        maintenance_staff = [
            {
                "first_name": "Rajesh",
                "last_name": "Kumar",
                "role_position": "Maintenance Technician",
                "contact_number": "+91 93456 78901",
                "salary": 45000.00
            },
            {
                "first_name": "Suresh",
                "last_name": "Patel",
                "role_position": "Plumber",
                "contact_number": "+91 93456 78902",
                "salary": 40000.00
            },
            {
                "first_name": "Amit",
                "last_name": "Sharma",
                "role_position": "Electrician",
                "contact_number": "+91 93456 78903",
                "salary": 42000.00
            },
            {
                "first_name": "Vijay",
                "last_name": "Singh",
                "role_position": "HVAC Specialist",
                "contact_number": "+91 93456 78904",
                "salary": 48000.00
            },
            {
                "first_name": "Arun",
                "last_name": "Verma",
                "role_position": "Handyman",
                "contact_number": "+91 93456 78905",
                "salary": 38000.00
            }
        ]
        
        # Add housekeeping staff
        print("\nAdding housekeeping staff...")
        housekeeping_staff = [
            {
                "first_name": "Pooja",
                "last_name": "Gupta",
                "role_position": "Head Housekeeper",
                "contact_number": "+91 93456 78906",
                "salary": 35000.00
            },
            {
                "first_name": "Ritu",
                "last_name": "Desai",
                "role_position": "Room Attendant",
                "contact_number": "+91 93456 78907",
                "salary": 28000.00
            },
            {
                "first_name": "Kavita",
                "last_name": "Sharma",
                "role_position": "Room Attendant",
                "contact_number": "+91 93456 78908",
                "salary": 28000.00
            },
            {
                "first_name": "Sanjay",
                "last_name": "Yadav",
                "role_position": "Laundry Supervisor",
                "contact_number": "+91 93456 78909",
                "salary": 32000.00
            }
        ]
        
        # Add front desk staff
        print("\nAdding front desk staff...")
        front_desk_staff = [
            {
                "first_name": "Neha",
                "last_name": "Mishra",
                "role_position": "Front Desk Manager",
                "contact_number": "+91 93456 78910",
                "salary": 38000.00
            },
            {
                "first_name": "Rahul",
                "last_name": "Joshi",
                "role_position": "Receptionist",
                "contact_number": "+91 93456 78911",
                "salary": 30000.00
            },
            {
                "first_name": "Priya",
                "last_name": "Reddy",
                "role_position": "Receptionist",
                "contact_number": "+91 93456 78912",
                "salary": 30000.00
            },
            {
                "first_name": "Deepak",
                "last_name": "Malhotra",
                "role_position": "Concierge",
                "contact_number": "+91 93456 78913",
                "salary": 32000.00
            }
        ]
        
        # Add management staff
        print("\nAdding management staff...")
        management_staff = [
            {
                "first_name": "Vikram",
                "last_name": "Kapoor",
                "role_position": "General Manager",
                "contact_number": "+91 93456 78914",
                "salary": 80000.00
            },
            {
                "first_name": "Aarti",
                "last_name": "Verma",
                "role_position": "Operations Manager",
                "contact_number": "+91 93456 78915",
                "salary": 65000.00
            },
            {
                "first_name": "Mukesh",
                "last_name": "Agarwal",
                "role_position": "Financial Controller",
                "contact_number": "+91 93456 78916",
                "salary": 70000.00
            }
        ]
        
        # Add food service staff
        print("\nAdding food service staff...")
        food_service_staff = [
            {
                "first_name": "Sanjeev",
                "last_name": "Kapoor",
                "role_position": "Head Chef",
                "contact_number": "+91 93456 78917",
                "salary": 60000.00
            },
            {
                "first_name": "Ritu",
                "last_name": "Dalmia",
                "role_position": "Sous Chef",
                "contact_number": "+91 93456 78918",
                "salary": 45000.00
            },
            {
                "first_name": "Ajay",
                "last_name": "Singh",
                "role_position": "Restaurant Manager",
                "contact_number": "+91 93456 78919",
                "salary": 42000.00
            },
            {
                "first_name": "Meena",
                "last_name": "Patel",
                "role_position": "Waitstaff",
                "contact_number": "+91 93456 78920",
                "salary": 25000.00
            },
            {
                "first_name": "Rakesh",
                "last_name": "Kumar",
                "role_position": "Waitstaff",
                "contact_number": "+91 93456 78921",
                "salary": 25000.00
            }
        ]
        
        # Add all staff members
        for staff in maintenance_staff:
            add_staff_member(
                staff["first_name"],
                staff["last_name"],
                maintenance_dept.Department_ID,
                staff["role_position"],
                staff["contact_number"],
                staff["salary"]
            )
        
        for staff in housekeeping_staff:
            add_staff_member(
                staff["first_name"],
                staff["last_name"],
                housekeeping_dept.Department_ID,
                staff["role_position"],
                staff["contact_number"],
                staff["salary"]
            )
        
        for staff in front_desk_staff:
            add_staff_member(
                staff["first_name"],
                staff["last_name"],
                front_desk_dept.Department_ID,
                staff["role_position"],
                staff["contact_number"],
                staff["salary"]
            )
        
        for staff in management_staff:
            add_staff_member(
                staff["first_name"],
                staff["last_name"],
                management_dept.Department_ID,
                staff["role_position"],
                staff["contact_number"],
                staff["salary"]
            )
        
        for staff in food_service_staff:
            add_staff_member(
                staff["first_name"],
                staff["last_name"],
                food_service_dept.Department_ID,
                staff["role_position"],
                staff["contact_number"],
                staff["salary"]
            )
        
        print("\nAll staff members added successfully!")
    except Exception as e:
        print(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    with app.app_context():
        try:
            add_staff_members()
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            sys.exit(1) 