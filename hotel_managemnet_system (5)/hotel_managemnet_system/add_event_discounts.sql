-- SQL script to add event discount codes to the database
USE HotelManagementNew;

-- Create an Event Discount table if it doesn't exist already
CREATE TABLE IF NOT EXISTS Event_Discount (
    Discount_ID INT AUTO_INCREMENT PRIMARY KEY,
    Discount_Code VARCHAR(50) NOT NULL UNIQUE,
    Description VARCHAR(255) NOT NULL,
    Discount_Percentage DECIMAL(5,2) NOT NULL,
    Valid_From DATE NOT NULL,
    Valid_Until DATE NOT NULL,
    Minimum_Attendees INT DEFAULT 1
);

-- Delete existing event discount codes (optional - only run this if you want to replace all codes)
-- DELETE FROM Event_Discount;

-- Insert new event discount codes
INSERT INTO Event_Discount (Discount_Code, Description, Discount_Percentage, Valid_From, Valid_Until, Minimum_Attendees)
VALUES 
('EVENT20', 'Event discount - 20% off any event booking',
 20.00, '2023-01-01', '2024-12-31', 1),
 
('WELCOME10', 'New customer discount - 10% off event bookings',
 10.00, '2023-01-01', '2024-12-31', 1),
 
('LOYALTY15', 'Loyalty discount - 15% off for returning customers',
 15.00, '2023-01-01', '2024-12-31', 1),
 
('GROUP30', 'Group discount - 30% off for 5 or more attendees',
 30.00, '2023-01-01', '2024-12-31', 5);

-- Verify event discount codes were added
SELECT * FROM Event_Discount; 