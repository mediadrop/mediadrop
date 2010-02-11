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
