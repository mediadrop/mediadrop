ALTER TABLE `media_files`
	DROP COLUMN `width`,
	DROP COLUMN `height`,
	DROP COLUMN `bitrate`,
	DROP COLUMN `position`,
	DROP COLUMN `enable_player`,
	DROP COLUMN `enable_feed`,
	DROP COLUMN `is_original`,
	CHANGE COLUMN `type` `container` VARCHAR(10) CHARACTER SET ascii COLLATE ascii_general_ci NOT NULL;

ALTER TABLE `media_files`
	ADD COLUMN `type` ENUM('video','audio','audio_desc','captions') NOT NULL AFTER `media_id`,
	ADD COLUMN `display_name` VARCHAR(255) NOT NULL AFTER `container`,
	ADD COLUMN `file_name` VARCHAR(255) AFTER `display_name`,
	MODIFY COLUMN `url` VARCHAR(255) CHARACTER SET ascii COLLATE ascii_general_ci DEFAULT NULL,
	ADD COLUMN `embed` VARCHAR(50) AFTER `url`;
