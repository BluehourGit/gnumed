#!/bin/bash

#==============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/external-tools/gm-read_chipcard.sh,v $
# $Id: gm-read_chipcard.sh,v 1.1 2009-09-08 12:21:54 ncq Exp $
#
# author: Karsten Hilbert
# license: GPL v2 or later
#
# - copy this to /usr/bin/gm-read_chipcard.sh
# - it is called from kvkcard when a new chipcard is inserted
#
#==============================================================

#set -x

CONF="/etc/gnumed/ekg+kvk-demon.conf"

#==============================================================
# There really should not be any need to
# change anything below this line.
#==============================================================

CARD_ID=$1
TS=`date +%Y-%m-%d-%H-%M-%S`


# load config file
if [ -r ${CONF} ] ; then
	. ${CONF}
else
	echo "Cannot read configuration file ${CONF}. Aborting."
	exit 1
fi


BEEP=""
if test "${BEEP_AFTER_READ}" == "true"; then
	BEEP="--beep"
fi


kvkcard read -c ${CARD_ID} --filename ${DUMP_FILE} ${BEEP}


CARD_TYPE=`grep KARTENTYP ${DUMP_FILE} | cut --delimiter=":" --fields=2`
if test "${CARD_TYPE}" == "Krankenversichertenkarte"; then
	mv ${DUMP_FILE} "KVK-${DUMP_FILE}"
elif test "${CARD_TYPE}" == "elektronische Gesundheitskarte"; then
	mv ${DUMP_FILE} "eGK-${DUMP_FILE}"
else
	# default to KVK as old libchipcard versions didn't offer "Kartentyp"
	mv ${DUMP_FILE} "KVK-${DUMP_FILE}"
fi


# signal GNUmed
# - XML-RPC ?
# - thread in GNUmed ?
# - database NOTIFY ?

#============================================================
# $Log: gm-read_chipcard.sh,v $
# Revision 1.1  2009-09-08 12:21:54  ncq
# - moved here
#
# Revision 1.2  2009/01/17 23:09:55  ncq
# - typo
#
# Revision 1.1  2008/08/28 18:04:04  ncq
# - first checkin
#
#
