/* 
# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code contained in this file is licensed under the GPL.
# See LICENSE.txt in the main project directory, for more information.
*/

/* Rename all of the TG user tables to remove unnecessary TG references and keep pluralization consistent */
/* part 1 of 3 */
ALTER TABLE `tg_group_permission`
	DROP FOREIGN KEY `tg_group_permission_ibfk_1`,
	DROP FOREIGN KEY `tg_group_permission_ibfk_2`;
