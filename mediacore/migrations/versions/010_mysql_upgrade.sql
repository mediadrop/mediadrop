/*
# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code contained in this file is licensed under the GPL.
# See LICENSE.txt in the main project directory, for more information.
*/

-- Originally the media >- podcast FK was ON UPDATE SET NULL but it should be CASCADE

ALTER TABLE `media`
	DROP FOREIGN KEY `media_ibfk_1`;
ALTER TABLE `media`
	ADD CONSTRAINT `media_ibfk_1` FOREIGN KEY `media_ibfk_1` (`podcast_id`)
	    REFERENCES `podcasts` (`id`)
	    ON DELETE SET NULL
	    ON UPDATE CASCADE;