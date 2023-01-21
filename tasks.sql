-- SQL 1
-- Напишите запрос, который выведет, сколько времени в среднем задачи каждой группы находятся в статусе “Open” 
-- Условия:
--  - Под группой подразумевается первый символ в ключе задачи. Например, для ключа “C-40460” группой будет “C”
--  - Задача может переходить в один и тот же статус несколько раз.
--  - Переведите время в часы с округлением до двух знаков после запятой.

SELECT group_name, round(avg(total_minutes) / 60, 2) AS avg_time
FROM (
SELECT issue_key, ifnull(sum(minutes_in_status), 0) AS total_minutes, substr(issue_key, 1, 1) AS group_name
FROM history
WHERE status = 'Open'
GROUP BY  issue_key
) total_time
GROUP BY group_name

-- SQL 2 
-- Напишите запрос, который выведет ключ задачи, последний статус и его время создания для задач, которые открыты на данный момент времени.
-- Условия:
--  - Открытыми считаются задачи, у которых последний статус в момент времени не “Closed” и не “Resolved”
--  - Задача может переходить в один и тот же статус несколько раз.
--  - Оформите запрос таким образом, чтобы, изменив дату, его можно было использовать для поиска открытых задач в любой момент времени в прошлом
--  - Переведите время в текстовое представление

SELECT issue_key, status, start_dt
FROM (
	SELECT issue_key, row_number() OVER(PARTITION BY issue_key ORDER BY started_at DESC) AS rn, status, t.previous_status, t.start_dt
	FROM (
		SELECT 
			issue_key,
			status,
			previous_status, 
			started_at, 
			strftime('%Y-%m-%d', started_at / 1000, 'unixepoch') AS start_dt,
			strftime('%Y-%m-%d', ended_at / 1000, 'unixepoch') AS end_dt
		FROM history
		) t
	where start_dt BETWEEN '2022-01-01' and '2022-01-12'
	) tt
WHERE status NOT IN ('Closed', 'Resolved') AND rn = 1