-- SQL script to add discount codes to the database
USE HotelManagementNew;

-- Delete existing discount codes (optional - only run this if you want to replace all codes)
-- DELETE FROM Discount;

-- Insert new discount codes
INSERT INTO Discount (Discount_Code, Description, Discount_Percentage, Valid_From, Valid_Until)
VALUES 
('SUMMER2023', 'Summer special discount - 15% off any booking',
 15.00, '2023-06-01', '2024-12-31'),
 
('WELCOME10', 'New customer discount - 10% off any booking',
 10.00, '2023-01-01', '2024-12-31'),
 
('FAMILY25', 'Family room discount - 25% off family room bookings',
 25.00, '2023-01-01', '2024-12-31'),
 
('WEEKEND15', 'Weekend stay discount - 15% off when staying over weekend',
 15.00, '2023-01-01', '2024-12-31'),
 
('EARLYBIRD', 'Early bird discount - 20% off when booking 30+ days in advance',
 20.00, '2023-01-01', '2024-12-31'),
 
('LOYALTY20', 'Loyalty discount - 20% off for loyal customers',
 20.00, '2023-01-01', '2024-12-31');

-- Verify discount codes were added
SELECT * FROM Discount; 