    SELECT b.scraperId, b.scraperStartTime, COUNT(b.rowid) as messages,
        COUNT(b.taskId) AS tasks,
        COUNT(c.rowid) AS warnings
    FROM log b, log c
    WHERE
        b.scraperId = c.scraperId AND
        (c.levelname = "WARN" OR c.levelname IS NULL)
    GROUP BY b.scraperId, b.scraperStartTime
    ORDER BY b.scraperStartTime DESC




SELECT b.scraperId, b.scraperStartTime, COUNT(b.rowid) as messages,
    COUNT(b.taskId) AS tasks,
    COUNT(c.rowid) AS warnings
FROM log b
    LEFT OUTER JOIN log c ON b.scraperId = c.scraperId
WHERE
    c.levelname = "WARN" OR c.levelname IS NULL
GROUP BY b.scraperId, b.scraperStartTime
ORDER BY b.scraperStartTime DESC;
