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
  `id` int(10) unsigned NOT NULL auto_increment,
  `type` varchar(15) character set ascii NOT NULL,
  `subject` varchar(100) NOT NULL,
  `created_on` datetime NOT NULL,
  `modified_on` datetime NOT NULL,
  `status` set('trash','publish','unreviewed','user_flagged') default NULL,
  `author_name` varchar(50) NOT NULL,
  `author_email` varchar(255) default NULL,
  `author_ip` int(10) unsigned NOT NULL,
  `body` text NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `comments`
--

LOCK TABLES `comments` WRITE;
/*!40000 ALTER TABLE `comments` DISABLE KEYS */;
INSERT INTO `comments` VALUES (1,'media','Re: The Black Knight','2009-05-11 10:54:58','2009-05-11 11:09:32','publish','Some comment',NULL,2130706433,'asdfsadf'),(2,'media','Re: Four Yorkshiremen','2009-05-19 17:33:11','2009-05-28 17:24:28','publish','testest',NULL,2130706433,'test'),(3,'media','Re: Four Yorkshiremen','2009-05-19 17:33:40','2009-05-19 17:33:40','','testsetsttest',NULL,2130706433,'teste'),(4,'media','Re: Four Yorkshiremen','2009-05-19 17:49:57','2009-05-19 17:49:57','','testagain',NULL,2130706433,'testmixin'),(5,'media','Re: Three Questions','2009-05-31 17:22:58','2009-05-31 17:22:58','','Nate',NULL,2130706433,'Here\'s a question for you.\r\n\r\nDoes this work?');
/*!40000 ALTER TABLE `comments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `media`
--

DROP TABLE IF EXISTS `media`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `media` (
  `id` int(10) unsigned NOT NULL auto_increment,
  `type` varchar(10) character set ascii NOT NULL,
  `slug` varchar(50) character set ascii default NULL,
  `status` set('trash','publish','draft','unencoded','unreviewed') default NULL,
  `podcast_id` int(10) unsigned default NULL,
  `created_on` datetime NOT NULL,
  `modified_on` datetime NOT NULL,
  `publish_on` datetime default NULL,
  `publish_until` datetime default NULL,
  `title` varchar(50) NOT NULL,
  `subtitle` varchar(255) default NULL,
  `description` text,
  `notes` text,
  `duration` int(10) unsigned NOT NULL,
  `views` int(10) unsigned NOT NULL default '0',
  `rating_sum` int(10) unsigned NOT NULL default '0',
  `rating_votes` int(10) unsigned NOT NULL default '0',
  `author_name` varchar(50) NOT NULL,
  `author_email` varchar(255) NOT NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `slug` (`slug`),
  KEY `media_ibfk_1` (`podcast_id`),
  CONSTRAINT `media_ibfk_1` FOREIGN KEY (`podcast_id`) REFERENCES `podcasts` (`id`) ON DELETE SET NULL ON UPDATE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `media`
--

LOCK TABLES `media` WRITE;
/*!40000 ALTER TABLE `media` DISABLE KEYS */;
INSERT INTO `media` VALUES (1,'video','black-knight','draft',NULL,'2009-01-12 16:29:57','2009-06-05 18:33:57',NULL,NULL,'The Black Knight',NULL,'A classic moment from Monty Python and the Holy Grail.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',4,21,0,0,'Nathan','nathan@simplestation.com'),(2,'video','french-taunting','publish',NULL,'2009-01-12 16:37:15','2009-06-05 18:33:57','2009-03-12 19:35:26',NULL,'French Taunting',NULL,'A memorable scene from Monty Python & the Holy Grail.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',640,6,0,0,'Verity','verity@norman.com'),(3,'video','four-yorkshiremen','publish',NULL,'2009-01-09 15:52:56','2009-06-05 18:33:57','2009-01-09 15:52:56',NULL,'Four Yorkshiremen',NULL,'Some silly nonsensical comedy for you, from Monty Python\'s Flying Circus.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',186,30,0,0,'George Clements','george@clements.com'),(4,'video','killer-bunny','publish',NULL,'2009-01-12 16:41:05','2009-06-05 18:33:57','2009-01-12 16:41:05',NULL,'Killer Bunny',NULL,'A bunny that can kill a man.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',126,1,0,0,'Tom','tom@hulu.com'),(5,'video','systems-government','publish',NULL,'2009-01-12 16:48:34','2009-06-05 18:33:57','2009-01-12 16:48:34',NULL,'Systems of Government',NULL,'Political satire.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',191,1,0,0,'George','george@dragon.com'),(6,'video','are-you-suggesting-coconuts-migrate','publish',NULL,'2009-01-12 16:53:53','2009-06-05 18:33:57','2009-01-12 16:53:53',NULL,'Are you suggesting coconuts migrate?',NULL,'King of the Britons, Defeater of the Saxons banging two empty halves of tropical coconuts together in a temporate climate.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',181,1,0,0,'Morgan','morgan@csps.com'),(7,'video','sir-lancelot','publish',NULL,'2009-01-12 16:57:03','2009-06-05 19:09:08','2009-05-19 12:45:03',NULL,'Sir Lancelot',NULL,'Sirrrrlancelot is brave and noble.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',478,1,0,0,'John Doe','jdoe@simplestation.com'),(8,'video','bring-out-your-dead','draft',NULL,'2009-01-12 17:06:47','2009-06-05 18:33:57',NULL,NULL,'Bring Out Your Dead',NULL,'But I\'m not dead yet!','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',118,0,0,0,'John Doe','jdoe@simplestation.com'),(9,'video','three-questions','draft',NULL,'2009-01-12 17:09:55','2009-06-05 18:33:57',NULL,NULL,'Three Questions',NULL,'Sir Lancelot faces skill testing questions.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',244,2,0,0,'John Doe','jdoe@simplestation.com'),(10,'video','tale-sir-robin','publish',NULL,'2009-01-12 18:17:07','2009-06-05 18:33:57','2009-05-19 11:49:36',NULL,'The Tale of Sir Robin',NULL,'Sing this song!','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',173,0,0,0,'John Doe','jdoe@simplestation.com'),(11,'video','guarding-room','publish',NULL,'2009-01-12 18:18:22','2009-06-05 18:33:57','2009-05-19 12:15:53',NULL,'Guarding the Room',NULL,'The trials and tribulations of being a dictator in a self-perpetuating autocracy.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',123,1,0,0,'John Doe','jdoe@simplestation.com'),(12,'video','knights-who-say-ni','publish',NULL,'2009-01-12 18:19:51','2009-06-05 18:33:57','2009-05-19 13:08:58',NULL,'Knights Who Say Ni',NULL,'These knights say ni.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',521,0,0,0,'John Doe','jdoe@simplestation.com'),(13,'video','tim-enchanter','publish',NULL,'2009-01-12 18:20:41','2009-06-05 18:33:57','2009-05-19 12:16:17',NULL,'Tim the Enchanter',NULL,'Tim enchants fire.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',52,1,0,0,'John Doe','jdoe@simplestation.com'),(14,'video','grenade-antioch','draft',NULL,'2009-01-12 18:21:50','2009-06-05 18:33:57',NULL,NULL,'Grenade of Antioch',NULL,'Holy hand grenade!','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',242,0,0,0,'John Doe','jdoe@simplestation.com'),(15,'video','intermission-music','publish',NULL,'2009-01-12 18:36:06','2009-06-05 19:09:08','2009-05-19 12:16:17',NULL,'Intermission Music',NULL,'My personal favorite part of the movie.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',546,2,0,0,'John Doe','jdoe@simplestation.com');
/*!40000 ALTER TABLE `media` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `media_comments`
--

DROP TABLE IF EXISTS `media_comments`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `media_comments` (
  `media_id` int(10) unsigned NOT NULL,
  `comment_id` int(10) unsigned NOT NULL,
  PRIMARY KEY  (`media_id`,`comment_id`),
  UNIQUE KEY `comment_id` (`comment_id`),
  CONSTRAINT `media_comments_ibfk_1` FOREIGN KEY (`media_id`) REFERENCES `media` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `media_comments_ibfk_2` FOREIGN KEY (`comment_id`) REFERENCES `comments` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `media_comments`
--

LOCK TABLES `media_comments` WRITE;
/*!40000 ALTER TABLE `media_comments` DISABLE KEYS */;
/*!40000 ALTER TABLE `media_comments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `media_files`
--

DROP TABLE IF EXISTS `media_files`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `media_files` (
  `id` int(10) unsigned NOT NULL auto_increment,
  `media_id` int(10) unsigned NOT NULL,
  `url` varchar(255) character set ascii NOT NULL,
  `size` int(11) default '0',
  `bitrate` int(11) default NULL,
  `type` varchar(10) default NULL,
  `is_original` tinyint(1) NOT NULL default '0',
  PRIMARY KEY  (`id`),
  KEY `media_files_ibfk_1` (`media_id`),
  CONSTRAINT `media_files_ibfk_1` FOREIGN KEY (`media_id`) REFERENCES `media` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `media_files`
--

LOCK TABLES `media_files` WRITE;
/*!40000 ALTER TABLE `media_files` DISABLE KEYS */;
INSERT INTO `media_files` VALUES (2,1,'1-black-knight.flv',8322240,NULL,'flv',1),(3,2,'http://youtube.com/v/9V7zbWNznbs',NULL,NULL,'youtube',1),(4,3,'http://youtube.com/v/Xe1a1wHxTyo',NULL,NULL,'youtube',1),(5,4,'http://youtube.com/v/XcxKIJTb3Hg',NULL,NULL,'youtube',1),(6,5,'http://youtube.com/v/5Xd_zkMEgkI',NULL,NULL,'youtube',1),(7,6,'http://youtube.com/v/rzcLQRXW6B0',NULL,NULL,'youtube',1),(8,7,'http://youtube.com/v/-jO1EOhGkY0',NULL,NULL,'youtube',1),(9,8,'http://youtube.com/v/grbSQ6O6kbs',NULL,NULL,'youtube',1),(10,9,'http://youtube.com/v/IMxWLuOFyZM',NULL,NULL,'youtube',1),(11,10,'http://youtube.com/v/c4SJ0xR2_bQ',NULL,NULL,'youtube',1),(12,11,'http://youtube.com/v/ekO3Z3XWa0Q',NULL,NULL,'youtube',1),(13,12,'http://youtube.com/v/QTQfGd3G6dg',NULL,NULL,'youtube',1),(14,13,'http://youtube.com/v/JTbrIo1p-So',NULL,NULL,'youtube',1),(15,14,'http://youtube.com/v/apDGPl2SfpA',NULL,NULL,'youtube',1),(16,15,'http://youtube.com/v/9hmDZz5pDOQ',NULL,NULL,'youtube',1);
/*!40000 ALTER TABLE `media_files` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `media_tags`
--

DROP TABLE IF EXISTS `media_tags`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `media_tags` (
  `media_id` int(10) unsigned NOT NULL,
  `tag_id` int(10) unsigned NOT NULL,
  PRIMARY KEY  (`media_id`,`tag_id`),
  KEY `tag_id` (`tag_id`),
  CONSTRAINT `media_tags_ibfk_1` FOREIGN KEY (`media_id`) REFERENCES `media` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `media_tags_ibfk_2` FOREIGN KEY (`tag_id`) REFERENCES `tags` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `media_tags`
--

LOCK TABLES `media_tags` WRITE;
/*!40000 ALTER TABLE `media_tags` DISABLE KEYS */;
/*!40000 ALTER TABLE `media_tags` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `podcasts`
--

DROP TABLE IF EXISTS `podcasts`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `podcasts` (
  `id` int(10) unsigned NOT NULL auto_increment,
  `slug` varchar(50) character set ascii NOT NULL,
  `created_on` datetime NOT NULL,
  `modified_on` datetime NOT NULL,
  `title` varchar(50) NOT NULL,
  `subtitle` varchar(255) default NULL,
  `description` text,
  `category` varchar(50) default NULL,
  `author_name` varchar(50) default NULL,
  `author_email` varchar(50) default NULL,
  `explicit` tinyint(1) NOT NULL,
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
  `id` int(10) unsigned NOT NULL auto_increment,
  `name` varchar(50) NOT NULL,
  `slug` varchar(50) character set ascii NOT NULL,
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
  `group_id` int(10) unsigned NOT NULL auto_increment,
  `group_name` varchar(16) NOT NULL,
  `display_name` varchar(255) default NULL,
  `created` datetime default NULL,
  PRIMARY KEY  (`group_id`),
  UNIQUE KEY `group_name` (`group_name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `tg_group`
--

LOCK TABLES `tg_group` WRITE;
/*!40000 ALTER TABLE `tg_group` DISABLE KEYS */;
INSERT INTO `tg_group` VALUES (1,'Admins','Administrators','2009-05-21 18:41:28');
/*!40000 ALTER TABLE `tg_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tg_group_permission`
--

DROP TABLE IF EXISTS `tg_group_permission`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `tg_group_permission` (
  `group_id` int(10) unsigned default NULL,
  `permission_id` int(10) unsigned default NULL,
  KEY `group_id` (`group_id`),
  KEY `permission_id` (`permission_id`),
  CONSTRAINT `tg_group_permission_ibfk_1` FOREIGN KEY (`group_id`) REFERENCES `tg_group` (`group_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tg_group_permission_ibfk_2` FOREIGN KEY (`permission_id`) REFERENCES `tg_permission` (`permission_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `tg_group_permission`
--

LOCK TABLES `tg_group_permission` WRITE;
/*!40000 ALTER TABLE `tg_group_permission` DISABLE KEYS */;
INSERT INTO `tg_group_permission` VALUES (1,1);
/*!40000 ALTER TABLE `tg_group_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tg_permission`
--

DROP TABLE IF EXISTS `tg_permission`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `tg_permission` (
  `permission_id` int(10) unsigned NOT NULL auto_increment,
  `permission_name` varchar(16) NOT NULL,
  `description` varchar(255) default NULL,
  PRIMARY KEY  (`permission_id`),
  UNIQUE KEY `permission_name` (`permission_name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `tg_permission`
--

LOCK TABLES `tg_permission` WRITE;
/*!40000 ALTER TABLE `tg_permission` DISABLE KEYS */;
INSERT INTO `tg_permission` VALUES (1,'admin','Grants access to the admin panel');
/*!40000 ALTER TABLE `tg_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tg_user`
--

DROP TABLE IF EXISTS `tg_user`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `tg_user` (
  `user_id` int(10) unsigned NOT NULL auto_increment,
  `user_name` varchar(16) NOT NULL,
  `email_address` varchar(255) NOT NULL,
  `display_name` varchar(255) default NULL,
  `password` varchar(80) default NULL,
  `created` datetime default NULL,
  PRIMARY KEY  (`user_id`),
  UNIQUE KEY `user_name` (`user_name`),
  UNIQUE KEY `email_address` (`email_address`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `tg_user`
--

LOCK TABLES `tg_user` WRITE;
/*!40000 ALTER TABLE `tg_user` DISABLE KEYS */;
INSERT INTO `tg_user` VALUES (1,'tmcy','tmcyouth@christianscience.com','TMCYouth','5c97c9bc5a0e00d49781c7d0b65ba545ce22d3ab310c9d0afc7230d9a79b0d1d55a17b03e5be89ed','2009-05-21 18:41:28'),(2,'simplestation','info@simplestation.com','Simple Station Inc.','63bd796fccc9fe83f4fd0ab7976e43e0edc26e3a3e9e447721caefd3d731ebb96ef4fec8d5f24774','2009-05-26 14:45:31');
/*!40000 ALTER TABLE `tg_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tg_user_group`
--

DROP TABLE IF EXISTS `tg_user_group`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `tg_user_group` (
  `user_id` int(10) unsigned default NULL,
  `group_id` int(10) unsigned default NULL,
  KEY `user_id` (`user_id`),
  KEY `group_id` (`group_id`),
  CONSTRAINT `tg_user_group_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `tg_user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tg_user_group_ibfk_2` FOREIGN KEY (`group_id`) REFERENCES `tg_group` (`group_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `tg_user_group`
--

LOCK TABLES `tg_user_group` WRITE;
/*!40000 ALTER TABLE `tg_user_group` DISABLE KEYS */;
INSERT INTO `tg_user_group` VALUES (1,1),(2,1);
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

-- Dump completed on 2009-06-06  2:14:15
