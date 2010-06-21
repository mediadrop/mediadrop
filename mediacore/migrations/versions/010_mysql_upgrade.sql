-- Originally the media >- podcast FK was ON UPDATE SET NULL but it should be CASCADE

ALTER TABLE `media`
	DROP FOREIGN KEY `media_ibfk_1`;
ALTER TABLE `media`
	ADD CONSTRAINT `media_ibfk_1` FOREIGN KEY `media_ibfk_1` (`podcast_id`)
	    REFERENCES `podcasts` (`id`)
	    ON DELETE SET NULL
	    ON UPDATE CASCADE;