/* Rearrange the media file columns */
/* part 2 of 2 */
ALTER TABLE `media_files`
	ADD COLUMN `type` ENUM('video','audio','audio_desc','captions') NOT NULL AFTER `media_id`,
	ADD COLUMN `display_name` VARCHAR(255) NOT NULL AFTER `container`,
	ADD COLUMN `file_name` VARCHAR(255) AFTER `display_name`,
	MODIFY COLUMN `url` VARCHAR(255) CHARACTER SET ascii COLLATE ascii_general_ci DEFAULT NULL,
	ADD COLUMN `embed` VARCHAR(50) AFTER `url`;