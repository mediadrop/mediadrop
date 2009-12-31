-- MySQL dump 10.11
--
-- Host: localhost    Database: mediacore
-- ------------------------------------------------------
-- Server version	5.0.51a

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
INSERT INTO `comments` VALUES (1,'media','Re: The Black Knight','2009-05-11 10:54:58','2009-05-11 11:09:32','publish','Some comment',NULL,2130706433,'asdfsadf'),
(2,'media','Re: Four Yorkshiremen','2009-05-19 17:33:11','2009-05-28 17:24:28','publish','testest',NULL,2130706433,'test'),
(3,'media','Re: Four Yorkshiremen','2009-05-19 17:33:40','2009-05-19 17:33:40','','testsetsttest',NULL,2130706433,'teste'),
(4,'media','Re: Four Yorkshiremen','2009-05-19 17:49:57','2009-05-19 17:49:57','','testagain',NULL,2130706433,'testmixin'),
(5,'media','Re: Three Questions','2009-05-31 17:22:58','2009-05-31 17:22:58','','Nate',NULL,2130706433,'Here\'s a question for you.\r\n\r\nDoes this work?');
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
  `type` enum('audio','video','placeholder') NOT NULL default 'placeholder',
  `slug` varchar(50) character set ascii default NULL,
  `status` set('trash','publish','draft','unencoded','unreviewed') default NULL,
  `podcast_id` int(10) unsigned default NULL,
  `created_on` datetime NOT NULL,
  `modified_on` datetime NOT NULL,
  `publish_on` datetime default NULL,
  `publish_until` datetime default NULL,
  `title` varchar(255) default NULL,
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
) ENGINE=InnoDB AUTO_INCREMENT=61 DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `media`
--

LOCK TABLES `media` WRITE;
/*!40000 ALTER TABLE `media` DISABLE KEYS */;
INSERT INTO `media` VALUES (1,'video','black-knight','draft',NULL,'2009-01-12 16:29:57','2009-06-09 12:19:31',NULL,NULL,'The Black Knight',NULL,'A classic moment from Monty Python and the Holy Grail.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',4,28,2,2,'Nathan','nathan@simplestation.com'),
(2,'video','french-taunting','publish',NULL,'2009-01-12 16:37:15','2009-06-09 14:29:46','2009-03-12 19:35:26',NULL,'French Taunting',NULL,'A memorable scene from Monty Python & the Holy Grail.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',640,14,0,0,'Verity','verity@norman.com'),
(3,'video','four-yorkshiremen','publish',NULL,'2009-01-09 15:52:56','2009-06-05 18:33:57','2009-01-09 15:52:56',NULL,'Four Yorkshiremen',NULL,'Some silly nonsensical comedy for you, from Monty Python\'s Flying Circus.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',186,30,0,0,'George Clements','george@clements.com'),
(4,'video','killer-bunny','publish',NULL,'2009-01-12 16:41:05','2009-06-09 11:58:59','2009-01-12 16:41:05',NULL,'Killer Bunny',NULL,'A bunny that can kill a man.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',126,7,4,4,'Tom','tom@hulu.com'),
(5,'video','systems-government','publish',NULL,'2009-01-12 16:48:34','2009-06-05 18:33:57','2009-01-12 16:48:34',NULL,'Systems of Government',NULL,'Political satire.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',191,1,0,0,'George','george@dragon.com'),
(6,'video','are-you-suggesting-coconuts-migrate','publish',NULL,'2009-01-12 16:53:53','2009-06-09 18:25:36','2009-01-12 16:53:53',NULL,'Are you suggesting coconuts migrate?',NULL,'King of the Britons, Defeater of the Saxons banging two empty halves of tropical coconuts together in a temporate climate.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',181,7,1,1,'Morgan','morgan@csps.com'),
(7,'video','sir-lancelot','publish',NULL,'2009-01-12 16:57:03','2009-06-05 19:09:08','2009-05-19 12:45:03',NULL,'Sir Lancelot',NULL,'Sirrrrlancelot is brave and noble.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',478,1,0,0,'John Doe','jdoe@simplestation.com'),
(8,'video','bring-out-your-dead','draft',NULL,'2009-01-12 17:06:47','2009-06-05 18:33:57',NULL,NULL,'Bring Out Your Dead',NULL,'But I\'m not dead yet!','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',118,0,0,0,'John Doe','jdoe@simplestation.com'),
(9,'video','three-questions','draft',NULL,'2009-01-12 17:09:55','2009-06-05 18:33:57',NULL,NULL,'Three Questions',NULL,'Sir Lancelot faces skill testing questions.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',244,2,0,0,'John Doe','jdoe@simplestation.com'),
(10,'video','tale-sir-robin','publish',NULL,'2009-01-12 18:17:07','2009-06-09 14:31:58','2009-05-19 11:49:36',NULL,'The Tale of Sir Robin',NULL,'Sing this song!','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',173,1,0,0,'John Doe','jdoe@simplestation.com'),
(11,'video','guarding-room','publish',NULL,'2009-01-12 18:18:22','2009-06-09 12:21:30','2009-05-19 12:15:53',NULL,'Guarding the Room',NULL,'The trials and tribulations of being a dictator in a self-perpetuating autocracy.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',123,4,3,3,'John Doe','jdoe@simplestation.com'),
(12,'video','knights-who-say-ni','publish',NULL,'2009-01-12 18:19:51','2009-06-05 18:33:57','2009-05-19 13:08:58',NULL,'Knights Who Say Ni',NULL,'These knights say ni.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',521,0,0,0,'John Doe','jdoe@simplestation.com'),
(13,'video','tim-enchanter','publish',NULL,'2009-01-12 18:20:41','2009-06-05 18:33:57','2009-05-19 12:16:17',NULL,'Tim the Enchanter',NULL,'Tim enchants fire.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',52,1,0,0,'John Doe','jdoe@simplestation.com'),
(14,'video','grenade-antioch','draft',NULL,'2009-01-12 18:21:50','2009-06-05 18:33:57',NULL,NULL,'Grenade of Antioch',NULL,'Holy hand grenade!','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',242,0,0,0,'John Doe','jdoe@simplestation.com'),
(15,'video','intermission-music','publish',NULL,'2009-01-12 18:36:06','2009-06-05 19:09:08','2009-05-19 12:16:17',NULL,'Intermission Music',NULL,'My personal favorite part of the movie.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',546,2,0,0,'John Doe','jdoe@simplestation.com'),
(16,'video','burglarizor','draft,unreviewed',NULL,'2009-06-09 12:56:52','2009-06-09 12:56:52',NULL,NULL,'Burglarizor',NULL,'Its the hamburglerizor','Bible References: None\nS&H References: None\nReviewer: None\nLicense: General Upload',135,0,0,0,'FirstName','email@email.com'),
(22,'audio','macbreak-145','publish',15,'2009-06-16 00:00:00','2009-06-16 00:00:00','2009-06-16 00:00:00',NULL,'MacBreak Weekly 145: The Bourne Rescue',NULL,'iPhone 3G S, Mophie Juice Pack Air, express card ports, App Store politics, and more.\n\niPhone 3G S, Mophie Juice Pack Air, express card ports, App Store politics, and more.\n\nPicks of the week:\n\n	* Leo Laporte: Google Quick Search Box - Free\n\n	* Alex Lindsay: Dock Gone - Free Trial; $14.95\n\n	* Scott Bourne: Fluid Mask 3 - Free Trial; $145\n\n	* Andy Ihnatko: aSmart HUD - $0.95\nAudible picks of the week: Ulysses, Unabridged, By James Joyce, Narrated by Jim Norton with Marcella Riordan and Survival Phrases - Chinese, Part 1: Lessons 1-30, Abridged, By Michael Armstrong, Narrated by Michael Armstrong. For a free audiobook, visit Audible.com/macbreak.',NULL,0,0,0,0,'Leo Laporte','a@b.c'),
(25,'audio','macbreak-144','publish',15,'2009-06-09 00:00:00','2009-06-09 00:00:00','2009-06-09 00:00:00',NULL,'MacBreak Weekly 144: WWDC Wrap Up',NULL,'WWDC report, a new iPhone, AT&T, Palm Pre, App Store power, video, voice dialing, compass, and more.',NULL,0,0,0,0,'Leo Laporte','a@b.c'),
(30,'audio','giz-wiz-853','publish',7,'2009-06-16 00:00:00','2009-06-16 00:00:00','2009-06-16 00:00:00',NULL,'Daily Giz Wiz 853: Snapper Boat Latch',NULL,'Hosts: Dick DeBartolo with Leo Laporte\n\nRelease your boat from its trailer remotely with the Snapper Boat Latch.\n\nAudible pick of the week: Yes!: 50 Scientifically Proven Ways to Be Persuasive, Unabridged, By Noah J. Goldstein, Steve J. Martin, Robert B. Cialdini. Narrated by Blair Hardman. For a free credit toward the audiobook of your choice, visit Audible.com/gizwiz.\n\nFor more details and a chance to win the Mad Magazine \"What The Heck Is It?\" contest, visit GizWizBiz.com.\n\nBandwidth for the Daily Giz Wiz is provided by AOL Radio',NULL,3,0,0,0,'Dick DeBartolo ','dick@gizwiz.biz'),
(32,'audio','giz-wiz-854','publish',7,'2009-06-17 00:00:00','2009-06-17 00:00:00','2009-06-17 00:00:00',NULL,'Daily Giz Wiz 854: Samsung U5',NULL,'Hosts: Dick DeBartolo with Leo Laporte\n\nListen to your music while out and about with the Samsung U5.\n\nFor more details and a chance to win the Mad Magazine \"What The Heck Is It?\" contest, visit GizWizBiz.com.\n\nBandwidth for the Daily Giz Wiz is provided by AOL Radio',NULL,3,0,0,0,'Dick DeBartolo ','dick@gizwiz.biz'),
(33,'audio','giz-wiz-852','publish',7,'2009-06-15 00:00:00','2009-06-15 00:00:00','2009-06-15 00:00:00',NULL,'Daily Giz Wiz 852: BlueAnt Q1',NULL,'Hosts: Dick DeBartolo with Leo Laporte\n\nYou only need to use your voice to control your BlueAnt Q1 Bluetooth headset.\n\nFor more details and a chance to win the Mad Magazine \"What The Heck Is It?\" contest, visit GizWizBiz.com.\n\nBandwidth for the Daily Giz Wiz is provided by AOL Radio',NULL,3,0,0,0,'Dick DeBartolo ','dick@gizwiz.biz'),
(34,'audio','giz-wiz-851','publish',7,'2009-06-14 00:00:00','2009-06-14 00:00:00','2009-06-14 00:00:00',NULL,'Daily Giz Wiz 851: ClickFree DVD Transformer',NULL,'Hosts: Dick DeBartolo with Leo Laporte\nBack up your files without opening your computer or messing with software, with the ClickFree DVD Transformer\n\nFor more details and a chance to win the Mad Magazine \"What The Heck Is It?\" contest, visit GizWizBiz.com.\n\nBandwidth for the Daily Giz Wiz is provided by AOL Radio',NULL,3,0,0,0,'Dick DeBartolo ','dick@gizwiz.biz'),
(35,'audio','twif-22','publish',16,'2009-06-16 00:00:00','2009-06-16 00:00:00','2009-06-16 00:00:00',NULL,'TWiF 22: I Love Corn',NULL,'Hosts: Sarah Lane and Martin Sargent\n\nFacebook name grab, Crunchberries arent real fruit, prison time for underwear theft, and more.\n\n	* The Digital TV Transition\n	* Millions Grab Facebook User Names, Leaving Others In Their Dust\n	* Judge \n	Dismisses Suit Claiming Cap’n Crunch ‘Crunchberries’ Aren’t Real Fruit\n	* No Company Vacations for Googlers This Year\n	* A Really Goode Job - View Applicant Videos: Who do you like?\n	* Ohio man sentenced to 9 years in prison for stealing underwear...\n	* Hundreds of snakes take over police station\n\nWiki for this episode\n\nThanks to Cachefly for the bandwidth for this show.',NULL,3,0,0,0,'Sarah Lane','sarah@sarahlane.com'),
(36,'audio','twif-21','publish',16,'2009-06-08 00:00:00','2009-06-08 00:00:00','2009-06-08 00:00:00',NULL,'TWiF 21: I Broke My Vaynerchuk',NULL,'Hosts: Sarah Lane and Martin Sargent\n\nTwittering into a tree, anti-piracy puppy, prosecutor prosecuted, boy booty boosts business, and more.\n\n	* Man jogs into tree while using Twitter\n	* Anti-piracy pup sniffs out 35,000 illegal DVDs\n	* Miami-Dade prosecutor charged with punching pizza delivery woman\n	* Wanted: Male Prostitutes at Nevada Brothel in Hopes of Boosting Business\n	* \"Space Headache\" a New Type of Astronaut Affliction?\n\nWiki for this episode\n\nThanks to Cachefly for the bandwidth for this show.',NULL,3,0,0,0,'Sarah Lane','sarah@sarahlane.com'),
(37,'audio','futures-biotech-43','publish',17,'2009-05-31 00:00:00','2009-05-31 00:00:00','2009-05-31 00:00:00',NULL,'Futures in Biotech 43: Temporal Alien Mammoth Over',NULL,'Marc Pelletier, Vincent Racaniello, Andre Nantel, Justin Sanchez, and Dave Brodbeck.\n\nFrom wooly mammoths, to cybernetics, and controlling your computer with your brain, a panel discusses the recent big stories in bioscience.\n\nShow notes wiki\nComments and suggestions on Futures in Biotech.\n\nTranscripts to the shows are now available on the FiB Extras blog thanks tom.price@podsinprint.com, PodsinPrint\n\nAlso thanks to Phil Pelletier and Will Hall for the great themes.',NULL,3,0,0,0,'Marc Pelletier','marc@futuresinbiotech.com'),
(38,'video','rim-introduces','publish',NULL,'2009-06-17 20:51:03','2009-06-17 20:51:03','2009-01-09 15:52:56',NULL,'RIM Introduces the BlackBerry Tour Smartphone',NULL,'New 3G World Phone Keeps You Connected on High-Speed CDMA Networks in North America and UMTS/HSPA Networks Abroad','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',17,20,15,15,'Anthony','anthony@simplestation.com'),
(39,'video','blackbery-9630-walkthrough','publish',NULL,'2009-06-17 20:51:03','2009-06-17 20:51:03','2009-01-09 15:52:56',NULL,'BlackBerry 9630 Walkthrough',NULL,'Check out our real brief walkthrough of the BlackBerry 9630. Look for more good stuff soon!','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',81,28,1,1,'Anthony','anthony@simplestation.com'),
(40,'video','htc-touch-diamond-2','publish',NULL,'2009-06-17 20:51:03','2009-06-17 20:51:03','2009-01-09 15:52:56',NULL,'HTC Touch Diamond 2 Promo & Demo',NULL,'A more personal way to converse. Keep the spotlight on the people in your life, with all your dialogues in one convenient screen!','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',112,1,0,0,'Anthony','anthony@simplestation.com'),
(41,'video','virtual-touchpad','publish',NULL,'2009-06-17 20:51:03','2009-06-17 20:51:03','2009-01-09 15:52:56',NULL,'Virtual Touchpad - Lets you scroll in the air!',NULL,'This new Microsoft interface could soon allow you to use the area around a phone to control it.\r\nRead more at http://technology.newscientist.com/channel/tech/dn15044?DCMP=youtube','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',59,31,19,19,'Anthony','anthony@simplestation.com'),
(42,'video','vortex-physics','publish',NULL,'2009-06-17 20:51:03','2009-06-17 20:51:03','2009-01-09 15:52:56',NULL,'State-of-the-art Graphics Reveal Vortex Physics',NULL,'Watch some stunning new vortex simulations that are helping physicists understand turbulence.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',121,17,8,8,'Anthony','anthony@simplestation.com'),
(43,'video','laser-pointer','publish',NULL,'2009-06-17 20:51:03','2009-06-17 20:51:03','2009-01-09 15:52:56',NULL,'Green Laser Pointer and Crystal Ball',NULL,'Amazing beam effects from a high power Viper green laser pointer when the beam is diffracted through a glass bowl.\r\nviper green laser pointer is from Dragonlasers at http://www.dragonlasers.com','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',11,20,7,7,'Anthony','anthony@simplestation.com'),
(44,'video','sonic-boom','publish',NULL,'2009-06-17 20:51:03','2009-06-17 20:51:03','2009-01-09 15:52:56',NULL,'Sonic Booms',NULL,'Join us as we look into the fascinating topic of supersonic travel and we examine the amazing phenomenon of sonic booms!\r\nLightning video courtesy of Rhino Concepts.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',151,0,0,0,'Anthony','anthony@simplestation.com'),
(45,'video','ukulele-weeps','publish',NULL,'2009-06-17 20:51:03','2009-06-17 20:51:03','2009-01-09 15:52:56',NULL,'Ukulele Gently Weeps',NULL,'Jake Shimabukuro plays a cover of George Harrison\'s While My Guitar Gently Weeps on ukulele in New York\'s Central Park','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',274,4,2,2,'Anthony','anthony@simplestation.com'),
(46,'video','orange-world','publish',NULL,'2009-06-17 20:51:03','2009-06-17 20:51:03','2009-01-09 15:52:56',NULL,'Jake Shimabukuro - Orange World',NULL,'Jake plays his song \"Orange World\" on Chicago TV show \"Corporate Country Sucks.\" Go www.corporatecountrysucks.com for links to the podcast.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',236,37,10,10,'Anthony','anthony@simplestation.com'),
(47,'video','ukulele-shredding','publish',NULL,'2009-06-17 20:51:03','2009-06-17 20:51:03','2009-01-09 15:52:56',NULL,'Jake Shimabukuro Shreds on his Ukulele',NULL,'Jake plays a jazz influenced ukulele solo for a crowd in 2006. Shredfest.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',72,6,1,1,'Anthony','anthony@simplestation.com'),
(48,'video','mario-kart','publish',NULL,'2009-06-17 20:51:03','2009-06-17 20:51:03','2009-01-09 15:52:56',NULL,'Mario Kart Love Song',NULL,'This is a song I wrote about Mario Kart and Love.\r\nPossibly my most emo video ever. Yes, I taped yarn to my face.\r\n\r\nlyrics:\r\n\r\nV1:\r\nYou be my princess\r\nI\'ll be your toad\r\nI\'ll follow behind you\r\non rainbow road\r\nProtect you from red shells\r\nwherever we go\r\nI promise.\r\n\r\nV2:\r\nNoone will touch us\r\nif we pick up a star\r\nIf you spin out\r\nyou can ride in my car\r\nWhen we slide together\r\nwe generate sparks\r\nin our wheels and our hearts\r\n\r\nChorus:\r\nThe finish line\r\nis just around the bend\r\nI\'ll pause this game\r\nso our love will never end\r\nLet\'s go again\r\n\r\nV3:\r\nThe blue shell is coming\r\nso I\'ll go ahead\r\nIf you hang behind\r\nit\'ll hit me instead\r\nbut never look back\r\ncause I\'m down but not dead\r\nI\'ll catch up to you\r\n\r\nBridge:\r\nDon\'t worry about\r\nBowser or DK\r\nEat this glowing mushroom\r\nand they\'ll all fade away\r\n\r\nChorusx2\r\n\r\nto the mushroom cup\r\nand the flower cup\r\nand the star cup\r\nand the reverse cup\r\n\r\nwalalalalala\r\nwalalalalalawaluigiiiiii\r\n\r\nCOPYRIGHT 2008\r\nMusic and Lyrics by Sam Hart ','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',159,30,26,26,'Anthony','anthony@simplestation.com'),
(49,'video','bohemian-rhapsody','publish',NULL,'2009-06-17 20:51:03','2009-06-17 20:51:03','2009-01-09 15:52:56',NULL,'Queen\'s Bohemian Rhapsody as performed by old prin',NULL,'This is dedicated to all fans of Queen and hey let\'s not forget about Mike Myers and Dana Carvey of Wayne\'s World.\r\nNo effects or sampling were used. What you see is what you hear (does that even make sense?)\r\nAtari 800XL was used for the lead piano/organ sound\r\nTexas Instruments TI-99/4a as lead guitar\r\n8 Inch Floppy Disk as Bass\r\n3.5 inch Harddrive as the gong\r\nHP ScanJet 3C was used for all vocals.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',365,5,1,1,'Anthony','anthony@simplestation.com'),
(50,'video','dot-matrix','publish',NULL,'2009-06-17 20:51:03','2009-06-17 20:51:03','2009-01-09 15:52:56',NULL,'Younnat - Dot Matrix Printer Etude',NULL,'To the accompaniment of dot matrix printer, Music by Younnat (unreleased track).','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',187,20,6,6,'Anthony','anthony@simplestation.com'),
(51,'video','clutch','publish',NULL,'2009-06-17 20:51:03','2009-06-17 20:51:03','2009-01-09 15:52:56',NULL,'How Clutches Work',NULL,'You probably know that any car with a manual transmission has a clutch. Learn how the clutch in your car works, and find out about some surprising places where clutches can also be found.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',113,25,24,24,'Anthony','anthony@simplestation.com'),
(52,'video','manual-transmission','publish',NULL,'2009-06-17 20:51:03','2009-06-17 20:51:03','2009-01-09 15:52:56',NULL,'How Manual Transmissions Work',NULL,'There\'s something about driving a stick-shift car that\'s both empowering and invigorating. Find out all about manual transmissions.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',143,32,2,2,'Anthony','anthony@simplestation.com'),
(53,'video','tchaikovsky-1-1','publish',NULL,'2009-06-17 20:51:03','2009-06-17 20:51:03','2009-01-09 15:52:56',NULL,'David Oistrakh plays Tchaikovsky Concerto (1st Mov',NULL,'David Oistrakh plays Tchaikovsky Violin Concerto in D Major, Op. 35: 1st Movement (Part 1)\r\n\r\nI had to cut it because the file was too big.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',780,3,1,1,'Anthony','anthony@simplestation.com'),
(54,'video','tchaikovsky-1-2','publish',NULL,'2009-06-17 20:51:03','2009-06-17 20:51:03','2009-01-09 15:52:56',NULL,'David Oistrakh plays Tchaikovsky Concerto (1st Mov',NULL,'David Oistrakh plays Tchaikovsky Violin Concerto in D Major, Op. 35: 1st Movement (Part 2)\r\n\r\nI had to cut it because the file was too big.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',385,25,19,19,'Anthony','anthony@simplestation.com'),
(55,'video','modular-robot','publish',NULL,'2009-06-17 20:51:03','2009-06-17 20:51:03','2009-01-09 15:52:56',NULL,'Modular robot reassembles when kicked apart',NULL,'A robot developed by roboticists at the University of Pennsylvania is made of modules that can recognise each other.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',191,38,13,13,'Anthony','anthony@simplestation.com'),
(56,'video','robots-inspired-by-animals','publish',NULL,'2009-06-17 20:51:03','2009-06-17 20:51:03','2009-01-09 15:52:56',NULL,'Robots Inspired by Animals',NULL,'Robotics researchers are increasingly turning to nature for inspiration. Watch a robotic salamander, a water strider robot, mechanical cockroaches and some cool self-configuring robots.\r\n\r\nFootage courtesy of: University of Essex, Ecole Polytechnique Federale de Lausanne, Carnegie Mellon University, ULB-EPFL, Tokyo Institute of Technology, National Institute of Advanced Science and Technology (AIST).','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',128,3,1,1,'Anthony','anthony@simplestation.com'),
(57,'video','robot-fish','publish',NULL,'2009-06-17 20:51:03','2009-06-17 20:51:03','2009-01-09 15:52:56',NULL,'Robot Fish',NULL,'A robotic fish developed by scientists from Essex University is put through its paces in a special tank at the London Aquarium. It works via sensors and has autonomous navigational control.\r\n\r\nwww.itnsource.com','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',209,39,22,22,'Anthony','anthony@simplestation.com'),
(58,'video','glass-harmonica','publish',NULL,'2009-06-17 20:51:03','2009-06-17 20:51:03','2009-01-09 15:52:56',NULL,'Glass Harmonica',NULL,'Invented by Benjamin Franklin in 1761. Music by Wolfgang A. Mozart. Played by French artist Thomas Bloch, exhibiting the glass harmonica in the Paris Music Museum, Nov. 29, 2007.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',92,23,15,15,'Anthony','anthony@simplestation.com'),
(59,'video','dan-bau','publish',NULL,'2009-06-17 20:51:03','2009-06-17 20:51:03','2009-01-09 15:52:56',NULL,'Brilliant performance on the Dan Bau',NULL,'Dan Bau solo -- Giot Mua Thu','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',238,19,2,2,'Anthony','anthony@simplestation.com'),
(60,'video','hydraulophone','publish',NULL,'2009-06-17 20:51:03','2009-06-17 20:51:03','2009-01-09 15:52:56',NULL,'The Hydraulophone - A New Instrument',NULL,'Shows invention of the hydraulophone, a musical instrument based on pressurized water jets, featuring \"Nessie\", a children\'s hydraulophone in the form of a cute green sea monster, as well as other hydraulophones, such as the single-jet hydraulophone in which all sound is made from one screeching water valve on a single jet. The video shows various changes in the sound, depending on how the water jets are blocked.','Bible References: None\r\nS&H References: None\r\nReviewer: None\r\nLicense: General Upload',414,11,6,6,'Anthony','anthony@simplestation.com');
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
INSERT INTO `media_comments` VALUES (1,1),
(2,2),
(2,3),
(2,4),
(9,5);
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
  `type` varchar(10) character set ascii NOT NULL,
  `url` varchar(255) character set ascii NOT NULL,
  `size` int(10) unsigned default NULL,
  `width` smallint(5) unsigned default NULL,
  `height` smallint(5) unsigned default NULL,
  `bitrate` smallint(5) unsigned default NULL,
  `enable_player` tinyint(1) NOT NULL default '1',
  `enable_feed` tinyint(1) NOT NULL default '1',
  `is_original` tinyint(1) NOT NULL default '0',
  `created_on` datetime NOT NULL,
  `modified_on` datetime NOT NULL,
  `position` smallint(5) unsigned default NULL,
  PRIMARY KEY  (`id`),
  KEY `media_files_ibfk_1` (`media_id`),
  CONSTRAINT `media_files_ibfk_1` FOREIGN KEY (`media_id`) REFERENCES `media` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `media_files`
--

LOCK TABLES `media_files` WRITE;
/*!40000 ALTER TABLE `media_files` DISABLE KEYS */;
INSERT INTO `media_files` VALUES (2,1,'flv','1-black-knight.flv',8322240,NULL,NULL,NULL,1,1,1,'2009-06-09 20:39:57','2009-06-09 20:39:57',0),
(3,2,'youtube','9V7zbWNznbs',NULL,NULL,NULL,NULL,1,1,1,'2009-06-09 20:39:57','2009-06-09 20:39:57',0),
(4,3,'youtube','Xe1a1wHxTyo',NULL,NULL,NULL,NULL,1,1,1,'2009-06-09 20:39:57','2009-06-09 20:39:57',0),
(5,4,'youtube','XcxKIJTb3Hg',NULL,NULL,NULL,NULL,1,1,1,'2009-06-09 20:39:57','2009-06-09 20:39:57',0),
(6,5,'youtube','5Xd_zkMEgkI',NULL,NULL,NULL,NULL,1,1,1,'2009-06-09 20:39:57','2009-06-09 20:39:57',0),
(7,6,'youtube','rzcLQRXW6B0',NULL,NULL,NULL,NULL,1,1,1,'2009-06-09 20:39:57','2009-06-09 20:39:57',0),
(8,7,'youtube','-jO1EOhGkY0',NULL,NULL,NULL,NULL,1,1,1,'2009-06-09 20:39:57','2009-06-09 20:39:57',0),
(9,8,'youtube','grbSQ6O6kbs',NULL,NULL,NULL,NULL,1,1,1,'2009-06-09 20:39:57','2009-06-09 20:39:57',0),
(10,9,'youtube','IMxWLuOFyZM',NULL,NULL,NULL,NULL,1,1,1,'2009-06-09 20:39:57','2009-06-09 20:39:57',0),
(11,10,'youtube','c4SJ0xR2_bQ',NULL,NULL,NULL,NULL,1,1,1,'2009-06-09 20:39:57','2009-06-09 20:39:57',0),
(12,11,'youtube','ekO3Z3XWa0Q',NULL,NULL,NULL,NULL,1,1,1,'2009-06-09 20:39:57','2009-06-09 20:39:57',0),
(13,12,'youtube','QTQfGd3G6dg',NULL,NULL,NULL,NULL,1,1,1,'2009-06-09 20:39:57','2009-06-09 20:39:57',0),
(14,13,'youtube','JTbrIo1p-So',NULL,NULL,NULL,NULL,1,1,1,'2009-06-09 20:39:57','2009-06-09 20:39:57',0),
(15,14,'youtube','apDGPl2SfpA',NULL,NULL,NULL,NULL,1,1,1,'2009-06-09 20:39:57','2009-06-09 20:39:57',0),
(16,15,'youtube','9hmDZz5pDOQ',NULL,NULL,NULL,NULL,1,1,1,'2009-06-09 20:39:57','2009-06-09 20:39:57',0),
(17,16,'flv','21-email@email.com-burglary.flv',5173248,NULL,NULL,NULL,1,1,1,'2009-06-09 20:39:57','2009-06-09 20:39:57',0),
(18,38,'youtube','WKIYzoqYjaQ',NULL,NULL,NULL,NULL,1,1,1,'2009-06-17 20:51:03','2009-06-17 20:51:03',0),
(19,39,'youtube','1Yu1rrEhRCM',NULL,NULL,NULL,NULL,1,1,1,'2009-06-17 20:51:03','2009-06-17 20:51:03',0),
(20,40,'youtube','t2Ij5Fbb6-s',NULL,NULL,NULL,NULL,1,1,1,'2009-06-17 20:51:03','2009-06-17 20:51:03',0),
(21,41,'youtube','NMlsIUaWaRI',NULL,NULL,NULL,NULL,1,1,1,'2009-06-17 20:51:03','2009-06-17 20:51:03',0),
(22,42,'youtube','vU6M5hAe-TU',NULL,NULL,NULL,NULL,1,1,1,'2009-06-17 20:51:03','2009-06-17 20:51:03',0),
(23,43,'youtube','trpL0ldEVFM',NULL,NULL,NULL,NULL,1,1,1,'2009-06-17 20:51:03','2009-06-17 20:51:03',0),
(24,44,'youtube','-d9A2oq1N38',NULL,NULL,NULL,NULL,1,1,1,'2009-06-17 20:51:03','2009-06-17 20:51:03',0),
(25,45,'youtube','puSkP3uym5k',NULL,NULL,NULL,NULL,1,1,1,'2009-06-17 20:51:03','2009-06-17 20:51:03',0),
(26,46,'youtube','bT_Jr3vasOo',NULL,NULL,NULL,NULL,1,1,1,'2009-06-17 20:51:03','2009-06-17 20:51:03',0),
(27,47,'youtube','m6snNwJNl-o',NULL,NULL,NULL,NULL,1,1,1,'2009-06-17 20:51:03','2009-06-17 20:51:03',0),
(28,48,'youtube','VDBpQVhCMb8',NULL,NULL,NULL,NULL,1,1,1,'2009-06-17 20:51:03','2009-06-17 20:51:03',0),
(29,49,'youtube','Ht96HJ01SE4',NULL,NULL,NULL,NULL,1,1,1,'2009-06-17 20:51:03','2009-06-17 20:51:03',0),
(30,50,'youtube','nM2ZcgMqhQc',NULL,NULL,NULL,NULL,1,1,1,'2009-06-17 20:51:03','2009-06-17 20:51:03',0),
(31,51,'youtube','6BaECAbapRg',NULL,NULL,NULL,NULL,1,1,1,'2009-06-17 20:51:03','2009-06-17 20:51:03',0),
(32,52,'youtube','vzYGcDZXgWQ',NULL,NULL,NULL,NULL,1,1,1,'2009-06-17 20:51:03','2009-06-17 20:51:03',0),
(33,53,'youtube','fNCeYKfAOZI',NULL,NULL,NULL,NULL,1,1,1,'2009-06-17 20:51:03','2009-06-17 20:51:03',0),
(34,54,'youtube','kc9gRZliWgA',NULL,NULL,NULL,NULL,1,1,1,'2009-06-17 20:51:03','2009-06-17 20:51:03',0),
(35,55,'youtube','uIn-sMq8-Ls',NULL,NULL,NULL,NULL,1,1,1,'2009-06-17 20:51:03','2009-06-17 20:51:03',0),
(36,56,'youtube','Tq8Yw19bn7Q',NULL,NULL,NULL,NULL,1,1,1,'2009-06-17 20:51:03','2009-06-17 20:51:03',0),
(37,57,'youtube','eO9oseiCTdk',NULL,NULL,NULL,NULL,1,1,1,'2009-06-17 20:51:03','2009-06-17 20:51:03',0),
(38,58,'youtube','_XPfoFZYso8',NULL,NULL,NULL,NULL,1,1,1,'2009-06-17 20:51:03','2009-06-17 20:51:03',0),
(39,59,'youtube','37qw5vNyYzE',NULL,NULL,NULL,NULL,1,1,1,'2009-06-17 20:51:03','2009-06-17 20:51:03',0),
(40,60,'youtube','WwUibDEH0nY',NULL,NULL,NULL,NULL,1,1,1,'2009-06-17 20:51:03','2009-06-17 20:51:03',0);
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
INSERT INTO `media_tags` VALUES (1,1),
(2,1),
(3,1),
(4,1),
(5,1),
(6,1),
(7,1),
(8,1),
(9,1),
(10,1),
(11,1),
(12,1),
(13,1),
(14,1),
(15,1),
(7,2),
(11,2),
(3,3),
(1,4),
(2,4),
(4,4),
(5,4),
(6,4),
(7,4),
(8,4),
(9,4),
(10,4),
(11,4),
(12,4),
(13,4),
(14,4),
(15,4),
(4,5),
(6,5),
(5,6),
(5,7),
(11,7),
(6,9),
(8,10),
(9,11),
(10,12),
(13,13),
(14,14);
/*!40000 ALTER TABLE `media_tags` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `media_topics`
--

DROP TABLE IF EXISTS `media_topics`;
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

--
-- Dumping data for table `media_topics`
--

LOCK TABLES `media_topics` WRITE;
/*!40000 ALTER TABLE `media_topics` DISABLE KEYS */;
INSERT INTO `media_topics` VALUES (1,1),
(2,1),
(3,1),
(4,1),
(5,1),
(6,1),
(7,1),
(8,1),
(9,1),
(10,1),
(11,1),
(12,1),
(13,1),
(14,1),
(15,1),
(7,2),
(11,2),
(3,3),
(1,4),
(2,4),
(4,4),
(5,4),
(6,4),
(7,4),
(8,4),
(9,4),
(10,4),
(11,4),
(12,4),
(13,4),
(14,4),
(15,4),
(4,5),
(6,5),
(5,6),
(5,7),
(11,7),
(6,9),
(8,10),
(9,11),
(10,12),
(13,13),
(14,14);
/*!40000 ALTER TABLE `media_topics` ENABLE KEYS */;
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
  `author_name` varchar(50) NOT NULL,
  `author_email` varchar(50) NOT NULL,
  `explicit` tinyint(1) default NULL,
  `copyright` varchar(50) default NULL,
  `itunes_url` varchar(80) character set ascii default NULL,
  `feedburner_url` varchar(80) character set ascii default NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `podcasts`
--

LOCK TABLES `podcasts` WRITE;
/*!40000 ALTER TABLE `podcasts` DISABLE KEYS */;
INSERT INTO `podcasts` VALUES (7,'daily-giz-wiz','2009-06-18 03:44:45','2009-06-18 03:44:45','Daily Giz Wiz','Daily Giz Wiz','Mad\'s maddest writer and The Giz Wiz, Dick DeBartolo, digs into his massive gadget collection for the gadget of the day. Released every weekday. This program is co-hosted by Leo Laporte.\r\n\r\nBandwidth for The Daily Giz Wiz is provided by AOL Radio','Technology','Dick DeBartolo','dick@gizwiz.biz',NULL,'2009',NULL,NULL),
(15,'macbreak-weekly','2009-06-18 04:39:05','2009-06-18 04:39:05','MacBreak Weekly','MacBreak Weekly','Get the latest Mac news and views from the top journalists covering Apple today. This roundtable discussion is audio only, and complements the video only MacBreak. Another great show from the Pixel Corps and the TWiT.tv network.','Mac','Leo Laporte','a@b.com',NULL,'2009',NULL,NULL),
(16,'this-week-in-fun','2009-06-18 04:40:36','2009-06-18 04:40:36','this WEEK in FUN','this WEEK in FUN','Welcome TechTV stalwarts, and my old friends, Sarah Lane and Martin Sargent as our newest podcast on TWiT. Sarah and Martin cover the week\'s news in a fast paced and irreverant romp each week. Watch them record live at 3p Pacific/6p Eastern/2000 UTC at http://live.twit.tv or listen to the show as a podcast (video version coming soon!). ','Fun','Sarah Lane','a@b.com',0,'2009',NULL,NULL),
(17,'futures-in-biotech','2009-06-18 05:47:14','2009-06-18 05:47:14','Futures in Biotech','Futures in Biotech','Explore the world of genetics, cloning, protein folding, genome mapping, and more with the most important researchers in biotech. Hosted by Marc Pelletier and Leo Laporte. Released most Wednesdays. ','biotech','Marc Pelletier','marc@futuresinbiotech.com',NULL,'2009',NULL,NULL);
/*!40000 ALTER TABLE `podcasts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `settings`
--

DROP TABLE IF EXISTS `settings`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `settings` (
  `id` int(10) unsigned NOT NULL auto_increment,
  `key` varchar(255) NOT NULL,
  `value` text,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `key_index` (`key`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `settings`
--

LOCK TABLES `settings` WRITE;
/*!40000 ALTER TABLE `settings` DISABLE KEYS */;
INSERT INTO `settings` VALUES (1,'email_media_uploaded',''),
(2,'email_comment_posted',''),
(3,'email_support_requests',''),
(4,'email_send_from',''),
(5,'ftp_server','my.ftp.server.com'),
(6,'ftp_username','ftpuser'),
(7,'ftp_password','secretpassword'),
(8,'ftp_upload_path','media'),
(9,'ftp_download_url','http://content.distribution.network/ftpuser/media/'),
(10,'wording_user_uploads',''),
(11,'wording_additional_notes','');
/*!40000 ALTER TABLE `settings` ENABLE KEYS */;
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
INSERT INTO `tags` VALUES (1,'Monty Python','monty-python'),
(2,'Chivalry','chivalry'),
(3,'Flying Circus','flying-circus'),
(4,'Holy Grail','holy-grail'),
(5,'Animals','animals'),
(6,'Politics','politics'),
(7,'Power','power'),
(8,'Fruit','fruit'),
(9,'Africa','africa'),
(10,'Life After Death','life-after-death'),
(11,'Challenges','challenges'),
(12,'Folk Songs','folk-songs'),
(13,'Fire','fire'),
(14,'Eccentric Performances','eccentric-performances'),
(15,'Limbo','limbo');
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
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `tg_group`
--

LOCK TABLES `tg_group` WRITE;
/*!40000 ALTER TABLE `tg_group` DISABLE KEYS */;
INSERT INTO `tg_group` VALUES (1,'Admins','Administrators','2009-05-21 18:41:28'),
(2,'Editors','Content Editors','2009-09-18 18:41:28');
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
INSERT INTO `tg_user` VALUES (1,'tmcy','tmcyouth@christianscience.com','TMCYouth','5c97c9bc5a0e00d49781c7d0b65ba545ce22d3ab310c9d0afc7230d9a79b0d1d55a17b03e5be89ed','2009-05-21 18:41:28'),
(2,'simplestation','info@simplestation.com','Simple Station Inc.','63bd796fccc9fe83f4fd0ab7976e43e0edc26e3a3e9e447721caefd3d731ebb96ef4fec8d5f24774','2009-05-26 14:45:31');
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
INSERT INTO `tg_user_group` VALUES (1,1),
(2,1);
/*!40000 ALTER TABLE `tg_user_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `topics`
--

DROP TABLE IF EXISTS `topics`;
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
-- Dumping data for table `topics`
--

LOCK TABLES `topics` WRITE;
/*!40000 ALTER TABLE `topics` DISABLE KEYS */;
INSERT INTO `topics` VALUES (1,'Monty Python','monty-python'),
(2,'Chivalry','chivalry'),
(3,'Flying Circus','flying-circus'),
(4,'Holy Grail','holy-grail'),
(5,'Animals','animals'),
(6,'Politics','politics'),
(7,'Power','power'),
(8,'Fruit','fruit'),
(9,'Africa','africa'),
(10,'Life After Death','life-after-death'),
(11,'Challenges','challenges'),
(12,'Folk Songs','folk-songs'),
(13,'Fire','fire'),
(14,'Eccentric Performances','eccentric-performances'),
(15,'Limbo','limbo');
/*!40000 ALTER TABLE `topics` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2009-12-31 20:06:38
