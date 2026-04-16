CREATE DATABASE IF NOT EXISTS BookEZDatabase;
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
-- Includes all rooms referenced later by Booking and RoomsAssociatedWithBookings
INSERT INTO Room (
    roomNumber,
    companyBuilding,
    wing,
    wheelchairAccessible,
    projectorAccess,
    whiteboardAccess,
    maximumCapacity
) VALUES
('1F05', 'NorthHall', 'East', 1, 1, 1, 8),
('1F06', 'NorthHall', 'East', 1, 0, 1, 6),
('1F07', 'NorthHall', 'East', 1, 1, 1, 8),
('1F08', 'NorthHall', 'East', 0, 1, 1, 10),
('1F09', 'NorthHall', 'East', 1, 0, 1, 6),
('1F10', 'NorthHall', 'East', 1, 1, 0, 12),
('1F11', 'NorthHall', 'East', 0, 1, 1, 14),

('1W01', 'NorthHall', 'West', 1, 1, 1, 8),
('1W02', 'NorthHall', 'West', 0, 1, 1, 10),
('1W03', 'NorthHall', 'West', 1, 0, 1, 6),
('1W04', 'NorthHall', 'West', 1, 1, 0, 12),
('1W05', 'NorthHall', 'West', 0, 1, 1, 14),

('2A10', 'TechCentre', 'A', 1, 1, 1, 12),
('2A11', 'TechCentre', 'A', 0, 1, 0, 10),
('2A12', 'TechCentre', 'A', 1, 1, 1, 8),
('2A13', 'TechCentre', 'A', 0, 1, 1, 10),
('2A14', 'TechCentre', 'A', 1, 0, 1, 6),
('2A15', 'TechCentre', 'A', 1, 1, 0, 12),
('2A16', 'TechCentre', 'A', 0, 1, 1, 14),

('2B01', 'TechCentre', 'B', 1, 1, 1, 8),
('2B02', 'TechCentre', 'B', 0, 1, 1, 10),
('2B03', 'TechCentre', 'B', 1, 0, 1, 6),
('2B04', 'TechCentre', 'B', 1, 1, 0, 12),
('2B05', 'TechCentre', 'B', 0, 1, 1, 14),

('3B21', 'WestWing', 'B', 0, 1, 1, 20),
('3B22', 'WestWing', 'B', 1, 1, 1, 8),
('3B23', 'WestWing', 'B', 0, 1, 1, 10),
('3B24', 'WestWing', 'B', 1, 0, 1, 6),
('3B25', 'WestWing', 'B', 1, 1, 0, 12),
('3B26', 'WestWing', 'B', 0, 1, 1, 14),

('3C01', 'WestWing', 'C', 1, 1, 1, 8),
('3C02', 'WestWing', 'C', 0, 1, 1, 10),
('3C03', 'WestWing', 'C', 1, 0, 1, 6),
('3C04', 'WestWing', 'C', 1, 1, 0, 12),
('3C05', 'WestWing', 'C', 0, 1, 1, 14),

('4C01', 'NorthHall', 'West', 1, 1, 0, 15),
('4C02', 'TechCentre', 'West', 1, 0, 1, 25);

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


-- EXTRA TEST ROOMS
INSERT INTO Room (
    roomNumber,
    companyBuilding,
    wing,
    wheelchairAccessible,
    projectorAccess,
    whiteboardAccess,
    maximumCapacity
) VALUES
('R050', 'NorthHall', 'Test', 1, 1, 1, 15),
('R051', 'NorthHall', 'Test', 1, 1, 1, 16),
('R052', 'NorthHall', 'Test', 1, 1, 1, 17),
('R053', 'NorthHall', 'Test', 1, 1, 1, 18),
('R054', 'NorthHall', 'Test', 1, 1, 1, 19),
('R055', 'NorthHall', 'Test', 1, 1, 1, 20),
('R056', 'NorthHall', 'Test', 1, 1, 1, 21),
('R057', 'NorthHall', 'Test', 1, 1, 1, 22),
('R058', 'NorthHall', 'Test', 1, 1, 1, 23),
('R059', 'NorthHall', 'Test', 1, 1, 1, 24),
('R060', 'NorthHall', 'Test', 1, 1, 1, 5),
('R061', 'NorthHall', 'Test', 1, 1, 1, 6),
('R062', 'NorthHall', 'Test', 1, 1, 1, 7),
('R063', 'NorthHall', 'Test', 1, 1, 1, 8),
('R064', 'NorthHall', 'Test', 1, 1, 1, 9),
('R065', 'NorthHall', 'Test', 1, 1, 1, 10),
('R066', 'NorthHall', 'Test', 1, 1, 1, 11),
('R067', 'NorthHall', 'Test', 1, 1, 1, 12),
('R068', 'NorthHall', 'Test', 1, 1, 1, 13),
('R069', 'NorthHall', 'Test', 1, 1, 1, 14),
('R070', 'NorthHall', 'Test', 1, 1, 1, 15),
('R071', 'NorthHall', 'Test', 1, 1, 1, 16),
('R072', 'NorthHall', 'Test', 1, 1, 1, 17),
('R073', 'NorthHall', 'Test', 1, 1, 1, 18),
('R074', 'NorthHall', 'Test', 1, 1, 1, 19),
('R075', 'NorthHall', 'Test', 1, 1, 1, 20),
('R076', 'NorthHall', 'Test', 1, 1, 1, 21),
('R077', 'NorthHall', 'Test', 1, 1, 1, 22),
('R078', 'NorthHall', 'Test', 1, 1, 1, 23),
('R079', 'NorthHall', 'Test', 1, 1, 1, 24),
('R080', 'NorthHall', 'Test', 1, 1, 1, 5),
('R081', 'NorthHall', 'Test', 1, 1, 1, 6),
('R082', 'NorthHall', 'Test', 1, 1, 1, 7),
('R083', 'NorthHall', 'Test', 1, 1, 1, 8),
('R084', 'NorthHall', 'Test', 1, 1, 1, 9),
('R085', 'NorthHall', 'Test', 1, 1, 1, 10),
('R086', 'NorthHall', 'Test', 1, 1, 1, 11),
('R087', 'NorthHall', 'Test', 1, 1, 1, 12),
('R088', 'NorthHall', 'Test', 1, 1, 1, 13),
('R089', 'NorthHall', 'Test', 1, 1, 1, 14),
('R090', 'NorthHall', 'Test', 1, 1, 1, 15),
('R091', 'NorthHall', 'Test', 1, 1, 1, 16),
('R092', 'NorthHall', 'Test', 1, 1, 1, 17),
('R093', 'NorthHall', 'Test', 1, 1, 1, 18),
('R094', 'NorthHall', 'Test', 1, 1, 1, 19),
('R095', 'NorthHall', 'Test', 1, 1, 1, 20),
('R096', 'NorthHall', 'Test', 1, 1, 1, 21),
('R097', 'NorthHall', 'Test', 1, 1, 1, 22),
('R098', 'NorthHall', 'Test', 1, 1, 1, 23),
('R099', 'NorthHall', 'Test', 1, 1, 1, 24),
('R100', 'NorthHall', 'Test', 1, 1, 1, 5),
('R101', 'NorthHall', 'Test', 1, 1, 1, 6),
('R102', 'NorthHall', 'Test', 1, 1, 1, 7),
('R103', 'NorthHall', 'Test', 1, 1, 1, 8),
('R104', 'NorthHall', 'Test', 1, 1, 1, 9),
('R105', 'NorthHall', 'Test', 1, 1, 1, 10),
('R106', 'NorthHall', 'Test', 1, 1, 1, 11),
('R107', 'NorthHall', 'Test', 1, 1, 1, 12),
('R108', 'NorthHall', 'Test', 1, 1, 1, 13),
('R109', 'NorthHall', 'Test', 1, 1, 1, 14),
('R110', 'NorthHall', 'Test', 1, 1, 1, 15),
('R111', 'NorthHall', 'Test', 1, 1, 1, 16),
('R112', 'NorthHall', 'Test', 1, 1, 1, 17),
('R113', 'NorthHall', 'Test', 1, 1, 1, 18),
('R114', 'NorthHall', 'Test', 1, 1, 1, 19),
('R115', 'NorthHall', 'Test', 1, 1, 1, 20),
('R116', 'NorthHall', 'Test', 1, 1, 1, 21),
('R117', 'NorthHall', 'Test', 1, 1, 1, 22),
('R118', 'NorthHall', 'Test', 1, 1, 1, 23),
('R119', 'NorthHall', 'Test', 1, 1, 1, 24),
('R120', 'NorthHall', 'Test', 1, 1, 1, 5),
('R121', 'NorthHall', 'Test', 1, 1, 1, 6),
('R122', 'NorthHall', 'Test', 1, 1, 1, 7),
('R123', 'NorthHall', 'Test', 1, 1, 1, 8),
('R124', 'NorthHall', 'Test', 1, 1, 1, 9),
('R125', 'NorthHall', 'Test', 1, 1, 1, 10),
('R126', 'NorthHall', 'Test', 1, 1, 1, 11),
('R127', 'NorthHall', 'Test', 1, 1, 1, 12),
('R128', 'NorthHall', 'Test', 1, 1, 1, 13),
('R129', 'NorthHall', 'Test', 1, 1, 1, 14),
('R130', 'NorthHall', 'Test', 1, 1, 1, 15),
('R131', 'NorthHall', 'Test', 1, 1, 1, 16),
('R132', 'NorthHall', 'Test', 1, 1, 1, 17),
('R133', 'NorthHall', 'Test', 1, 1, 1, 18),
('R134', 'NorthHall', 'Test', 1, 1, 1, 19),
('R135', 'NorthHall', 'Test', 1, 1, 1, 20),
('R136', 'NorthHall', 'Test', 1, 1, 1, 21),
('R137', 'NorthHall', 'Test', 1, 1, 1, 22),
('R138', 'NorthHall', 'Test', 1, 1, 1, 23),
('R139', 'NorthHall', 'Test', 1, 1, 1, 24),
('R140', 'NorthHall', 'Test', 1, 1, 1, 5),
('R141', 'NorthHall', 'Test', 1, 1, 1, 6),
('R142', 'NorthHall', 'Test', 1, 1, 1, 7),
('R143', 'NorthHall', 'Test', 1, 1, 1, 8),
('R144', 'NorthHall', 'Test', 1, 1, 1, 9),
('R145', 'NorthHall', 'Test', 1, 1, 1, 10),
('R146', 'NorthHall', 'Test', 1, 1, 1, 11),
('R147', 'NorthHall', 'Test', 1, 1, 1, 12),
('R148', 'NorthHall', 'Test', 1, 1, 1, 13),
('R149', 'NorthHall', 'Test', 1, 1, 1, 14);