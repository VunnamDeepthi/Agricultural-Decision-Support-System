use test;

select * From crop;
select* from fert;
select* from user;
select* from contact_us;
select* from dis;


SET SQL_SAFE_UPDATES = 0;

delete from fert ;
drop table dis;

CREATE TABLE disease (
	id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    date Date,
	image LONGBLOB,
	prediction VARCHAR(255),
	supplement VARCHAR(255),
	rating INT,
	review TEXT,
    FOREIGN KEY (user_id) REFERENCES user(id)
);