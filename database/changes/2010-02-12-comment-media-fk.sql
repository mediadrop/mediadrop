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
