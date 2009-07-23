--
-- Table structure for table `topics`
--

SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `topics` (
  `id` int(10) unsigned NOT NULL auto_increment,
  `name` varchar(50) NOT NULL,
  `slug` varchar(50) character set ascii NOT NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `media_topics`
--

SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `media_topics` (
  `media_id` int(10) unsigned NOT NULL,
  `topic_id` int(10) unsigned NOT NULL,
  PRIMARY KEY  (`media_id`,`topic_id`),
  KEY `topic_id` (`topic_id`),
  CONSTRAINT `media_topics_ibfk_1` FOREIGN KEY (`media_id`) REFERENCES `media` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `media_topics_ibfk_2` FOREIGN KEY (`topic_id`) REFERENCES `topics` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

