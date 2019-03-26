-- Select passengers who give a rating<5
SELECT *
FROM Comments C, Passengers P
WHERE C.uid=P.userName AND rating<5;

-- Index on rating (commentRating)
CREATE INDEX commentRating ON Comments(rating);
-- Drop Index on rating (commentRating)
DROP INDEX commentRating;


-- Selects driver rating and rank
select uid, COUNT(leads.tripid) from leads
join trips on
  leads.tripid = trips.tripid and
  trips.starttime between '2019-01-03' AND '2019-07-10'
group by uid
order by count(leads.tripid) desc;

-- Index on trip starttime (tripDate)
CREATE INDEX tripDate ON Trips(starttime);
-- Drop index on trip starttime (tripDate)
DROP INDEX commentRating;


-- Stored procedure for unified trip renaming
CREATE OR REPLACE FUNCTION RenameTrips(specifiedStartTime TIMESTAMP, specifiedEndTime TIMESTAMP) RETURNS Void 
AS $$
DECLARE 
	curSeat CURSOR (specifiedTripId INT) FOR 
		SELECT COUNT(*) AS num
		FROM Books 
		WHERE specifiedTripId = tripId;
	curSeatRec RECORD;
	Trec RECORD;
	seatsUsed INT;
	seatsLeft INT;
BEGIN
	FOR Trec IN SELECT * 
		FROM Trips 	
		WHERE startTime BETWEEN specifiedStartTime AND specifiedEndTime
	LOOP
		OPEN curSeat (specifiedTripId := Trec.tripId);
		FETCH curSeat INTO curSeatRec;
		seatsUsed := curSeatRec.num;
		CLOSE curSeat;
		seatsLeft := Trec.numberOfSeatsAvailable - seatsUsed;
		IF seatsLeft<=0 OR Trec.startTime<current_timestamp 
		THEN 
			UPDATE Trips
			SET title = '[Closed] Trip from ' || CAST(startLocation AS TEXT)
				|| ' at ' || CAST(startTime AS TEXT) || ' with ' 
            	|| CAST (seatsLeft AS TEXT) || ' seats left'
				WHERE tripId=Trec.tripId;
		ELSE
			UPDATE Trips 
			SET title = 'Trip from ' || CAST(startLocation AS TEXT)
				|| ' at ' || CAST(startTime AS TEXT) || ' with ' 
            	|| CAST (seatsLeft AS TEXT) || ' seats left'
				WHERE tripId=Trec.tripId;	
		END IF;
	END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Rename trips with startDate between 2019-01-01 and 2019-05-01
SELECT RenameTrips('2019-01-01', '2019-05-01');

-- Check the effect of invocation
SELECT * FROM Trips;

-- Drop the stored procedure
DROP FUNCTION renametrips(timestamp without time zone);