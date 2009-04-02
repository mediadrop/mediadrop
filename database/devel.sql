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

SET character_set_client = utf8;

--
-- Table structure for table `comments`
--

DROP TABLE IF EXISTS `comments`;
CREATE TABLE `comments` (
  `id` int(10) UNSIGNED NOT NULL auto_increment,
  `type` varchar(15) NOT NULL,
  `subject` varchar(100) NOT NULL,
  `created_on` datetime NOT NULL,
  `modified_on` datetime NOT NULL,
  `status` enum('trash','publish','pending_review') NOT NULL,
  `author_name` varchar(50) NOT NULL,
  `author_email` varchar(255) default NULL,
  `author_ip` int(10) UNSIGNED NOT NULL,
  `body` text NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB CHARSET=utf8;

--
-- Table structure for table `media`
--

DROP TABLE IF EXISTS `media`;
CREATE TABLE `media` (
  `id` int(10) UNSIGNED NOT NULL auto_increment,
  `type` varchar(10) NOT NULL,
  `slug` varchar(50) NOT NULL,
  `created_on` datetime NOT NULL,
  `modified_on` datetime NOT NULL,
  `publish_on` datetime default NULL,
  `status` set('trash','publish','draft','pending_encoding','pending_review') NOT NULL,
  `title` varchar(50) NOT NULL,
  `description` text,
  `notes` text,
  `duration` int(10) UNSIGNED NOT NULL,
  `views` int(10) UNSIGNED NOT NULL default 0,
  `upload_url` varchar(255) default NULL,
  `url` varchar(255) default NULL,
  `author_name` varchar(50) NOT NULL,
  `author_email` varchar(255) NOT NULL,
  `rating_sum` int(10) UNSIGNED NOT NULL default 0,
  `rating_votes` int(10) UNSIGNED NOT NULL default 0,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB CHARSET=utf8;

--
-- Table structure for table `media_comments`
--

DROP TABLE IF EXISTS `media_comments`;
CREATE TABLE `media_comments` (
  `media_id` int(10) UNSIGNED NOT NULL,
  `comment_id` int(10) UNSIGNED NOT NULL,
  PRIMARY KEY  (`media_id`,`comment_id`),
  UNIQUE KEY `comment_id` (`comment_id`),
  CONSTRAINT `media_comments_ibfk_1` FOREIGN KEY (`media_id`) REFERENCES `media` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `media_comments_ibfk_2` FOREIGN KEY (`comment_id`) REFERENCES `comments` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB CHARSET=utf8;

--
-- Table structure for table `media_tags`
--

DROP TABLE IF EXISTS `media_tags`;
CREATE TABLE `media_tags` (
  `media_id` int(10) UNSIGNED NOT NULL,
  `tag_id` int(10) UNSIGNED NOT NULL,
  PRIMARY KEY  (`media_id`,`tag_id`),
  KEY `tag_id` (`tag_id`),
  CONSTRAINT `media_tags_ibfk_1` FOREIGN KEY (`media_id`) REFERENCES `media` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `media_tags_ibfk_2` FOREIGN KEY (`tag_id`) REFERENCES `tags` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB CHARSET=utf8;

--
-- Table structure for table `podcast_episodes`
--

DROP TABLE IF EXISTS `podcast_episodes`;
CREATE TABLE `podcast_episodes` (
  `id` int(10) UNSIGNED NOT NULL auto_increment,
  `slug` varchar(50) NOT NULL,
  `podcast_id` int(10) UNSIGNED NOT NULL,
  `media_id` int(10) UNSIGNED NOT NULL,
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
) ENGINE=InnoDB CHARSET=utf8;

--
-- Table structure for table `podcasts`
--

DROP TABLE IF EXISTS `podcasts`;
CREATE TABLE `podcasts` (
  `id` int(10) UNSIGNED NOT NULL auto_increment,
  `slug` varchar(50) NOT NULL,
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
) ENGINE=InnoDB CHARSET=utf8;

--
-- Table structure for table `tags`
--

DROP TABLE IF EXISTS `tags`;
CREATE TABLE `tags` (
  `id` int(10) UNSIGNED NOT NULL auto_increment,
  `name` varchar(50) NOT NULL,
  `slug` varchar(50) NOT NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB CHARSET=utf8;

--
-- Table structure for table `tg_group`
--

DROP TABLE IF EXISTS `tg_group`;
CREATE TABLE `tg_group` (
  `group_id` int(10) UNSIGNED NOT NULL auto_increment,
  `group_name` varchar(16) NOT NULL,
  `display_name` varchar(255) default NULL,
  `created` datetime default NULL,
  PRIMARY KEY  (`group_id`),
  UNIQUE KEY `group_name` (`group_name`)
) ENGINE=InnoDB CHARSET=utf8;

--
-- Table structure for table `tg_group_permission`
--

DROP TABLE IF EXISTS `tg_group_permission`;
CREATE TABLE `tg_group_permission` (
  `group_id` int(10) UNSIGNED default NULL,
  `permission_id` int(10) UNSIGNED default NULL,
  KEY `group_id` (`group_id`),
  KEY `permission_id` (`permission_id`),
  CONSTRAINT `tg_group_permission_ibfk_1` FOREIGN KEY (`group_id`) REFERENCES `tg_group` (`group_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tg_group_permission_ibfk_2` FOREIGN KEY (`permission_id`) REFERENCES `tg_permission` (`permission_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB CHARSET=utf8;

--
-- Table structure for table `tg_permission`
--

DROP TABLE IF EXISTS `tg_permission`;
CREATE TABLE `tg_permission` (
  `permission_id` int(10) UNSIGNED NOT NULL auto_increment,
  `permission_name` varchar(16) NOT NULL,
  `description` varchar(255) default NULL,
  PRIMARY KEY  (`permission_id`),
  UNIQUE KEY `permission_name` (`permission_name`)
) ENGINE=InnoDB CHARSET=utf8;

--
-- Table structure for table `tg_user`
--

DROP TABLE IF EXISTS `tg_user`;
CREATE TABLE `tg_user` (
  `user_id` int(10) UNSIGNED NOT NULL auto_increment,
  `user_name` varchar(16) NOT NULL,
  `email_address` varchar(255) NOT NULL,
  `display_name` varchar(255) default NULL,
  `password` varchar(80) default NULL,
  `created` datetime default NULL,
  PRIMARY KEY  (`user_id`),
  UNIQUE KEY `user_name` (`user_name`),
  UNIQUE KEY `email_address` (`email_address`)
) ENGINE=InnoDB CHARSET=utf8;

--
-- Table structure for table `tg_user_group`
--

DROP TABLE IF EXISTS `tg_user_group`;
CREATE TABLE `tg_user_group` (
  `user_id` int(10) UNSIGNED default NULL,
  `group_id` int(10) UNSIGNED default NULL,
  KEY `user_id` (`user_id`),
  KEY `group_id` (`group_id`),
  CONSTRAINT `tg_user_group_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `tg_user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tg_user_group_ibfk_2` FOREIGN KEY (`group_id`) REFERENCES `tg_group` (`group_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB CHARSET=utf8;


UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
