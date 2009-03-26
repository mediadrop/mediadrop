-- MySQL dump 10.11
--
-- Host: localhost    Database: mediaplex
-- ------------------------------------------------------
-- Server version	5.0.67

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `comments`
--

DROP TABLE IF EXISTS `comments`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `comments` (
  `id` int(11) NOT NULL auto_increment,
  `type` varchar(15) NOT NULL,
  `subject` varchar(100) default NULL,
  `created_on` datetime NOT NULL,
  `modified_on` datetime NOT NULL,
  `status` varchar(15) NOT NULL,
  `author_name` varchar(50) NOT NULL,
  `author_email` varchar(255) default NULL,
  `body` text NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `comments`
--

LOCK TABLES `comments` WRITE;
/*!40000 ALTER TABLE `comments` DISABLE KEYS */;
/*!40000 ALTER TABLE `comments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `media`
--

DROP TABLE IF EXISTS `media`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `media` (
  `id` int(11) NOT NULL auto_increment,
  `type` varchar(10) NOT NULL,
  `slug` varchar(50) NOT NULL,
  `created_on` datetime NOT NULL,
  `modified_on` datetime NOT NULL,
  `publish_on` datetime default NULL,
  `status` varchar(15) NOT NULL,
  `title` varchar(50) NOT NULL,
  `description` text,
  `notes` text,
  `duration` int(11) NOT NULL,
  `views` int(11) NOT NULL,
  `upload_url` varchar(255) default NULL,
  `url` varchar(255) default NULL,
  `author_name` varchar(50) NOT NULL,
  `author_email` varchar(255) NOT NULL,
  `rating_sum` int(11) NOT NULL,
  `rating_votes` int(11) NOT NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `media`
--

LOCK TABLES `media` WRITE;
/*!40000 ALTER TABLE `media` DISABLE KEYS */;
INSERT INTO `media` VALUES (1,'video','black-knight','2009-01-12 16:29:57','2009-01-12 16:29:57','2009-01-12 16:29:57','publishable','The Black Knight','More silliness.',NULL,266,0,NULL,'http://youtube.com/v/2eMkth8FWno','John','john@bowisle.ca',0,0),(2,'video','french-taunting','2009-01-12 16:37:15','2009-03-12 19:35:26','2009-03-12 19:35:26','publishable','French Taunting','Insults from Monty Python, handy for all occasions!',NULL,640,1,NULL,'http://youtube.com/v/9V7zbWNznbs','Verity','verity@norman.com',0,0),(3,'video','monty-pythons','2009-01-09 15:52:56','2009-01-09 15:52:56','2009-01-09 15:52:56','publishable','Monty Python\'s','Some silly nonsensical comedy for you, from Monty Python\'s Flying Circus.',NULL,194,0,NULL,'http://youtube.com/v/Xe1a1wHxTyo','George','george@clements.com',0,0),(4,'video','killer-bunny','2009-01-12 16:41:05','2009-01-12 16:41:05','2009-01-12 16:41:05','publishable','Killer Bunny','A bunny that can kill a man.',NULL,126,0,NULL,'http://youtube.com/v/XcxKIJTb3Hg','Tom','tom@hulu.com',0,0),(5,'video','systems-government','2009-01-12 16:48:34','2009-01-12 16:48:34','2009-01-12 16:48:34','publishable','Systems of Government','Political satire.',NULL,191,0,NULL,'http://youtube.com/v/5Xd_zkMEgkI','George','george@dragon.com',0,0),(6,'video','are-you-suggesting-coconuts-migrate','2009-01-12 16:53:53','2009-01-12 16:53:53','2009-01-12 16:53:53','publishable','Are you suggesting coconuts migrate?','King of the Britons, Defeater of the Saxons banging two empty halves of tropical coconuts together in a temporate climate.',NULL,181,0,NULL,'http://youtube.com/v/rzcLQRXW6B0','Morgan','morgan@csps.com',0,0),(7,'video','sir-lancelot','2009-01-12 16:57:03','2009-01-12 16:57:03','2009-01-12 16:57:03','publishable','Sir Lancelot','Sirrrrlancelot is brave and noble.',NULL,478,0,NULL,'http://youtube.com/v/-jO1EOhGkY0','John Doe','jdoe@simplestation.com',0,0),(8,'video','bring-out-your-dead','2009-01-12 17:06:47','2009-01-12 17:06:47','2009-01-12 17:06:47','publishable','Bring Out Your Dead','But I\'m not dead yet!',NULL,118,0,NULL,'http://youtube.com/v/grbSQ6O6kbs','John Doe','jdoe@simplestation.com',0,0),(9,'video','three-questions','2009-01-12 17:09:55','2009-01-12 17:09:55','2009-01-12 17:09:55','publishable','Three Questions','Sir Lancelot faces skill testing questions.',NULL,244,0,NULL,'http://youtube.com/v/IMxWLuOFyZM','John Doe','jdoe@simplestation.com',0,0),(10,'video','tale-sir-robin','2009-01-12 18:17:07','2009-01-12 18:17:07','2009-01-12 18:17:07','publishable','The Tale of Sir Robin','Sing this song!',NULL,173,0,NULL,'http://youtube.com/v/c4SJ0xR2_bQ','John Doe','jdoe@simplestation.com',0,0),(11,'video','guarding-room','2009-01-12 18:18:22','2009-01-12 18:18:22','2009-01-12 18:18:22','publishable','Guarding the Room','Something goes here, something like a description.',NULL,123,0,NULL,'http://youtube.com/v/ekO3Z3XWa0Q','John Doe','jdoe@simplestation.com',0,0),(12,'video','knights-who-say-ni','2009-01-12 18:19:51','2009-01-12 18:19:51','2009-01-12 18:19:51','publishable','Knights Who Say Ni','These knights say ni.',NULL,521,0,NULL,'http://youtube.com/v/QTQfGd3G6dg','John Doe','jdoe@simplestation.com',0,0),(13,'video','tim-enchanter','2009-01-12 18:20:41','2009-01-12 18:20:41','2009-01-12 18:20:41','publishable','Tim the Enchanter','Enchanting tim',NULL,52,0,NULL,'http://youtube.com/v/JTbrIo1p-So','John Doe','jdoe@simplestation.com',0,0),(14,'video','grenade-antioch','2009-01-12 18:21:50','2009-01-12 18:21:50','2009-01-12 18:21:50','publishable','Grenade of Antioch','Holy hand grenade!',NULL,242,0,NULL,'http://youtube.com/v/apDGPl2SfpA','John Doe','jdoe@simplestation.com',0,0),(15,'video','intermission-music','2009-01-12 18:36:06','2009-01-12 18:36:06','2009-01-12 18:36:06','publishable','Intermission Music','From the movie',NULL,546,0,NULL,'http://youtube.com/v/9hmDZz5pDOQ','John Doe','jdoe@simplestation.com',0,0);
/*!40000 ALTER TABLE `media` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `media_comments`
--

DROP TABLE IF EXISTS `media_comments`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `media_comments` (
  `media_id` int(11) NOT NULL,
  `comment_id` int(11) NOT NULL,
  PRIMARY KEY  (`media_id`,`comment_id`),
  UNIQUE KEY `comment_id` (`comment_id`),
  CONSTRAINT `media_comments_ibfk_1` FOREIGN KEY (`media_id`) REFERENCES `media` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `media_comments_ibfk_2` FOREIGN KEY (`comment_id`) REFERENCES `comments` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `media_comments`
--

LOCK TABLES `media_comments` WRITE;
/*!40000 ALTER TABLE `media_comments` DISABLE KEYS */;
/*!40000 ALTER TABLE `media_comments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `media_tags`
--

DROP TABLE IF EXISTS `media_tags`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `media_tags` (
  `media_id` int(11) NOT NULL,
  `tag_id` int(11) NOT NULL,
  PRIMARY KEY  (`media_id`,`tag_id`),
  KEY `tag_id` (`tag_id`),
  CONSTRAINT `media_tags_ibfk_1` FOREIGN KEY (`media_id`) REFERENCES `media` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `media_tags_ibfk_2` FOREIGN KEY (`tag_id`) REFERENCES `tags` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `media_tags`
--

LOCK TABLES `media_tags` WRITE;
/*!40000 ALTER TABLE `media_tags` DISABLE KEYS */;
/*!40000 ALTER TABLE `media_tags` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `podcast_episodes`
--

DROP TABLE IF EXISTS `podcast_episodes`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `podcast_episodes` (
  `id` int(11) NOT NULL auto_increment,
  `slug` varchar(50) character set latin1 NOT NULL,
  `podcast_id` int(11) NOT NULL,
  `media_id` int(11) NOT NULL,
  `created_on` datetime NOT NULL,
  `modified_on` datetime NOT NULL,
  `publish_on` datetime default NULL,
  `invalid_on` datetime default NULL,
  `title` varchar(50) character set latin1 NOT NULL,
  `subtitle` varchar(255) character set latin1 default NULL,
  `description` text character set latin1,
  `category` varchar(50) character set latin1 default NULL,
  `author_name` varchar(50) character set latin1 default NULL,
  `author_email` varchar(50) character set latin1 default NULL,
  `copyright` varchar(50) character set latin1 default NULL,
  PRIMARY KEY  (`id`),
  KEY `podcast_id` (`podcast_id`),
  KEY `media_id` (`media_id`),
  CONSTRAINT `podcast_episodes_ibfk_1` FOREIGN KEY (`podcast_id`) REFERENCES `podcasts` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `podcast_episodes_ibfk_2` FOREIGN KEY (`media_id`) REFERENCES `media` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `podcast_episodes`
--

LOCK TABLES `podcast_episodes` WRITE;
/*!40000 ALTER TABLE `podcast_episodes` DISABLE KEYS */;
/*!40000 ALTER TABLE `podcast_episodes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `podcasts`
--

DROP TABLE IF EXISTS `podcasts`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `podcasts` (
  `id` int(11) NOT NULL auto_increment,
  `slug` varchar(50) character set latin1 NOT NULL,
  `created_on` datetime NOT NULL,
  `modified_on` datetime NOT NULL,
  `title` varchar(50) character set latin1 NOT NULL,
  `subtitle` varchar(255) character set latin1 default NULL,
  `description` text character set latin1,
  `category` varchar(50) character set latin1 default NULL,
  `author_name` varchar(50) character set latin1 default NULL,
  `author_email` varchar(50) character set latin1 default NULL,
  `copyright` varchar(50) character set latin1 default NULL,
  `explicit` tinyint(1) NOT NULL,
  `block_itunes` tinyint(1) NOT NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `podcasts`
--

LOCK TABLES `podcasts` WRITE;
/*!40000 ALTER TABLE `podcasts` DISABLE KEYS */;
/*!40000 ALTER TABLE `podcasts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tags`
--

DROP TABLE IF EXISTS `tags`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `tags` (
  `id` int(11) NOT NULL auto_increment,
  `name` varchar(50) NOT NULL,
  `slug` varchar(50) NOT NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `tags`
--

LOCK TABLES `tags` WRITE;
/*!40000 ALTER TABLE `tags` DISABLE KEYS */;
/*!40000 ALTER TABLE `tags` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tg_group`
--

DROP TABLE IF EXISTS `tg_group`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `tg_group` (
  `group_id` int(11) NOT NULL auto_increment,
  `group_name` varchar(16) NOT NULL,
  `display_name` varchar(255) default NULL,
  `created` datetime default NULL,
  PRIMARY KEY  (`group_id`),
  UNIQUE KEY `group_name` (`group_name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `tg_group`
--

LOCK TABLES `tg_group` WRITE;
/*!40000 ALTER TABLE `tg_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `tg_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tg_group_permission`
--

DROP TABLE IF EXISTS `tg_group_permission`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `tg_group_permission` (
  `group_id` int(11) default NULL,
  `permission_id` int(11) default NULL,
  KEY `group_id` (`group_id`),
  KEY `permission_id` (`permission_id`),
  CONSTRAINT `tg_group_permission_ibfk_1` FOREIGN KEY (`group_id`) REFERENCES `tg_group` (`group_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tg_group_permission_ibfk_2` FOREIGN KEY (`permission_id`) REFERENCES `tg_permission` (`permission_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `tg_group_permission`
--

LOCK TABLES `tg_group_permission` WRITE;
/*!40000 ALTER TABLE `tg_group_permission` DISABLE KEYS */;
/*!40000 ALTER TABLE `tg_group_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tg_permission`
--

DROP TABLE IF EXISTS `tg_permission`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `tg_permission` (
  `permission_id` int(11) NOT NULL auto_increment,
  `permission_name` varchar(16) NOT NULL,
  `description` varchar(255) default NULL,
  PRIMARY KEY  (`permission_id`),
  UNIQUE KEY `permission_name` (`permission_name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `tg_permission`
--

LOCK TABLES `tg_permission` WRITE;
/*!40000 ALTER TABLE `tg_permission` DISABLE KEYS */;
/*!40000 ALTER TABLE `tg_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tg_user`
--

DROP TABLE IF EXISTS `tg_user`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `tg_user` (
  `user_id` int(11) NOT NULL auto_increment,
  `user_name` varchar(16) NOT NULL,
  `email_address` varchar(255) NOT NULL,
  `display_name` varchar(255) default NULL,
  `password` varchar(80) default NULL,
  `created` datetime default NULL,
  PRIMARY KEY  (`user_id`),
  UNIQUE KEY `user_name` (`user_name`),
  UNIQUE KEY `email_address` (`email_address`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `tg_user`
--

LOCK TABLES `tg_user` WRITE;
/*!40000 ALTER TABLE `tg_user` DISABLE KEYS */;
/*!40000 ALTER TABLE `tg_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tg_user_group`
--

DROP TABLE IF EXISTS `tg_user_group`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `tg_user_group` (
  `user_id` int(11) default NULL,
  `group_id` int(11) default NULL,
  KEY `user_id` (`user_id`),
  KEY `group_id` (`group_id`),
  CONSTRAINT `tg_user_group_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `tg_user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tg_user_group_ibfk_2` FOREIGN KEY (`group_id`) REFERENCES `tg_group` (`group_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `tg_user_group`
--

LOCK TABLES `tg_user_group` WRITE;
/*!40000 ALTER TABLE `tg_user_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `tg_user_group` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2009-03-18 18:47:32
