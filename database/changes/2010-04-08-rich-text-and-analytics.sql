DELETE FROM `settings` WHERE `key` = 'enable_tinymce';
INSERT INTO `settings` VALUES
(NULL, 'rich_text_editor', 'tinymce'),
(NULL, 'google_analytics_uacct', '');
