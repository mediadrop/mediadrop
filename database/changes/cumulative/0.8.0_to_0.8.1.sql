-- 2010-05-26-remove-category-unique-index.sql
ALTER TABLE `categories`
	DROP INDEX `name`,
	ADD INDEX name USING BTREE(`name`);
