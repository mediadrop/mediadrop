ALTER TABLE `media`
	ADD COLUMN `reviewed` TINYINT(1) UNSIGNED NOT NULL DEFAULT 0 AFTER `status`,
	ADD COLUMN `encoded` TINYINT(1) UNSIGNED NOT NULL DEFAULT 0 AFTER `reviewed`,
	ADD COLUMN `publishable` TINYINT(1) UNSIGNED NOT NULL DEFAULT 0 AFTER `encoded`;

UPDATE media SET reviewed = 0 WHERE status LIKE '%unreviewed%';
UPDATE media SET reviewed = 1 WHERE status NOT LIKE '%unreviewed%';
UPDATE media SET encoded = 1 WHERE status NOT LIKE '%unencoded%';
UPDATE media SET publishable = 1 WHERE status LIKE '%publish%';
