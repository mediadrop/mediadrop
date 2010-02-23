ALTER TABLE `comments`
	ADD COLUMN `reviewed` TINYINT(1) UNSIGNED NOT NULL DEFAULT 0 AFTER `status`,
	ADD COLUMN `publishable` TINYINT(1) UNSIGNED NOT NULL DEFAULT 0 AFTER `reviewed`;

UPDATE comments SET reviewed = 0, publishable = 0 WHERE status LIKE '%unreviewed%';
UPDATE comments SET reviewed = 1, publishable = 1 WHERE status LIKE '%publish%';
UPDATE comments SET reviewed = 1, publishable = 0 WHERE status LIKE '%trash%';

ALTER TABLE comments DROP COLUMN `status`;
