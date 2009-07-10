ALTER TABLE `media_files` DROP COLUMN `is_original`,
 CHANGE COLUMN `is_primary` `enable_player` TINYINT(1) NOT NULL DEFAULT 1,
 DROP COLUMN `is_public`,
 CHANGE COLUMN `display_order` `enable_feed` TINYINT(1) NOT NULL DEFAULT 1,
 ADD COLUMN `order` TINYINT(3) NOT NULL DEFAULT 0 AFTER `bitrate`;

