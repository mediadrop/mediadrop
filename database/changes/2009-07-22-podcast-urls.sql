ALTER TABLE `podcasts`
 ADD COLUMN `itunes_url` VARCHAR(80) CHARACTER SET ascii COLLATE ascii_general_ci AFTER `copyright`,
 ADD COLUMN `feedburner_url` VARCHAR(80) CHARACTER SET ascii COLLATE ascii_general_ci AFTER `itunes_url`;
