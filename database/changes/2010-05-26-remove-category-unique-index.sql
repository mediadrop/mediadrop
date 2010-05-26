ALTER TABLE `categories`
	DROP INDEX `name`,
	ADD INDEX name USING BTREE(`name`);
