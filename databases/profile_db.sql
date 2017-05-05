USE gymplanner;

-- USER PROFILE --
DROP TABLE IF EXISTS USERS;
CREATE TABLE USERS (
    uid char(25),
    name char(20),
    email text,
    photo text,
    family_name char(20),
    given_name char(20),
    gender char(8),
    dob date,
    bas_ctr int,  -- bas: Basketball
    str_ctr int,  -- str: Strength
    car_ctr int,  -- car: Cardio
    swi_ctr int,  -- swi: Swimming
    squ_ctr int,  -- squ: Squash
    ctr int,
    rating int,
    rating_ctr int,
    signup_date date,
    lat float,
    lng float,
    PRIMARY KEY(uid)
);

-- BUS TABLE --
DROP TABLE IF EXISTS BUS;
CREATE TABLE BUS (
	bid int,
    line char(20),
	departure_time time,
	primary key (bid)
);

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
