#!/bin/bash

#------------------------------------------------------------------
# $Id: create-tag.sh,v 1.3.4.1 2009-03-24 10:43:50 ncq Exp $
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/create-tag.sh,v $
# $Revision: 1.3.4.1 $
# License: GPL
#------------------------------------------------------------------

TAG=$1

if ! [[ "${TAG}" =~ "rel-[0-9]-[0-9]-[0-9]\$" ]] ; then
	echo ""
	echo "usage: $0 <tag>"
	echo ""
	echo "   tag syntax convention:"
	echo ""
	echo "      rel-X-Y-Z:"
	echo "         - root of branch rel-x-y-z-patches for release x.y.z"
	echo "         - apply to TRUNK"
	echo "      rel-X-Y-Z-rcN:"
	echo "         - Release Candidate N for release x.y.z.0"
	echo "         - apply to branch rel-x-y-z-patches"
	echo "      rel-X-Y-Z-N:"
	echo "         - release x.y.z.n"
	echo "         - apply to branch rel-x-y-z-patches"
	echo ""
	exit
fi

echo ""
echo "Are you absolutely positively sure you want"
echo "to tag the CVS tree as \"${TAG}\" ?"
echo "Note that you must have checked in all changes."
echo ""
read -e -p "Tag CVS tree ? [yes/no]: "

if test "${REPLY}" != "yes" ; then
	echo ""
	echo "Tagging aborted."
	echo ""
	exit 0
fi

read -p "Hit [ENTER] to start tagging ..."
echo ""
echo "Tagging CVS tree as \"${TAG}\" ..."
cvs tag -c ${TAG}

#------------------------------------------------------------------
# $Log: create-tag.sh,v $
# Revision 1.3.4.1  2009-03-24 10:43:50  ncq
# - fix checking
#
# Revision 1.3  2008/01/30 13:28:20  ncq
# - properly use cvs
#
# Revision 1.2  2008/01/03 16:28:17  ncq
# - stricter TAG checking
#
# Revision 1.1  2008/01/03 15:53:39  ncq
# - make tagging easier
#
#