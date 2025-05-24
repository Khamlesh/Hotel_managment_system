from app import app, db, Staff, Department
from tabulate import tabulate

def list_departments():
    """List all departments in the database"""
    with app.app_context():
        departments = Department.query.all()
        
        if not departments:
            print("No departments found in the database.")
            return
        
        dept_data = []
        for dept in departments:
            dept_data.append([
                dept.Department_ID,
                dept.Department_Name,
                dept.Contact_Number,
                dept.Email,
                dept.Number_of_Employees,
                dept.Location
            ])
        
        headers = ["ID", "Name", "Contact Number", "Email", "Employee Count", "Location"]
        print("\n===== DEPARTMENTS =====")
        print(tabulate(dept_data, headers=headers, tablefmt="grid"))

def list_staff():
    """List all staff members in the database"""
    with app.app_context():
        staff_members = Staff.query.all()
        
        if not staff_members:
            print("No staff members found in the database.")
            return
        
        staff_data = []
        for staff in staff_members:
            department_name = "N/A"
            if staff.Department_ID and staff.department:
                department_name = staff.department.Department_Name
                
            staff_data.append([
                staff.Staff_ID,
                f"{staff.First_Name} {staff.Last_Name}",
                department_name,
                staff.Role_Position,
                staff.Contact_Number,
                f"₹{staff.Salary:,.2f}"
            ])
        
        headers = ["ID", "Name", "Department", "Position", "Contact Number", "Salary"]
        print("\n===== STAFF MEMBERS =====")
        print(tabulate(staff_data, headers=headers, tablefmt="grid"))

if __name__ == "__main__":
    list_departments()
    list_staff() 