ALTER TABLE matchsession
ADD CONSTRAINT time_slot CHECK (time_slot>=1 AND time_slot<=4);