from app import app, db, Service, Staff
from tabulate import tabulate

def list_services():
    """
    List all services from the database with their assigned staff members.
    """
    with app.app_context():
        services = Service.query.all()
        
        if not services:
            print("No services found in the database.")
            return
        
        service_data = []
        for service in services:
            # Get assigned staff if available
            staff_name = "Not assigned"
            if service.Staff_In_Charge:
                staff = Staff.query.get(service.Staff_In_Charge)
                if staff:
                    staff_name = f"{staff.First_Name} {staff.Last_Name} ({staff.Role_Position})"
            
            # Format price
            formatted_price = f"₹{service.Price:.2f}" if service.Price else "Free"
            
            service_data.append([
                service.Service_ID,
                service.Service_Name,
                service.Description[:50] + "..." if len(service.Description) > 50 else service.Description,
                formatted_price,
                f"{service.Duration} minutes" if service.Duration else "N/A",
                "Available" if service.Availability_Status else "Unavailable",
                staff_name
            ])
        
        headers = ["ID", "Service Name", "Description", "Price", "Duration", "Status", "Assigned Staff"]
        print("\n=== HOTEL SERVICES ===")
        print(tabulate(service_data, headers=headers, tablefmt="grid"))
        print(f"Total Services: {len(services)}\n")

if __name__ == "__main__":
    list_services() 