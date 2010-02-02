#!/bin/bash

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/doc/make-schemadocs.sh,v $
# $Revision: 1.24 $
# license: GPL
# author: Karsten.Hilbert@gmx.net

DB_LIST="gnumed_v12 gnumed_v13"

export PGUSER="gm-dbo"

for DB in ${DB_LIST} ; do

	mkdir -p ~/gm-schemadocs/${DB}/

	postgresql_autodoc -d ${DB} -f ~/gm-schemadocs/${DB}/gnumed-schema -t html
	postgresql_autodoc -d ${DB} -f ~/gm-schemadocs/${DB}/gnumed-schema -t dot
	postgresql_autodoc -d ${DB} -f ~/gm-schemadocs/${DB}/gnumed-schema -t dia
	postgresql_autodoc -d ${DB} -f ~/gm-schemadocs/${DB}/gnumed-schema -t zigzag.dia

	grep -v log_ ~/gm-schemadocs/${DB}/gnumed-schema.dot > ~/gm-schemadocs/${DB}/gnumed-schema-no_audit.dot

	dot -Tpng -o ~/gm-schemadocs/${DB}/gnumed-schema.png ~/gm-schemadocs/${DB}/gnumed-schema-no_audit.dot

done

#============================================
# $Log: make-schemadocs.sh,v $
# Revision 1.24  2010-02-02 13:50:50  ncq
# - bump DB version
#
# Revision 1.23  2009/08/24 20:05:34  ncq
# - bump db version
#
# Revision 1.22  2009/04/03 11:08:07  ncq
# - bump db version
#
# Revision 1.21  2008/12/09 23:22:32  ncq
# - mkdir can use a -p
#
# Revision 1.20  2008/09/02 15:44:18  ncq
# - bump db version
#
# Revision 1.19  2008/08/01 10:08:49  ncq
# - /bin/sh -> /bin/bash
#
# Revision 1.18  2008/01/07 19:45:11  ncq
# - bump db version
#
# Revision 1.17  2007/12/08 15:18:55  ncq
# - remove -tar.sql
#
# Revision 1.16  2007/12/08 15:11:31  ncq
# - make it multi-DB
#
# Revision 1.15  2007/10/22 12:37:02  ncq
# - default database change
#
# Revision 1.14  2007/09/24 18:26:20  ncq
# - v5 -> v7
#
# Revision 1.13  2007/03/31 21:19:07  ncq
# - work with gnumed_v5
#
# Revision 1.12  2007/01/24 11:01:18  ncq
# - document v4 schema for now
#
# Revision 1.11  2006/01/07 09:06:24  ncq
# - remove audit tables from schema ER diagram
#
# Revision 1.10  2005/12/23 16:24:18  ncq
# - remove absolute path prefix on pg autodoc binary
#
# Revision 1.9  2005/12/09 20:43:25  ncq
# - improved output
#
# Revision 1.8  2005/01/25 17:35:03  ncq
# - Thilo wanted the other formats, too, so here it is ...
#
# Revision 1.7  2005/01/19 09:27:59  ncq
# - let callers deal with output, don't predefine target as file (cron mails it)
#
# Revision 1.6  2005/01/12 14:47:48  ncq
# - in DB speak the database owner is customarily called dbo, hence use that
#
# Revision 1.5  2005/01/10 12:26:40  ncq
# - properly installing pg_autodoc on Carlos' machine should help
#
# Revision 1.4  2005/01/10 12:06:13  ncq
# - tell pg autodoc to act as gm-dbowner
#
# Revision 1.3  2005/01/06 19:21:29  ncq
# - adjust for running on Carlos' server
#
# Revision 1.2  2004/07/15 06:28:46  ncq
# - fixed some pathes
#
# Revision 1.1  2004/07/15 06:25:32  ncq
# - first checkin
