/*
 * This file is a part of MediaDrop (http://www.mediadrop.net),
 * Copyright 2009-2013 MediaCore Inc., Felix Schwarz and other contributors.
 * For the exact contribution history, see the git revision log.
 * The source code contained in this file is licensed under the GPLv3 or
 * (at your option) any later version.
 * See LICENSE.txt in the main project directory, for more information.
 **/

/* Add the fulltext table and associated triggers */
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
