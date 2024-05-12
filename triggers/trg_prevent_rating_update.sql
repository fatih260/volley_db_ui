DELIMITER //

DROP TRIGGER if exists prevent_rating_update //

CREATE TRIGGER prevent_rating_update
BEFORE UPDATE ON matchsession
FOR EACH ROW
BEGIN
    IF OLD.rating IS NOT NULL AND NEW.rating != OLD.rating AND session_ID == NEW.session_ID THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Rating for this match session cannot be updated once set';
    END IF;
END //

DELIMITER ;
