#!/bin/bash

#====================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/dists/Linux/make-release_tarball.sh,v $
# $Id: make-release_tarball.sh,v 1.81.2.3 2009-12-10 10:04:55 ncq Exp $
# license: GPL
#====================================================
CLIENTREV="0.5.1"
CLIENTARCH="GNUmed-client.$CLIENTREV.tgz"

SRVREV="11.1"
SRVARCH="GNUmed-server.v$SRVREV.tgz"

FILES_REMOVE=\
"./GNUmed-$CLIENTREV/client/business/README "\
"./GNUmed-$CLIENTREV/client/business/gmOrganization.py "\
"./GNUmed-$CLIENTREV/client/business/gmXmlDocDesc.py "\
"./GNUmed-$CLIENTREV/client/pycommon/gmDrugObject.py "\
"./GNUmed-$CLIENTREV/client/pycommon/gmDrugView.py "\
"./GNUmed-$CLIENTREV/client/pycommon/gmSchemaRevisionCheck.py "\
"./GNUmed-$CLIENTREV/client/pycommon/gmSerialTools.py "\
"./GNUmed-$CLIENTREV/client/pycommon/gmTrace.py "\
"./GNUmed-$CLIENTREV/client/pycommon/gmdbf.py "\
"./GNUmed-$CLIENTREV/client/pycommon/gmCLI.py "\
"./GNUmed-$CLIENTREV/client/pycommon/gmPG.py "\
"./GNUmed-$CLIENTREV/server/business/README "\
"./GNUmed-$CLIENTREV/server/business/gmOrganization.py "\
"./GNUmed-$CLIENTREV/server/business/gmXmlDocDesc.py "\
"./GNUmed-$CLIENTREV/server/pycommon/gmDrugObject.py "\
"./GNUmed-$CLIENTREV/server/pycommon/gmDrugView.py "\
"./GNUmed-$CLIENTREV/server/pycommon/gmSchemaRevisionCheck.py "\
"./GNUmed-$CLIENTREV/server/pycommon/gmSerialTools.py "\
"./GNUmed-$CLIENTREV/server/pycommon/gmTrace.py "\
"./GNUmed-$CLIENTREV/server/pycommon/gmdbf.py "\
"./GNUmed-$CLIENTREV/server/pycommon/gmPG.py "\
"./GNUmed-$CLIENTREV/server/bootstrap/README "\
"./GNUmed-$CLIENTREV/client/wxGladeWidgets/README "\
"./GNUmed-$CLIENTREV/client/wxGladeWidgets/wxgAU_AdminLoginV01.py "\
"./GNUmed-$CLIENTREV/client/wxGladeWidgets/wxgAU_DBUserSetupV01.py "\
"./GNUmed-$CLIENTREV/client/wxGladeWidgets/wxgAU_StaffMgrPanel.py "\
"./GNUmed-$CLIENTREV/client/wxGladeWidgets/wxgAU_StaffV01.py "\
"./GNUmed-$CLIENTREV/client/wxGladeWidgets/wxgRequest.py "\
"./GNUmed-$CLIENTREV/client/wxGladeWidgets/wxgDoubleListSplitterPnl.py "\
"./GNUmed-$CLIENTREV/client/wxpython/StyledTextCtrl_1.py "\
"./GNUmed-$CLIENTREV/client/wxpython/gmDermTool.py "\
"./GNUmed-$CLIENTREV/client/wxpython/gmProgressNoteSTC.py "\
"./GNUmed-$CLIENTREV/client/wxpython/zz-gmNewFileTemplate.py "\
"./GNUmed-$CLIENTREV/client/wxpython/gmAU_VaccV01.py "\
"./GNUmed-$CLIENTREV/client/wxpython/gmBMIWidgets.py "\
"./GNUmed-$CLIENTREV/client/wxpython/gmCharacterValidator.py "\
"./GNUmed-$CLIENTREV/client/wxpython/gmCryptoText.py "\
"./GNUmed-$CLIENTREV/client/wxpython/gmFormPrinter.py "\
"./GNUmed-$CLIENTREV/client/wxpython/gmGP_ActiveProblems.py "\
"./GNUmed-$CLIENTREV/client/wxpython/gmGP_FamilyHistorySummary.py "\
"./GNUmed-$CLIENTREV/client/wxpython/gmGP_HabitsRiskFactors.py "\
"./GNUmed-$CLIENTREV/client/wxpython/gmGP_Inbox.py "\
"./GNUmed-$CLIENTREV/client/wxpython/gmGP_PatientPicture.py "\
"./GNUmed-$CLIENTREV/client/wxpython/gmGP_SocialHistory.py "\
"./GNUmed-$CLIENTREV/client/wxpython/gmLabWidgets.py "\
"./GNUmed-$CLIENTREV/client/wxpython/gmListCtrlMapper.py "\
"./GNUmed-$CLIENTREV/client/wxpython/gmMultiColumnList.py "\
"./GNUmed-$CLIENTREV/client/wxpython/gmMultiSash.py "\
"./GNUmed-$CLIENTREV/client/wxpython/gmPatientHolder.py "\
"./GNUmed-$CLIENTREV/client/wxpython/gmPlugin_Patient.py "\
"./GNUmed-$CLIENTREV/client/wxpython/gmPregWidgets.py "\
"./GNUmed-$CLIENTREV/client/wxpython/gmSelectPerson.py "\
"./GNUmed-$CLIENTREV/client/wxpython/gmShadow.py "\
"./GNUmed-$CLIENTREV/client/wxpython/gmSQLListControl.py "\
"./GNUmed-$CLIENTREV/client/wxpython/gmSQLSimpleSearch.py "\
"./GNUmed-$CLIENTREV/client/wxpython/gui/gmAllergiesPlugin.py "\
"./GNUmed-$CLIENTREV/client/wxpython/gui/gmAU_VaccV01Plugin.py "\
"./GNUmed-$CLIENTREV/client/wxpython/gui/gmClinicalWindowManager.py "\
"./GNUmed-$CLIENTREV/client/wxpython/gui/gmContacts.py "\
"./GNUmed-$CLIENTREV/client/wxpython/gui/gmConfigRegistry.py "\
"./GNUmed-$CLIENTREV/client/wxpython/gui/gmDemographicsEditor.py "\
"./GNUmed-$CLIENTREV/client/wxpython/gui/gmDrugDisplay.py "\
"./GNUmed-$CLIENTREV/client/wxpython/gui/gmEMRTextDumpPlugin.py "\
"./GNUmed-$CLIENTREV/client/wxpython/gui/gmGuidelines.py "\
"./GNUmed-$CLIENTREV/client/wxpython/gui/gmLabJournal.py "\
"./GNUmed-$CLIENTREV/client/wxpython/gui/gmManual.py "\
"./GNUmed-$CLIENTREV/client/wxpython/gui/gmMultiSashedProgressNoteInputPlugin.py "\
"./GNUmed-$CLIENTREV/client/wxpython/gui/gmOffice.py "\
"./GNUmed-$CLIENTREV/client/wxpython/gui/gmPython.py "\
"./GNUmed-$CLIENTREV/client/wxpython/gui/gmRequest.py "\
"./GNUmed-$CLIENTREV/client/wxpython/gui/gmShowLab.py "\
"./GNUmed-$CLIENTREV/client/wxpython/gui/gmSQL.py "\
"./GNUmed-$CLIENTREV/client/wxpython/gui/gmVaccinationsPlugin.py "\
"./GNUmed-$CLIENTREV/server/bootstrap/xxx-upgrade-instructions.txt "\
"./GNUmed-$CLIENTREV/server/bootstrap/amis-config.set "\
"./GNUmed-$CLIENTREV/server/bootstrap/bootstrap-amis.conf "\
"./GNUmed-$CLIENTREV/server/bootstrap/bootstrap-archive.conf "\
"./GNUmed-$CLIENTREV/server/bootstrap/install_AMIS_data.sh "\
"./GNUmed-$CLIENTREV/server/bootstrap/redo-max.sh "\
"./GNUmed-$CLIENTREV/server/bootstrap/update_db-v1_v2.conf "\
"./GNUmed-$CLIENTREV/server/bootstrap/update_db-v1_v2.sh "\
"./GNUmed-$CLIENTREV/server/sql/gmappoint.sql "\
"./GNUmed-$CLIENTREV/server/sql/gmmodule.sql "\
"./GNUmed-$CLIENTREV/server/sql/gmrecalls.sql "\
"./GNUmed-$CLIENTREV/server/sql/update_db-v1_v2.sql "\
"./GNUmed-$CLIENTREV/server/sql/gmCrossDB_FKs.sql "\
"./GNUmed-$CLIENTREV/server/sql/gmCrossDB_FK-views.sql "\
"./GNUmed-$CLIENTREV/server/sql/gmFormDefs.sql "\
"./GNUmed-$CLIENTREV/server/sql/gmPhraseWheelTest.sql "\
"./GNUmed-$CLIENTREV/server/sql/test-data/BC-Excelleris-test_patients.sql "


echo "cleaning up"
rm -R ./GNUmed-$CLIENTREV/
rm -vf $CLIENTARCH
rm -vf $SRVARCH
cd ../../../
./remove_pyc.sh
cd -


# create client package
echo "____________"
echo "=> client <="
echo "============"


# external tools
mkdir -p ./GNUmed-$CLIENTREV/external-tools/
cp -R ../../external-tools/gm-install_arriba ./GNUmed-$CLIENTREV/external-tools/
cp -R ../../external-tools/gm-download_loinc ./GNUmed-$CLIENTREV/external-tools/
cp -R ../../external-tools/gm-download_atc ./GNUmed-$CLIENTREV/external-tools/

# client
mkdir -p ./GNUmed-$CLIENTREV/client/
cp -R ../../client/__init__.py ./GNUmed-$CLIENTREV/client/
cp -R ../../client/gm-from-cvs.conf ./GNUmed-$CLIENTREV/client/
cp -R ../../client/gm-from-cvs.sh ./GNUmed-$CLIENTREV/client/
cp -R ../../client/gm-from-cvs.bat ./GNUmed-$CLIENTREV/client/
cp -R ./gnumed ./GNUmed-$CLIENTREV/client/
cp -R ./gnumed-client.desktop ./GNUmed-$CLIENTREV/client/
cp -R ./gm-read_chipcard.sh ./GNUmed-$CLIENTREV/client/
cp -R ./gm-install_client_locally.sh ./GNUmed-$CLIENTREV/client/
cp -R ../../server/gm-remove_person.sh ./GNUmed-$CLIENTREV/client/
cp -R ../../client/sitecustomize.py ./GNUmed-$CLIENTREV/client/
cp -R ../../../check-prerequisites.* ./GNUmed-$CLIENTREV/client/
cp -R ../../../GnuPublicLicense.txt ./GNUmed-$CLIENTREV/client/


# bitmaps
mkdir -p ./GNUmed-$CLIENTREV/client/bitmaps/
cp -R ./gnumed.xpm ./GNUmed-$CLIENTREV/client/bitmaps/
cp -R ../../client/bitmaps/gnumedlogo.png ./GNUmed-$CLIENTREV/client/bitmaps/
cp -R ../../client/bitmaps/empty-face-in-bust.png ./GNUmed-$CLIENTREV/client/bitmaps/
cp -R ../../client/bitmaps/serpent.png ./GNUmed-$CLIENTREV/client/bitmaps/
chmod -cR -x ./GNUmed-$CLIENTREV/client/bitmaps/*.*


# business
mkdir -p ./GNUmed-$CLIENTREV/client/business/
cp -R ../../client/business/*.py ./GNUmed-$CLIENTREV/client/business/


# connectors
mkdir -p ./GNUmed-$CLIENTREV/client/connectors/
cp -R ../../client/connectors/gm_ctl_client.* ./GNUmed-$CLIENTREV/client/connectors/


# doc
mkdir -p ./GNUmed-$CLIENTREV/client/doc/
cp -R ../../client/gm-from-cvs.conf ./GNUmed-$CLIENTREV/client/doc/gnumed.conf.example
cp -R ../../client/doc/hook_script_example.py ./GNUmed-$CLIENTREV/client/doc/hook_script_example.py
cp -R ../../client/doc/man-pages/gnumed.1 ./GNUmed-$CLIENTREV/client/doc/gnumed.1
cp -R ../../client/doc/man-pages/gm_ctl_client.1 ./GNUmed-$CLIENTREV/client/doc/gm_ctl_client.1


# etc
mkdir -p ./GNUmed-$CLIENTREV/client/etc/gnumed/
cp -R ../../client/etc/gnumed-client-init_script.sh ./GNUmed-$CLIENTREV/client/etc/
cp -R ../../client/etc/gnumed/gnumed-client.conf.example ./GNUmed-$CLIENTREV/client/etc/gnumed/
cp -R ../../client/etc/gnumed/mime_type2file_extension.conf.example ./GNUmed-$CLIENTREV/client/etc/gnumed/
cp -R ../../client/etc/gnumed/egk+kvk-demon.conf.example ./GNUmed-$CLIENTREV/client/etc/gnumed/


# exporters
mkdir -p ./GNUmed-$CLIENTREV/client/exporters/
cp -R ../../client/exporters/__init__.py ./GNUmed-$CLIENTREV/client/exporters
cp -R ../../client/exporters/gmPatientExporter.py ./GNUmed-$CLIENTREV/client/exporters


# locale
mkdir -p ./GNUmed-$CLIENTREV/client/locale/
cp -R ../../client/locale/de.po ./GNUmed-$CLIENTREV/client/locale
cp -R ../../client/locale/es.po ./GNUmed-$CLIENTREV/client/locale
cp -R ../../client/locale/fr.po ./GNUmed-$CLIENTREV/client/locale
cp -R ../../client/locale/it.po ./GNUmed-$CLIENTREV/client/locale

cd ../../client/locale/
./create-gnumed_mo.sh de
./create-gnumed_mo.sh es
./create-gnumed_mo.sh fr
./create-gnumed_mo.sh it
cd -

cp -R ../../client/locale/de-gnumed.mo ./GNUmed-$CLIENTREV/client/locale
cp -R ../../client/locale/es-gnumed.mo ./GNUmed-$CLIENTREV/client/locale
cp -R ../../client/locale/fr-gnumed.mo ./GNUmed-$CLIENTREV/client/locale
cp -R ../../client/locale/it-gnumed.mo ./GNUmed-$CLIENTREV/client/locale


# pycommon
mkdir -p ./GNUmed-$CLIENTREV/client/pycommon/
cp -R ../../client/pycommon/*.py ./GNUmed-$CLIENTREV/client/pycommon/


# wxGladeWidgets
mkdir -p ./GNUmed-$CLIENTREV/client/wxGladeWidgets/
cp -R ../../client/wxGladeWidgets/*.py ./GNUmed-$CLIENTREV/client/wxGladeWidgets/
chmod -cR -x ./GNUmed-$CLIENTREV/client/wxGladeWidgets/*.*


# wxpython
mkdir -p ./GNUmed-$CLIENTREV/client/wxpython/
cp -R ../../client/wxpython/*.py ./GNUmed-$CLIENTREV/client/wxpython/
mkdir -p ./GNUmed-$CLIENTREV/client/wxpython/gui/
cp -R ../../client/wxpython/gui/*.py ./GNUmed-$CLIENTREV/client/wxpython/gui/
chmod -cR -x ./GNUmed-$CLIENTREV/client/wxpython/*.*
chmod -cR -x ./GNUmed-$CLIENTREV/client/wxpython/gui/*.*


# pick up current User Manual
echo "picking up GNUmed User Manual from the web"
mkdir -p ./GNUmed-$CLIENTREV/client/doc/user-manual/
wget -v http://wiki.gnumed.de/bin/view/Gnumed/PublishManual		#http://wiki.gnumed.de/bin/publish/Gnumed
rm -vf PublishManual*
wget -v -O ./GNUmed-$CLIENTREV/client/doc/user-manual/GNUmed-User-Manual.zip http://wiki.gnumed.de/pub/Gnumed.zip
cd ./GNUmed-$CLIENTREV/client/doc/user-manual/
unzip GNUmed-User-Manual.zip
#tar -xvzf GNUmed-User-Manual.tgz
rm -vf Release-02.html
ln -s GnumedManual.html index.html
rm -vf GNUmed-User-Manual.zip
#rm -vf GNUmed-User-Manual.tgz
cd -

#----------------------------------
# create server package
echo "____________"
echo "=> server <="
echo "============"


# scripts
mkdir -p ./GNUmed-$CLIENTREV/server
cp -R ../../../GnuPublicLicense.txt ./GNUmed-$CLIENTREV/server/

cp -R ../../server/gm-bootstrap_server ./GNUmed-$CLIENTREV/server/
cp -R ../../server/gm-upgrade_server ./GNUmed-$CLIENTREV/server/
cp -R ../../server/gm-fixup_server ./GNUmed-$CLIENTREV/server/
cp -R ../../server/gm-adjust_db_settings.sh ./GNUmed-$CLIENTREV/server/

cp -R ../../server/gm-backup_database.sh ./GNUmed-$CLIENTREV/server/
cp -R ../../server/gm-restore_database.sh ./GNUmed-$CLIENTREV/server/

cp -R ../../server/gm-backup_data.sh ./GNUmed-$CLIENTREV/server/
cp -R ../../server/gm-restore_data.sh ./GNUmed-$CLIENTREV/server/

cp -R ../../server/gm-zip+sign_backups.sh ./GNUmed-$CLIENTREV/server/
cp -R ../../server/gm-move_backups_offsite.sh ./GNUmed-$CLIENTREV/server/

cp -R ../../server/gm-remove_person.sh ./GNUmed-$CLIENTREV/server/

cp -R ../../external-tools/gm-download_loinc ./GNUmed-$CLIENTREV/server/
cp -R ../../external-tools/gm-download_atc ./GNUmed-$CLIENTREV/server/

cp -R ../../client/__init__.py ./GNUmed-$CLIENTREV/server/


# pycommon
mkdir -p ./GNUmed-$CLIENTREV/server/pycommon
cp -R ../../client/pycommon/*.py ./GNUmed-$CLIENTREV/server/pycommon/


# bootstrap
mkdir -p ./GNUmed-$CLIENTREV/server/bootstrap
cp -R ../../server/bootstrap/* ./GNUmed-$CLIENTREV/server/bootstrap/


# doc
mkdir -p ./GNUmed-$CLIENTREV/server/doc/
cp -R ../../server/bootstrap/README ./GNUmed-$CLIENTREV/server/doc/
cp -R ../../client/doc/man-pages/gm-bootstrap_server.8 ./GNUmed-$CLIENTREV/server/doc/
cp -R ../../client/doc/man-pages/gm-upgrade_server.8 ./GNUmed-$CLIENTREV/server/doc/
cp -R ../../client/doc/man-pages/gm-fixup_server.8 ./GNUmed-$CLIENTREV/server/doc/


# etc
mkdir -p ./GNUmed-$CLIENTREV/server/etc/gnumed/
cp -R ../../client/etc/gnumed/gnumed-backup.conf.example ./GNUmed-$CLIENTREV/server/etc/gnumed/
cp -R ../../client/etc/gnumed/gnumed-restore.conf.example ./GNUmed-$CLIENTREV/server/etc/gnumed/


# sql
mkdir -p ./GNUmed-$CLIENTREV/server/sql
cp -R ../../server/sql/*.sql ./GNUmed-$CLIENTREV/server/sql/
mkdir -p ./GNUmed-$CLIENTREV/server/sql/country.specific
mkdir -p ./GNUmed-$CLIENTREV/server/sql/country.specific/au
cp -R ../../server/sql/country.specific/au/*.sql ./GNUmed-$CLIENTREV/server/sql/country.specific/au
mkdir -p ./GNUmed-$CLIENTREV/server/sql/country.specific/ca
cp -R ../../server/sql/country.specific/ca/*.sql ./GNUmed-$CLIENTREV/server/sql/country.specific/ca
mkdir -p ./GNUmed-$CLIENTREV/server/sql/country.specific/de
cp -R ../../server/sql/country.specific/de/*.sql ./GNUmed-$CLIENTREV/server/sql/country.specific/de
mkdir -p ./GNUmed-$CLIENTREV/server/sql/country.specific/es
cp -R ../../server/sql/country.specific/es/*.sql ./GNUmed-$CLIENTREV/server/sql/country.specific/es
mkdir -p ./GNUmed-$CLIENTREV/server/sql/test-data
cp -R ../../server/sql/test-data/*.sql ./GNUmed-$CLIENTREV/server/sql/test-data

mkdir -p ./GNUmed-$CLIENTREV/server/sql/v2-v3
mkdir -p ./GNUmed-$CLIENTREV/server/sql/v2-v3/dynamic
cp -R ../../server/sql/v2-v3/dynamic/*.sql ./GNUmed-$CLIENTREV/server/sql/v2-v3/dynamic
mkdir -p ./GNUmed-$CLIENTREV/server/sql/v2-v3/static
cp -R ../../server/sql/v2-v3/static/*.sql ./GNUmed-$CLIENTREV/server/sql/v2-v3/static
mkdir -p ./GNUmed-$CLIENTREV/server/sql/v2-v3/superuser
cp -R ../../server/sql/v2-v3/superuser/*.sql ./GNUmed-$CLIENTREV/server/sql/v2-v3/superuser

mkdir -p ./GNUmed-$CLIENTREV/server/sql/v3-v4
mkdir -p ./GNUmed-$CLIENTREV/server/sql/v3-v4/dynamic
cp -R ../../server/sql/v3-v4/dynamic/*.sql ./GNUmed-$CLIENTREV/server/sql/v3-v4/dynamic
mkdir -p ./GNUmed-$CLIENTREV/server/sql/v3-v4/static
cp -R ../../server/sql/v3-v4/static/*.sql ./GNUmed-$CLIENTREV/server/sql/v3-v4/static
mkdir -p ./GNUmed-$CLIENTREV/server/sql/v3-v4/superuser
cp -R ../../server/sql/v3-v4/superuser/*.sql ./GNUmed-$CLIENTREV/server/sql/v3-v4/superuser

mkdir -p ./GNUmed-$CLIENTREV/server/sql/v4-v5
mkdir -p ./GNUmed-$CLIENTREV/server/sql/v4-v5/dynamic
cp -R ../../server/sql/v4-v5/dynamic/*.sql ./GNUmed-$CLIENTREV/server/sql/v4-v5/dynamic
mkdir -p ./GNUmed-$CLIENTREV/server/sql/v4-v5/static
cp -R ../../server/sql/v4-v5/static/*.sql ./GNUmed-$CLIENTREV/server/sql/v4-v5/static
mkdir -p ./GNUmed-$CLIENTREV/server/sql/v4-v5/superuser
cp -R ../../server/sql/v4-v5/superuser/*.sql ./GNUmed-$CLIENTREV/server/sql/v4-v5/superuser

mkdir -p ./GNUmed-$CLIENTREV/server/sql/v5-v6
mkdir -p ./GNUmed-$CLIENTREV/server/sql/v5-v6/dynamic
mkdir -p ./GNUmed-$CLIENTREV/server/sql/v5-v6/static

cp -R ../../server/sql/v5-v6/dynamic/*.sql ./GNUmed-$CLIENTREV/server/sql/v5-v6/dynamic
cp -R ../../server/sql/v5-v6/static/*.sql ./GNUmed-$CLIENTREV/server/sql/v5-v6/static


mkdir -p ./GNUmed-$CLIENTREV/server/sql/v6-v7
mkdir -p ./GNUmed-$CLIENTREV/server/sql/v6-v7/dynamic
mkdir -p ./GNUmed-$CLIENTREV/server/sql/v6-v7/static
mkdir -p ./GNUmed-$CLIENTREV/server/sql/v6-v7/data
mkdir -p ./GNUmed-$CLIENTREV/server/sql/v6-v7/python

cp -R ../../server/sql/v6-v7/dynamic/*.sql ./GNUmed-$CLIENTREV/server/sql/v6-v7/dynamic
cp -R ../../server/sql/v6-v7/static/*.sql ./GNUmed-$CLIENTREV/server/sql/v6-v7/static
cp -R ../../server/sql/v6-v7/data/* ./GNUmed-$CLIENTREV/server/sql/v6-v7/data
cp -R ../../server/sql/v6-v7/python/*.py ./GNUmed-$CLIENTREV/server/sql/v6-v7/python


mkdir -p ./GNUmed-$CLIENTREV/server/sql/v7-v8
mkdir -p ./GNUmed-$CLIENTREV/server/sql/v7-v8/dynamic
mkdir -p ./GNUmed-$CLIENTREV/server/sql/v7-v8/static

cp -R ../../server/sql/v7-v8/dynamic/*.sql ./GNUmed-$CLIENTREV/server/sql/v7-v8/dynamic
cp -R ../../server/sql/v7-v8/static/*.sql ./GNUmed-$CLIENTREV/server/sql/v7-v8/static


mkdir -p ./GNUmed-$CLIENTREV/server/sql/v8-v9
mkdir -p ./GNUmed-$CLIENTREV/server/sql/v8-v9/dynamic
mkdir -p ./GNUmed-$CLIENTREV/server/sql/v8-v9/static

cp -R ../../server/sql/v8-v9/dynamic/*.sql ./GNUmed-$CLIENTREV/server/sql/v8-v9/dynamic
cp -R ../../server/sql/v8-v9/static/*.sql ./GNUmed-$CLIENTREV/server/sql/v8-v9/static


mkdir -p ./GNUmed-$CLIENTREV/server/sql/v9-v10
mkdir -p ./GNUmed-$CLIENTREV/server/sql/v9-v10/dynamic
mkdir -p ./GNUmed-$CLIENTREV/server/sql/v9-v10/static
mkdir -p ./GNUmed-$CLIENTREV/server/sql/v9-v10/superuser
mkdir -p ./GNUmed-$CLIENTREV/server/sql/v9-v10/fixups

cp -R ../../server/sql/v9-v10/dynamic/*.sql ./GNUmed-$CLIENTREV/server/sql/v9-v10/dynamic
cp -R ../../server/sql/v9-v10/static/*.sql ./GNUmed-$CLIENTREV/server/sql/v9-v10/static
cp -R ../../server/sql/v9-v10/superuser/*.sql ./GNUmed-$CLIENTREV/server/sql/v9-v10/superuser
cp -R ../../server/sql/v9-v10/fixups/*.sql ./GNUmed-$CLIENTREV/server/sql/v9-v10/fixups


mkdir -p ./GNUmed-$CLIENTREV/server/sql/v10-v11
mkdir -p ./GNUmed-$CLIENTREV/server/sql/v10-v11/dynamic
mkdir -p ./GNUmed-$CLIENTREV/server/sql/v10-v11/static
mkdir -p ./GNUmed-$CLIENTREV/server/sql/v10-v11/superuser
mkdir -p ./GNUmed-$CLIENTREV/server/sql/v10-v11/fixups

cp -R ../../server/sql/v10-v11/dynamic/*.sql ./GNUmed-$CLIENTREV/server/sql/v10-v11/dynamic
cp -R ../../server/sql/v10-v11/static/*.sql ./GNUmed-$CLIENTREV/server/sql/v10-v11/static
cp -R ../../server/sql/v10-v11/superuser/*.sql ./GNUmed-$CLIENTREV/server/sql/v10-v11/superuser
cp -R ../../server/sql/v10-v11/fixups/*.sql ./GNUmed-$CLIENTREV/server/sql/v10-v11/fixups

#----------------------------------
# weed out unnecessary stuff
for fname in $FILES_REMOVE ; do
	rm -f $fname
done ;


echo "cleaning out debris"
find ./ -name '*.pyc' -exec rm -v '{}' ';'
find ./ -name '*.log' -exec rm -v '{}' ';'
find ./GNUmed-$CLIENTREV/ -name 'CVS' -type d -exec rm -v -r '{}' ';'
find ./GNUmed-$CLIENTREV/ -name 'wxg' -type d -exec rm -v -r '{}' ';'


# now make tarballs
# - client
cd GNUmed-$CLIENTREV
ln -s client Gnumed
cd ..
tar -czf $CLIENTARCH ./GNUmed-$CLIENTREV/client/ ./GNUmed-$CLIENTREV/external-tools/ ./GNUmed-$CLIENTREV/Gnumed
# - server
mv GNUmed-$CLIENTREV GNUmed-v$SRVREV
cd GNUmed-v$SRVREV
rm Gnumed
ln -s server Gnumed
cd ..
tar -czf $SRVARCH ./GNUmed-v$SRVREV/server/ ./GNUmed-v$SRVREV/Gnumed


# cleanup
rm -R ./GNUmed-v$SRVREV/

echo "include schema docs"

#------------------------------------------
# $Log: make-release_tarball.sh,v $
# Revision 1.81.2.3  2009-12-10 10:04:55  ncq
# - user manual now .zip rather than .tgz
#
# Revision 1.81.2.2  2009/09/15 17:55:30  ncq
# - include v11 fixup scripts
# - 0.5.1/11.1
#
# Revision 1.81.2.1  2009/08/13 12:53:34  ncq
# - set proper versions
#
# Revision 1.81  2009/08/11 11:04:28  ncq
# - version fix, prep for release
#
# Revision 1.80  2009/08/04 13:03:19  ncq
# - bump version
# - remove gmManual.py
# - copy client.conf.example from gm-from-cvs.conf
#
# Revision 1.79  2009/07/18 12:15:53  ncq
# - (0.5/v11).rc4
#
# Revision 1.78  2009/07/06 19:52:54  ncq
# - 0.5.rc3/11.rc3
#
# Revision 1.77  2009/06/22 12:40:01  ncq
# - bump versions
#
# Revision 1.76  2009/06/11 13:08:15  ncq
# - bump version
#
# Revision 1.75  2009/06/11 13:04:35  ncq
# - cleanup
#
# Revision 1.74  2009/06/10 21:03:40  ncq
# - include ATC downloader
#
# Revision 1.73  2009/06/04 16:35:03  ncq
# - include gm-download_loinc
#
# Revision 1.72  2009/05/18 15:35:52  ncq
# - include fixups 9-10
#
# Revision 1.71  2009/05/13 13:13:23  ncq
# - exclude some test data
#
# Revision 1.70  2009/05/04 11:41:01  ncq
# - include gm-fixup_server
#
# Revision 1.69  2009/04/24 12:11:08  ncq
# - include ARRIBA installer
#
# Revision 1.68  2009/04/03 11:08:48  ncq
# - include v11 upgrade scripts
#
# Revision 1.67  2009/04/03 09:53:33  ncq
# - fix manual zip location
#
# Revision 1.66  2009/03/04 13:50:25  ncq
# - bump version
#
# Revision 1.65  2009/03/02 11:24:40  ncq
# - bump version
#
# Revision 1.64  2009/02/27 12:41:27  ncq
# - bump version
#
# Revision 1.63  2009/02/25 09:56:34  ncq
# - proper path
#
# Revision 1.62  2009/02/24 18:06:03  ncq
# - include new local installer
#
# Revision 1.61  2009/02/18 16:55:45  shilbert
# - added missing file for v9 to v10 upgrade
#
# Revision 1.60  2009/02/17 12:00:09  ncq
# - bump version
#
# Revision 1.59  2009/02/05 13:05:08  ncq
# - fix typo
#
# Revision 1.58  2009/01/17 23:10:25  ncq
# - bump version
#
# Revision 1.57  2009/01/15 11:41:41  ncq
# - the user manual now is a zip file
#
# Revision 1.56  2009/01/07 12:30:48  ncq
# - fix double README in server package
# - put man pages into proper section
#
# Revision 1.55  2009/01/06 18:27:02  ncq
# - include more server side scripts and man pages
#
# Revision 1.54  2008/08/31 16:17:43  ncq
# - include gm-read_chipcard.sh
#
# Revision 1.53  2008/08/28 18:35:36  ncq
# - include scripts for KVKd startup
#
# Revision 1.52  2008/08/23 15:00:05  ncq
# - bump RC version
#
# Revision 1.51  2008/08/21 13:30:27  ncq
# - rearrange version vars
#
# Revision 1.50  2008/08/06 13:25:46  ncq
# - explicitely bash it
#
# Revision 1.49  2008/07/24 18:22:52  ncq
# - some cleaup
#
# Revision 1.48  2008/04/22 21:20:03  ncq
# - no more gmCLI
#
# Revision 1.47  2008/03/17 14:56:33  ncq
# - properly cleanup pycommon/ in server/, too
#
# Revision 1.46  2008/02/25 17:45:50  ncq
# - include Italian
#
# Revision 1.45  2008/01/16 19:40:55  ncq
# - deprecate gmConfigRegistry
# - include v8-v9 sql dirs
#
# Revision 1.44  2008/01/05 16:42:38  ncq
# - include example conf file for mime type to file extension mapping
#
# Revision 1.43  2007/12/26 18:36:35  ncq
# - delete old CLI/PG libs from tarball
#
# Revision 1.42  2007/12/06 13:08:55  ncq
# - include v7-v8/static/
#
# Revision 1.41  2007/12/02 11:43:39  ncq
# - include gm-backup_data.sh
#
# Revision 1.40  2007/10/25 12:22:04  ncq
# - include desktop file
#
# Revision 1.39  2007/10/22 12:31:53  ncq
# - include v8 stuff
#
# Revision 1.38  2007/10/19 12:53:00  ncq
# - include Snellen
#
# Revision 1.37  2007/09/24 18:40:49  ncq
# - include v7 sql scripts
# - include zip+sign script
#
# Revision 1.36  2007/08/15 09:21:21  ncq
# - we do need gmForms.py now
#
# Revision 1.35  2007/05/22 14:03:43  ncq
# - cleanup of files
#
# Revision 1.34  2007/05/08 16:07:32  ncq
# - include restore script and docs in server package
#
# Revision 1.33  2007/04/27 13:30:28  ncq
# - properly download manual again
#
# Revision 1.32  2007/04/19 13:18:46  ncq
# - cleanup
#
# Revision 1.31  2007/04/06 23:16:21  ncq
# - add v5 -> v6 schema files
#
# Revision 1.30  2007/03/31 21:52:04  ncq
# - rename client to server directory when packing tarballs
# - add cleanup
#
# Revision 1.29  2007/03/26 17:18:39  ncq
# - set CVS HEAD revision to CVS-HEAD
#
# Revision 1.28  2007/03/18 14:12:40  ncq
# - exclude some as-yet unused wxGlade widgets
#
# Revision 1.27  2007/02/19 16:45:45  ncq
# - include hook_script_example.py
#
# Revision 1.26  2007/02/17 14:02:36  ncq
# - no more STIKO browser plugin
#
# Revision 1.25  2007/02/16 15:34:53  ncq
# - include backup and offsite moving script with proper name
#
# Revision 1.24  2007/02/15 14:58:37  ncq
# - fix caps typo
#
# Revision 1.23  2007/02/04 16:18:36  ncq
# - include __init__.py in server/
# - include SQL for 3-4 und 4-5
#
# Revision 1.22  2007/01/29 13:00:01  ncq
# - include man page for gm_ctl_client.py
#
# Revision 1.21  2007/01/24 11:05:59  ncq
# - bump client rev to 0.2.next
# - bump server rev to v5
# - better name for server tgz
#
# Revision 1.20  2006/12/18 18:39:15  ncq
# - include backup script
#
# Revision 1.19  2006/12/18 15:52:38  ncq
# - port improvements from rel-0-2-patches branch
# - make it 0.2.3 now
#
# Revision 1.18  2006/08/15 08:06:39  ncq
# - better name for tgz
#
# Revision 1.17  2006/08/14 20:27:01  ncq
# - don't call it 0.2 anymore as it isn't
#
# Revision 1.16  2006/08/12 19:47:06  ncq
# - link index.html directly to GnumedManual.html
#
# Revision 1.15  2006/08/08 14:04:38  ncq
# - include xdt connector
#
# Revision 1.14  2006/08/07 07:16:23  ncq
# - properly call remove_pyc.sh
#
# Revision 1.13  2006/08/04 06:14:00  ncq
# - fix missing /gui/ part in deletion filenames as well as copy
#
# Revision 1.12  2006/07/30 18:01:19  ncq
# - fix rights
#
# Revision 1.11  2006/07/30 17:10:47  ncq
# - improve by Debian suggestions
#
# Revision 1.10  2006/07/26 10:36:55  ncq
# - move gnumed.xpm to more proper location
#
# Revision 1.9  2006/07/25 07:35:57  ncq
# - move user-manual into doc/
#
# Revision 1.8  2006/07/24 20:04:43  ncq
# - we do not need the bmi calculator png
#
# Revision 1.7  2006/07/23 20:39:50  ncq
# - more cleanup
#
# Revision 1.6  2006/07/22 12:49:26  ncq
# - don't need bmi for now
#
# Revision 1.5  2006/07/21 15:56:14  ncq
# - add User Manual
#
# Revision 1.4  2006/07/21 12:59:16  ncq
# - do not produce *.orig.tar.gz
#
# Revision 1.3  2006/07/19 22:10:14  ncq
# - properly clean up
#
# Revision 1.2  2006/07/19 20:03:35  ncq
# - improved client packages
#
# Revision 1.1  2006/07/19 11:31:17  ncq
# - renamed to better reflect its use
#
# Revision 1.1  2006/06/21 21:58:13  shilbert
# - cosmetic changes
#
# Revision 1.10  2006/02/12 18:07:42  shilbert
# - nearing v0.2
#
# Revision 1.9  2005/08/24 09:33:53  ncq
# - remove CVS/ debris as requested by Debian packager
#
# Revision 1.8  2005/08/22 13:51:11  ncq
# - include CHANGELOG
#
# Revision 1.7  2005/07/19 20:43:21  ncq
# - make index.html link to Release-0.1.html
#
# Revision 1.6  2005/07/19 17:16:06  shilbert
# - gmManual now actually displays some content again
#
# Revision 1.5  2005/07/19 15:31:14  ncq
# - retrieve manual zip file from the web with wget
#
# Revision 1.4  2005/07/16 10:56:38  shilbert
# - copy user manual from wiki to workplace
#
# Revision 1.3  2005/07/10 18:46:39  ncq
# - build mo-files, too
#
# Revision 1.2  2005/07/10 17:42:32  ncq
# - move README style files directly below GNUmed-0.1 directory
#
# Revision 1.1  2005/07/07 20:19:04  shilbert
# - script to create packaging environment
#
