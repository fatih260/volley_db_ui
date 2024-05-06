DELIMITER //

DROP TRIGGER if exists prevent_overlapping_sessions //

CREATE TRIGGER prevent_overlapping_sessions
BEFORE INSERT ON matchsession
FOR EACH ROW
BEGIN
    DECLARE overlapping_sessions INT;
    
    -- Check for overlapping sessions in terms of stadium and playing time
    SELECT COUNT(*)
    INTO overlapping_sessions
    FROM matchsession
    WHERE stadium_id = NEW.stadium_id
    AND date = NEW.date
    AND ABS(time_slot - NEW.time_slot) <= 1;
    
    -- If there are any overlapping sessions, prevent the insertion
    IF overlapping_sessions > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Cannot insert. Overlapping sessions detected.';
    END IF;
END //

DELIMITER ;
