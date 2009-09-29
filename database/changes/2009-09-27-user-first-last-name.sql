ALTER TABLE `tg_user`
ADD COLUMN `first_name` VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_general_ci AFTER `display_name`,
ADD COLUMN `last_name` VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_general_ci AFTER `first_name`;

