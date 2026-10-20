DROP DATABASE IF EXISTS text_service
CREATE DATABASE IF NOT EXISTS text_service;
USE text_service;

-- =========================================================================
-- 1. BASE MASTER TABLES & PUBLIC PRESENTATION VIEWS
-- =========================================================================

CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    phone_number VARCHAR(20) UNIQUE DEFAULT NULL, 
    password VARCHAR(255) NOT NULL,
    status ENUM('ONLINE', 'OFFLINE') DEFAULT 'OFFLINE'
);

CREATE OR REPLACE VIEW public_users AS
SELECT 
    user_id,
    username,
    phone_number,
    status
FROM users;

-- =========================================================================
-- 2. RELATION TABLES (MUTUAL CONTACT LINKS)
-- =========================================================================

CREATE TABLE IF NOT EXISTS contact_relations (
    user1_id INT NOT NULL, 
    user2_id INT NOT NULL,
    PRIMARY KEY (user1_id, user2_id),
    FOREIGN KEY (user1_id) REFERENCES users(user_id), 
    FOREIGN KEY (user2_id) REFERENCES users(user_id),
    CHECK (user1_id < user2_id)
);

-- =========================================================================
-- 3. CHAT LOGGER STORAGE
-- =========================================================================

CREATE TABLE IF NOT EXISTS messages (
    text_id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT NOT NULL,   
    receiver_id INT NOT NULL, 
    body_text TEXT NOT NULL,                  
    dispatched_at TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP(6), 
    FOREIGN KEY (sender_id) REFERENCES users(user_id),
    FOREIGN KEY (receiver_id) REFERENCES users(user_id)
);

-- Optimal index routing for concurrent network queries
CREATE INDEX idx_msg_routing ON messages (sender_id, receiver_id, dispatched_at);

-- =========================================================================
-- 4. FIREWALL UTILITIES & AUTH PROCEDURES
-- =========================================================================

CREATE PROCEDURE VerifySession()
BEGIN
    -- Intercepts pipeline memory room. If empty, drops request instantly.
    IF @current_authenticated_user_id IS NULL THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Access Denied: Session unauthorized. Please log in first.';
    END IF;
END;

CREATE PROCEDURE RegisterUser(
    IN guest_username VARCHAR(50),
    IN guest_phone_number VARCHAR(20),
    IN guest_password VARCHAR(255)
)
SQL SECURITY DEFINER
BEGIN
    INSERT INTO users (username, phone_number, password)
    VALUES (guest_username, guest_phone_number, guest_password);
END;

CREATE PROCEDURE UserLogin(
    IN p_username VARCHAR(50),
    IN p_password VARCHAR(255)
)
BEGIN
    SET @found_id = NULL;

    SELECT user_id INTO @found_id 
    FROM users 
    WHERE username = p_username 
      AND password = p_password;

    IF @found_id IS NULL THEN
        SET @current_authenticated_user_id = NULL;
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Authentication Failed: Invalid username or password.';
    ELSE
        SET @current_authenticated_user_id = @found_id;
        UPDATE users SET status = 'ONLINE' WHERE user_id = @found_id;
        SELECT 'Login Successful!' AS status;
    END IF;
END;

CREATE PROCEDURE UserLogout()
BEGIN
    IF @current_authenticated_user_id IS NOT NULL THEN
        UPDATE users SET status = 'OFFLINE' WHERE user_id = @current_authenticated_user_id;
        SET @current_authenticated_user_id = NULL;
        SELECT 'Logout Successful!' AS status;
    ELSE
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: You are not logged in.';
    END IF;
END;

-- =========================================================================
-- 5. TEXT SERVICES & APP OPERATIONS (REFACTORED WITH CLEAN FIREWALL)
-- =========================================================================

CREATE PROCEDURE StreamNewTexts(
    IN target_contact_username VARCHAR(50),
    IN last_timestamp TIMESTAMP
)
SQL SECURITY DEFINER
BEGIN
    CALL VerifySession(); -- 🛡️ Interceptor checks pipeline memory

    SET @target_id = (SELECT user_id FROM users WHERE username = target_contact_username);

    SELECT 
        m.text_id,
        u.username AS sender_username,
        m.body_text,
        m.dispatched_at
    FROM messages m
    JOIN users u ON m.sender_id = u.user_id
    WHERE ((m.sender_id = @current_authenticated_user_id AND m.receiver_id = @target_id)
       OR (m.sender_id = @target_id AND m.receiver_id = @current_authenticated_user_id))
      AND m.dispatched_at > last_timestamp
    ORDER BY m.dispatched_at ASC;
END;

CREATE PROCEDURE SendText(
    IN input_receiver_username VARCHAR(50),
    IN input_body_text TEXT
)
SQL SECURITY DEFINER
BEGIN
    CALL VerifySession(); -- 🛡️ Interceptor checks pipeline memory

    SET @rec_id = (SELECT user_id FROM users WHERE username = input_receiver_username);

    IF @rec_id IS NULL THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Error: The recipient username does not exist.';
    END IF;

    INSERT INTO messages (sender_id, receiver_id, body_text)
    VALUES (@current_authenticated_user_id, @rec_id, input_body_text);
END;

CREATE PROCEDURE AddContactRelation(
    IN target_username VARCHAR(50)
)
SQL SECURITY DEFINER
BEGIN
    CALL VerifySession(); -- 🛡️ Interceptor checks pipeline memory

    SET @target_id = (SELECT user_id FROM users WHERE username = target_username);
    
    IF @target_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: Target user does not exist.';
    END IF;

    INSERT IGNORE INTO contact_relations (user1_id, user2_id)
    VALUES (LEAST(@current_authenticated_user_id, @target_id), GREATEST(@current_authenticated_user_id, @target_id));
END;

CREATE PROCEDURE GetContactList()
SQL SECURITY DEFINER
BEGIN
    CALL VerifySession(); -- 🛡️ Interceptor checks pipeline memory

    SELECT u.user_id, u.username, u.status
    FROM contact_relations cr
    JOIN users u ON cr.user2_id = u.user_id
    WHERE cr.user1_id = @current_authenticated_user_id
    
    UNION ALL
    
    SELECT u.user_id, u.username, u.status
    FROM contact_relations cr
    JOIN users u ON cr.user1_id = u.user_id
    WHERE cr.user2_id = @current_authenticated_user_id;
END;

CREATE PROCEDURE SearchContact(
    IN user_name VARCHAR(50)
)
SQL SECURITY DEFINER
BEGIN
    CALL VerifySession(); -- 🛡️ Interceptor checks pipeline memory

    SELECT user_id, username, status
    FROM public_users
    WHERE username = user_name;
END;

-- =========================================================================
-- 6. SYSTEM PRIVILEGES & GLOBAL PIPELINE SECURITY
-- =========================================================================

-- Standardise user account setup
CREATE USER IF NOT EXISTS 'client_user'@'%';
ALTER USER 'client_user'@'%' IDENTIFIED BY 'AppSecureAccessPass2026!';

-- Clean baseline execution box
REVOKE ALL PRIVILEGES, GRANT OPTION FROM 'client_user'@'%';

-- Safely expose execution boundaries only
GRANT EXECUTE ON PROCEDURE text_service_db.RegisterUser TO 'client_user'@'%';
GRANT EXECUTE ON PROCEDURE text_service_db.UserLogin TO 'client_user'@'%';
GRANT EXECUTE ON PROCEDURE text_service_db.UserLogout TO 'client_user'@'%';
GRANT EXECUTE ON PROCEDURE text_service_db.StreamNewTexts TO 'client_user'@'%';
GRANT EXECUTE ON PROCEDURE text_service_db.SendText TO 'client_user'@'%';
GRANT EXECUTE ON PROCEDURE text_service_db.AddContactRelation TO 'client_user'@'%';
GRANT EXECUTE ON PROCEDURE text_service_db.GetContactList TO 'client_user'@'%';
GRANT EXECUTE ON PROCEDURE text_service_db.SearchContact TO 'client_user'@'%';

-- Open access strictly to the password-free visual wrapper
GRANT SELECT ON text_service_db.public_users TO 'client_user'@'%';

FLUSH PRIVILEGES;
