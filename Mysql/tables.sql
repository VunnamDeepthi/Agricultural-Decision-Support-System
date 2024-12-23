CREATE TABLE crop (
    idc INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    date DATE,
    input VARCHAR(255),
    prediction VARCHAR(255),
    rating INT,
    review TEXT,
    FOREIGN KEY (user_id) REFERENCES user(id)
);

CREATE TABLE fert (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    date DATE,
    input VARCHAR(255),
    prediction VARCHAR(255),
    rating INT,
    review TEXT,
    FOREIGN KEY (user_id) REFERENCES user(id)
);


CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    password VARCHAR(50),
    phoneno VARCHAR(255),
    age INT,
    Occupation VARCHAR(255),
    Crop_cultivating VARCHAR(255)
);

CREATE TABLE contact_us (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255),
    message TEXT
);

CREATE TABLE dis (
	id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
	image LONGBLOB,
	prediction VARCHAR(255),
	supplement VARCHAR(255),
	rating INT,
	review TEXT,
    FOREIGN KEY (user_id) REFERENCES user(id)
);


