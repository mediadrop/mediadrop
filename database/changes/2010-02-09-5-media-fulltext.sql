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
