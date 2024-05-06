DELIMITER //

DROP TRIGGER if exists player_time_conflict //

CREATE TRIGGER player_time_conflict
BEFORE INSERT ON sessionsquads
FOR EACH ROW
BEGIN
    DECLARE conflicting_sessions_number INT;

    -- Get the date and time_slot of the new session from matchsession table
    DECLARE new_date VARCHAR(512);
    DECLARE new_time_slot INT;

    -- Convert the date format to 'YYYY-MM-DD' directly in the SELECT statement
    SELECT date, time_slot INTO new_date, new_time_slot
    FROM matchsession
    WHERE session_ID = NEW.session_ID;

    -- Check if the new session conflicts with any existing sessions for the same player
    SELECT COUNT(*) INTO conflicting_sessions_number
    FROM matchsession AS m
    WHERE EXISTS (
        SELECT 1
        FROM sessionsquads AS s
        WHERE s.session_ID = m.session_ID
          AND s.played_player_username = NEW.played_player_username
    )
    AND m.session_ID != NEW.session_ID
    AND m.date = new_date
    AND ABS(m.time_slot - new_time_slot) <= 1;

    -- If a conflicting session is found, raise an error
    IF conflicting_sessions_number > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Player cannot play in matches with time conflicts';
    END IF;
END//

DELIMITER ;
