ALTER TABLE `media_files`
 ADD COLUMN `order` TINYINT(3) NOT NULL DEFAULT 0 AFTER `bitrate`;
 ADD COLUMN `enable_player` TINYINT(1) NOT NULL DEFAULT 1 AFTER `order`,
 ADD COLUMN `enable_feed` TINYINT(1) NOT NULL DEFAULT 1 AFTER `enable_player`;
