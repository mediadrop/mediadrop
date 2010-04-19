CREATE TABLE `groups` (
  `group_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `group_name` varchar(16) NOT NULL,
  `display_name` varchar(255) DEFAULT NULL,
  `created` datetime DEFAULT NULL,
  PRIMARY KEY (`group_id`),
  UNIQUE KEY `group_name` (`group_name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

CREATE TABLE `permissions` (
  `permission_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `permission_name` varchar(16) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`permission_id`),
  UNIQUE KEY `permission_name` (`permission_name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

CREATE TABLE `users` (
  `user_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `user_name` varchar(16) NOT NULL,
  `email_address` varchar(255) NOT NULL,
  `display_name` varchar(255) DEFAULT NULL,
  `password` varchar(80) DEFAULT NULL,
  `created` datetime DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `user_name` (`user_name`),
  UNIQUE KEY `email_address` (`email_address`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

CREATE TABLE `users_groups` (
  `user_id` int(10) unsigned DEFAULT NULL,
  `group_id` int(10) unsigned DEFAULT NULL,
  KEY `user_id` (`user_id`),
  KEY `group_id` (`group_id`),
  CONSTRAINT `users_groups_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `users_groups_ibfk_2` FOREIGN KEY (`group_id`) REFERENCES `groups` (`group_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `groups_permissions` (
  `group_id` int(10) unsigned DEFAULT NULL,
  `permission_id` int(10) unsigned DEFAULT NULL,
  KEY `group_id` (`group_id`),
  KEY `permission_id` (`permission_id`),
  CONSTRAINT `groups_permissions_ibfk_1` FOREIGN KEY (`group_id`) REFERENCES `groups` (`group_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `groups_permissions_ibfk_2` FOREIGN KEY (`permission_id`) REFERENCES `permissions` (`permission_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO groups (group_id, group_name, display_name, created)
SELECT t.group_id, t.group_name, t.display_name, t.created
FROM tg_group t;

INSERT INTO permissions (permission_id, permission_name, description)
SELECT t.permission_id, t.permission_name, t.description
FROM tg_permission t;

INSERT INTO users (user_id, user_name, email_address, display_name, password, created)
SELECT t.user_id, t.user_name, t.email_address, t.display_name, t.password, t.created
FROM tg_user t;

INSERT INTO users_groups (user_id, group_id)
SELECT t.user_id, t.group_id
FROM tg_user_group t;

INSERT INTO groups_permissions (group_id, permission_id)
SELECT t.group_id, t.permission_id
FROM tg_group_permission t;

DROP TABLE tg_group_permission;
DROP TABLE tg_user_group;
DROP TABLE tg_permission;
DROP TABLE tg_group;
DROP TABLE tg_user;
