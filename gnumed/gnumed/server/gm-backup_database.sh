#!/bin/bash

#==============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/gm-backup_database.sh,v $
# $Id: gm-backup_database.sh,v 1.21 2009-04-24 12:12:09 ncq Exp $
#
# author: Karsten Hilbert
# license: GPL v2
#
# This script creates a backup of the database schema,
# data, and roles which can be used to restore a GNUmed
# database from scratch.
#
# You need to allow root to access the GNUmed database as
# user "gm-dbo" by either editing pg_hba.conf or using a
# .pgpass file.
#
#
# anacron
# -------
#  The following line could be added to a system's
#  /etc/anacrontab to make sure it creates daily
#  database backups for GNUmed:
#
#  1       15      backup-gnumed-<your-company>    /usr/bin/gm-backup_database.sh
#
#
# cron
# ----
#  add the following line to a crontab file to run a
#  database backup at 12:47 and 19:47 every day
#
#  47 12,19 * * * * /usr/bin/gm-backup_database.sh
#
#==============================================================

CONF="/etc/gnumed/gnumed-backup.conf"

#==============================================================
# There really should not be any need to
# change anything below this line.
#==============================================================

# load config file
if [ -r ${CONF} ] ; then
	. ${CONF}
else
	echo "Cannot read configuration file ${CONF}. Aborting."
	exit 1
fi


# switched off ? (database name empty)
if [ "$GM_DATABASE" = "" ] ; then
	exit 0
fi

# FIXME: check PORT/DBO/BACKUP_FILENAME too


# sanity check
if ! su postgres -c 'psql -t -l' | grep -q "^[[:space:]]*${GM_DATABASE}" ; then
	echo "The configuration in ${CONF} is set to backup"
	echo "the GNUmed database ${GM_DATABASE}. This"
	echo "database does not exist, however. Aborting."
	exit 1
fi


# are we backing up the latest DB ?
OUR_VER=`echo ${GM_DATABASE} | cut -f 2 -d v`
if test -z ${GM_HOST} ; then
	HAS_HIGHER_VER=`sudo -u postgres psql -A -t -d ${GM_DATABASE} -p ${GM_PORT} -c "SELECT exists (select 1 from pg_database where datname like 'gnumed_v%' and substring(datname from 9 for 3)::integer > '${OUR_VER}');"`
else
	HAS_HIGHER_VER=`sudo -u postgres psql -A -t -h ${GM_HOST} -d ${GM_DATABASE} -p ${GM_PORT} -c "SELECT exists (select 1 from pg_database where datname like 'gnumed_v%' and substring(datname from 9 for 3)::integer > '${OUR_VER}');"`
fi;

if test "${HAS_HIGHER_VER}" = "t" ; then
	echo "Backing up database ${GM_DATABASE}. However,"
	echo "a newer database seems to exist:"
	echo ""
	sudo -u postgres psql -l | grep gnumed_v
	echo ""
	echo "Make sure you really want to backup the old database !"
fi ;


# generate backup file name
TS=`date +%Y-%m-%d-%H-%M-%S`
if test -z ${GM_HOST} ; then
	BACKUP_BASENAME="backup-${GM_DATABASE}-${INSTANCE_OWNER}-"`hostname`
else
	BACKUP_BASENAME="backup-${GM_DATABASE}-${INSTANCE_OWNER}-${GM_HOST}"
fi ;
BACKUP_FILENAME="${BACKUP_BASENAME}-${TS}"


cd ${BACKUP_DIR}
if test "$?" != "0" ; then
	echo "Cannot change into backup directory [${BACKUP_DIR}]. Aborting."
	exit 1
fi


# create dumps
if test -z ${GM_HOST} ; then
	# locally
	# -r -> -g for older versions
	sudo -u postgres pg_dumpall -r -v -p ${GM_PORT} > ${BACKUP_FILENAME}-roles.sql 2> /dev/null

	echo "" >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
	echo "-- -----------------------------------------------------" >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
	echo "-- Below find a list of database roles which were in use" >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
	echo "-- in the GNUmed database \"${GM_DATABASE}\"."            >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
	echo "-- -----------------------------------------------------" >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
	echo "" >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
	echo "-- "`psql -A -d ${GM_DATABASE} -p ${GM_PORT} -U ${GM_DBO} -c "select gm.get_users('${GM_DATABASE}');"` >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null

	pg_dump -C -v -d ${GM_DATABASE} -p ${GM_PORT} -U ${GM_DBO} -f ${BACKUP_FILENAME}-database.sql 2> /dev/null
else
	# remotely
	if ping -c 3 -i 2 ${GM_HOST} > /dev/null; then
		# -r -> -g
		pg_dumpall -r -v -h ${GM_HOST} -p ${GM_PORT} -U postgres > ${BACKUP_FILENAME}-roles.sql 2> /dev/null

		echo "" >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
		echo "-- -----------------------------------------------------" >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
		echo "-- Below find a list of database roles which were in use" >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
		echo "-- in the GNUmed database \"${GM_DATABASE}\"."            >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
		echo "-- -----------------------------------------------------" >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
		echo "" >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null
		echo "-- "`psql -A -h ${GM_HOST} -d ${GM_DATABASE} -p ${GM_PORT} -U ${GM_DBO} -c "select gm.get_users('${GM_DATABASE}');"` >> ${BACKUP_FILENAME}-roles.sql 2> /dev/null

		pg_dump -C -v -h ${GM_HOST} -d ${GM_DATABASE} -p ${GM_PORT} -U ${GM_DBO} -f ${BACKUP_FILENAME}-database.sql 2> /dev/null
	else
		echo "Cannot ping database host ${GM_HOST}."
		exit 1
	fi ;
fi ;


# tar and test it
if test -z ${VERIFY_TAR} ; then
	tar -cf ${BACKUP_FILENAME}.tar ${BACKUP_FILENAME}-database.sql ${BACKUP_FILENAME}-roles.sql
else
	tar -cWf ${BACKUP_FILENAME}.tar ${BACKUP_FILENAME}-database.sql ${BACKUP_FILENAME}-roles.sql
fi ;
if test "$?" != "0" ; then
	echo "Creating backup tar archive [${BACKUP_FILENAME}.tar] failed. Aborting."
	exit 1
fi
rm -f ${BACKUP_FILENAME}-database.sql
rm -f ${BACKUP_FILENAME}-roles.sql


chown ${BACKUP_OWNER} ${BACKUP_FILENAME}.tar

exit 0

#==============================================================
# $Log: gm-backup_database.sh,v $
# Revision 1.21  2009-04-24 12:12:09  ncq
# - more sanity checks pulled from Debian
#
# Revision 1.20  2009/04/14 18:32:40  ncq
# - remove spurious exit left over from testing
#
# Revision 1.19  2009/01/08 16:43:18  ncq
# - improve docstring
#
# Revision 1.18  2008/12/28 15:06:21  ncq
# - warn if backing up older database
#
# Revision 1.17  2008/12/01 12:18:02  ncq
# - log accounts in use during backup
#
# Revision 1.16  2008/11/03 10:29:57  ncq
# - cleanup
#
# Revision 1.15  2007/12/08 15:23:14  ncq
# - minor cleanup
#
# Revision 1.14  2007/10/25 12:27:46  ncq
# - we don't compress so don't say so
#
# Revision 1.13  2007/09/24 18:40:04  ncq
# - commit VERIFY_TAR flag
# - redirect stderror progress output when -v used on pg_dump(all)
#
# Revision 1.12  2007/08/12 00:14:39  ncq
# - us -v on pg_dump to log timestamp etc
#
# Revision 1.11  2007/06/05 14:59:44  ncq
# - improved docstring
# - better error checking
# - factor out bzipping and signing
#
# Revision 1.10  2007/05/17 15:17:24  ncq
# - abort on ping error
#
# Revision 1.9  2007/05/17 15:16:23  ncq
# - set backup base name based on GM_HOST, not localhost
# - ping remote GM_HOST before trying to dump
#
# Revision 1.8  2007/05/14 21:29:24  ncq
# - start supporting dumps from remote hosts
#
# Revision 1.7  2007/05/14 16:46:33  ncq
# - be a bit more resource friendly
#
# Revision 1.6  2007/05/08 11:18:20  ncq
# - robustify
# - include database creation commands, dump roles only
#
# Revision 1.5  2007/05/07 08:06:16  ncq
# - include roles in dump
# - make zipping up old backups safer
#
# Revision 1.4  2007/05/01 19:41:38  ncq
# - better docs
# - factor out config
#
# Revision 1.3  2007/04/27 13:30:49  ncq
# - add FIXME
#
# Revision 1.2  2007/02/19 10:35:14  ncq
# - add some (ana)crontab lines and a few lines of documentation
#
# Revision 1.1  2007/02/16 15:33:37  ncq
# - renamed for smoother compliance into target systems
#
# Revision 1.6  2007/02/13 17:10:03  ncq
# - better docs
# - bzip up leftover dumps from when bzipping got interrupted by, say, shutdown
#
# Revision 1.5  2007/01/24 22:56:05  ncq
# - support gnotarization
#
# Revision 1.4  2007/01/07 23:10:24  ncq
# - more documentation
# - add backup file permission mask
#
# Revision 1.3  2006/12/25 22:55:10  ncq
# - comment on gnotary support
#
# Revision 1.2  2006/12/21 19:01:21  ncq
# - add target owner chown
#
# Revision 1.1  2006/12/05 14:48:08  ncq
# - first release of a backup script
#
#