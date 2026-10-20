CREATE DATABASE IF NOT EXISTS booking_system
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE booking_system;
SET NAMES utf8mb4;

CREATE TABLE IF NOT EXISTS hotel_notes (
    note_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    hotel_id BIGINT NOT NULL,
    title VARCHAR(100) NOT NULL,
    note_text TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    KEY idx_hotel_notes_hotel (hotel_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS reservation_delete_log (
    log_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    deleted_reservation_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    room_id BIGINT NOT NULL,
    check_in_date DATE NOT NULL,
    check_out_date DATE NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    reservation_status VARCHAR(20),
    deleted_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    KEY idx_reservation_delete_log_id (deleted_reservation_id),
    KEY idx_reservation_delete_log_time (deleted_at)
) ENGINE=InnoDB;

DROP TRIGGER IF EXISTS bi_hotel_notes_validate_hotel;
DROP TRIGGER IF EXISTS bu_hotel_notes_validate_hotel;
DROP TRIGGER IF EXISTS bu_hotels_protect_note_parent_id;
DROP TRIGGER IF EXISTS ad_hotels_remove_notes;
DROP TRIGGER IF EXISTS bi_reservations_validate_dates_price;
DROP TRIGGER IF EXISTS bu_reservations_validate_dates_price;
DROP TRIGGER IF EXISTS ad_reservations_write_delete_log;

DROP PROCEDURE IF EXISTS sp_add_hotel_note;
DROP PROCEDURE IF EXISTS sp_add_review_by_names;
DROP PROCEDURE IF EXISTS sp_insert_ten_noname;
DROP PROCEDURE IF EXISTS sp_show_reservation_metric;
DROP PROCEDURE IF EXISTS sp_split_users_with_cursor;
DROP FUNCTION IF EXISTS fn_reservation_metric;

DELIMITER $$

CREATE TRIGGER bi_hotel_notes_validate_hotel
BEFORE INSERT ON hotel_notes
FOR EACH ROW
BEGIN
    DECLARE v_exists INT DEFAULT 0;
    SELECT COUNT(*) INTO v_exists FROM hotels WHERE hotel_id = NEW.hotel_id;
    IF v_exists = 0 THEN
        SIGNAL SQLSTATE '45000'
          SET MESSAGE_TEXT = 'hotel_notes.hotel_id must reference an existing hotel';
    END IF;
END$$

CREATE TRIGGER bu_hotel_notes_validate_hotel
BEFORE UPDATE ON hotel_notes
FOR EACH ROW
BEGIN
    DECLARE v_exists INT DEFAULT 0;
    SELECT COUNT(*) INTO v_exists FROM hotels WHERE hotel_id = NEW.hotel_id;
    IF v_exists = 0 THEN
        SIGNAL SQLSTATE '45000'
          SET MESSAGE_TEXT = 'hotel_notes.hotel_id must reference an existing hotel';
    END IF;
END$$

CREATE TRIGGER ad_hotels_remove_notes
AFTER DELETE ON hotels
FOR EACH ROW
BEGIN
    DELETE FROM hotel_notes WHERE hotel_id = OLD.hotel_id;
END$$

CREATE TRIGGER bu_hotels_protect_note_parent_id
BEFORE UPDATE ON hotels
FOR EACH ROW
BEGIN
    DECLARE v_children INT DEFAULT 0;
    IF NEW.hotel_id <> OLD.hotel_id THEN
        SELECT COUNT(*) INTO v_children FROM hotel_notes WHERE hotel_id = OLD.hotel_id;
        IF v_children > 0 THEN
            SIGNAL SQLSTATE '45000'
              SET MESSAGE_TEXT = 'hotel_id cannot change while hotel_notes reference it';
        END IF;
    END IF;
END$$

CREATE TRIGGER bi_reservations_validate_dates_price
BEFORE INSERT ON reservations
FOR EACH ROW
BEGIN
    IF NEW.check_out_date <= NEW.check_in_date THEN
        SIGNAL SQLSTATE '45000'
          SET MESSAGE_TEXT = 'check_out_date must be later than check_in_date';
    END IF;
    IF NEW.total_price <= 0 THEN
        SIGNAL SQLSTATE '45000'
          SET MESSAGE_TEXT = 'total_price must be greater than zero';
    END IF;
END$$

CREATE TRIGGER bu_reservations_validate_dates_price
BEFORE UPDATE ON reservations
FOR EACH ROW
BEGIN
    IF NEW.check_out_date <= NEW.check_in_date THEN
        SIGNAL SQLSTATE '45000'
          SET MESSAGE_TEXT = 'check_out_date must be later than check_in_date';
    END IF;
    IF NEW.total_price <= 0 THEN
        SIGNAL SQLSTATE '45000'
          SET MESSAGE_TEXT = 'total_price must be greater than zero';
    END IF;
END$$

CREATE TRIGGER ad_reservations_write_delete_log
AFTER DELETE ON reservations
FOR EACH ROW
BEGIN
    INSERT INTO reservation_delete_log (
        deleted_reservation_id, user_id, room_id, check_in_date,
        check_out_date, total_price, reservation_status, deleted_at
    ) VALUES (
        OLD.reservation_id, OLD.user_id, OLD.room_id, OLD.check_in_date,
        OLD.check_out_date, OLD.total_price, OLD.status, CURRENT_TIMESTAMP
    );
END$$

CREATE PROCEDURE sp_add_hotel_note(
    IN p_hotel_id BIGINT,
    IN p_title VARCHAR(100),
    IN p_note_text TEXT
)
BEGIN
    IF p_title IS NULL OR CHAR_LENGTH(TRIM(p_title)) = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'title must not be empty';
    END IF;
    IF p_note_text IS NULL OR CHAR_LENGTH(TRIM(p_note_text)) = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'note_text must not be empty';
    END IF;

    INSERT INTO hotel_notes (hotel_id, title, note_text)
    VALUES (p_hotel_id, p_title, p_note_text);

    SELECT LAST_INSERT_ID() AS note_id, p_hotel_id AS hotel_id,
           p_title AS title, p_note_text AS note_text;
END$$

CREATE PROCEDURE sp_add_review_by_names(
    IN p_first_name VARCHAR(50),
    IN p_last_name VARCHAR(50),
    IN p_hotel_name VARCHAR(100),
    IN p_rating INT,
    IN p_comment TEXT,
    IN p_review_date DATE
)
BEGIN
    DECLARE v_user_count INT DEFAULT 0;
    DECLARE v_hotel_count INT DEFAULT 0;
    DECLARE v_user_id BIGINT DEFAULT NULL;
    DECLARE v_hotel_id BIGINT DEFAULT NULL;

    IF p_rating < 1 OR p_rating > 5 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'rating must be from 1 to 5';
    END IF;

    SELECT COUNT(*), MIN(user_id)
      INTO v_user_count, v_user_id
      FROM users
     WHERE first_name = p_first_name AND last_name = p_last_name;

    IF v_user_count <> 1 THEN
        SIGNAL SQLSTATE '45000'
          SET MESSAGE_TEXT = 'First name and last name must identify exactly one user';
    END IF;

    SELECT COUNT(*), MIN(hotel_id)
      INTO v_hotel_count, v_hotel_id
      FROM hotels
     WHERE name = p_hotel_name;

    IF v_hotel_count <> 1 THEN
        SIGNAL SQLSTATE '45000'
          SET MESSAGE_TEXT = 'Hotel name must identify exactly one hotel';
    END IF;

    INSERT INTO reviews (user_id, hotel_id, rating, comment, review_date)
    VALUES (v_user_id, v_hotel_id, p_rating, p_comment, COALESCE(p_review_date, CURRENT_DATE));

    SELECT LAST_INSERT_ID() AS review_id, v_user_id AS user_id,
           v_hotel_id AS hotel_id, p_rating AS rating;
END$$

CREATE PROCEDURE sp_insert_ten_noname(IN p_start_number INT)
BEGIN
    DECLARE v_offset INT DEFAULT 0;
    IF p_start_number IS NULL OR p_start_number < 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'start_number must be a non-negative integer';
    END IF;

    WHILE v_offset < 10 DO
        INSERT INTO hotel_chains (name, description)
        VALUES (CONCAT('Noname', p_start_number + v_offset),
                'Inserted by sp_insert_ten_noname');
        SET v_offset = v_offset + 1;
    END WHILE;

    SELECT p_start_number AS first_number,
           p_start_number + 9 AS last_number,
           10 AS inserted_rows;
END$$

CREATE FUNCTION fn_reservation_metric(p_operation VARCHAR(10))
RETURNS DECIMAL(14,2)
READS SQL DATA
BEGIN
    DECLARE v_result DECIMAL(14,2) DEFAULT NULL;
    CASE UPPER(TRIM(p_operation))
        WHEN 'MAX' THEN SELECT MAX(total_price) INTO v_result FROM reservations;
        WHEN 'MIN' THEN SELECT MIN(total_price) INTO v_result FROM reservations;
        WHEN 'SUM' THEN SELECT SUM(total_price) INTO v_result FROM reservations;
        WHEN 'AVG' THEN SELECT AVG(total_price) INTO v_result FROM reservations;
        ELSE SET v_result = NULL;
    END CASE;
    RETURN v_result;
END$$

CREATE PROCEDURE sp_show_reservation_metric(IN p_operation VARCHAR(10))
BEGIN
    IF UPPER(TRIM(p_operation)) NOT IN ('MAX', 'MIN', 'SUM', 'AVG') THEN
        SIGNAL SQLSTATE '45000'
          SET MESSAGE_TEXT = 'operation must be MAX, MIN, SUM or AVG';
    END IF;
    SELECT UPPER(TRIM(p_operation)) AS operation,
           fn_reservation_metric(p_operation) AS metric_value,
           'reservations.total_price' AS source_column;
END$$

CREATE PROCEDURE sp_split_users_with_cursor(
    OUT p_table_a VARCHAR(64),
    OUT p_table_b VARCHAR(64)
)
BEGIN
    DECLARE v_done BOOLEAN DEFAULT FALSE;
    DECLARE v_user_id BIGINT;
    DECLARE v_first_name VARCHAR(50);
    DECLARE v_last_name VARCHAR(50);
    DECLARE v_email VARCHAR(100);
    DECLARE v_phone_number VARCHAR(20);
    DECLARE v_registration_date DATE;

    DECLARE cur_users CURSOR FOR
        SELECT user_id, first_name, last_name, email, phone_number, registration_date
          FROM users ORDER BY user_id;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_done = TRUE;

    SET p_table_a = CONCAT('users_split_a_', DATE_FORMAT(CURRENT_TIMESTAMP(6), '%Y%m%d%H%i%s%f'));
    SET p_table_b = CONCAT('users_split_b_', DATE_FORMAT(CURRENT_TIMESTAMP(6), '%Y%m%d%H%i%s%f'));

    SET @ddl_users_a = CONCAT('CREATE TABLE `', p_table_a, '` LIKE `users`');
    PREPARE stmt_create_users_a FROM @ddl_users_a;
    EXECUTE stmt_create_users_a;
    DEALLOCATE PREPARE stmt_create_users_a;

    SET @ddl_users_b = CONCAT('CREATE TABLE `', p_table_b, '` LIKE `users`');
    PREPARE stmt_create_users_b FROM @ddl_users_b;
    EXECUTE stmt_create_users_b;
    DEALLOCATE PREPARE stmt_create_users_b;

    SET @insert_users_a = CONCAT('INSERT INTO `', p_table_a,
        '` (user_id, first_name, last_name, email, phone_number, registration_date) VALUES (?, ?, ?, ?, ?, ?)');
    SET @insert_users_b = CONCAT('INSERT INTO `', p_table_b,
        '` (user_id, first_name, last_name, email, phone_number, registration_date) VALUES (?, ?, ?, ?, ?, ?)');
    PREPARE stmt_insert_users_a FROM @insert_users_a;
    PREPARE stmt_insert_users_b FROM @insert_users_b;

    OPEN cur_users;
    users_loop: LOOP
        FETCH cur_users INTO v_user_id, v_first_name, v_last_name, v_email,
                            v_phone_number, v_registration_date;
        IF v_done THEN
            LEAVE users_loop;
        END IF;

        SET @src_user_id = v_user_id;
        SET @src_first_name = v_first_name;
        SET @src_last_name = v_last_name;
        SET @src_email = v_email;
        SET @src_phone_number = v_phone_number;
        SET @src_registration_date = v_registration_date;

        IF RAND() < 0.5 THEN
            EXECUTE stmt_insert_users_a USING @src_user_id, @src_first_name,
                @src_last_name, @src_email, @src_phone_number, @src_registration_date;
        ELSE
            EXECUTE stmt_insert_users_b USING @src_user_id, @src_first_name,
                @src_last_name, @src_email, @src_phone_number, @src_registration_date;
        END IF;
    END LOOP;
    CLOSE cur_users;

    DEALLOCATE PREPARE stmt_insert_users_a;
    DEALLOCATE PREPARE stmt_insert_users_b;

    SELECT p_table_a AS table_a, p_table_b AS table_b,
           'Rows from users were randomly split by cursor' AS message;
END$$

DELIMITER ;