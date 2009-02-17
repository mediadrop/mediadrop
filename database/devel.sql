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
  `name` varchar(50) NOT NULL,
  `subject` varchar(50) default NULL,
  `date_added` datetime NOT NULL,
  `date_modified` datetime NOT NULL,
  `body` text NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `comments`
--

LOCK TABLES `comments` WRITE;
/*!40000 ALTER TABLE `comments` DISABLE KEYS */;
INSERT INTO `comments` VALUES (1,'Nathan Wright','Something else','2009-02-16 15:33:11','2009-02-16 15:33:11','LOUD NOISES!'),(2,'Nathan Wright','And another thing...','2009-02-16 16:12:17','2009-02-16 16:12:17','I love lamp.'),(3,'Nathan Wright','And another thing...','2009-02-16 16:19:35','2009-02-16 16:19:35','I love lamp.');
/*!40000 ALTER TABLE `comments` ENABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `tags`
--

LOCK TABLES `tags` WRITE;
/*!40000 ALTER TABLE `tags` DISABLE KEYS */;
INSERT INTO `tags` VALUES (1,'Monty Python','monty-python'),(2,'Chivalry','chivalry');
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
  `group_name` varchar(16) character set latin1 NOT NULL,
  `display_name` varchar(255) character set latin1 default NULL,
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
  `group_id` int(11) default NULL,
  `permission_id` int(11) default NULL,
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
  `permission_id` int(11) NOT NULL auto_increment,
  `permission_name` varchar(16) character set latin1 NOT NULL,
  `description` varchar(255) character set latin1 default NULL,
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
  `user_id` int(11) NOT NULL auto_increment,
  `user_name` varchar(16) character set latin1 NOT NULL,
  `email_address` varchar(255) character set latin1 NOT NULL,
  `display_name` varchar(255) character set latin1 default NULL,
  `password` varchar(80) character set latin1 default NULL,
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
  `user_id` int(11) default NULL,
  `group_id` int(11) default NULL,
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

--
-- Table structure for table `videos`
--

DROP TABLE IF EXISTS `videos`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `videos` (
  `id` int(11) NOT NULL auto_increment,
  `slug` varchar(50) character set latin1 NOT NULL,
  `title` varchar(50) character set latin1 NOT NULL,
  `url` varchar(255) character set latin1 NOT NULL,
  `length` int(11) NOT NULL,
  `date_added` datetime NOT NULL,
  `date_modified` datetime NOT NULL,
  `views` int(11) NOT NULL,
  `description` text character set latin1,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `videos`
--

LOCK TABLES `videos` WRITE;
/*!40000 ALTER TABLE `videos` DISABLE KEYS */;
INSERT INTO `videos` VALUES (1,'black-knight','The Black Knight','http://www.youtube.com/watch?v=2eMkth8FWno',266,'2009-01-12 16:29:57','2009-01-12 16:29:57',0,'More silliness.'),(2,'french-taunting','French Taunting','http://www.youtube.com/watch?v=9V7zbWNznbs',640,'2009-01-12 16:37:15','2009-01-12 16:37:15',0,'Insults from Monty Python, handy for all occasions!'),(3,'monty-pythons','Monty Python\'s','http://www.youtube.com/watch?v=Xe1a1wHxTyo',194,'2009-01-09 15:52:56','2009-01-09 15:52:56',0,'Some silly nonsensical comedy for you, from Monty Python\'s Flying Circus.'),(4,'killer-bunny','Killer Bunny','http://www.youtube.com/watch?v=XcxKIJTb3Hg',126,'2009-01-12 16:41:05','2009-01-12 16:41:05',0,'A bunny that can kill a man.'),(5,'systems-government','Systems of Government','http://www.youtube.com/watch?v=5Xd_zkMEgkI',191,'2009-01-12 16:48:34','2009-01-12 16:48:34',0,'Political satire.'),(6,'are-you-suggesting-coconuts-migrate','Are you suggesting coconuts migrate?','http://www.youtube.com/watch?v=rzcLQRXW6B0',181,'2009-01-12 16:53:53','2009-01-12 16:53:53',0,'King of the Britons, Defeater of the Saxons banging two empty halves of tropical coconuts together in a temporate climate.'),(7,'sir-lancelot','Sir Lancelot','http://www.youtube.com/watch?v=-jO1EOhGkY0',478,'2009-01-12 16:57:03','2009-01-12 16:57:03',0,'Sirrrrlancelot is brave and noble.'),(8,'bring-out-your-dead','Bring Out Your Dead','http://www.youtube.com/watch?v=grbSQ6O6kbs',118,'2009-01-12 17:06:47','2009-01-12 17:06:47',0,'But I\'m not dead yet!'),(9,'three-questions','Three Questions','http://www.youtube.com/watch?v=IMxWLuOFyZM',244,'2009-01-12 17:09:55','2009-01-12 17:09:55',0,'Sir Lancelot faces skill testing questions.'),(10,'tale-sir-robin','The Tale of Sir Robin','http://www.youtube.com/watch?v=c4SJ0xR2_bQ',173,'2009-01-12 18:17:07','2009-01-12 18:17:07',0,'Sing this song!'),(11,'guarding-room','Guarding the Room','http://www.youtube.com/watch?v=ekO3Z3XWa0Q',123,'2009-01-12 18:18:22','2009-01-12 18:18:22',0,'Something goes here, something like a description.'),(12,'knights-who-say-ni','Knights Who Say Ni','http://www.youtube.com/watch?v=QTQfGd3G6dg',521,'2009-01-12 18:19:51','2009-01-12 18:19:51',0,'These knights say ni.'),(13,'tim-enchanter','Tim the Enchanter','http://www.youtube.com/watch?v=JTbrIo1p-So',52,'2009-01-12 18:20:41','2009-01-12 18:20:41',0,'Enchanting tim'),(14,'grenade-antioch','Grenade of Antioch','http://www.youtube.com/watch?v=apDGPl2SfpA',242,'2009-01-12 18:21:50','2009-01-12 18:21:50',0,'Holy hand grenade!'),(15,'intermission-music','Intermission Music','http://www.youtube.com/watch?v=9hmDZz5pDOQ',546,'2009-01-12 18:36:06','2009-01-12 18:36:06',0,'From the movie');
/*!40000 ALTER TABLE `videos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `videos_comments`
--

DROP TABLE IF EXISTS `videos_comments`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `videos_comments` (
  `video_id` int(11) NOT NULL,
  `comment_id` int(11) NOT NULL,
  PRIMARY KEY  (`video_id`,`comment_id`),
  UNIQUE KEY `comment_id` (`comment_id`),
  CONSTRAINT `videos_comments_ibfk_1` FOREIGN KEY (`video_id`) REFERENCES `videos` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `videos_comments_ibfk_2` FOREIGN KEY (`comment_id`) REFERENCES `comments` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `videos_comments`
--

LOCK TABLES `videos_comments` WRITE;
/*!40000 ALTER TABLE `videos_comments` DISABLE KEYS */;
INSERT INTO `videos_comments` VALUES (1,1),(1,2),(1,3);
/*!40000 ALTER TABLE `videos_comments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `videos_tags`
--

DROP TABLE IF EXISTS `videos_tags`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `videos_tags` (
  `video_id` int(11) NOT NULL,
  `tag_id` int(11) NOT NULL,
  PRIMARY KEY  (`video_id`,`tag_id`),
  KEY `tag_id` (`tag_id`),
  CONSTRAINT `videos_tags_ibfk_1` FOREIGN KEY (`video_id`) REFERENCES `videos` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `videos_tags_ibfk_2` FOREIGN KEY (`tag_id`) REFERENCES `tags` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `videos_tags`
--

LOCK TABLES `videos_tags` WRITE;
/*!40000 ALTER TABLE `videos_tags` DISABLE KEYS */;
INSERT INTO `videos_tags` VALUES (1,1),(1,2);
/*!40000 ALTER TABLE `videos_tags` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2009-02-17 18:02:05
