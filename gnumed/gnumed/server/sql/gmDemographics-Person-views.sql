-- project: GNUMed

-- purpose: views for easier identity access
-- author: Karsten Hilbert
-- license: GPL (details at http://gnu.org)

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmDemographics-Person-views.sql,v $
-- $Id: gmDemographics-Person-views.sql,v 1.28 2005-01-26 21:29:11 ncq Exp $

-- ==========================================================
\unset ON_ERROR_STOP
drop index idx_identity_dob;
drop index idx_names_last_first;
drop index idx_names_firstnames;
\set ON_ERROR_STOP 1

create index idx_identity_dob on identity(dob);
-- useful for queries on "last and first" or "last"
create index idx_names_last_first on names(lastnames, firstnames);
-- need this for queries on "first" only
create index idx_names_firstnames on names(firstnames);

-- ==========================================================
-- rules/triggers/functions on table "names"

-- allow only unique names
\unset ON_ERROR_STOP
drop index idx_uniq_act_name;
create unique index idx_uniq_act_name on names(id_identity) where active = true;
\set ON_ERROR_STOP 1

-- IH: 9/3/02
-- trigger function to ensure only one name is active
-- it's behaviour is to set all other names to inactive when
-- a name is made active
\unset ON_ERROR_STOP
drop trigger tr_uniq_active_name on names;
drop function f_uniq_active_name();

drop trigger tr_always_active_name on names;
drop function f_always_active_name();
\set ON_ERROR_STOP 1

-- do not allow multiple active names per person
create FUNCTION F_uniq_active_name() RETURNS OPAQUE AS '
DECLARE
--	tmp text;
BEGIN
--	tmp := ''identity:'' || NEW.id_identity || '',id:'' || NEW.id || '',name:'' || NEW.firstnames || '' '' || NEW.lastnames;
--	raise notice ''uniq_active_name: [%]'', tmp;
	if NEW.active = true then
		update names set active = false
		where
			id_identity = NEW.id_identity
				and
			active = true;
	end if;
	return NEW;
END;' LANGUAGE 'plpgsql';

--create TRIGGER tr_uniq_active_name
--	BEFORE insert ON names
--	FOR EACH ROW EXECUTE PROCEDURE F_uniq_active_name();

-- ensure we always have an active name
create function f_always_active_name() returns opaque as '
BEGIN
	if NEW.active = false then
		raise exception ''Cannot delete/disable active name. Another name must be activated first.'';
		return OLD;
	end if;
	return NEW;
END;
' language 'plpgsql';

--create trigger tr_always_active_name
--	before update or delete on names
--	for each row execute procedure f_always_active_name();


-- FIXME: we don't actually want this to be available
\unset ON_ERROR_STOP
drop trigger TR_delete_names on identity;
drop function F_delete_names();
\set ON_ERROR_STOP 1

CREATE FUNCTION F_delete_names() RETURNS OPAQUE AS '
DECLARE
BEGIN
	DELETE FROM names WHERE id_identity=OLD.id;
	RETURN OLD;
END;' LANGUAGE 'plpgsql';

-- only re-enable this once we know how to do it !!
--CREATE TRIGGER TR_delete_names
--	BEFORE DELETE ON identity
--	FOR EACH ROW EXECUTE PROCEDURE F_delete_names();

-- business functions

\unset ON_ERROR_STOP
drop function add_name(integer, text, text, bool);
\set ON_ERROR_STOP 1

create function add_name(integer, text, text, bool) returns integer as '
DECLARE
	identity_id alias for $1;
	first alias for $2;
	last alias for $3;
	activate_name alias for $4;

	n_rec record;
BEGIN
	-- name already there for this identity ?
	select into n_rec * from names where id_identity = identity_id and firstnames = first and lastnames = last;
	if FOUND then
		update names set active = activate_name where id = n_rec.id;
		if FOUND then
			return n_rec.id;
		end if;
		return NULL;
	end if;
	-- no, insert new name
	if activate_name then
	    -- deactivate all the existing names
		update names set active=''f'' where id_identity = identity_id;
	end if;
	insert into names (id_identity, firstnames, lastnames, active) values (identity_id, first, last, activate_name);
	if FOUND then
		return n_rec.id;
	end if;
	return NULL;
END;' language 'plpgsql';

-- ==========================================================

\unset ON_ERROR_STOP 
drop function create_occupation (text);
\set ON_ERROR_STOP 1

CREATE FUNCTION create_occupation (text) RETURNS integer AS '
DECLARE
	occ_name alias for $1;
	occ_id integer;
	n_rec RECORD;
BEGIN
	select into n_rec * from occupation where name = occ_name;
	if FOUND then
		return n_rec.id;
	else
		insert into occupation (name) values (occ_name);
		return currval (''occupation_id_seq'');
	end if;
END;' LANGUAGE 'plpgsql';

\unset ON_ERROR_STOP
drop function new_pupic();
\set ON_ERROR_STOP 1

CREATE FUNCTION new_pupic() RETURNS char(24) AS '
DECLARE
BEGIN
   -- how does this work? How do we get new ''unique'' numbers?
   RETURN ''0000000000'';
END;' LANGUAGE 'plpgsql';

-- ==========================================================
\unset ON_ERROR_STOP
drop view v_basic_person;
\set ON_ERROR_STOP 1

create view v_basic_person as
select
	i.id as id,
	i.id as i_id,
	n.id as n_id,
	i.title as title,
	n.firstnames as firstnames,
	n.lastnames as lastnames,
	i.dob as dob,
	i.cob as cob,
	i.gender as gender,
	i.karyotype as karyotype,
	i.pupic as pupic,
	ms.name as marital_status,
	fk_marital_status as pk_marital_status,
	n.preferred as preferred,
	i.xmin as xmin_identity
from
	identity i,
	names n,
	marital_status ms
where
	i.deceased is NULL and
	n.active=true and
	n.id_identity=i.id and
	ms.pk = i.fk_marital_status
;

-- "i.id as id" is legacy compatibility code, remove it once Archive is updated

-- ----------------------------------------------------------
-- create new name and new identity
create RULE r_insert_basic_person AS
	ON INSERT TO v_basic_person DO INSTEAD (
		INSERT INTO identity (pupic, gender, dob, cob, title)
					values (new_pupic(), NEW.gender, NEW.dob, NEW.cob, NEW.title);
		INSERT INTO names (firstnames, lastnames, id_identity)
					VALUES (NEW.firstnames, NEW.lastnames, currval('identity_id_seq'));
	)
;

-- rule for name change - add new name to list, making it active
create RULE r_update_basic_person1 AS ON UPDATE TO v_basic_person 
    WHERE NEW.firstnames != OLD.firstnames OR NEW.lastnames != OLD.lastnames 
    OR NEW.title != OLD.title DO INSTEAD 
    INSERT INTO names (firstnames, lastnames, id_identity, active)
     VALUES (NEW.firstnames, NEW.lastnames, NEW.i_id, true);

-- rule for identity change
-- yes, you would use this, think carefully.....
create RULE r_update_basic_person2 AS ON UPDATE TO v_basic_person
    DO INSTEAD UPDATE identity SET dob=NEW.dob, cob=NEW.cob, gender=NEW.gender
    WHERE id=NEW.i_id;

-- deletes names as well by use of a trigger (double rule would be simpler, 
-- but didn't work)
create RULE r_delete_basic_person AS ON DELETE TO v_basic_person DO INSTEAD
       DELETE FROM identity WHERE id=OLD.i_id;

-- =============================================
-- staff views
\unset ON_ERROR_STOP
drop view v_staff;
\set ON_ERROR_STOP 1

create view v_staff as
select
	vbp.i_id as pk_identity,
	s.pk as pk_staff,
	vbp.title as title,
	vbp.firstnames as firstnames,
	vbp.lastnames as lastnames,
	s.sign as sign,
	_(sr.name) as role,
	vbp.dob as dob,
	vbp.gender as gender,
	s.db_user as db_user,
	s.comment as comment
from
	staff s,
	staff_role sr,
	v_basic_person vbp
where
	s.fk_role = sr.pk
		and
	s.fk_identity = vbp.i_id
;

-- =========================================================
-- emulate previous structure of address linktables
\unset ON_ERROR_STOP
drop view lnk_person2address;
drop view lnk_org2address;
\set ON_ERROR_STOP 1

CREATE VIEW lnk_person2address AS
	SELECT id_identity, id_address, id_type
	FROM lnk_person_org_address;

CREATE VIEW lnk_org2address AS
	SELECT id_org, id_address
	FROM lnk_person_org_address;

-- ==========================================================
\unset ON_ERROR_STOP			-- cascade doesn't work on 7.1
drop view v_person_comms_flat cascade;
drop view v_person_comms_flat;
\set ON_ERROR_STOP 1


create view v_person_comms_flat as
select distinct on (id_identity)
	v1.id_identity as id_identity,
	v1.url as email,
	v2.url as fax,
	v3.url as homephone,
	v4.url as workphone,
	v5.url as mobile
from
	lnk_identity2comm v1,
	lnk_identity2comm v2,
	lnk_identity2comm v3,
	lnk_identity2comm v4,
	lnk_identity2comm v5
where
	v1.id_identity = v2.id_identity
	and v2.id_identity = v3.id_identity
	and v3.id_identity = v4.id_identity
	and v4.id_identity = v5.id_identity
	and v1.id_type = 1
	and v2.id_type = 2
	and v3.id_type = 3
	and v4.id_type = 4
	and v5.id_type = 5 ;

-- =========================================================

-- ==========================================================
\unset ON_ERROR_STOP
drop index idx_lnk_pers2rel;
\set ON_ERROR_STOP 1

create index idx_lnk_pers2rel on lnk_person2relative(id_identity, id_relation_type);
-- consider regular "CLUSTER idx_lnk_pers2rel ON lnk_person2relative;"

-- ==========================================================
-- permissions
-- ==========================================================
GRANT SELECT ON
	v_staff
	, lnk_person2address
	, lnk_org2address
	, v_person_comms_flat
TO GROUP "gm-doctors";

GRANT SELECT, INSERT, UPDATE, DELETE ON
	v_basic_person
TO GROUP "gm-doctors";

-- =============================================
-- do simple schema revision tracking
delete from gm_schema_revision where filename = '$RCSfile: gmDemographics-Person-views.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmDemographics-Person-views.sql,v $', '$Revision: 1.28 $');

-- =============================================
-- $Log: gmDemographics-Person-views.sql,v $
-- Revision 1.28  2005-01-26 21:29:11  ncq
-- - added missing GRANT
--
-- Revision 1.27  2004/12/21 09:59:40  ncq
-- - comm_channel -> comm else too long on server < 7.3
--
-- Revision 1.26  2004/12/20 19:04:37  ncq
-- - fixes by Ian while overhauling the demographics API
--
-- Revision 1.25  2004/12/15 09:30:48  ncq
-- - correctly pull in martial status in v_basic_person
--   (update/insert rules may be lacking now, though ?)
--
-- Revision 1.24  2004/12/15 04:18:03  ihaywood
-- minor changes
-- pointless irregularity in v_basic_address
-- extended v_basic_person to more fields.
--
-- Revision 1.23  2004/10/19 23:27:11  sjtan
-- this came up as script stopping bug , when run inside a in-order
-- concatenated monolithic sql script.
--
-- Revision 1.22  2004/08/16 19:35:52  ncq
-- - added idx_lnk_pers2rel based on ideas by Aldfaer (Anne v.d.Ploeg)
--
-- Revision 1.21  2004/07/20 07:19:12  ncq
-- - in add_name() only deactivate existing names if new name is to be active
--   or else we'd be able to have patients without an active name ...
--
-- Revision 1.20  2004/07/20 01:01:46  ihaywood
-- changing a patients name works again.
-- Name searching has been changed to query on names rather than v_basic_person.
-- This is so the old (inactive) names are still visible to the search.
-- This is so when Mary Smith gets married, we can still find her under Smith.
-- [In Australia this odd tradition is still the norm, even female doctors
-- have their medical registration documents updated]
--
-- SOAPTextCtrl now has popups, but the cursor vanishes (?)
--
-- Revision 1.19  2004/07/17 20:57:53  ncq
-- - don't use user/_user workaround anymore as we dropped supporting
--   it (but we did NOT drop supporting readonly connections on > 7.3)
--
-- Revision 1.18  2004/06/28 12:16:19  ncq
-- - drop ... cascade; doesn't work on 7.1
--
-- Revision 1.17  2004/06/27 02:39:46  sjtan
--
-- fix-up for lots of empty rows.
--
-- Revision 1.16  2004/06/25 15:19:42  ncq
-- - add v_person_comms_flat by Syan, this isn't really
--   nice since it uses hardcoded comm types
--
-- Revision 1.15  2004/06/25 15:08:57  ncq
-- - v_pat_comms by Syan
--
-- Revision 1.14  2004/04/07 18:16:06  ncq
-- - move grants into re-runnable scripts
-- - update *.conf accordingly
--
-- Revision 1.13  2004/03/27 18:35:56  ncq
-- - cleanup
--
-- Revision 1.12  2004/03/27 04:37:01  ihaywood
-- lnk_person2address now lnk_person_org_address
-- sundry bugfixes
--
-- Revision 1.11  2003/12/29 15:35:15  uid66147
-- - staff views and grants
--
-- Revision 1.10  2003/12/02 02:14:40  ncq
-- - comment out triggers on name.active until we know how to to them :-(
-- - at least we CAN do active names now
-- - ensure unique active name by means of an index, though
--
-- Revision 1.9  2003/12/01 22:11:26  ncq
-- - remove a raise notice
--
-- Revision 1.8  2003/11/26 23:54:51  ncq
-- - lnk_vaccdef2reg does not exist anymore
--
-- Revision 1.7  2003/11/23 23:37:09  ncq
-- - names.title -> identity.title
-- - yet another go at uniq_active_name triggers
--
-- Revision 1.6  2003/11/23 14:05:38  sjtan
--
-- slight debugging of add_names: start off with active=false, and then other attributes won't be affected
-- by trigger side effects.
--
-- Revision 1.5  2003/11/23 12:53:20  sjtan
-- *** empty log message ***
--
-- Revision 1.4  2003/11/23 00:02:47  sjtan
--
-- NEW.active is not the same as NEW.active = true; does it mean 'is there a NEW.active' ?
-- the syntax for n_id variable didn't seem to work; this works?
--
-- Revision 1.3  2003/11/22 13:58:25  ncq
-- - rename constraint for unique active names
-- - add add_name() function
--
-- Revision 1.2  2003/10/19 13:01:20  ncq
-- - add omitted "index"
--
-- Revision 1.1  2003/08/02 10:46:03  ncq
-- - rename schema files by service
--
-- Revision 1.2  2003/05/12 12:43:39  ncq
-- - gmI18N, gmServices and gmSchemaRevision are imported globally at the
--   database level now, don't include them in individual schema file anymore
--
-- Revision 1.1  2003/04/18 13:17:38  ncq
-- - collect views for Identity DB here
--
