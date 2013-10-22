/*
 * This file is a part of MediaDrop (http://www.mediadrop.net),
 * Copyright 2009-2013 MediaCore Inc., Felix Schwarz and other contributors.
 * For the exact contribution history, see the git revision log.
 * The source code contained in this file is licensed under the GPLv3 or
 * (at your option) any later version.
 * See LICENSE.txt in the main project directory, for more information.
 **/

/* Rename topics to categories */
/* part 2 of 2 */
RENAME TABLE `media_topics` TO `media_categories`;
RENAME TABLE `topics` TO `categories`;
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
