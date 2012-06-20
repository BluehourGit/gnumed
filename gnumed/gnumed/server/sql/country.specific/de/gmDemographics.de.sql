-- GNUmed
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/de/gmDemographics.de.sql,v $
-- $Revision: 1.10 $

-- license: GPL v2 or later

-- demographics tables specific for Germany

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================================
create schema de_de authorization "gm-dbo";
grant usage on schema de_de to group "gm-doctors";

-- set client_encoding to 'LATIN1';
-- ===================================================================
-- tables related to the German Krankenversichtenkarte KVK
create table de_de.kvk (
	pk serial
		primary key,
	fk_patient integer
		not null
		references dem.identity(pk),

	-- eigentliche KVK-Felder
	-- Datenbereich (020h-0FFh)				--  Feldtag	L�nge	Feldname				Optional
	KK_Name varchar(28) not null,			--  0x80	2-28	Krankenkassenname		nein
	KK_Nummer character(7) not null,		--  0x81	7		Krankenkassennummer		nein
	KVK_Nummer character(5),				--  0x8F	5		Versichertenkarten-Nr.	ja
	Mitgliedsnummer varchar(12) not null,	--  0x82	6-12	Versichertennummer		nein
	Mitgliedsstatus varchar(4) not null,	--  0x83	1/4		Versichertenstatus		nein
	Zusatzstatus varchar(3),				--  0x90	1-3		Statuserg�nzung			ja
	Titel varchar(15),						--  0x84	3-15	Titel					ja
	Vorname varchar(28),					--  0x85	2-28	Vorname					ja
	Namenszuatz varchar(15),				--  0x86	1-15	Namenszusatz			ja
	Familienname varchar(28) not null,		--  0x87	2-28	Familienname			nein
	Geburtsdatum character(8) not null,		--  0x88	8		Geburtsdatum			nein
	Strasse varchar(28),					--  0x89	1-28	Stra�enname				ja
	Landescode  varchar(3),					--  0x8A	1-3		Wohnsitzl�ndercode		ja
	PLZ varchar(7) not null,				--  0x8B	4-7		Postleitzahl			nein
	Ort varchar(23) not null,				--  0x8C	2-23	Ortsname				nein
	Gueltigkeit character(4),				--  0x8D	4		G�ltigkeitsdatum		ja
	CRC character(1) not null,				--  0x8E	1		Pr�fsumme				nein

	is_valid_address boolean default true,

	valid_since timestamp with time zone not null,
	presented timestamp with time zone [] not null,
	invalidated timestamp with time zone default null
);

-- Der Datenbereich ist wie folgt gegliedert:
--  1. Feldtag (1 Byte)
--  2. Feldlaenge (1 Byte)
--  3. ASCII-codierter Text (der angegebenen Feldlaenge, 1 Zeichen=1 Byte )

comment on table de_de.kvk is
	'Speichert die Daten einer bestimmten KVK. Wir trennen die KVK-Daten von
	 den Daten ueber Person, Wohnort, Kassenzugehoerigkeit, Mitgliedsstatus und
	 Abrechnungsfaellen. Diese Daten werden jedoch a) als Vorgaben fuer die
	 eigentlichen Personendaten und b) als gueltig fuer abrechnungstechnische
	 Belange angesehen.';

comment on column de_de.kvk.invalidated is
	'Kann durchaus vor Ende von "Gueltigkeit" liegen. Zeitpunkt des
	 Austritts aus der Krankenkasse. Beim Setzen dieses Feldes muss
	 auch die Zuzahlungsbefreiung auf NULL gesetzt werden.';

-- ---------------------------------------------
--create table de_de.kvk_presented (
--	id serial primary key,
--	id_kvk integer not null references kvk(id),
--	presented timestamp with time zone not null,
--	unique (id_kvk, presented)
--);

-- ---------------------------------------------
create table de_de.zuzahlungsbefreiung (
	id serial primary key,
	id_patient integer references dem.identity(pk),

	Medikamente date default null,
	Heilmittel date default null,
	Hilfsmittel date default null,

	presented timestamp with time zone not null default CURRENT_TIMESTAMP
);

-- =============================================
-- Praxisgebuehr
-- ---------------------------------------------
create table de_de.beh_fall_typ (
	pk serial primary key,
	code text unique not null,
	kurzform text unique not null,
	name text unique not null
) inherits (audit.audit_fields);

select audit.add_table_for_audit('de_de', 'beh_fall_typ');

comment on table de_de.beh_fall_typ is
	'Art des Behandlungsfalls (MuVo/Impfung/...)';

-- ---------------------------------------------
create table de_de.behandlungsfall (
	pk serial primary key,
	fk_patient integer
		not null
		references dem.identity(pk)
		on delete restrict
		on update cascade,
	fk_falltyp integer
		not null
		references de_de.beh_fall_typ(pk)
		on delete restrict
		on update cascade,
	started date
		not null
		default CURRENT_DATE,
	must_pay_prax_geb boolean
		not null
		default true
);

select audit.add_table_for_audit('de_de', 'behandlungsfall');

-- ---------------------------------------------
-- this general table belongs elsewhere
create table de_de.payment_method (
	pk serial primary key,
	description text unique not null
);

-- ---------------------------------------------
create table de_de.prax_geb_paid (
	pk serial primary key,
	fk_fall integer
		not null
		references de_de.behandlungsfall(pk)
		on delete restrict
		on update cascade,
	paid_amount numeric
		not null
		default 0,
	paid_when date
		not null
		default CURRENT_DATE,
	paid_with integer
		not null
		references de_de.payment_method(pk)
		on delete restrict
		on update cascade
) inherits (audit.audit_fields);

select audit.add_table_for_audit('de_de', 'prax_geb_paid');

comment on table de_de.prax_geb_paid is
	'';

-- =============================================
-- do simple revision tracking
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmDemographics.de.sql,v $', '$Revision: 1.10 $');

-- =============================================
-- $Log: gmDemographics.de.sql,v $
-- Revision 1.10  2006-01-06 10:12:02  ncq
-- - add missing grants
-- - add_table_for_audit() now in "audit" schema
-- - demographics now in "dem" schema
-- - add view v_inds4vaccine
-- - move staff_role from clinical into demographics
-- - put add_coded_term() into "clin" schema
-- - put German things into "de_de" schema
--
-- Revision 1.9  2006/01/05 16:04:37  ncq
-- - move auditing to its own schema "audit"
--
-- Revision 1.8  2005/11/25 15:06:25  ncq
-- - create schema de_DE
--
-- Revision 1.7  2005/11/19 13:51:46  ncq
-- - stra�e -> strasse
--
-- Revision 1.6  2005/09/19 16:38:52  ncq
-- - adjust to removed is_core from gm_schema_revision
--
-- Revision 1.5  2005/07/14 21:31:43  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.4  2005/04/14 16:48:33  ncq
-- - name_gender_map moved to generic demographics script
--
-- Revision 1.3  2005/02/12 13:49:14  ncq
-- - identity.id -> identity.pk
-- - allow NULL for identity.fk_marital_status
-- - subsequent schema changes
--
-- Revision 1.2  2003/12/29 16:02:28  uid66147
-- - client_encoding breakage
--
-- Revision 1.1  2003/08/05 08:16:00  ncq
-- - cleanup/renaming
--
