DROP DATABASE IF EXISTS soloDB;
CREATE DATABASE soloDB;
USE soloDB;

CREATE TABLE temperature_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ip_address VARCHAR(15),
    temperature_celsius FLOAT,
    temperature_fahrenheit FLOAT,
    incheon_min_temp FLOAT,
    incheon_max_temp FLOAT,
    date DATETIME
);
SELECT * FROM temperature_data;