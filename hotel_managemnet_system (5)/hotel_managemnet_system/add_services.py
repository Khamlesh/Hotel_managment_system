from app import app, db, Service, Staff
from datetime import datetime, time
import random

def add_service_if_not_exists(service_name, description, price, duration, availability_status='Available'):
    """
    Add a service to the database if it doesn't already exist
    """
    with app.app_context():
        # Check if service already exists
        existing_service = Service.query.filter_by(Service_Name=service_name).first()
        if existing_service:
            print(f"Service '{service_name}' already exists.")
            return existing_service
        
        # Format the duration string into a time object
        duration_time = datetime.strptime(duration, '%H:%M:%S').time()
        
        # Create new service
        new_service = Service(
            Service_Name=service_name,
            Description=description,
            Price=price,
            Availability_Status=availability_status,
            Duration=duration_time
        )
        
        # Add to database
        try:
            db.session.add(new_service)
            db.session.commit()
            print(f"Added service: {service_name}")
            return new_service
        except Exception as e:
            db.session.rollback()
            print(f"Error adding service '{service_name}': {str(e)}")
            return None

def assign_staff_to_services():
    """
    Assign staff members to services based on their departments
    """
    with app.app_context():
        # Get all services that don't have staff assigned
        services = Service.query.filter_by(Staff_In_Charge=None).all()
        if not services:
            print("All services already have staff assigned or no services found.")
            return
        
        # Get all staff members
        staff_members = Staff.query.all()
        if not staff_members:
            print("No staff members found in the database.")
            return
        
        # Create a mapping of services to appropriate departments
        service_department_mapping = {
            'Room Service': 'Food Service',
            'Spa Treatment': 'Housekeeping', 
            'Airport Shuttle': 'Front Desk',
            'Laundry Service': 'Housekeeping',
            'Guided Tours': 'Front Desk',
            'Fitness Center': 'Housekeeping',
            'Concierge': 'Front Desk',
            'Babysitting': 'Housekeeping',
            'Business Center': 'Management',
            'Pet Care': 'Housekeeping',
            'Valet Parking': 'Front Desk',
            'Limo Service': 'Front Desk'
        }
        
        # Group staff by department
        staff_by_department = {}
        for staff in staff_members:
            if staff.department:
                dept_name = staff.department.Department_Name
                if dept_name not in staff_by_department:
                    staff_by_department[dept_name] = []
                staff_by_department[dept_name].append(staff)
        
        # Assign staff to services
        for service in services:
            # Determine which department should handle this service
            target_dept = service_department_mapping.get(service.Service_Name, 'Front Desk')
            
            # Find staff from appropriate department
            dept_staff = staff_by_department.get(target_dept, [])
            if not dept_staff:
                # If no staff in the preferred department, choose from any department
                random_staff = random.choice(staff_members) if staff_members else None
            else:
                # Choose a random staff member from the appropriate department
                random_staff = random.choice(dept_staff)
            
            if random_staff:
                service.Staff_In_Charge = random_staff.Staff_ID
                print(f"Assigned {random_staff.First_Name} {random_staff.Last_Name} ({random_staff.Role_Position}) to {service.Service_Name}")
            else:
                print(f"No staff available to assign to {service.Service_Name}")
        
        # Commit all assignments
        try:
            db.session.commit()
            print("Staff assignments complete.")
        except Exception as e:
            db.session.rollback()
            print(f"Error assigning staff to services: {str(e)}")

def add_services():
    """
    Add a variety of hotel services to the database
    """
    print("Adding services to the database...")
    
    # Core services
    services = [
        # Basic services
        {
            'name': 'Room Service',
            'description': 'Enjoy delicious meals delivered directly to your room 24/7, with a diverse menu featuring international and local cuisine.',
            'price': 250.00,
            'duration': '00:30:00'
        },
        {
            'name': 'Spa Treatment',
            'description': 'Indulge in our signature massage treatments, facials, and body wraps designed to revitalize your body and mind.',
            'price': 1500.00,
            'duration': '01:30:00'
        },
        {
            'name': 'Airport Shuttle',
            'description': 'Convenient transportation to and from the airport with our comfortable, air-conditioned vehicles.',
            'price': 800.00,
            'duration': '00:45:00'
        },
        {
            'name': 'Laundry Service',
            'description': 'Professional cleaning and pressing for your clothes with same-day service available upon request.',
            'price': 350.00, 
            'duration': '03:00:00'
        },
        {
            'name': 'Guided Tours',
            'description': 'Explore local attractions, historical sites, and hidden gems with our experienced local guides.',
            'price': 1200.00,
            'duration': '04:00:00'
        },
        {
            'name': 'Fitness Center',
            'description': 'Access to our state-of-the-art fitness equipment, personal trainers, and daily fitness classes.',
            'price': 200.00,
            'duration': '02:00:00'
        },
        
        # Additional premium services
        {
            'name': 'Concierge',
            'description': 'Personalized assistance with restaurant reservations, event tickets, travel arrangements, and special requests.',
            'price': 0.00,  # Complimentary service
            'duration': '00:15:00'
        },
        {
            'name': 'Babysitting',
            'description': 'Professional childcare services provided by certified caregivers in the comfort of your room.',
            'price': 600.00, 
            'duration': '03:00:00'
        },
        {
            'name': 'Business Center',
            'description': 'Full-service business facilities including computer workstations, printing, scanning, and video conferencing.',
            'price': 150.00,
            'duration': '01:00:00'
        },
        {
            'name': 'Pet Care',
            'description': 'Pet sitting, walking, grooming, and specialized pet menu options for your furry companions.',
            'price': 450.00,
            'duration': '01:00:00'
        },
        {
            'name': 'Valet Parking',
            'description': 'Convenient valet parking service with 24/7 access to your vehicle upon request.',
            'price': 300.00,
            'duration': '00:10:00'
        },
        {
            'name': 'Limo Service',
            'description': 'Luxury transportation in our premium fleet of vehicles for special occasions or city exploration.',
            'price': 2500.00,
            'duration': '02:00:00'
        }
    ]
    
    # Add each service to the database
    added_services = []
    for service in services:
        result = add_service_if_not_exists(
            service['name'], 
            service['description'], 
            service['price'], 
            service['duration']
        )
        if result:
            added_services.append(result)
    
    print(f"Added {len(added_services)} new services to the database.")
    
    # Assign staff to services
    assign_staff_to_services()
    
    return added_services

if __name__ == "__main__":
    with app.app_context():
        add_services()
        
        # Verify services were added
        all_services = Service.query.all()
        print(f"\nTotal services in database: {len(all_services)}")
        
        print("\nAll services:")
        for service in all_services:
            staff_name = "Not assigned"
            if service.Staff_In_Charge:
                staff = Staff.query.get(service.Staff_In_Charge)
                if staff:
                    staff_name = f"{staff.First_Name} {staff.Last_Name}"
            
            print(f"- {service.Service_Name} (₹{service.Price}) - Staff: {staff_name}") 