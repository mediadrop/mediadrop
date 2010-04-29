/* Remove the comments.status column, in favour of 'reviewed' and 'publishible' columns. */
ALTER TABLE `comments`
	ADD COLUMN `reviewed` TINYINT(1) UNSIGNED NOT NULL DEFAULT 0 AFTER `status`,
	ADD COLUMN `publishable` TINYINT(1) UNSIGNED NOT NULL DEFAULT 0 AFTER `reviewed`;
UPDATE comments SET reviewed = 0, publishable = 0 WHERE status LIKE '%unreviewed%';
UPDATE comments SET reviewed = 1, publishable = 1 WHERE status LIKE '%publish%';
UPDATE comments SET reviewed = 1, publishable = 0 WHERE status LIKE '%trash%';
ALTER TABLE comments DROP COLUMN `status`;

/* ------------------------------------------------------- */

/* remove the media.status column, in favour of reviewed, encoded, publishable columns. */
ALTER TABLE `media`
	ADD COLUMN `reviewed` TINYINT(1) UNSIGNED NOT NULL DEFAULT 0 AFTER `status`,
	ADD COLUMN `encoded` TINYINT(1) UNSIGNED NOT NULL DEFAULT 0 AFTER `reviewed`,
	ADD COLUMN `publishable` TINYINT(1) UNSIGNED NOT NULL DEFAULT 0 AFTER `encoded`;
UPDATE media SET reviewed = 0 WHERE status LIKE '%unreviewed%';
UPDATE media SET reviewed = 1 WHERE status NOT LIKE '%unreviewed%';
UPDATE media SET encoded = 1 WHERE status NOT LIKE '%unencoded%';
UPDATE media SET publishable = 1 WHERE status LIKE '%publish%';
DELETE FROM media WHERE status LIKE '%trash%';
ALTER TABLE media DROP COLUMN `status`;

/* ------------------------------------------------------- */

/* Rearrange some media columns */
ALTER TABLE `media`
	DROP COLUMN `rating_sum`,
	CHANGE COLUMN `rating_votes` `likes` INTEGER UNSIGNED NOT NULL DEFAULT 0,
	ADD COLUMN `popularity_points` INTEGER UNSIGNED NOT NULL DEFAULT 0 AFTER `likes`,
	ADD COLUMN `description_plain` TEXT DEFAULT NULL AFTER `description`;

/* ------------------------------------------------------- */

/* Remove the join table for comments and media. There's no real need for one. */
ALTER TABLE `comments`
	DROP COLUMN `type`,
	ADD COLUMN `media_id` INTEGER UNSIGNED AFTER `id`,
	ADD CONSTRAINT `comments_media_fk1` FOREIGN KEY `comments_media` (`media_id`)
		REFERENCES `media` (`id`)
		ON DELETE CASCADE
		ON UPDATE CASCADE;
UPDATE comments AS c
SET c.media_id = (SELECT j.media_id
	FROM media_comments AS j
	WHERE c.id = j.comment_id);
DROP TABLE media_comments;

/* ------------------------------------------------------- */

/* Rename topics to categories */
ALTER TABLE `media_topics` DROP FOREIGN KEY `media_topics_ibfk_1`;
ALTER TABLE `media_topics` DROP FOREIGN KEY `media_topics_ibfk_2`;
ALTER TABLE `media_topics` DROP KEY `topic_id`;
ALTER TABLE `media_topics` DROP PRIMARY KEY;
ALTER TABLE `media_topics` CHANGE COLUMN `topic_id` `category_id` int(10) unsigned NOT NULL;
ALTER TABLE `media_topics` ADD PRIMARY KEY (`media_id`, `category_id`);
RENAME TABLE
	`media_topics` TO `media_categories`,
	`topics` TO `categories`;
ALTER TABLE `media_categories`
	ADD CONSTRAINT `media_categories_ibfk_1` FOREIGN KEY (`media_id`) REFERENCES `media` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
	ADD CONSTRAINT `media_categories_ibfk_2` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE `categories`
	ADD COLUMN `parent_id` INT UNSIGNED DEFAULT NULL AFTER `slug`,
	ADD CONSTRAINT `categories_ibfk_1` FOREIGN KEY `categories_ibfk_1` (`parent_id`)
		REFERENCES `categories` (`id`)
		ON DELETE CASCADE
		ON UPDATE CASCADE;

/* ------------------------------------------------------- */

/* Rearrange the media file columns */
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

/* ------------------------------------------------------- */

/* Add all of our new settings */
INSERT INTO `settings` VALUES
	(NULL, 'popularity_decay_exponent', '4'),
	(NULL, 'popularity_decay_lifetime', '36'),
	(NULL, 'rich_text_editor', 'tinymce'),
	(NULL, 'google_analytics_uacct', ''),
	(NULL, 'flash_player', 'flowplayer'),
	(NULL, 'html5_player', 'html5'),
	(NULL, 'player_type', 'best'),
	(NULL, 'featured_category', '1');

/* ------------------------------------------------------- */

/* Rename all of the TG user tables to remove unnecessary TG references and keep pluralization consistent */
ALTER TABLE `tg_user_group`
	DROP FOREIGN KEY `tg_user_group_ibfk_1`,
	DROP FOREIGN KEY `tg_user_group_ibfk_2`;
ALTER TABLE `tg_group_permission`
	DROP FOREIGN KEY `tg_group_permission_ibfk_1`,
	DROP FOREIGN KEY `tg_group_permission_ibfk_2`;
RENAME TABLE `tg_group` to `groups`;
RENAME TABLE `tg_permission` to `permissions`;
RENAME TABLE `tg_user` to `users`;
RENAME TABLE `tg_user_group` to `users_groups`;
RENAME TABLE `tg_group_permission` to `groups_permissions`;
ALTER TABLE `users_groups`
  ADD CONSTRAINT `users_groups_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `users_groups_ibfk_2` FOREIGN KEY (`group_id`) REFERENCES `groups` (`group_id`) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE `groups_permissions`
  ADD CONSTRAINT `groups_permissions_ibfk_1` FOREIGN KEY (`group_id`) REFERENCES `groups` (`group_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `groups_permissions_ibfk_2` FOREIGN KEY (`permission_id`) REFERENCES `permissions` (`permission_id`) ON DELETE CASCADE ON UPDATE CASCADE;

/* ------------------------------------------------------- */

/* Add the fulltext table and associated triggers */
DROP TABLE IF EXISTS `media_fulltext`;
CREATE TABLE `media_fulltext` (
	`media_id` INT(10) UNSIGNED NOT NULL,
	`title` VARCHAR(255) DEFAULT NULL,
	`subtitle` VARCHAR(255) DEFAULT NULL,
	`description_plain` TEXT,
	`notes` TEXT,
	`author_name` VARCHAR(50) NOT NULL,
	`tags` TEXT,
	`categories` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
	PRIMARY KEY  (`media_id`),
	FULLTEXT INDEX media_public(`title`, `subtitle`, `description_plain`, `tags`, `categories`),
	FULLTEXT INDEX media_admin(`title`, `subtitle`, `description_plain`, `notes`, `tags`, `categories`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

INSERT INTO media_fulltext (`media_id`, `title`, `subtitle`, `description_plain`, `notes`, `author_name`, `tags`, `categories`)
	SELECT id AS media_id, title, subtitle, description_plain, notes, author_name
	, (SELECT GROUP_CONCAT(t.name SEPARATOR ', ')
		 FROM media_tags j
		 LEFT JOIN tags t ON j.tag_id = t.id
		 WHERE j.media_id = m.id
		 GROUP BY j.media_id) AS tags
	, (SELECT GROUP_CONCAT(t.name SEPARATOR ', ')
		 FROM media_categories j
		 LEFT JOIN categories t ON j.category_id = t.id
		 WHERE j.media_id = m.id
		 GROUP BY j.media_id) AS categories
	FROM media AS m;


DELIMITER // /* set the delimiter to // for aid in creating triggers */

-- After Media is Inserted
-- Create a new Search row --
CREATE TRIGGER media_ai
	AFTER INSERT ON media FOR EACH ROW
BEGIN
	INSERT INTO media_fulltext
		SET `media_id` = NEW.`id`,
		    `title` = NEW.`title`,
		    `subtitle` = NEW.`subtitle`,
		    `description_plain` = NEW.`description_plain`,
		    `notes` = NEW.`notes`,
		    `author_name` = NEW.`author_name`,
		    `tags` = '',
		    `categories` = '';
END;//

-- After Media is Updated
-- Copies changes to the corresponding Search row
CREATE TRIGGER media_au
	AFTER UPDATE ON media FOR EACH ROW
BEGIN
	UPDATE media_fulltext
		SET `media_id` = NEW.`id`,
		    `title` = NEW.`title`,
		    `subtitle` = NEW.`subtitle`,
		    `description_plain` = NEW.`description_plain`,
		    `notes` = NEW.`notes`,
		    `author_name` = NEW.`author_name`
		WHERE media_id = OLD.id;
END;//

-- 
-- Deletes the corresponding Search row
CREATE TRIGGER media_ad
	AFTER DELETE ON media FOR EACH ROW
BEGIN
	DELETE FROM media_fulltext WHERE media_id = OLD.id;
END;//

-- Add Tag to Media
-- Append the tag to the Search row's tag TEXT column
CREATE TRIGGER media_tags_ai
	AFTER INSERT ON media_tags FOR EACH ROW
BEGIN
	UPDATE media_fulltext
		SET tags = CONCAT(tags, ', ', (SELECT name FROM tags WHERE id = NEW.tag_id))
		WHERE media_id = NEW.media_id;
END;//

-- Remove Tag From Media
-- Remove the tag from the Search row's tag TEXT column
CREATE TRIGGER media_tags_ad
	AFTER DELETE ON media_tags FOR EACH ROW
BEGIN
	UPDATE media_fulltext
		SET tags = TRIM(', ' FROM REPLACE(
			CONCAT(', ', tags, ', '),
			CONCAT(', ', (SELECT name FROM tags WHERE id = OLD.tag_id), ', '),
			', '))
		WHERE media_id = OLD.media_id;
END;//

-- Rename Tag
-- Update all Search row's which use this Tag
CREATE TRIGGER tags_au
	AFTER UPDATE ON tags FOR EACH ROW
BEGIN
	IF OLD.name != NEW.name THEN
		UPDATE media_fulltext
			SET tags = TRIM(', ' FROM REPLACE(
				CONCAT(', ', tags,     ', '),
				CONCAT(', ', OLD.name, ', '),
				CONCAT(', ', NEW.name, ', ')))
			WHERE media_id IN (SELECT media_id FROM media_tags
				WHERE tag_id = OLD.id);
	END IF;
END;//

-- Delete Tag
-- Remove the tag from all Search row's which use this Tag
CREATE TRIGGER tags_ad
	AFTER DELETE ON tags FOR EACH ROW
BEGIN
	UPDATE media_fulltext
		SET tags = TRIM(', ' FROM REPLACE(
			CONCAT(', ', tags,     ', '),
			CONCAT(', ', OLD.name, ', '),
			', '))
		WHERE media_id IN (SELECT media_id FROM media_tags
			WHERE media_id = OLD.id);
END;//

-- Add Category to Media
-- Append the Category to the Search row's Category TEXT column
CREATE TRIGGER media_categories_ai
	AFTER INSERT ON media_categories FOR EACH ROW
BEGIN
	UPDATE media_fulltext
		SET categories = CONCAT(categories, ', ', (SELECT name FROM categories WHERE id = NEW.category_id))
		WHERE media_id = NEW.media_id;
END;//

-- Remove Category From Media
-- Remove the Category from the Search row's Category TEXT column
CREATE TRIGGER media_categories_ad
	AFTER DELETE ON media_categories FOR EACH ROW
BEGIN
	UPDATE media_fulltext
		SET categories = TRIM(', ' FROM REPLACE(
			CONCAT(', ', categories, ', '),
			CONCAT(', ', (SELECT name FROM categories WHERE id = OLD.category_id), ', '),
			', '))
		WHERE media_id = OLD.media_id;
END;//

-- Rename Category
-- Update all Search row's which use this Category
CREATE TRIGGER categories_au
	AFTER UPDATE ON categories FOR EACH ROW
BEGIN
	IF OLD.name != NEW.name THEN
		UPDATE media_fulltext
			SET categories = TRIM(', ' FROM REPLACE(
				CONCAT(', ', categories,   ', '),
				CONCAT(', ', OLD.name, ', '),
				CONCAT(', ', NEW.name, ', ')))
			WHERE media_id IN (SELECT media_id FROM media_categories
				WHERE category_id = OLD.id);
	END IF;
END;//

-- Delete Category
-- Remove the Category from all Search row's which use this Category
CREATE TRIGGER categories_ad
	AFTER DELETE ON categories FOR EACH ROW
BEGIN
	UPDATE media_fulltext
		SET categories = TRIM(', ' FROM REPLACE(
			CONCAT(', ', categories,   ', '),
			CONCAT(', ', OLD.name, ', '),
			', '))
		WHERE media_id IN (SELECT media_id FROM media_categories
			WHERE category_id = OLD.id);
END;//

DELIMITER ; /* set the delimiter back to ; */
