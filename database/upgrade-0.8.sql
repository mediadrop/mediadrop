ALTER TABLE `media`
	DROP COLUMN `rating_sum`,
	CHANGE COLUMN `rating_votes` `likes` INTEGER UNSIGNED NOT NULL DEFAULT 0;

ALTER TABLE `comments`
	ADD COLUMN `reviewed` TINYINT(1) UNSIGNED NOT NULL DEFAULT 0 AFTER `status`,
	ADD COLUMN `publishable` TINYINT(1) UNSIGNED NOT NULL DEFAULT 0 AFTER `reviewed`;

UPDATE comments SET reviewed = 0 WHERE status LIKE '%unreviewed%';
UPDATE comments SET reviewed = 1 WHERE status NOT LIKE '%unreviewed%';
UPDATE comments SET publishable = 1 WHERE status LIKE '%publish%';

ALTER TABLE comments DROP COLUMN `status`;

ALTER TABLE `media`
	ADD COLUMN `description_plain` TEXT DEFAULT NULL AFTER `description`;

DROP TABLE IF EXISTS `media_fulltext`;
CREATE TABLE `media_fulltext` (
  `media_id` INT(10) UNSIGNED NOT NULL,
  `title` VARCHAR(255) DEFAULT NULL,
  `subtitle` VARCHAR(255) DEFAULT NULL,
  `description_plain` TEXT,
  `notes` TEXT,
  `author_name` VARCHAR(50) NOT NULL,
  `tags` TEXT,
  `topics` TEXT,
  PRIMARY KEY  (`media_id`),
  FULLTEXT INDEX media_public(`title`, `subtitle`, `description_plain`, `tags`, `topics`),
  FULLTEXT INDEX media_admin(`title`, `subtitle`, `description_plain`, `notes`, `tags`, `topics`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

INSERT INTO media_fulltext (`media_id`, `title`, `subtitle`, `description_plain`, `notes`, `author_name`, `tags`, `topics`)
	SELECT id AS media_id, title, subtitle, description_plain, notes, author_name
	, (SELECT GROUP_CONCAT(t.name SEPARATOR ', ')
		 FROM media_tags j
		 LEFT JOIN tags t ON j.tag_id = t.id
		 WHERE j.media_id = m.id
		 GROUP BY j.media_id) AS tags
	, (SELECT GROUP_CONCAT(t.name SEPARATOR ', ')
		 FROM media_topics j
		 LEFT JOIN topics t ON j.topic_id = t.id
		 WHERE j.media_id = m.id
		 GROUP BY j.media_id) AS topics
	FROM media AS m;

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



DELIMITER //

-- After Media is Inserted
-- Create a new Search row --
DROP TRIGGER IF EXISTS media_ai//
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
		    `topics` = '';
END;//

-- After Media is Updated
-- Copies changes to the corresponding Search row
DROP TRIGGER IF EXISTS media_au//
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
DROP TRIGGER IF EXISTS media_ad//
CREATE TRIGGER media_ad
	AFTER DELETE ON media FOR EACH ROW
BEGIN
	DELETE FROM media_fulltext WHERE media_id = OLD.id;
END;//

-- Add Tag to Media
-- Append the tag to the Search row's tag TEXT column
DROP TRIGGER IF EXISTS media_tags_ai//
CREATE TRIGGER media_tags_ai
	AFTER INSERT ON media_tags FOR EACH ROW
BEGIN
	UPDATE media_fulltext
		SET tags = CONCAT(tags, ', ', (SELECT name FROM tags WHERE id = NEW.tag_id))
		WHERE media_id = NEW.media_id;
END;//

-- Remove Tag From Media
-- Remove the tag from the Search row's tag TEXT column
DROP TRIGGER IF EXISTS media_tags_ad//
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
DROP TRIGGER IF EXISTS tags_au//
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
DROP TRIGGER IF EXISTS tags_ad//
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



-- Add Topic to Media
-- Append the Topic to the Search row's Topic TEXT column
DROP TRIGGER IF EXISTS media_topics_ai//
CREATE TRIGGER media_topics_ai
	AFTER INSERT ON media_topics FOR EACH ROW
BEGIN
	UPDATE media_fulltext
		SET topics = CONCAT(topics, ', ', (SELECT name FROM topics WHERE id = NEW.topic_id))
		WHERE media_id = NEW.media_id;
END;//

-- Remove Topic From Media
-- Remove the Topic from the Search row's Topic TEXT column
DROP TRIGGER IF EXISTS media_topics_ad//
CREATE TRIGGER media_topics_ad
	AFTER DELETE ON media_topics FOR EACH ROW
BEGIN
	UPDATE media_fulltext
		SET topics = TRIM(', ' FROM REPLACE(
			CONCAT(', ', topics, ', '),
			CONCAT(', ', (SELECT name FROM topics WHERE id = OLD.topic_id), ', '),
			', '))
		WHERE media_id = OLD.media_id;
END;//

-- Rename Topic
-- Update all Search row's which use this Topic
DROP TRIGGER IF EXISTS topics_au//
CREATE TRIGGER topics_au
	AFTER UPDATE ON topics FOR EACH ROW
BEGIN
	IF OLD.name != NEW.name THEN
		UPDATE media_fulltext
			SET topics = TRIM(', ' FROM REPLACE(
				CONCAT(', ', topics,   ', '),
				CONCAT(', ', OLD.name, ', '),
				CONCAT(', ', NEW.name, ', ')))
			WHERE media_id IN (SELECT media_id FROM media_topics
				WHERE topic_id = OLD.id);
	END IF;
END;//

-- Delete Topic
-- Remove the Topic from all Search row's which use this Topic
DROP TRIGGER IF EXISTS topics_ad//
CREATE TRIGGER topics_ad
	AFTER DELETE ON topics FOR EACH ROW
BEGIN
	UPDATE media_fulltext
		SET topics = TRIM(', ' FROM REPLACE(
			CONCAT(', ', topics,   ', '),
			CONCAT(', ', OLD.name, ', '),
			', '))
		WHERE media_id IN (SELECT media_id FROM media_topics
			WHERE topic_id = OLD.id);
END;//

DELIMITER ;