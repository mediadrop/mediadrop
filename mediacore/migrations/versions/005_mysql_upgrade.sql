/*
 * This file is a part of MediaDrop (http://www.mediadrop.net),
 * Copyright 2009-2013 MediaCore Inc., Felix Schwarz and other contributors.
 * For the exact contribution history, see the git revision log.
 * The source code contained in this file is licensed under the GPLv3 or
 * (at your option) any later version.
 * See LICENSE.txt in the main project directory, for more information.
 **/

/* ------------------------------------------------------- */

/* Rename all of the TG user tables to remove unnecessary TG references and keep pluralization consistent */
/* part 1 of 3 */
/* Rename all of the TG user tables to remove unnecessary TG references and keep pluralization consistent */
/* part 2 of 3 */
ALTER TABLE `tg_user_group`
	DROP FOREIGN KEY `tg_user_group_ibfk_1`,
	DROP FOREIGN KEY `tg_user_group_ibfk_2`;
RENAME TABLE `tg_group` to `groups`;
RENAME TABLE `tg_permission` to `permissions`;
RENAME TABLE `tg_user` to `users`;
RENAME TABLE `tg_user_group` to `users_groups`;
RENAME TABLE `tg_group_permission` to `groups_permissions`;
ALTER TABLE `users_groups`
	ADD CONSTRAINT `users_groups_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE,
	ADD CONSTRAINT `users_groups_ibfk_2` FOREIGN KEY (`group_id`) REFERENCES `groups` (`group_id`) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE `groups_permissions`
	ADD CONSTRAINT `groups_permissions_ibfk_1` FOREIGN KEY (`group_id`) REFERENCES `groups` (`group_id`) ON DELETE CASCADE ON UPDATE CASCADE,
	ADD CONSTRAINT `groups_permissions_ibfk_2` FOREIGN KEY (`permission_id`) REFERENCES `permissions` (`permission_id`) ON DELETE CASCADE ON UPDATE CASCADE;
