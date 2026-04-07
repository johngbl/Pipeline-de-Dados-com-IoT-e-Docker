-- View 1: average temperature per device/room
DROP VIEW IF EXISTS avg_temp_por_dispositivo;
CREATE VIEW avg_temp_por_dispositivo AS
SELECT room_id AS device_id, AVG(temperature) AS avg_temp
FROM temperature_readings
GROUP BY room_id;

-- View 2: daily temperature stats
DROP VIEW IF EXISTS temp_stats_por_dia;
CREATE VIEW temp_stats_por_dia AS
SELECT DATE(noted_date) AS date,
       MIN(temperature) AS min_temp,
       MAX(temperature) AS max_temp,
       AVG(temperature) AS avg_temp,
       COUNT(*) AS total_readings
FROM temperature_readings
GROUP BY DATE(noted_date)
ORDER BY DATE(noted_date);

-- View 3: in/out counts and ratio per room
DROP VIEW IF EXISTS in_out_ratio_por_room;
CREATE VIEW in_out_ratio_por_room AS
SELECT room_id,
       SUM(CASE WHEN in_out = 'In' THEN 1 ELSE 0 END) AS in_count,
       SUM(CASE WHEN in_out = 'Out' THEN 1 ELSE 0 END) AS out_count,
       CASE WHEN COUNT(*) = 0 THEN 0 ELSE SUM(CASE WHEN in_out = 'In' THEN 1.0 ELSE 0 END) / COUNT(*) END AS in_ratio
FROM temperature_readings
GROUP BY room_id;
