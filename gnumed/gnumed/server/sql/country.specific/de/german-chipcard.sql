-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/de/Attic/german-chipcard.sql,v $
-- $Revision: 1.3 $

-- part of GnuMed
-- license: GPL

-- tables related to the German Krankenversichtenkarte KVK
-- belongs into service personalia
-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

set client_encoding to 'LATIN1';
-- ---------------------------------------------
create table name_gender_map (
	id serial primary key,
	name varchar(255) unique not null,
	gender character(1) check (gender in ('m', 'f'))
);

COMMENT on table name_gender_map is
	'maps (first) names to their most frequently locally assigned gender, 
	 this table is updated nightly by a cron script, 
	 names whose gender distribution is between 70/30 and 30/70 are 
	 ignored for ambiguity reasons,
	 names with "ambigous" gender are also ignored';

-- ---------------------------------------------
create table de_kvk (
	id serial primary key,
	id_patient references identity(id),

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
	Stra�e varchar(28),						--  0x89	1-28	Stra�enname				ja
	Landescode  varchar(3),					--  0x8A	1-3		Wohnsitzl�ndercode		ja
	PLZ varchar(7) not null,				--  0x8B	4-7		Postleitzahl			nein
	Ort varchar(23) not null,				--  0x8C	2-23	Ortsname				nein
	Gueltigkeit character(4),				--  0x8D	4		G�ltigkeitsdatum		ja
	CRC character(1) not null,				--  0x8E	1		Pr�fsumme				nein

	is_valid_address boolean default true,

	valid_since timestamp with time zone not null,
	presented timestamp with time zone[] not null,
	invalidated timestamp with time zone default null
);

-- Der Datenbereich ist wie folgt gegliedert:
--  1. Feldtag (1 Byte)
--  2. Feldl�nge (1 Byte)
--  3. ASCII-codierter Text (der angegebenen Feldl�nge, 1 Zeichen=1 Byte )

comment on table de_kvk is
	'Speichert die Daten einer bestimmten KVK. Wir trennen die KVK-Daten von
	 den Daten �ber Person, Wohnort, Kassenzugeh�rigkeit, Mitgliedsstatus und
	 Abrechnungsf�llen. Diese Daten werden jedoch a) als Vorgaben f�r die
	 eigentlichen Personendaten und b) als g�ltig f�r abrechnungstechnische
	 Belange angesehen.';

comment on column de_kvk.invalidated is
	'Kann durchaus vor *Gueltigkeit* liegen. Zeitpunkt des Austritts aus
	 der Krankenkasse. Beim Setzen dieses Feldes mu� auch die Zuzahlungsbefreiung
	 auf NULL gesetzt werden.';

-- ---------------------------------------------
create table de_zuzahlungsbefreiung (
	id serial primary key,
	id_patient references identity(id),

	Medikamente date default null,
	Heilmittel date default null,
	Hilfsmittel date default null,

	presented timestamp with time zone default CURRENT_TIMESTAMP
);

-- =============================================
-- do simple revision tracking
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: german-chipcard.sql,v $', '$Revision: 1.3 $');

-- =============================================
-- $Log: german-chipcard.sql,v $
-- Revision 1.3  2003-06-11 14:03:44  ncq
-- - set encoding
--
-- Revision 1.2  2003/05/12 12:43:40  ncq
-- - gmI18N, gmServices and gmSchemaRevision are imported globally at the
--   database level now, don't include them in individual schema file anymore
--
-- Revision 1.1  2003/02/03 16:16:51  ncq
-- - first shot at KVK tables
--
