create database BookEZDatabase;
USE BookEZDatabase;

CREATE TABLE Building(
    buildingName VARCHAR(20) PRIMARY KEY NOT NULL,
    location VARCHAR(20) NOT NULL,
    hoursOfOperation VARCHAR(15) NOT NULL
);

CREATE TABLE Room(
    roomNumber VARCHAR(4) PRIMARY KEY NOT NULL,
    companyBuilding VARCHAR(20),
    wing VARCHAR(5) NOT NULL,
    wheelchairAccessible BOOL NOT NULL,
    projectorAccess BOOL NOT NULL,
    whiteboardAccess BOOL NOT NULL,
    maximumCapacity INT NOT NULL,
    FOREIGN KEY (companyBuilding) REFERENCES Building(buildingName)
);

CREATE TABLE RegisteredUser(
    RUID INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
    username VARCHAR(30) NOT NULL,
    email VARCHAR(40) NOT NULL,
    pass VARCHAR(200),
    firstName VARCHAR(30),
    lastName VARCHAR(30)
);

CREATE TABLE Booking(
    BID INT AUTO_INCREMENT PRIMARY KEY,
    meetingDate DATE NOT NULL,
    startTime TIME NOT NULL,
    duration TIME NOT NULL,
    numberOfConfirmations INT,
    meetingOwner INT NOT NULL,
    reminderSent BOOL,
    shareableLink VARCHAR(50),
    meetingRoom VARCHAR(4) NOT NULL,
    meetingSize INT NOT NULL,
    FOREIGN KEY (meetingRoom) REFERENCES Room(roomNumber),
    FOREIGN KEY (meetingOwner) REFERENCES RegisteredUser(RUID)
);

CREATE TABLE UnregisteredUser(
    URUID INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
    nickname VARCHAR(30) NOT NULL,
    email VARCHAR(40)
);

CREATE TABLE RoomsAssociatedWithBookings(
    BID INT,
    RID VARCHAR(4),
    FOREIGN KEY (BID) REFERENCES Booking(BID),
    FOREIGN KEY (RID) REFERENCES Room(roomNumber)
);

CREATE TABLE UnregisteredBookingAttendees(
    BID INT,
    unregisteredAttendee INT,
    FOREIGN KEY (BID) REFERENCES Booking(BID),
    FOREIGN KEY (unregisteredAttendee) REFERENCES UnregisteredUser(URUID)
);

CREATE TABLE RegisteredBookingAttendees(
    BID INT,
    RegisteredAttendee INT,
    FOREIGN KEY (BID) REFERENCES Booking(BID),
    FOREIGN KEY (RegisteredAttendee) REFERENCES RegisteredUser(RUID)
);

ALTER TABLE Booking AUTO_INCREMENT = 1000;
ALTER TABLE RegisteredUser AUTO_INCREMENT = 1000;
ALTER TABLE UnregisteredUser AUTO_INCREMENT = 1000;

-- =========================
-- TEST DATA
-- =========================

-- Buildings
INSERT INTO Building (buildingName, location, hoursOfOperation) VALUES
('NorthHall', 'Waterloo', '08:00-22:00'),
('TechCentre', 'Kitchener', '07:00-21:00'),
('WestWing', 'Cambridge', '09:00-18:00');

-- Rooms
-- Additional rooms to bring total room count to 100
INSERT INTO Room (
    roomNumber,
    companyBuilding,
    wing,
    wheelchairAccessible,
    projectorAccess,
    whiteboardAccess,
    maximumCapacity
) VALUES
('1F07', 'NorthHall', 'East', 1, 1, 1, 8),
('1F08', 'NorthHall', 'East', 0, 1, 1, 10),
('1F09', 'NorthHall', 'East', 1, 0, 1, 6),
('1F10', 'NorthHall', 'East', 1, 1, 0, 12),
('1F11', 'NorthHall', 'East', 0, 1, 1, 14),
('1F12', 'NorthHall', 'East', 1, 0, 0, 4),
('1F13', 'NorthHall', 'East', 1, 1, 1, 16),
('1F14', 'NorthHall', 'East', 0, 0, 1, 20),
('1F15', 'NorthHall', 'East', 1, 1, 0, 18),
('1F16', 'NorthHall', 'East', 1, 0, 1, 22),

('1W01', 'NorthHall', 'West', 1, 1, 1, 8),
('1W02', 'NorthHall', 'West', 0, 1, 1, 10),
('1W03', 'NorthHall', 'West', 1, 0, 1, 6),
('1W04', 'NorthHall', 'West', 1, 1, 0, 12),
('1W05', 'NorthHall', 'West', 0, 1, 1, 14),
('1W06', 'NorthHall', 'West', 1, 0, 0, 4),
('1W07', 'NorthHall', 'West', 1, 1, 1, 16),
('1W08', 'NorthHall', 'West', 0, 0, 1, 20),
('1W09', 'NorthHall', 'West', 1, 1, 0, 18),
('1W10', 'NorthHall', 'West', 1, 0, 1, 22),

('2A12', 'TechCentre', 'A', 1, 1, 1, 8),
('2A13', 'TechCentre', 'A', 0, 1, 1, 10),
('2A14', 'TechCentre', 'A', 1, 0, 1, 6),
('2A15', 'TechCentre', 'A', 1, 1, 0, 12),
('2A16', 'TechCentre', 'A', 0, 1, 1, 14),
('2A17', 'TechCentre', 'A', 1, 0, 0, 4),
('2A18', 'TechCentre', 'A', 1, 1, 1, 16),
('2A19', 'TechCentre', 'A', 0, 0, 1, 20),
('2A20', 'TechCentre', 'A', 1, 1, 0, 18),
('2A21', 'TechCentre', 'A', 1, 0, 1, 22),

('2B01', 'TechCentre', 'B', 1, 1, 1, 8),
('2B02', 'TechCentre', 'B', 0, 1, 1, 10),
('2B03', 'TechCentre', 'B', 1, 0, 1, 6),
('2B04', 'TechCentre', 'B', 1, 1, 0, 12),
('2B05', 'TechCentre', 'B', 0, 1, 1, 14),
('2B06', 'TechCentre', 'B', 1, 0, 0, 4),
('2B07', 'TechCentre', 'B', 1, 1, 1, 16),
('2B08', 'TechCentre', 'B', 0, 0, 1, 20),
('2B09', 'TechCentre', 'B', 1, 1, 0, 18),
('2B10', 'TechCentre', 'B', 1, 0, 1, 22),

('3B22', 'WestWing', 'B', 1, 1, 1, 8),
('3B23', 'WestWing', 'B', 0, 1, 1, 10),
('3B24', 'WestWing', 'B', 1, 0, 1, 6),
('3B25', 'WestWing', 'B', 1, 1, 0, 12),
('3B26', 'WestWing', 'B', 0, 1, 1, 14),
('3B27', 'WestWing', 'B', 1, 0, 0, 4),
('3B28', 'WestWing', 'B', 1, 1, 1, 16),
('3B29', 'WestWing', 'B', 0, 0, 1, 20),
('3B30', 'WestWing', 'B', 1, 1, 0, 18),
('3B31', 'WestWing', 'B', 1, 0, 1, 22),

('3C01', 'WestWing', 'C', 1, 1, 1, 8),
('3C02', 'WestWing', 'C', 0, 1, 1, 10),
('3C03', 'WestWing', 'C', 1, 0, 1, 6),
('3C04', 'WestWing', 'C', 1, 1, 0, 12),
('3C05', 'WestWing', 'C', 0, 1, 1, 14),
('3C06', 'WestWing', 'C', 1, 0, 0, 4),
('3C07', 'WestWing', 'C', 1, 1, 1, 16),
('3C08', 'WestWing', 'C', 0, 0, 1, 20),
('3C09', 'WestWing', 'C', 1, 1, 0, 18),
('3C10', 'WestWing', 'C', 1, 0, 1, 22),

('4C03', 'NorthHall', 'West', 1, 1, 1, 8),
('4C04', 'NorthHall', 'West', 0, 1, 1, 10),
('4C05', 'NorthHall', 'West', 1, 0, 1, 6),
('4C06', 'NorthHall', 'West', 1, 1, 0, 12),
('4C07', 'NorthHall', 'West', 0, 1, 1, 14),
('4C08', 'NorthHall', 'West', 1, 0, 0, 4),
('4C09', 'NorthHall', 'West', 1, 1, 1, 16),
('4C10', 'NorthHall', 'West', 0, 0, 1, 20),
('4C11', 'NorthHall', 'West', 1, 1, 0, 18),
('4C12', 'NorthHall', 'West', 1, 0, 1, 22),

('5T01', 'TechCentre', 'West', 1, 1, 1, 8),
('5T02', 'TechCentre', 'West', 0, 1, 1, 10),
('5T03', 'TechCentre', 'West', 1, 0, 1, 6),
('5T04', 'TechCentre', 'West', 1, 1, 0, 12),
('5T05', 'TechCentre', 'West', 0, 1, 1, 14),
('5T06', 'TechCentre', 'West', 1, 0, 0, 4),
('5T07', 'TechCentre', 'West', 1, 1, 1, 16),
('5T08', 'TechCentre', 'West', 0, 0, 1, 20),
('5T09', 'TechCentre', 'West', 1, 1, 0, 18),
('5T10', 'TechCentre', 'West', 1, 0, 1, 22),

('6W01', 'WestWing', 'D', 1, 1, 1, 8),
('6W02', 'WestWing', 'D', 0, 1, 1, 10),
('6W03', 'WestWing', 'D', 1, 0, 1, 6),
('6W04', 'WestWing', 'D', 1, 1, 0, 12),
('6W05', 'WestWing', 'D', 0, 1, 1, 14),
('6W06', 'WestWing', 'D', 1, 0, 0, 4),
('6W07', 'WestWing', 'D', 1, 1, 1, 16),
('6W08', 'WestWing', 'D', 0, 0, 1, 20),
('6W09', 'WestWing', 'D', 1, 1, 0, 18),
('6W10', 'WestWing', 'D', 1, 0, 1, 22),

('7N01', 'NorthHall', 'North', 1, 1, 1, 8),
('7N02', 'NorthHall', 'North', 0, 1, 1, 10),
('7N03', 'NorthHall', 'North', 1, 0, 1, 6),
('7N04', 'NorthHall', 'North', 1, 1, 0, 12),
('7N05', 'NorthHall', 'North', 0, 1, 1, 14),
('7N06', 'NorthHall', 'North', 1, 0, 0, 4),
('7N07', 'NorthHall', 'North', 1, 1, 1, 16),
('7N08', 'NorthHall', 'North', 0, 0, 1, 20),
('7N09', 'NorthHall', 'North', 1, 1, 0, 18),
('7N10', 'NorthHall', 'North', 1, 0, 1, 22),
('7N11', 'NorthHall', 'North', 1, 1, 1, 24),
('7N12', 'NorthHall', 'North', 0, 1, 0, 30);

-- Registered users
-- Passwords here are just placeholder test strings
INSERT INTO RegisteredUser (
    username,
    email,
    pass,
    firstName,
    lastName
) VALUES
('cg_user',       'colin@test.com',    'hashed_pw_1', 'Colin',   'Greenidge'),
('blippert',      'ben@test.com',      'hashed_pw_2', 'Benjamin','Lippert'),
('asmith',        'anna@test.com',     'hashed_pw_3', 'Anna',    'Smith'),
('jdoe',          'john@test.com',     'hashed_pw_4', 'John',    'Doe'),
('mnguyen',       'minh@test.com',     'hashed_pw_5', 'Minh',    'Nguyen'),
('sjohnson',      'sarah@test.com',    'hashed_pw_6', 'Sarah',   'Johnson');

-- These users will receive RUIDs 1000 to 1005 in the order inserted.

-- Unregistered users
INSERT INTO UnregisteredUser (
    nickname,
    email
) VALUES
('guest_alex',   'alex_guest@test.com'),
('guest_taylor', 'taylor_guest@test.com'),
('guest_jamie',  'jamie_guest@test.com'),
('walkin_kim',   'kim_walkin@test.com');

-- These unregistered users will receive URUIDs 1000 to 1003.

-- Bookings
INSERT INTO Booking (
    meetingDate,
    startTime,
    duration,
    numberOfConfirmations,
    meetingOwner,
    reminderSent,
    shareableLink,
    meetingRoom,
    meetingSize
) VALUES
('2026-03-20', '09:00:00', '01:00:00', 3, 1000, 0, 'bookez-1000-alpha',   '1F05', 4),
('2026-03-20', '11:00:00', '02:00:00', 5, 1001, 1, 'bookez-1001-design',  '2A10', 6),
('2026-03-21', '14:00:00', '01:30:00', 2, 1002, 0, 'bookez-1002-review',  '3B21', 3),
('2026-03-22', '08:30:00', '00:30:00', 1, 1003, 1, 'bookez-1003-sync',    '1F06', 2),
('2026-03-22', '15:00:00', '01:00:00', 4, 1004, 0, 'bookez-1004-client',  '4C01', 5),
('2026-03-23', '10:00:00', '03:00:00', 7, 1005, 0, 'bookez-1005-training','4C02', 10);

-- These bookings will receive BIDs 1000 to 1005.

-- Optional extra rooms tied to bookings
-- Useful if your system supports multi-room or overflow associations
INSERT INTO RoomsAssociatedWithBookings (BID, RID) VALUES
(1000, '1F05'),
(1001, '2A10'),
(1001, '2A11'),
(1002, '3B21'),
(1003, '1F06'),
(1004, '4C01'),
(1005, '4C02'),
(1005, '3B21');

-- Registered attendees
INSERT INTO RegisteredBookingAttendees (BID, RegisteredAttendee) VALUES
(1000, 1001),
(1000, 1002),
(1000, 1003),

(1001, 1000),
(1001, 1002),
(1001, 1004),
(1001, 1005),

(1002, 1003),
(1002, 1005),

(1003, 1001),

(1004, 1000),
(1004, 1002),
(1004, 1003),

(1005, 1000),
(1005, 1001),
(1005, 1002),
(1005, 1003),
(1005, 1004);

-- Unregistered attendees
INSERT INTO UnregisteredBookingAttendees (BID, unregisteredAttendee) VALUES
(1000, 1000),
(1001, 1001),
(1002, 1002),
(1004, 1003);

-- Reset AUTO_INCREMENT to the next clean values after seeded inserts
ALTER TABLE RegisteredUser AUTO_INCREMENT = 1006;
ALTER TABLE UnregisteredUser AUTO_INCREMENT = 1004;
ALTER TABLE Booking AUTO_INCREMENT = 1006;
