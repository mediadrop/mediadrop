ALTER TABLE `media` DROP COLUMN `player_override`;
DELETE FROM  `settings` WHERE `key` = 'player';
INSERT INTO `settings` VALUES
(NULL, 'flash_player', 'flowplayer'),
(NULL, 'html5_player', 'html5'),
(NULL, 'player_type', 'best');
;
