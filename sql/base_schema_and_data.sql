CREATE DATABASE IF NOT EXISTS booking_system
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE booking_system;
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS payment_holds;
DROP TABLE IF EXISTS email_confirmations;
DROP TABLE IF EXISTS reservations;
DROP TABLE IF EXISTS rooms;
DROP TABLE IF EXISTS room_types;
DROP TABLE IF EXISTS hotels;
DROP TABLE IF EXISTS locations;
DROP TABLE IF EXISTS hotel_chains;
DROP TABLE IF EXISTS users;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE users (
  user_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  first_name VARCHAR(50) NOT NULL,
  last_name VARCHAR(50) NOT NULL,
  email VARCHAR(100) NOT NULL,
  phone_number VARCHAR(20),
  registration_date DATE NOT NULL,
  UNIQUE KEY idx_user_email (email)
) ENGINE=InnoDB;

CREATE TABLE hotel_chains (
  chain_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  description TEXT
) ENGINE=InnoDB;

CREATE TABLE locations (
  location_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  country VARCHAR(50) NOT NULL,
  city VARCHAR(50) NOT NULL,
  zip_code VARCHAR(20),
  KEY idx_locations_country_city (country, city)
) ENGINE=InnoDB;

CREATE TABLE hotels (
  hotel_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  chain_id BIGINT NULL,
  location_id BIGINT NOT NULL,
  star_rating INT NULL,
  address VARCHAR(255) NOT NULL,
  KEY idx_hotels_location (location_id),
  KEY idx_hotels_chain (chain_id),
  CONSTRAINT fk_hotels_chains FOREIGN KEY (chain_id)
    REFERENCES hotel_chains(chain_id) ON DELETE SET NULL,
  CONSTRAINT fk_hotels_locations FOREIGN KEY (location_id)
    REFERENCES locations(location_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE room_types (
  room_type_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  hotel_id BIGINT NOT NULL,
  type_name VARCHAR(50) NOT NULL,
  base_price DECIMAL(10,2) NOT NULL,
  max_guests INT NOT NULL,
  KEY idx_room_types_hotel (hotel_id),
  CONSTRAINT fk_room_types_hotels FOREIGN KEY (hotel_id)
    REFERENCES hotels(hotel_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE rooms (
  room_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  hotel_id BIGINT NOT NULL,
  room_type_id BIGINT NOT NULL,
  room_number VARCHAR(20) NOT NULL,
  is_available BOOLEAN DEFAULT TRUE,
  UNIQUE KEY uq_rooms_hotel_number (hotel_id, room_number),
  KEY idx_rooms_type (room_type_id),
  CONSTRAINT fk_rooms_hotels FOREIGN KEY (hotel_id)
    REFERENCES hotels(hotel_id) ON DELETE CASCADE,
  CONSTRAINT fk_rooms_types FOREIGN KEY (room_type_id)
    REFERENCES room_types(room_type_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE reservations (
  reservation_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT NOT NULL,
  room_id BIGINT NOT NULL,
  check_in_date DATE NOT NULL,
  check_out_date DATE NOT NULL,
  total_price DECIMAL(10,2) NOT NULL,
  status VARCHAR(20) DEFAULT 'Pending',
  KEY idx_reservation_dates (check_in_date, check_out_date),
  KEY idx_reservations_user (user_id),
  KEY idx_reservations_room (room_id),
  CONSTRAINT fk_reservations_users FOREIGN KEY (user_id)
    REFERENCES users(user_id) ON DELETE CASCADE,
  CONSTRAINT fk_reservations_rooms FOREIGN KEY (room_id)
    REFERENCES rooms(room_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE email_confirmations (
  email_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT NOT NULL,
  reservation_id BIGINT NULL,
  email_type VARCHAR(50) NOT NULL,
  sent_date DATETIME NOT NULL,
  KEY idx_email_confirmations_user (user_id),
  KEY idx_email_confirmations_reservation (reservation_id),
  CONSTRAINT fk_emails_users FOREIGN KEY (user_id)
    REFERENCES users(user_id) ON DELETE CASCADE,
  CONSTRAINT fk_emails_reservations FOREIGN KEY (reservation_id)
    REFERENCES reservations(reservation_id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE payment_holds (
  hold_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  reservation_id BIGINT NOT NULL,
  amount DECIMAL(10,2) NOT NULL,
  hold_status VARCHAR(20) NOT NULL,
  hold_date DATETIME NOT NULL,
  KEY idx_payment_holds_reservation (reservation_id),
  CONSTRAINT fk_holds_reservations FOREIGN KEY (reservation_id)
    REFERENCES reservations(reservation_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE reviews (
  review_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT NOT NULL,
  hotel_id BIGINT NOT NULL,
  rating INT NOT NULL,
  comment TEXT,
  review_date DATE NOT NULL,
  KEY idx_reviews_user (user_id),
  KEY idx_reviews_hotel (hotel_id),
  CONSTRAINT fk_reviews_users FOREIGN KEY (user_id)
    REFERENCES users(user_id) ON DELETE CASCADE,
  CONSTRAINT fk_reviews_hotels FOREIGN KEY (hotel_id)
    REFERENCES hotels(hotel_id) ON DELETE CASCADE
) ENGINE=InnoDB;

INSERT INTO users (user_id, first_name, last_name, email, phone_number, registration_date) VALUES
(1,'Іван','Петренко','ivan.p@gmail.com','+380501234567','2025-01-10'),
(2,'Олена','Коваль','olena.koval@ukr.net','+380671234567','2025-02-15'),
(3,'Андрій','Мельник','andriy.mel@gmail.com','+380931234567','2025-03-20'),
(4,'Марія','Шевченко','masha.shev@gmail.com','+380509998877','2025-04-05'),
(5,'Віталій','Бойко','vitaliy.b@ukr.net','+380679998877','2025-05-11'),
(6,'John','Doe','john.doe@gmail.com','+14155551234','2025-06-12'),
(7,'Anna','Smith','anna.smith@yahoo.com','+14155555678','2025-07-22'),
(8,'Олег','Гриценко','oleg.g@gmail.com','+380991112233','2025-08-30'),
(9,'Наталія','Ткачук','nataliya.t@ukr.net','+380971112233','2025-09-01'),
(10,'Сергій','Романенко','sergiy.r@gmail.com','+380731112233','2025-10-10');

INSERT INTO hotel_chains (chain_id, name, description) VALUES
(1,'Hilton','Міжнародна мережа готелів преміум-класу'),
(2,'Marriott','Велика американська транснаціональна компанія'),
(3,'Radisson','Міжнародна готельна мережа бізнес-класу'),
(4,'Reikartz','Готельна мережа в Україні'),
(5,'Accor','Французька міжнародна готельна група'),
(6,'InterContinental','Міжнародна мережа готелів'),
(7,'Hyatt','Американська мережа готелів вищого класу'),
(8,'Ibis','Міжнародна мережа бюджетних готелів'),
(9,'Premier Hotels','Колекція українських готелів'),
(10,'Boutique Collection','Мережа невеликих ексклюзивних готелів');

INSERT INTO locations (location_id, country, city, zip_code) VALUES
(1,'Україна','Київ','01001'),
(2,'Україна','Львів','79000'),
(3,'Україна','Одеса','65000'),
(4,'Україна','Харків','61000'),
(5,'Україна','Буковель','78593'),
(6,'Польща','Варшава','00-001'),
(7,'Польща','Краків','30-001'),
(8,'Чехія','Прага','110 00'),
(9,'США','Нью-Йорк','10001'),
(10,'Франція','Париж','75000');

INSERT INTO hotels (hotel_id, name, chain_id, location_id, star_rating, address) VALUES
(1,'Hilton Kyiv',1,1,5,'бульвар Тараса Шевченка, 30'),
(2,'Grand Hotel Lviv',9,2,5,'проспект Свободи, 13'),
(3,'Reikartz Odesa',4,3,4,'вул. Олександрівська, 20'),
(4,'Radisson Blu Podil',3,1,4,'вул. Братська, 17'),
(5,'Radisson Resort Bukovel',3,5,5,'Щивка 220'),
(6,'Ibis Warsaw Stare Miasto',8,6,3,'ul. Muranowska 2'),
(7,'Hyatt Regency Kyiv',7,1,5,'вул. Алли Тарасової, 5'),
(8,'Premier Palace Hotel',9,1,5,'бульвар Тараса Шевченка/Пушкінська, 5-7/29'),
(9,'Boutique Hotel Prague',10,8,4,'Karlova 15'),
(10,'Marriott New York',2,9,5,'1535 Broadway');

INSERT INTO room_types (room_type_id, hotel_id, type_name, base_price, max_guests) VALUES
(1,1,'Standard Single',3500.00,1),
(2,1,'Deluxe Double',5500.00,2),
(3,2,'Classic Twin',2800.00,2),
(4,2,'Executive Suite',8500.00,3),
(5,3,'Standard Sea View',3200.00,2),
(6,4,'Business Class Room',4500.00,2),
(7,5,'Mountain View Suite',7000.00,4),
(8,6,'Economy Twin',1500.00,2),
(9,7,'Presidential Suite',25000.00,4),
(10,8,'Premium King',6000.00,2);

INSERT INTO rooms (room_id, hotel_id, room_type_id, room_number, is_available) VALUES
(1,1,1,'101',TRUE),
(2,1,2,'102',FALSE),
(3,2,3,'201',TRUE),
(4,2,4,'202',TRUE),
(5,3,5,'305',FALSE),
(6,4,6,'410',TRUE),
(7,5,7,'501',FALSE),
(8,6,8,'11',TRUE),
(9,7,9,'777',TRUE),
(10,8,10,'801',FALSE);

INSERT INTO reservations (reservation_id, user_id, room_id, check_in_date, check_out_date, total_price, status) VALUES
(1,1,2,'2026-10-01','2026-10-05',22000.00,'Confirmed'),
(2,2,5,'2026-10-10','2026-10-12',6400.00,'Confirmed'),
(3,3,7,'2026-12-25','2026-12-30',35000.00,'Confirmed'),
(4,4,10,'2026-11-01','2026-11-03',12000.00,'Confirmed'),
(5,5,1,'2026-10-20','2026-10-22',7000.00,'Pending'),
(6,6,3,'2026-10-15','2026-10-18',8400.00,'Cancelled'),
(7,7,9,'2026-11-20','2026-11-25',125000.00,'Pending'),
(8,8,4,'2026-12-01','2026-12-05',34000.00,'Confirmed'),
(9,9,6,'2026-10-05','2026-10-07',9000.00,'Confirmed'),
(10,10,8,'2026-11-10','2026-11-15',7500.00,'Cancelled');

INSERT INTO email_confirmations (email_id, user_id, reservation_id, email_type, sent_date) VALUES
(1,1,1,'Reservation_Confirm','2026-09-15 10:00:00'),
(2,2,2,'Reservation_Confirm','2026-09-20 11:30:00'),
(3,3,3,'Reservation_Confirm','2026-09-25 09:15:00'),
(4,4,4,'Reservation_Confirm','2026-10-01 14:20:00'),
(5,5,NULL,'Registration','2026-05-11 08:00:00'),
(6,6,6,'Cancellation','2026-10-02 16:45:00'),
(7,7,7,'Payment_Reminder','2026-11-10 10:00:00'),
(8,8,8,'Reservation_Confirm','2026-10-15 11:11:00'),
(9,9,9,'Reservation_Confirm','2026-09-28 12:00:00'),
(10,10,10,'Cancellation','2026-10-30 09:30:00');

INSERT INTO payment_holds (hold_id, reservation_id, amount, hold_status, hold_date) VALUES
(1,1,22000.00,'Captured','2026-09-15 10:05:00'),
(2,2,6400.00,'Captured','2026-09-20 11:35:00'),
(3,3,35000.00,'Captured','2026-09-25 09:20:00'),
(4,4,12000.00,'Captured','2026-10-01 14:25:00'),
(5,5,7000.00,'Held','2026-10-18 10:00:00'),
(6,6,8400.00,'Released','2026-10-02 16:50:00'),
(7,7,125000.00,'Held','2026-11-18 09:00:00'),
(8,8,34000.00,'Captured','2026-10-15 11:15:00'),
(9,9,9000.00,'Captured','2026-09-28 12:05:00'),
(10,10,7500.00,'Released','2026-10-30 09:35:00');

INSERT INTO reviews (review_id, user_id, hotel_id, rating, comment, review_date) VALUES
(1,1,1,5,'Чудовий готель у самому центрі Києва. Все на високому рівні.','2026-10-06'),
(2,2,3,4,'Гарний вид на море, але сніданки могли б бути кращими.','2026-10-13'),
(3,3,5,5,'Неймовірний відпочинок у горах! Рекомендую.','2026-12-31'),
(4,4,8,5,'Розкішний готель, дуже зручне ліжко.','2026-11-04'),
(5,6,2,4,'Все сподобалося, гарна локація.','2026-10-19'),
(6,8,4,5,'Чудовий сервіс, зручно для бізнес-поїздки.','2026-12-06'),
(7,9,4,4,'Чисто, охайно, смачна кава.','2026-10-08'),
(8,10,6,3,'Звичайний бюджетний готель. На одну ніч піде.','2026-11-16'),
(9,1,7,5,'Зупинявся раніше, Hyatt як завжди бездоганний.','2025-11-20'),
(10,2,1,5,'Прекрасний сервіс та басейн.','2026-05-15');
