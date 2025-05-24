-- SQL script to add events to the database
USE HotelManagementNew;

-- Delete existing events (optional - only run this if you want to replace all events)
-- DELETE FROM Event;

-- Insert new events
INSERT INTO Event (Event_Name, Description, Event_Date, Location, Organizer_ID, Expected_Guests)
VALUES 
('Wine Tasting', 'Enjoy a selection of fine wines from local vineyards paired with gourmet cheese.',
 DATE_ADD(CURDATE(), INTERVAL 5 DAY), 'Hotel Wine Cellar', 1, 30),
 
('Live Music', 'A relaxing evening with live jazz music in our elegant lounge.',
 DATE_ADD(CURDATE(), INTERVAL 12 DAY), 'Hotel Lounge', 1, 50),
 
('Cooking Class', 'Learn to prepare signature dishes with our executive chef.',
 DATE_ADD(CURDATE(), INTERVAL 18 DAY), 'Hotel Kitchen', 1, 15),
 
('Yoga Session', 'Start your morning with a refreshing yoga session by the pool.',
 DATE_ADD(CURDATE(), INTERVAL 25 DAY), 'Poolside Deck', 1, 20),
 
('Cultural Dance Night', 'Experience the vibrant cultural dances performed by local artists.',
 DATE_ADD(CURDATE(), INTERVAL 8 DAY), 'Grand Ballroom', 1, 70),
 
('Cocktail Masterclass', 'Learn to mix and craft delicious cocktails with our expert bartenders.',
 DATE_ADD(CURDATE(), INTERVAL 15 DAY), 'Hotel Bar', 1, 25),
 
('Movie Night Under Stars', 'Enjoy classic movies projected on a large screen by the pool.',
 DATE_ADD(CURDATE(), INTERVAL 10 DAY), 'Poolside Garden', 1, 40),
 
('Art Exhibition', 'Featuring works from local artists showcasing the culture and beauty of our region.',
 DATE_ADD(CURDATE(), INTERVAL 30 DAY), 'Exhibition Hall', 1, 100),
 
('Gourmet Food Festival', 'Sample exquisite dishes prepared by renowned chefs from around the country.',
 DATE_ADD(CURDATE(), INTERVAL 22 DAY), 'Hotel Gardens', 1, 150),
 
('Salsa Dancing Night', 'Learn the basics of salsa dancing and enjoy an evening of Latin rhythms.',
 DATE_ADD(CURDATE(), INTERVAL 3 DAY), 'Dance Studio', 1, 35);

-- Verify events were added
SELECT * FROM Event; 