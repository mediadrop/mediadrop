ALTER TABLE `media`
  MODIFY COLUMN `type` ENUM('audio','video') CHARACTER SET ascii COLLATE ascii_general_ci DEFAULT NULL;
