ALTER TABLE `categories`
	ADD COLUMN `parent_id` INT UNSIGNED DEFAULT NULL AFTER `slug`,
	ADD CONSTRAINT `categories_ibfk_1` FOREIGN KEY `categories_ibfk_1` (`parent_id`)
		REFERENCES `categories` (`id`)
		ON DELETE CASCADE
		ON UPDATE CASCADE;
