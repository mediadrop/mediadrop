ALTER TABLE `media_topics` DROP KEY `topic_id`;
ALTER TABLE `media_topics` DROP FOREIGN KEY `media_topics_ibfk_1`,
ALTER TABLE `media_topics` DROP FOREIGN KEY `media_topics_ibfk_2`;
ALTER TABLE `media_topics` DROP PRIMARY KEY;

ALTER TABLE `media_topics` CHANGE COLUMN `topic_id` `category_id` int(10) unsigned NOT NULL;
ALTER TABLE `media_topics` ADD PRIMARY KEY (`media_id`, `category_id`);

RENAME TABLE
	`media_topics` TO `media_categories`,
	`topics` TO `categories`;

ALTER TABLE `media_categories`
	ADD CONSTRAINT `media_categories_ibfk_1` FOREIGN KEY (`media_id`) REFERENCES `media` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
	ADD CONSTRAINT `media_categories_ibfk_2` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;
