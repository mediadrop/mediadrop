/* Rename all of the TG user tables to remove unnecessary TG references and keep pluralization consistent */
/* part 1 of 3 */
ALTER TABLE `tg_group_permission`
	DROP FOREIGN KEY `tg_group_permission_ibfk_1`,
	DROP FOREIGN KEY `tg_group_permission_ibfk_2`;