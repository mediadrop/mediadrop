/*
 * This file is a part of MediaDrop (http://www.mediadrop.net),
 * Copyright 2009-2013 MediaCore Inc., Felix Schwarz and other contributors.
 * For the exact contribution history, see the git revision log.
 * The source code contained in this file is licensed under the GPLv3 or
 * (at your option) any later version.
 * See LICENSE.txt in the main project directory, for more information.
 **/

/* Rename topics to categories */
/* part 1 of 2 */
ALTER TABLE `media_topics`
	DROP FOREIGN KEY `media_topics_ibfk_1`,
	DROP FOREIGN KEY `media_topics_ibfk_2`,
	DROP KEY `topic_id`,
	DROP PRIMARY KEY,
	CHANGE COLUMN `topic_id` `category_id` int(10) unsigned NOT NULL,
	ADD PRIMARY KEY (`media_id`, `category_id`);

/* ------------------------------------------------------- */

/* Rearrange some media columns */
/* remove the media.status column, in favour of reviewed, encoded, publishable columns. */
ALTER TABLE `media`
	DROP COLUMN `rating_sum`,
	CHANGE COLUMN `rating_votes` `likes` INTEGER UNSIGNED NOT NULL DEFAULT 0,
	ADD COLUMN `popularity_points` INTEGER UNSIGNED NOT NULL DEFAULT 0 AFTER `likes`,
	ADD COLUMN `description_plain` TEXT DEFAULT NULL AFTER `description`,
	ADD COLUMN `reviewed` TINYINT(1) UNSIGNED NOT NULL DEFAULT 0 AFTER `status`,
	ADD COLUMN `encoded` TINYINT(1) UNSIGNED NOT NULL DEFAULT 0 AFTER `reviewed`,
	ADD COLUMN `publishable` TINYINT(1) UNSIGNED NOT NULL DEFAULT 0 AFTER `encoded`;
UPDATE media SET reviewed = 0 WHERE status LIKE '%%unreviewed%%';
UPDATE media SET reviewed = 1 WHERE status NOT LIKE '%%unreviewed%%';
UPDATE media SET encoded = 1 WHERE status NOT LIKE '%%unencoded%%';
UPDATE media SET publishable = 1 WHERE status LIKE '%%publish%%';
DELETE FROM media WHERE status LIKE '%%trash%%';
ALTER TABLE media DROP COLUMN `status`;
