SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `settings` (
  `id` INTEGER UNSIGNED NOT NULL AUTO_INCREMENT,
  `key` VARCHAR(255) NOT NULL,
  `value` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

INSERT INTO `settings` VALUES
(1, 'email_media_uploaded', ''),
(2, 'email_comment_posted', ''),
(3, 'email_support_requests', ''),
(4, 'email_send_from', ''),
(5, 'ftp_server', ''),
(6, 'ftp_username', ''),
(7, 'ftp_password', ''),
(8, 'ftp_upload_path', ''),
(9, 'ftp_download_url', ''),
(10, 'wording_user_uploads', '');

