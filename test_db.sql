DROP TABLE IF EXISTS Users;
CREATE TABLE Users 
(uid int,
password VARCHAR(20),
name char(20),
email text, 
PRIMARY KEY(uid)
);

DROP TABLE IF EXISTS BUS;
CREATE TABLE BUS (
	bid int,
    line char(20),
	departure_time time,
	primary key (bid)
);


DROP TABLE IF EXISTS Reservation;
CREATE TABLE Reservation ( rid int,  uid int, timeslot char(20),  review char(20), primary key (rid) );


insert into Users values
(1,'admin','admin', 'admin@columbia.edu');



insert into BUS values
(1,'Blue Line' , '10:05:00'),
(2,'Blue Line' , '11:05:00'),
(3,'Blue Line' , '12:35:00'),
(4,'Blue Line' , '14:05:00'),
(5,'Blue Line' , '15:05:00'),
(6,'Blue Line' , '16:05:00'),
(7,'Red Line' , '10:35:00'),
(8,'Red Line' , '11:35:00'),
(9,'Red Line' , '13:35:00'),
(10,'Red Line' , '14:35:00'),
(11,'Red Line' , '15:35:00'),
(12,'Red Line' , '16:35:00'),
(13,'Green Line' , '09:15:00'),
(14,'Green Line' , '10:50:00'),
(15,'Green Line' , '12:05:00'),
(16,'Green Line' , '13:05:00'),
(17,'Green Line' , '15:20:00'),
(18,'Green Line' , '16:20:00'),
(19,'Blue Line' , '20:05:00'),
(20,'Blue Line' , '22:05:00'),
(21,'Blue Line' , '23:05:00'),
(22,'Blue Line' , '24:05:00');