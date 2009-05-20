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
  `type` varchar(15) NOT NULL,
  `subject` varchar(100) NOT NULL,
  `created_on` datetime NOT NULL,
  `modified_on` datetime NOT NULL,
  `status` set('trash','publish','pending_review','user_flagged') NOT NULL default 'publish',
  `author_name` varchar(50) NOT NULL,
  `author_email` varchar(255) default NULL,
  `author_ip` int(10) unsigned NOT NULL,
  `body` text NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `comments`
--

LOCK TABLES `comments` WRITE;
/*!40000 ALTER TABLE `comments` DISABLE KEYS */;
INSERT INTO `comments` VALUES (1,'media','Re: The Black Knight','2009-05-11 10:54:58','2009-05-11 11:09:32','publish','Some comment',NULL,2130706433,'asdfsadf'),(2,'media','Re: Four Yorkshiremen','2009-05-19 17:33:11','2009-05-19 17:33:11','pending_review','testest',NULL,2130706433,'test'),(3,'media','Re: Four Yorkshiremen','2009-05-19 17:33:40','2009-05-19 17:33:40','pending_review','testsetsttest',NULL,2130706433,'teste'),(4,'media','Re: Four Yorkshiremen','2009-05-19 17:49:57','2009-05-19 17:49:57','pending_review','testagain',NULL,2130706433,'testmixin');
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
  `type` varchar(10) NOT NULL,
  `slug` varchar(50) character set ascii default NULL,
  `created_on` datetime NOT NULL,
  `modified_on` datetime NOT NULL,
  `publish_on` datetime default NULL,
  `status` set('trash','publish','draft','pending_encoding','pending_review') NOT NULL,
  `title` varchar(50) NOT NULL,
  `description` text,
  `notes` text,
  `duration` int(10) unsigned NOT NULL,
  `views` int(10) unsigned NOT NULL default '0',
  `upload_url` varchar(255) default NULL,
  `url` varchar(255) default NULL,
  `author_name` varchar(50) NOT NULL,
  `author_email` varchar(255) NOT NULL,
  `rating_sum` int(10) unsigned NOT NULL default '0',
  `rating_votes` int(10) unsigned NOT NULL default '0',
  PRIMARY KEY  (`id`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `media`
--

LOCK TABLES `media` WRITE;
/*!40000 ALTER TABLE `media` DISABLE KEYS */;
INSERT INTO `media` VALUES (1,'video','black-knight','2009-01-12 16:29:57','2009-05-11 20:27:00','0000-00-00 00:00:00','draft,pending_encoding,pending_review','The Black Knight','A classic moment from Monty Python and the Holy Grail.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',4,21,NULL,'/video/flv/1-black-knight.flv','Nathan','nathan@simplestation.com',0,0),(2,'video','french-taunting','2009-01-12 16:37:15','2009-05-19 17:06:41','2009-03-12 19:35:26','publish','French Taunting','A memorable scene from Monty Python & the Holy Grail.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',640,6,NULL,'http://youtube.com/v/9V7zbWNznbs','Verity','verity@norman.com',0,0),(3,'video','four-yorkshiremen','2009-01-09 15:52:56','2009-05-19 17:51:58','2009-01-09 15:52:56','publish','Four Yorkshiremen','Some silly nonsensical comedy for you, from Monty Python\'s Flying Circus.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',186,30,NULL,'http://youtube.com/v/Xe1a1wHxTyo','George Clements','george@clements.com',0,0),(4,'video','killer-bunny','2009-01-12 16:41:05','2009-05-08 13:50:03','2009-01-12 16:41:05','publish','Killer Bunny','A bunny that can kill a man.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',126,1,NULL,'http://youtube.com/v/XcxKIJTb3Hg','Tom','tom@hulu.com',0,0),(5,'video','systems-government','2009-01-12 16:48:34','2009-05-08 13:55:53','2009-01-12 16:48:34','publish','Systems of Government','Political satire.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',191,1,NULL,'http://youtube.com/v/5Xd_zkMEgkI','George','george@dragon.com',0,0),(6,'video','are-you-suggesting-coconuts-migrate','2009-01-12 16:53:53','2009-05-13 14:15:40','2009-01-12 16:53:53','publish','Are you suggesting coconuts migrate?','King of the Britons, Defeater of the Saxons banging two empty halves of tropical coconuts together in a temporate climate.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',181,1,NULL,'http://youtube.com/v/rzcLQRXW6B0','Morgan','morgan@csps.com',0,0),(7,'video','sir-lancelot','2009-01-12 16:57:03','2009-05-19 12:45:03','2009-05-19 12:45:03','publish','Sir Lancelot','Sirrrrlancelot is brave and noble.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',478,1,NULL,'http://youtube.com/v/-jO1EOhGkY0','John Doe','jdoe@simplestation.com',0,0),(8,'video','bring-out-your-dead','2009-01-12 17:06:47','2009-05-08 13:52:13','0000-00-00 00:00:00','draft,pending_review','Bring Out Your Dead','But I\'m not dead yet!','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',118,0,NULL,'http://youtube.com/v/grbSQ6O6kbs','John Doe','jdoe@simplestation.com',0,0),(9,'video','three-questions','2009-01-12 17:09:55','2009-05-14 14:31:38','0000-00-00 00:00:00','draft,pending_review','Three Questions','Sir Lancelot faces skill testing questions.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',244,2,NULL,'http://youtube.com/v/IMxWLuOFyZM','John Doe','jdoe@simplestation.com',0,0),(10,'video','tale-sir-robin','2009-01-12 18:17:07','2009-05-19 11:49:36','2009-05-19 11:49:36','publish','The Tale of Sir Robin','Sing this song!','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',173,0,NULL,'http://youtube.com/v/c4SJ0xR2_bQ','John Doe','jdoe@simplestation.com',0,0),(11,'video','guarding-room','2009-01-12 18:18:22','2009-05-19 12:15:53','2009-05-19 12:15:53','publish','Guarding the Room','The trials and tribulations of being a dictator in a self-perpetuating autocracy.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',123,1,NULL,'http://youtube.com/v/ekO3Z3XWa0Q','John Doe','jdoe@simplestation.com',0,0),(12,'video','knights-who-say-ni','2009-01-12 18:19:51','2009-05-19 13:08:58','2009-05-19 13:08:58','publish','Knights Who Say Ni','These knights say ni.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',521,0,NULL,'http://youtube.com/v/QTQfGd3G6dg','John Doe','jdoe@simplestation.com',0,0),(13,'video','tim-enchanter','2009-01-12 18:20:41','2009-05-08 14:01:49','2009-05-19 12:16:17','publish','Tim the Enchanter','Tim enchants fire.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',52,1,NULL,'http://youtube.com/v/JTbrIo1p-So','John Doe','jdoe@simplestation.com',0,0),(14,'video','grenade-antioch','2009-01-12 18:21:50','2009-05-08 14:04:15','0000-00-00 00:00:00','draft,pending_review','Grenade of Antioch','Holy hand grenade!','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',242,0,NULL,'http://youtube.com/v/apDGPl2SfpA','John Doe','jdoe@simplestation.com',0,0),(15,'video','intermission-music','2009-01-12 18:36:06','2009-05-19 12:16:17','2009-05-19 12:16:17','publish','Intermission Music','My personal favorite part of the movie.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',546,2,NULL,'http://youtube.com/v/9hmDZz5pDOQ','John Doe','jdoe@simplestation.com',0,0);
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
INSERT INTO `media_comments` VALUES (1,1),(3,2),(3,3),(3,4);
/*!40000 ALTER TABLE `media_comments` ENABLE KEYS */;
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
INSERT INTO `media_tags` VALUES (1,1),(2,1),(3,1),(4,1),(5,1),(6,1),(7,1),(8,1),(9,1),(10,1),(11,1),(12,1),(13,1),(14,1),(15,1),(7,2),(11,2),(3,3),(1,4),(2,4),(4,4),(5,4),(6,4),(7,4),(8,4),(9,4),(10,4),(11,4),(12,4),(13,4),(14,4),(15,4),(4,5),(6,5),(5,6),(5,7),(11,7),(6,9),(8,10),(9,11),(10,12),(13,13),(14,14);
/*!40000 ALTER TABLE `media_tags` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `podcast_episodes`
--

DROP TABLE IF EXISTS `podcast_episodes`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `podcast_episodes` (
  `id` int(10) unsigned NOT NULL auto_increment,
  `slug` varchar(50) character set ascii NOT NULL,
  `podcast_id` int(10) unsigned NOT NULL,
  `media_id` int(10) unsigned NOT NULL,
  `created_on` datetime NOT NULL,
  `modified_on` datetime NOT NULL,
  `publish_on` datetime default NULL,
  `publish_until` datetime default NULL,
  `title` varchar(50) NOT NULL,
  `subtitle` varchar(255) default NULL,
  `description` text,
  `category` varchar(50) default NULL,
  `author_name` varchar(50) default NULL,
  `author_email` varchar(50) default NULL,
  `copyright` varchar(50) default NULL,
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
  `copyright` varchar(50) default NULL,
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
  `id` int(10) unsigned NOT NULL auto_increment,
  `name` varchar(50) NOT NULL,
  `slug` varchar(50) character set ascii NOT NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `tags`
--

LOCK TABLES `tags` WRITE;
/*!40000 ALTER TABLE `tags` DISABLE KEYS */;
INSERT INTO `tags` VALUES (1,'Monty Python','monty-python'),(2,'Chivalry','chivalry'),(3,'Flying Circus','flying-circus'),(4,'Holy Grail','holy-grail'),(5,'Animals','animals'),(6,'Politics','politics'),(7,'Power','power'),(8,'Fruit','fruit'),(9,'Africa','africa'),(10,'Life After Death','life-after-death'),(11,'Challenges','challenges'),(12,'Folk Songs','folk-songs'),(13,'Fire','fire'),(14,'Eccentric Performances','eccentric-performances'),(15,'Limbo','limbo');
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
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
  `user_id` int(10) unsigned NOT NULL auto_increment,
  `user_name` varchar(16) NOT NULL,
  `email_address` varchar(255) NOT NULL,
  `display_name` varchar(255) default NULL,
  `password` varchar(80) default NULL,
  `created` datetime default NULL,
  PRIMARY KEY  (`user_id`),
  UNIQUE KEY `user_name` (`user_name`),
  UNIQUE KEY `email_address` (`email_address`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
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

-- Dump completed on 2009-05-20  2:10:49
