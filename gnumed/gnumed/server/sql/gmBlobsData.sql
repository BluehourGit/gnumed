-- BLOB table data for GnuMed

-- license: GPL
-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmBlobsData.sql,v $
-- $Revision: 1.5 $ $Date: 2004-03-02 23:59:11 $ $Author: ihaywood $

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
INSERT into doc_type(id, name) values(1, i18n('discharge summary internal'));
INSERT into doc_type(id, name) values(2, i18n('discharge summary surgical'));
INSERT into doc_type(id, name) values(3, i18n('discharge summary psychiatric'));
INSERT into doc_type(id, name) values(4, i18n('discharge summary neurological'));
INSERT into doc_type(id, name) values(5, i18n('discharge summary orthopaedic'));
INSERT into doc_type(id, name) values(6, i18n('discharge summary other'));
INSERT into doc_type(id, name) values(7, i18n('discharge summary rehabilitation'));
INSERT into doc_type(id, name) values(8, i18n('referral report internal'));
INSERT into doc_type(id, name) values(9, i18n('referral report surgical'));
INSERT into doc_type(id, name) values(10, i18n('referral report ENT'));
INSERT into doc_type(id, name) values(11, i18n('referral report eye'));
INSERT into doc_type(id, name) values(12, i18n('referral report urology'));
INSERT into doc_type(id, name) values(13, i18n('referral report orthopaedic'));
INSERT into doc_type(id, name) values(14, i18n('referral report neuro'));
INSERT into doc_type(id, name) values(15, i18n('referral report radiology'));
INSERT into doc_type(id, name) values(16, i18n('referral report other'));
INSERT into doc_type(id, name) values(17, i18n('referral report cardiology'));
INSERT into doc_type(id, name) values(18, i18n('referral report psychotherapy'));
INSERT into doc_type(id, name) values(19, i18n('discharge summary urology'));
INSERT into doc_type(id, name) values(20, i18n('referral report oncology'));
INSERT into doc_type(id, name) values(21, i18n('discharge summary neurosurgery'));
INSERT into doc_type(id, name) values(22, i18n('discharge summary ophthalmology'));
INSERT into doc_type(id, name) values(23, i18n('discharge summary ENT'));
INSERT into doc_type(id, name) values(24, i18n('referral report pathology'));
INSERT into doc_type(id, name) values(25, i18n('referral report neurosurgery'));
INSERT into doc_type(id, name) values(26, i18n('patient photograph'));
--INSERT into doc_type(id, name) values(, i18n(''));

-- your own doc types can only have ids between 100 and 200

-- =============================================
-- do simple schema revision tracking
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmBlobsData.sql,v $', '$Revision: 1.5 $');

-- =============================================
-- $Log: gmBlobsData.sql,v $
-- Revision 1.5  2004-03-02 23:59:11  ihaywood
-- New document type 26: patient photograph
--
-- Revision 1.4  2003/07/20 09:39:25  ncq
-- - added some doc types
--
-- Revision 1.3  2003/05/12 12:43:39  ncq
-- - gmI18N, gmServices and gmSchemaRevision are imported globally at the
--   database level now, don't include them in individual schema file anymore
--
-- Revision 1.2  2003/04/18 13:30:35  ncq
-- - add doc types
-- - update comment on allergy.id_substance
--
-- Revision 1.1  2003/04/07 11:09:54  ncq
-- - separated out data inserts from schema definition
--
