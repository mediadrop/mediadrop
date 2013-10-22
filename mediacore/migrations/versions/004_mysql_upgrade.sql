/*
 * This file is a part of MediaDrop (http://www.mediadrop.net),
 * Copyright 2009-2013 MediaCore Inc., Felix Schwarz and other contributors.
 * For the exact contribution history, see the git revision log.
 * The source code contained in this file is licensed under the GPLv3 or
 * (at your option) any later version.
 * See LICENSE.txt in the main project directory, for more information.
 **/

/* Rename all of the TG user tables to remove unnecessary TG references and keep pluralization consistent */
/* part 1 of 3 */
ALTER TABLE `tg_group_permission`
	DROP FOREIGN KEY `tg_group_permission_ibfk_1`,
	DROP FOREIGN KEY `tg_group_permission_ibfk_2`;
