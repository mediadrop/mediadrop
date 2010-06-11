ALTER TABLE `categories`
	MODIFY COLUMN `slug` VARCHAR(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;

ALTER TABLE `comments`
	MODIFY COLUMN `subject` VARCHAR(100) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL;

ALTER TABLE `media`
	MODIFY COLUMN `type` ENUM('video','audio') CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
	MODIFY COLUMN `slug` VARCHAR(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
	MODIFY COLUMN `title` VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;

# Originally the media -> podcast FK was ON UPDATE SET NULL but it should be CASCADE
ALTER TABLE `media`
	DROP FOREIGN KEY `media_ibfk_1`;
ALTER TABLE `media`
	ADD CONSTRAINT `media_ibfk_1` FOREIGN KEY `media_ibfk_1` (`podcast_id`)
	    REFERENCES `podcasts` (`id`)
	    ON DELETE SET NULL
	    ON UPDATE CASCADE;

ALTER TABLE `media_files`
	MODIFY COLUMN `type` ENUM('video','audio','audio_desc','captions') CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
	MODIFY COLUMN `container` VARCHAR(10) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
	MODIFY COLUMN `url` VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL;

ALTER TABLE `podcasts`
	MODIFY COLUMN `slug` VARCHAR(50) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
	MODIFY COLUMN `itunes_url` VARCHAR(80) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
	MODIFY COLUMN `feedburner_url` VARCHAR(80) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL;

ALTER TABLE `media_fulltext`
	MODIFY COLUMN `title` VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;

ALTER TABLE `podcasts`
	MODIFY COLUMN `slug` VARCHAR(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;

ALTER TABLE `tags`
	MODIFY COLUMN `slug` VARCHAR(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;

# These columns have False defined as their default value in SQLAlchemy, but this doesn't make it to the database.
# - Comments.reviewed
# - Comments.publishable
# - Media.reviewed
# - Media.encoded
# - Media.publishable

# We are no longer using UNSIGNED ints. this is not a part of the SQL standard.
