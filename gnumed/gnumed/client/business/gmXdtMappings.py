# -*- encoding: latin-1 -*-
"""GnuMed German XDT mapping data.

This maps XDT fields in various ways.
"""
#==============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmXdtMappings.py,v $
# $Id: gmXdtMappings.py,v 1.26 2004-06-25 12:37:20 ncq Exp $
__version__ = "$Revision: 1.26 $"
__author__ = "S.Hilbert, K.Hilbert"
__license__ = "GPL"

if __name__ == '__main__':
	_ = lambda x:x
#==============================================================
xdt_id_map = {
	# Turbomed fehlerhafte Feldkennungen ?
	# (sind nicht definiert nach BDT2/94, aber nach KVDT !)
	# '0215':'PLZ',
	# '0216':'Ort',
	# '3112':'PLZ',
	# '3113':'Ort',
	# '3673':'ICD??',
	'6295':'??',
	'6296':'??',
	'6297':'??',
	'6298':'??',
	'6299':'??',

	#KBV-Pr�fnummer 
	'0101':'KBV-Pr�fnummer',
	#responsible software vendor 
	'0102':'Softwareverantwortlicher',
	#software package 
	'0103':'Software',
	#PC hardware 
	'0104':'Hardware',
	'0105':'KBV-Pr�fnummer',
	'0111':'Email-Adresse des SV',
	'0121':'Strasse des SV',
	'0122':'PLZ des SV',
	'0123':'Ort des SV',
	'0124':'Telefonnummer des SV',
	'0125':'Telefaxnummer des SV',
	'0126':'Regionaler Systembetreuer (SB)',
	'0127':'Strasse des SB',
	'0128':'PLZ des SB',
	'0129':'Ort des SB',
	'0130':'Telfonnummer des SB',
	'0131':'Telefaxnummer des SB',
	'0132':'Release-Stand der Software',
	#Arztnummer 
	'0201':'Arztnummer',
	#Praxistyp 
	'0202':'Praxistyp',
	#Arztname
	'0203':'Arztname',
	#Arztgruppe verbal 
	'0204':'Arztgruppe verbal',
	#street
	'0205':'Strasse der Praxisadresse',
	#postcode and city
	'0206':'PLZ Ort',
	#Arzt und Leistungskennzeichen
	'0207':'Arzt mit Leistungskennzeichen',
	#phone
	'0208':'Telefonnummer',
	#fax
	'0209':'Telefaxnummer',
	#modem
	'0210':'Modemnummer',
	'0211':'Arztname f�r Leistungsdifferenzierung',
	'0213':'Leistungskennzeichen',
	'0214':'Erl�uterung zum Leistungskennzeichen',
	'0215':'PLZ der Praxisadresse',
	'0216':'Ort der Praxisadresse',
	#number of doctors
	'0225':'Anzahl der �rzte',
	#name of first free category
	'0250':'Name erste freie Kategorie',
	#content of first free category
	'0251':'Inhalt erste freie Kategorie',
	'0915':'PZN Medikament auf Kassenrezept',
	'0917':'Packungsgr�sse Medikament auf Kassenrezept',
	'0918':'Packungsgr�sse Medikament auf Privatrezept',
	'0919':'Hilfsmittelbezeichnung',
	'0920':'Hilfsmittelnummer',
	'0922':'PZN Hilfsmittel',
	'0923':'Anzahl Hilfsmittel',
	'0925':'Heilmittel',
	'0950':'PZN Dauermedikament',
	'0951':'PZN Medikament auf Privatrezept',
	'0952':'PZN �rztemuster',
	'0953':'Packungsgr�sse �rztemuster',
	'0960':'Kennzeichnung Geb�hrenpflichtig',
	'0961':'Kennzeichnung aut idem',
	'0962':'Kennzeichnung noctu',
	'0970':'Anzahl (Packungen) Medikament auf Rezept',
	'0971':'Anzahl (Packungen) Medikament auf Privatrezept',
	'2700':'IK des Krankenhauses',
	'2701':'Fachgebiet laut LKA',
	'2702':'Arztnummer des An�sthesisten',
	'2706':'Indikationsschl�ssel',
	'2709':'Lfd. OP-Nummer',
	'2710':'Lfd. OP-Nummer',
	'2711':'OP-Datum',
	'2720':'Blutung',
	'2721':'Narkosezwischenfall',
	'2722':'Pneumonie',
	'2723':'Wundinfektion',
	'2724':'Gef�ss- oder Nervenl�sion',
	'2725':'Lagerungssch�den',
	'2726':'Venenthrombose',
	'2727':'Komplikation',
	'2728':'Erfolgsbeurteilung hinsichtlich Indikationsstellung',
	'2729':'Erfolgsbeurteilung hinsichtlich Histologie',
	'2730':'Revisionseingriff',
	'2731':'Station�re Aufnahme',
	'2732':'Angaben zu implantierten Materialien',
	'2740':'Art der Operation',
	'2741':'Dauer der Operation',
	'2742':'Operierte Seite',
	'2743':'Art der An�sthesie',
	'2744':'Art der An�sthesie gem�ss Klassifikation Strukturvertrag',
	'2750':'Operateur hat Facharztstatus',
	'2751':'Anzahl �rztl. Assistenten bei OP',
	'2752':'(Ein) OP-Assistent hat Facharztstatus',
	'2753':'Anzahl nicht�rzticher Assistenten bei OP',
	'2760':'Art der An�sthesie',
	'2761':'An�sthesie erbracht',
	'2762':'Dauer der An�sthesie',
	'2770':'Blutung',
	'2771':'Narkosezwischenfall',
	'2772':'Pneumonie',
	'2773':'Wundinfektion',
	'2774':'Gef�ss- oder Nervenl�sion',
	'2775':'Lagerungssch�den',
	'2776':'Venenthrombose',
	'2780':'Revisionseingriff erforderlich',
	'2781':'Histologie',
	'2782':'Station�re Weiterbehandlung erforderlich',
	#Patientennummer/Patientenkennung
	'3000':'Patientennummer',
	#Namenszusatz/Vorsatzwort des Patienten
	'3100':'Namenszusatz',
	#Name des Patienten
	'3101':'Name des Patienten',
	#Vorname des Patienten
	'3102':'Vorname des Patienten',
	#Geburstdatum des Patienten
	'3103':'Geburstdatum des Patienten', 
	#Titel des Patienten 
	'3104':'Titel des Patienten',
	#Versichertennummer des Patienten
	'3105':'Versichertennummer des Patienten',
	#Wohnort des Patienten
	'3106':'Wohnort des Patienten',
	#Strasse des Patienten
	'3107':'Strasse des Patienten',
	#Versichertenart M/F/R
	'3108':'Versichertenart MFR',
	#Geschlecht des Patienten
	'3110':'Geschlecht des Patienten',
	'3111':'Geburtsjahr des Patienten',
	'3112':'PLZ des Patienten',
	'3113':'Wohnort des Patienten',
	'3114':'Wohnsitzl�ndercode',
	'3116':'KV-Bereich',
	#Arbeitgeber -- nur bei header 0191 --
	'3150':'Arbeitgeber',
	#Bezeichnung des Unfallversicherungstr�gers -- nur bei header 0191 --
	'3152':'Unfallversicherungstr�ger',
	#Name des Hauptversicherten
	'3200':'Namenszusatz/Vorsatzwort des Hauptversicherten',
	'3201':'Name des Hauptversicherten',
	#Vorname des Hauptversicherten
	'3202':'Vorname des Hauptversicherten',
	#Geburtsdatum des Hauptversicherten
	'3203':'Geburtsdatum des Hauptversicherten',
	#Wohnort des Hauptversicherten
	'3204':'Wohnort des Hauptversicherten',
	#Strasse des Hauptversicherten
	'3205':'Strasse des Hauptversicherten',
	'3206':'Titel des Hauptversicherten',
	'3207':'PLZ des Hauptversicherten',
	#Telefonnummer des Verletzten -- nur bei header 0191 -- 
	'3208':'Telefonnummer des Verletzten',
	'3209':'Wohnort des Hauptversicherten',
	#Geschlecht des Hauptversicherten -- nur bei header 0190 --
	'3210':'Geschlecht des Hauptversicherten',
	#R�ntgennummer -- nur bei header 6100 --
	'3601':'R�ntgennummer',
	#Archivnummer -- nur bei header 6100 --
	 '3602':'Archivnummer',
	#BG-Nummer -- nur bei header 6100 --
	'3603':'BG-Nummer',
	#Datum Patient seit -- nur bei header 6100 --
	'3610':'Datum Patient seit',
	#Datum Versichertenbeginn bei Kassenwechsel -- nur bei header 6100 --
	 '3612':'Datum Versichertenbeginn bei Wechsel',
	#Beruf des Patienten -- nur bei header 6100 --
	'3620':'Beruf des Patienten',
	#Gr�sse des Patienten -- nur bei header 6200 --
	'3622':'Gr�sse des Patienten',
	#Gewicht des Patienten -- nur bei header 6200 --
	'3623':'Gewicht des Patienten',
	#Arbeitgeber des Patienten -- nur bei header 6100 --
	'3625':'Arbeitgeber des Patienten',
	#Telefonnummer des Patienten -- nur bei header 6100 --
	'3626':'Telefonnummer des Patienten',
	#Nationalit�t des Patienten -- nur bei header 6100 --
	'3627':'Nationalit�t des Patienten',
	#Muttersprache Patient -- nur bei header 6100 --
	'3628':'Muttersprache des Patienten',
	#Arztnummer des Hausarztes -- nur bei header 6100 --
	'3630':'Arztnummer des Hausarztes',
	#Entfernung Wohnung/Praxis-- nur bei header 6100 --
	'3631':'Entfernung Wohnung-Praxis',
	#interne Zuordnung Arzt bei Gemeinschaftspraxen -- nur bei header 6100 --
	'3635':'interne Zuordnung Arzt bei GP',
	#Rezeptkennung -- nur bei header 6100 --
	'3637':'Rezeptkennung',
	#Dauerdiagnosen ab Datum -- nur bei header 6100 --
	'3649':'Dauerdiagnosen ab Datum',
	#Dauerdiagnosen  -- nur bei header 6100 --
	'3650':'Dauerdiagnosen',
	#Dauermedikamente ab Datum -- nur bei header 6100 --
	'3651':'Dauermedikamente ab Datum',
	#Dauermedikamente -- nur bei header 6100 --
	'3652':'Dauermedikamente',
	#Risikofaktoren -- nur bei header 6100 --
	'3654':'Risikofaktoren',
	#Allergien -- nur bei header 6100 --
	'3656':'Allergien',
	#Unf�lle -- nur bei header 6100 --
	'3658':'Unf�lle',
	#Operationen -- nur bei header 6100 --
	'3660':'Operationen',
	#Anamnese -- nur bei header 6100 --
	'3662':'Anamnese',
	#Anzahl Geburten -- nur bei header 6100 --
	'3664':'Anzahl Geburten',
	#Anzahl Kinder -- nur bei header 6100 --
	'3666':'Anzahl Kinder',
	#Anzahl Schwangerschaften -- nur bei header 6100 --
	'3668':'Anzahl Schwangerschaften',
	#Dauertherapie -- nur bei header 6100 --
	'3670':'Dauertherapie',
	#Kontrolltermine -- nur bei header 6100 --
	'3672':'Kontrolltermine',
	'3673':'Dauerdiagnose (ICD-Code)',
	'3674':'Diagnosensicherheit Dauerdiagnose',
	'3675':'Seitenlokalisation Dauerdiagnose',
	#Name erste freie Kategorie -- nur bei header 6100 --
	'3700':'Name erste freie Kategorie',
	#Inhalt erste freie Kategorie -- nur bei header 6100 --
	'3701':'Inhalt erste freie Kategorie',
	#3704-3719 freie Kategorien
	#Quartal
	'4101':'Quartal',
	#Ausstellungsdatum
	'4102':'Ausstellungsdatum',
	#G�ltigkeitsdatum
	'4103':'G�ltigkeitsdatum',
	#VKNR- Vertragskassenarztnummer
	'4104':'Abrechnungs-VKNR',
	#Gesch�ftsstelle
	'4105':'Gesch�ftsstelle',
	#Kostentr�gergruppe
	'4106':'Kostentr�ger-Abrechnungsbereich(KTAB)',
	#Abrechnungsart
	'4107':'Abrechnungsart',
	#letzter Einlesetag der VK im Quartal TTMMJJ
	'4109':'letzter Einlesetag der KVK im Quartal',
	#Bis-Datum der G�ltigkeit MMJJ
	'4110':'Bis-Datum der G�ltigigkeit',
	#Krankenkassennummer
	'4111':'Krankenkassennummer (IK)',
	#Versichertenstatus VK
	'4112':'Versichertenstatus VK',
	##'4113':'Statuserg�nzung/DMP-Kennzeichnung',
	'4113':'Ost/West-Status VK',
	#Geb�hrenordnung
	'4121':'Geb�hrenordnung',
	#Abrechnungsgebiet
	'4122':'Abrechnungsgebiet',
	'4123':'Personenkreis/Untersuchungskategorie',
	'4124':'SKT-Zusatzangaben',
	'4125':'G�ltigkeitszeitraum von ... bis ...',
	#Ursache des Leidens 
	'4201':'Ursache des Leidens',
	'4202':'Unfall, Unfallfolgen',
	#mutmasslicher Tag der Entbindung
	'4206':'mutmasslicher Tag der Entbindung',
	#Diagnose/Verdacht -- nur bei header 0102 --
	'4207':'Diagnose/Verdacht',
	#erl�uternder Text zur �berweisung -- nur bei header 0102 --
	'4209':'erl�uternder Text zur �berweisung',
	#Ankreuzfeld LSR  -- nur bei header 0102 --
	'4210':'Ankreuzfeld LSR',
	#Ankreuzfeld HAH  -- nur bei header 0102 --
	'4211':'Ankreuzfeld HAH',
	#Ankreuzfeld ABO.RH  -- nur bei header 0102 --
	'4212':'Ankreuzfeld ABO.RH',
	#Ankreuzfeld AK  -- nur bei header 0102 --
	'4213':'Ankreuzfeld AK',
	#�berweisung von Arztnummer  -- nur bei header 0102 --
	'4217':'Vertragsarzt-Nr. des Erstveranlassers',
	'4218':'�berweisung von Arztnummer',
	#�berweisung an  -- nur bei header 0102 --
	'4219':'�berweisung von anderen �rzten',
	'4220':'�berweisung an',
	'4221':'Kurativ / Pr�ventiv / Sonstige Hilfen / bei beleg�rztlicher Behandlung',
	'4222':'Kennziffer OI./O.II.',
	'4223':'Kennziffer OIII.',
	#station�re Behandlung von bis -- nur bei header 0103/0190 --
	'4233':'station�re Behandlung von... bis...',
	'4234':'anerkannte Psychotherapie',
	'4235':'Datum des Anerkennungsbescheides',
	#Klasse bei station�rer Behandlung -- nur bei header 0190 --
	'4236':'Klasse bei Behandlung',
	#Krankenhausname -- nur bei header 0190 --
	'4237':'Krankenhausname',
	#Krankenhausaufenthalt -- nur bei header 0190 --
	'4238':'Krankenhausaufenthalt',
	#Scheinuntergruppe
	'4239':'Scheinuntergruppe',
	#weiterbehandelnder Arzt -- nur bei header 0104 --
	'4243':'weiterbehandelnder Arzt',
	'4261':'Kurart',
	'4262':'Durchf�hrung als Kompaktkur',
	'4263':'genehmigte Kurdauer in Wochen',
	'4264':'Anreisetag',
	'4265':'Abreisetag',
	'4266':'Kurabbruch am',
	'4267':'Bewilligte Kurverl�ngerung in Wochen',
	'4268':'Bewilligungsdatum Kurverl�ngerung',
	'4269':'Verhaltenspr�ventive Massnahmen angeregt',
	'4270':'Verhaltenspr�ventive Massnahmen durchgef�hrt',
	'4271':'Kompaktkur nicht m�glich',
	#Unfalltag -- nur bei header 0191 --
	'4500':'Unfalltag',
	#Uhrzeit des Unfalls -- nur bei header 0191 --
	'4501':'Uhrzeit des Unfalls',
	#Eingetroffen in Praxis am -- nur bei header 0191 --
	'4502':'Eingetroffen in Praxis am',
	#Uhrzeit des Eintreffens -- nur bei header 0191 --
	'4503':'Uhrzeit des Eintreffens',
	#Beginn Arbeitszeit -- nur bei header 0191 --
	'4504':'Beginn der Arbeitszeit',
	#Unfallort -- nur bei header 0191 --
	'4505':'Unfallort',
	#Besch�ftigung als -- nur bei header 0191 --
	'4506':'Besch�ftigung als',
	#Besch�ftigung seit -- nur bei header 0191 --
	'4507':'Besch�ftigung seit',
	#Staatsangeh�rigkeit -- nur bei header 0191 --
	'4508':'Staatsangeh�rigkeit',
	#Unfallbetrieb -- nur bei header 0191 --
	'4509':'Unfallbetrieb',
	#Unfallhergang -- nur bei header 0191 --
	'4510':'Unfallhergang',
	#Verhalten des Verletzten nach dem Unfall -- nur bei header 0191 --
	'4512':'Verhalten des Verletzten nach dem Unfall',
	#Erstmalige Behandlung -- nur bei header 0191 --
	'4513':'Erstmalige_Behandlung',
	#Behandlung durch -- nur bei header 0191 --
	'4514':'Behandlung_durch',
	#Art dieser ersten �rztlichen Behandlung -- nur bei header 0191 --
	'4515':'Art dieser ersten �rztlichen Behandlung',
	#Alkoholeinfluss -- nur bei header 0191 --
	'4520':'Alkoholeinfluss',
	#Anzeichen eines Alkoholeinflusses -- nur bei header 0191 --
	'4521':'Anzeichen eines Alkoholeinflusses',
	#Blutentnahme -- nur bei header 0191 --
	'4522':'Blutentnahme',
	#Befund -- nur bei header 0191 --
	'4530':'Befund',
	#R�ntgenergebniss -- nur bei header 0191 --
	'4540':'R�ntgenergebniss',
	#Art etwaiger Erstversorgung durch D-Arzt -- nur bei header 0191 --
	'4550':'Art etwaiger Versorgung durch D-Arzt',
	#krankhafte Ver�nderungen unabh�ngig vom Unfall -- nur bei header 0191 --
	'4551':'krankhafte Ver�ndrungen unabh�ngig vom Unfall',
	#Bedenken gegen Angaben -- nur bei header 0191 --
	'4552':'Bedenken gegen Angaben',
	#Art der Bedenken bei allegemeinen Bedenken-- nur bei header 0191 --
	'4553':'Art der Bedenken gegen Angaben',
	#Bedenken gegen Vorliegen eines Arbeitsunfalls -- nur bei header 0191 --
	'4554':'Bedenken gegen Arbeistunfall',
	#Art der Bedenken gegen Arbeitsunfall -- nur bei header 0191 --
	'4555':'Art_Bedenken gegen Arbeitsunfall',
	#arbeitsf�hig -- nur bei header 0191 --
	'4560':'arbeitsf�hig',
	#wieder arbeitsf�hig ab -- nur bei header 0191 --
	'4561':'wieder arbeitsf�hig ab',
	#AU-Bescheinigung ausgestellt -- nur bei header 0191 --
	'4562':'AU ausgestellt',
	#besondere Heilbehandlung erforderlich -- nur bei header 0191 --
	'4570':'besondere Heilbehandlung erforderlich',
	#besondere Heilbehandlung durch -- nur bei header 0191 --
	'4571':'bes_Heilbehandlung_durch',
	#Anschrift des behandelnden Arztes -- nur bei header 0191 --
	'4572':'Anschrift behandelnder Arzt',
	#AU ab -- nur bei header 0191 --
	'4573':'AU ab',
	#voraussichtliche Dauer der AU -- nur bei header 0191 --
	'4574':'voraussichliche Dauer der AU',
	#Rechnungsart -- nur bei header 0190 --
	'4580':'Rechnungsart',
	#allgemeine Heilbehandlung durch -- nur bei header 0191 --
	'4581':'allgemeine Heilbehandlung durch',
	#AU �ber 3 Tage -- nur bei header 0191 --
	'4582':'AU �ber 3 Tage',
	#AU bescheinigt als -- nur bei header 0191 --
	'4583':'AU bescheinigt als',
	#Nachschau erforderlich -- nur bei header 0191 --
	'4584':'Nachschau erforderlich',
	#Rechnungsnummer -- nur bei header 0190 --
	'4601':'Rechnungsnummer',
	#Anschrift des Rechnungsadressaten (Empf�nger) -- nur bei header 0190 --
	'4602':'Rechnungsanschrift',
	#�berweisender Arzt -- nur bei header 0190 --
	'4603':'�berweisender Arzt',
	#Rechnungsdatum -- nur bei header 0190 --
	'4604':'Rechnungsdatum',
	#Endsumme -- nur bei header 0190 --
	'4605':'Endsumme',
	#Abdingungserkl�rung vorhanden -- nur bei header 0190 --
	'4608':'Abdingungserkl�rung vorhanden',
	#Unterkonto Arzt -- nur bei header 0190 --
	'4611':'Unterkonto Arzt',
	#Anlage erforderlich -- nur bei header 0190 --
	'4613':'Anlage erforderlich',
	#Kopfzeile -- nur bei header 0190 --
	'4615':'Kopfzeile',
	#Fusszeile -- nur bei header 0190 --
	'4617': 'Fu�zeile',
	'5000': 'Leistungstag',
	'5001': 'GNR',
	#Art der Untersuchung
	'5002':'Art der Untersuchung',
	#Empf�nger des Briefes
	'5003':'Empf�nger des Briefes',
	#Kilometer (nur bei GOA)
	'5004':'Kilometer',
	#Multiplikator
	'5005':'Multiplikator',
	#Um-Uhrzeit
	'5006':'Um-Uhrzeit',
	#Bestellzeit-Ausf�hrungszeit
	'5007':'Bestellzeit-Ausf�hrungszeit',
	#DKM=Doppelkilometer
	'5008':'Doppel-KM',
	#freier Begr�ndungstext
	'5009':'freier Begr�ndungstext',
	#Medikament als Begr�ndung -- nur bei header 0190 --
	'5010':'Medikament als Begr�ndung',
	#Sachkosten-Bezeichnung
	'5011':'Sachkosten-Bezeichnung',
	#Sachkosten/Materialkosten (Dpf)
	'5012':'Sachkosten/Materialkosten in Cent',
	#Prozent der Leistung
	'5013':'Prozent der Leistung',
	#Organ
	'5015':'Organ',
	'5016':'Name des Arztes',
	#Besuchsort bei Hausbesuchen
	'5017':'Besuchsort bei Hausbesuchen',
	#Zone bei Besuchen
	'5018':'Zone bei Besuchen',
	'5019':'Erbringungsort,Standort des Ger�tes',
	'5023':'GO-Nummern-Zusatz',
	'5024':'GNR-Zusatzkennzeichen f�r poststation�r erbrachte Leistungen',
	#Beschreibung der GNR -- nur bei header 0190 --
	'5060':'Beschreibung der GNR',
	#Geb�hr -- nur bei header 0190 --
	'5061':'Geb�hr',
	#Faktor -- nur bei header 0190 --
	'5062':'Faktor',
	#Betrag -- nur bei header 0190 --
	'5063':'Betrag',
	#Punktwert -- nur bei header 0191 --
	'5065':'Punktwert',
	#Honorarbezeichnung -- nur bei header 0190 --
	'5090':'Honorarbezeichnung',
	#Gutachten-Bezeichnung -- nur bei header 0190 --
	'5091':'Gutachtenbezeichnung',
	#Abrechnungsdiagnosen -- nur bei header 0102 --
	'6000':'Abrechnungsdiagnosen',
	#ICD-Schl�ssel
	'6001':'ICD-Schl�ssel',
	'6003':'Diagnosensicherheit',
	'6004':'Seitenlokalisation',
	'6005':'Histologischer Befund bei Malignit�t',
	'6006':'Diagnosenerl�uterung',
	#Tag der Speicherung von Behandlungsdaten -- nur bei header 6200 --
	'6200':'gespeichert am',
	#aktuelle Diagnose -- nur bei header 6200 --
	'6205':'aktuelle Diagnose',
	#Medikament verordnet auf Rezept -- nur bei header 6200 --
	'6210':'Medikament verordnet auf Kassenrezept',
	#ausserhalb Rezept verordnetes Medikament -- nur bei header 6200 --
	'6211':'Medikament verordnet auf Privatrezept',
	#�rztenummer -- nur bei header 6200 --
	 ##'6215':'�rztenummer',
	'6215':'�rztemuster',
	#Befund -- nur bei header 6200 --
	'6220':'Befund',
	#Fremdbefund -- nur bei header 6200 --
	'6221':'Fremdbefund',
	#Laborbefund -- nur bei header 6200 --
	'6222':'Laborbefund',
	#R�ntgenbefund -- nur bei header 6200 --
	'6225':'R�ntgenbefund',
	#Blutdruck -- nur bei header 6200 --
	'6230':'Blutdruck',
	#Symptome -- nur bei header 6200 --
	'6240':'Symptome',
	#Therapie -- nur bei header 6200 --
	'6260':'Therapie',
	#physikalische Therapie -- nur bei header 6200 --
	'6265':'physikalische Therapie',
	#�berweisung Inhalt -- nur bei header 6200 --
	'6280':'�berweisung Inhalt',
	#AU-Dauer -- nur bei header 6200 --
	'6285':'AU Dauer (von - bis)',
	#AU-wegen -- nur bei header 6200 --
	'6286':'AU wegen',
	'6287':'AU wegen (ICD-Code)',
	'6288':'Diagnosesicherheit AU wegen',
	'6289':'Seitenlokalisation AU wegen',
	#Krankenhauseinweisung,Krankenhaus -- nur bei header 6200 --
	'6290':'Krankenhauseinweisung,Krankenhaus',
	#Krankenhauseinweisung -- nur bei header 6200 --
	'6291':'Krankenhauseinweisung',
	'6292':'Krankenhauseinweisung wegen (ICD-Code)',
	'6293':'Diagnosesicherheit Krankenhauseinweisung wegen',
	'6294':'Seitenlokalisation Krankenhauseinweisung wegen',
	#Bescheiningung -- nur bei header 6200 --
	'6300':'Bescheinigung',
	#Inhalt der Bescheinigung -- nur bei header 6200 --
	'6301':'Inhalt der Bescheinigung',
	#Attest -- nur bei header 6200 --
	'6306':'Attest',
	#Inhalt des Attestes -- nur bei header 6200 --
	'6307':'Inhalt des Attestes',
	#Name des Briefempf�ngers -- nur bei header 6200 --
	'6310':'Name des Briefempf�ngers',
	#Anrede -- nur bei header 6200 --
	'6311':'Anrede',
	#Strasse -- nur bei header 6200 --
	'6312':'Strasse',
	#PLZ -- nur bei header 6200 --
	'6313':'PLZ',
	#Wohnort -- nur bei header 6200 --
	'6314':'Wohnort',
	#Schlussatz -- nur bei header 6200 --
	'6315':'Schlusssatz',
	#Telefonnummer -- nur bei header 6200 --
	'6316':'Telefonnummer',
	#Telefax -- nur bei header 6200 --
	'6317':'Telefax',
	#Arztnummer/Arztident -- nur bei header 6200 --
	'6319':'Arztnummer/Arztident',
	#Briefinhalt -- nur bei header 6200 --
	'6320':'Briefinhalt',
	#Bild-Archivierungsnummer -- nur bei header 6200 --
	'6325':'Bild-Archivierungsnummer',
	#Graphikformat -- nur bei header 6200 --
	'6326':'Graphikformat',
	#Bildinhalt -- nur bei header 6200 --
	'6327':'Bildinhalt',
	#Name der ersten freien Kategorie -- nur bei header 6200 --
	'6330':'Name der ersten freien Kategorie',
	#Inhalt der ersten freien Kategorie -- nur bei header 6200 --
	'6331':'Inhalt der ersten freien Kategorie',

	#--------------------------------------------------------
	# more free categories
	# Satzidentifikation
	'8000':'Satzidentifikation >>===============',
	# Satzl�nge
	'8100': 'Satzl�nge',
	# LDT
	'8310': 'Anforderungsnummer', 
	# Befundstatus -- nur bei header 6200/8202 --
	'8401': 'Befundstatus',
	#Ger�te- bzw. Verfahrensspezifisches Kennfeld -- nur bei header 6200 --
	'8402':'Ger�tespezifisches Kennfeld',
	# LDT
	'8403': 'Geb�hrenordnung',
	# LDT
	'8404': 'Kosten in Doppelpfennigen',
	'8406': 'Kosten in Cent',
	#Test-Ident -- nur bei header 6200 --
	'8410':'Test-Ident',
	#Testbezeichnung -- nur bei header 6200 --
	'8411':'Testbezeichnung',
	#Teststatus -- nur bei header 6200 --
	'8418':'Teststatus',
	#Ergebnis-Wert -- nur bei header 6200 --
	'8420':'Ergebnis Wert',
	#Einheit -- nur bei header 6200 --
	'8421':'Einheit',
	#Grenzwert Indikator -- nur bei header 6200 --
	'8422':'Grenzwert Indikator',
	#Probematerial-Nummer -- nur bei header 6200 --
	'8429':'Probenmaterial-Nummer',
	#Probenmaterial-Bezeichnung -- nur bei header 6200 --
	'8430':'Probenmaterial-Bezeichnung',
	#Material-Spezifikation -- nur bei header 6200 --
	'8431':'Material_Spezifikation',
	#Abnahme-Datum -- nur bei header 6200 --
	'8432':'Abnahme-Datum',
	#Abnahme-Zeit -- nur bei header 6200 --
	'8433':'Abnahme-Zeit',
	#Keim-Ident -- nur bei header 6200 --
	'8440':'Keim-Ident',
	#Keim-Bezeichnung -- nur bei header 6200 --
	'8441':'Keim-Bezeichnung',
	#Keim-Nummer -- nur bei header 6200 --
	'8442':'Keim-Nummer',
	#Resistenz-Methode -- nur bei header 6200 --
	'8443':'Resistenz-Methode',
	#Wirkstoff-Ident -- nur bei header 6200 --
	'8444':'Wirkstoff-Ident',
	#Wirkstoff-Generic-Nummmer -- nur bei header 6200 --
	'8445':'Wirkstoff-Generic-Nummer',
	#MHK/Breakpoint-Wert -- nur bei header 6200 --
	'8446':'MHK',
	#Resistenz-Interpretation -- nur bei header 6200 --
	'8447':'Resistenz-Interpretation',
	#Normalwert-Text -- nur bei header 6200 --
	'8460':'Normalwert-Text',
	#Anmerkung -- nur bei header 6200 --
	'8470':'Anmerkung',
	#Ergebnis-Text -- nur bei header 6200 --
	'8480':'Ergebnis-Text',
	#Abschluss-Zeile -- nur bei header 6200 --
	'8490':'Abschluss-Zeile',
	# LDT
	'8609': 'Geb�hrenordung',
	#Signatur -- nur bei header 6200 --
	'8990':'Signatur',
	'9100':'Arztnummer des Absenders',
	'9102':'Empf�nger',
	'9103':'Erstellungsdatum',
	'9105':'Lfd.Nr. Datentr�ger im Paket',	
	'9106':'verwendeter Zeichensatz',
	'9115':'Erstellungsdatum ADT-Datenpaket',
	'9116':'Erstellungsdatum KADT-Datenpaket',
	'9117':'Erstellungsdatum AODT-Datenpaket',
	'9118':'Erstellungsdatum STDT-Datenpaket',
	'9132':'enthaltene Datenpakete dieser Datei',
	'9202':'Gesamtl�nge Datenpaket',
	#number of media for this data package     
	'9203':'Anzahl Datentr�ger im Paket',
	'9204':'Abrechnungsquartal',
	#ADT-version
	'9210':'Version ADT-Satzbeschreibung',
	'9212':'Version der Satzbeschreibung',
	'9213':'Version BDT',
	'9233':'GO-Stammdatei-Version',
	#way data is archived
	'9600':'Archivierungsart',
	#storage timeframe
	'9601':'Zeitraum der Speicherung',
	#time of transfer start
	'9602':'Beginn der �bertragung',
	'9901':'Systeminterner Parameter'
}
#--------------------------------------------------------------
# 8000
xdt_packet_type_map = {
	'0020': "========<< Anfang Datentr�ger >>========",
	'0021': "========<< Ende Datentr�ger >>========",
	'0022': "========<< Anfang Datenpaket >>========",
	'0023': "========<< Ende Datenpaket >>========",
	'0010': "========<< Praxisdaten >>========",
	'0101': "========<< Fall: Prim�rarzt >>========",
	'0102': "========<< Fall: �berweisung >>========",
	'0103': "========<< Fall: Belegarzt  >>========",
	'0104': "========<< Fall: Notfall/Dienst/Vertretung >>========",
	'0109': "========<< Kur�rztliche Abrechnung >>========",
	'0190': "========<< Fall: Privat >>========",
	'0191': "========<< Fall: BG >>========",
	'0199': "========<< Fall: unstrukturiert >>========",
	'6100': "========<< Patientenstamm >>========",
	'6200': "========<< Behandlungsdaten >>========",
	'adt0': "========<< ADT-Datenpaket-Header >>========",
	'adt9': "========<< ADT-Datenpaket-Abschluss >>========",
	'con0': "========<< Container-Header >>========",
	'con9': "========<< Container-Abschluss >>========",
	'prax': "========<< Praxisdaten >>========",
	'kad0': "========<< KADT-Datenpaket-Header >>========",
	'kad9': "========<< KADT-Datenpaket-Abschlu� >>========",
	'std0': "========<< STDT-Datenpaket-Header >>========",
	'std9': "========<< STDT-Datenpaket-Abschlu� >>========",
	'st13': "========<< Statistiksatz >>========"
}
#--------------------------------------------------------------
# XDT:
# dob: ddmmyyyy
# gender: 1 - male, 2 - female

# patient record fields
name_xdtID_map = {
	'last name': '3101',
	'first name': '3102',
	'date of birth': '3103',
	'gender': '3110'
}
#    'city': '3106',\
#    'street': '3107',\

# sort of GnuMed compatible
map_gender_xdt2gm = {
	'1': 'm',
	'2': 'f',
	'm': 'm',
	'f': 'f'
}

# LDT "gender", 8407
map_8407_2str = {
	'0': _('unknown gender'),
	'1': _('male'),
	'2': _('female'),
	'3': _('child'),
	'4': _('boy'),
	'5': _('girl'),
	'6': _('animal')
}

# xDT character code mapping : 9106
xdt_character_code_map = {
	'1':'7-bit-Code ASCII',
	'2':'8-bit-Code ASCII',
	##'2':'IBM-Code',
	'3':'ISO 8859-1 Code'
}
# Archivierungsart : 9600
xdt_Archivierungsart_map = {
	'1':'Speicherung Gesamtbestand',
	'2':'Speicherung beliebiger Zeitraum',
	'3':'Speicherung eines Quartals'
}
# Praxistyp : 0202
xdt_Praxistyp_map = {
	'1':'Einzelpraxis',
	'2':'Gemeinschaftspraxis',
	'3':'Fach�bergreifende GP',
	'4':'Praxisgemeinschaft',
	'5':'Fach�bergreifende GP ohne Kennzeichen Leistung',
	'6':'erm�chtigter Arzt',
	'7':'Krankenhaus oder �rztlich geleitete Einrichtung'
}
# Versichertenart MFR : 3108
xdt_Versichertenart_map = {
	'1':'Mitglied',
	'3':'Familienversicherter',
	'5':'Rentner',
}
# Kostentr�geruntergruppe : 4106
xdt_Kostentraegeruntergruppe_map = {
	'00':'default',
	'01':'SVA(Sozialversicherungsabkommen)',
	'02':'BVG(Bundesversorgungsgesetz)',
	'03':'BEG(Bundesentsch�digungsgesetz)',
	'04':'Grenzg�nger',
	'05':'Rheinschiffer',
	'06':'SHT(Sozialhilfetr�ger, ohne Asylstellen)',
	'07':'BVFG(Bundesvertriebenengesetz)',
	'08':'Asylstellen(AS)',
	'09':'Schwangerschaftsabbr�che'
}
# Abrechnungsart : 4107
xdt_Abrechnungsart_map = {
	'1':'PKA(Prim�rkassen)',
	'2':'EKK(Ersatzkassen)',
	'3':'SKT(Sonstige Kostentr�ger)',
}
# Ost/West-Status VK : 4113
xdt_Ost_West_Status_map = {
	'1':'West',
	'6':'BVG',
	'7':'SVA',
	'8':'SVA',
	'9':'Ost',
	'M':'eingeschriebene Versicherte in Disease-Management-Programmen f�r Diabetes mellitus Typ2 - RK West',
	'X':'eingeschriebene Versicherte in Disease-Management-Programmen f�r Diabetes mellitus Typ2 - RK Ost',
	'A':'eingeschriebene Versicherte in Disease-Management-Programmen f�r Brustkrebs - RK West',
	'C':'eingeschriebene Versicherte in Disease-Management-Programmen f�r Brustkrebs - RK Ost',
}
# Geb�hrenordnung : 4121
xdt_Gebuehrenordnung_map = {
	'1':'BMA',
	'2':'E-GO',
	'3':'GOA'
}
# Abrechnungsgebiet : 4122
xdt_Abrechnungsgebiet_map = {
	'00':'kein besonderes Abrechnungsgebiet (Defaultwert)',
	'01':'Dialyse-Arztkosten',
	'02':'Dialyse-Sachkosten',
	'03':'Methadon-Substitutionsbehandlung',
	'04':'Grosse Psychotherapie',
	##'04':'pers�nlich erbrachte Notfallleistungen durch erm�chtigte Krankenhaus�rzte',
	'05':'Verhaltenstherapie',
	##'05':'sonstige Notfallleistungen durch erm�chtigte Krankenhaus�rzte',
	'06':'Fremde Zytologie',
	'07':'Diabestesabrechnung',
	'08':'Umweltmedizin',
	'09':'Rheuma',
	'10':'Hirnleistungsst�rungen',
	'11':'Kodex-Anhangsarzt',
	'12':'Kodex-Arzt',
	'13':'Kodex-Listenarzt',
	'14':'Ambulantes Operieren'
}
# Ursache des Leidens : 4201
xdt_Ursache_des_Leidens_map = {
	'2':'Unfall, Unfallfolgen',
	'3':'Versorgungsleiden'
}
# Ankreuzfeld LSR, HAH, ABO.RH, AK
xdt_Ankreuzfeld_map = {
	'1':'angekreuzt'
}
# Scheinuntergruppe
xdt_Scheinuntergruppe_map = {
	'00':'Ambulante Behandlung (Defaultwert)',
	'20':'Selbstaustellung',
	'21':'Zielauftrag (Defaultwert bei Einsendepraxen)',
	'22':'Rahmenauftrag',
	'23':'Konsillaruntersuchung',
	'24':'Mit/Weiterbehandlung (Defaultwert ausser bei Einsendepraxen)',
	'25':'�berweisung aus anderen Gr�nden',
	'26':'Stat. Mitbehandlung, Verg�tung nach amb. Grunds�tzen',
	'27':'�berweisungs-/Abrechnungssschein f�r Laboratoriumsuntersuchungen als Auftragsleistung',
	'30':'Beleg�rztliche Behandlung (Default bei SA 0103)',
	'31':'Beleg�rztliche Mitbehandlung',
	'32':'Urlaubs-/bzw. Krankheitsvertretung bei beleg�rztlicher Behandlung',
	'41':'�rztlicher Notfalldienst',
	'42':'Urlaubs-bzw. Krankheitsvertretung',
	'43':'Notfall',
	'44':'Notfalldienst bei Taxi',
	'45':'Notarzt-/Rettungswagen (Rettungsdienst)',
	'46':'Zentraler Notfalldienst',
	'90':'default bei SA 0190',
	'91':'Konsillaruntersuchung',
	'92':'stat. Mitbehandlung Verg�tung nach stat. Grunds�tzen',
	'93':'stat. Mitbehandlung Verg�tung nach ambul. Grunds�tzen',
	'94':'beleg�rztliche Behandlung im Krankenhaus'
}
# Gesetzlicher Abzug zur station�ren Behandlung gem�ss Paragraph 6a GOA
xdt_gesetzlicher_Abzug_map = {
	'1':'nein',
	'2':'ja'
}
# Klasse bei station�rer Behandlung
xdt_Klasse_stationaere_Behandlung_map = {
	'1':'Einbettzimmer',
	'2':'Zweibettzimmer',
	'3':'Mehrbettzimmmer'
}
# Rechnungsart
xdt_Rechnungsart_map = {
	'01':'Privat',
	'20':'KVB',
	'21':'Bahn-Unfall',
	'30':'Post',
	'31':'Post-Unfall',
	'40':'Allgemeines Heilverfahren',
	'41':'Berufsgenossenschaft Heilverfahren',
	'50':'Bundesknappschaft',
	'70':'Justizvollzugsanstalt',
	'71':'Jugendarbeitsschutz',
	'72':'Landesversicherungsanstalt',
	'73':'Bundesversicherungsanstalt f�r Angestellte',
	'74':'Sozialamt',
	'75':'Sozialgericht',
	'80':'Studenten-Deutsche',
	'81':'Studenten-Ausl�nder'
}
# Abdingungserkl�rung vorhanden
xdt_Abdingungserklaerung_map = {
	'1':'nein',
	'2':'ja'
}
# Anlage erforderlich
xdt_Anlage_erforderlich_map = {
	'1':'nein',
	'2':'ja'
}
#Alkoholeinfluss
xdt_Alkoholeinfluss_map = {
	'1':'nein',
	'2':'ja'
}
# Blutentnahme
xdt_Blutentnahme_map = {
	'1':'nein',
	'2':'ja'
}
# Bedenken gegen das Vorliegen eines Arbeitsunfalls
xdt_Arbeitsunfall_map = {
	'1':'nein',
	'2':'ja'
}
# arbeitsf�hig
xdt_arbeitsfaehig_map = {
	'1':'angekreuzt'
}
# Besondere Heilbehandlung erforderlich
xdt_Heilbehandlung_erforderlich_map = {
	'1':'ambulant',
	'2':'station�r'
}
# Besondere Heilbehandlung durch
xdt_Besondere_Heilbehandlung_durch_map = {
	'1':'selbst',
	'2':'anderer Durchgangsarzt'
}
# Allgemeine Heilbehandlung durch
xdt_Allgemeine_Heilbehandlung_durch_map = {
	'1':'selbst',
	'2':'anderer Arzt'
}
# AU �ber 3 Tage
xdt_AU_3Tage_map = {
	'1':'angekreuzt'
}
# 8401: Befundstatus
xdt_Befundstatus_map = {
	'E': '(kompletter) Endbefund',
	'T': 'Teilbefund',
	'V': '(kompletter) Vorbefund',
	'A': 'Archivbefund',
	'N': 'Nachforderung'
}

map_Befundstatus_xdt2gm = {
	'E': _('final'),
	'T': _('partial'),
	'V': _('preliminary'),
	'A': _('final'),
	'N': _('final')
}

# Teststatus : 8418
xdt_Teststatus_map = {
	'B': _('already reported'),
	'K': _('corrected result'),
	'F': _('missing, reported later')
}

# Resistenzmethode
xdt_Resistenzmethode_map = {
	'1':'Agardiffusion',
	'2':'Agardilution',
	'3':'MHK-Bestimmung',
	'4':'Breakpoint-Bestimmung'
}
# Resistenz-Interpretation
xdt_Resistenzinterpretation_map = {
	'0':'nicht getestet',
	'1':'sensibel/wirksam',
	'2':'m�ssig sensibel/schwach wirksam',
	'3':'resistent/unwirksam',
	'4':'wirksam in hohen Konzentrationen'
}
# enthaltene Datenpakete in dieser Datei : 9132
kvdt_enthaltene_Datenpakete_map = {
	'1':'ADT-Datenpaket',
	'2':'AODT-Datenpaket(roter Erhebungsbogen)',
	'3':'Kur�rztliches Abrechnungsdatenpaket',
	'4':'AODT-Hessen-Datenpaket (gr�ner Erhebungsbogen der KV Hessen)',
	'5':'STDT-Datenpaket'
}
#KV-Bereich : 3116
kvdt_KV_Bereich_map = {
	'01':'Schleswig-Holstein',
	'02':'Hamburg',
	'03':'Bremen',
	'17':'Niedersachsen',
	'20':'Westfalen-Lippe',
	'38':'Nordrhein',
	'46':'Hessen',
	'47':'Koblenz',
	'48':'Rheinhessen',
	'49':'Pfalz',
	'50':'Trier',
	'55':'Nordbaden',
	'60':'S�dbaden',
	'61':'Nordw�rtemberg',
	'62':'S�dw�rtemberg',
	'71':'Bayern',
	'72':'Berlin',
	'73':'Saarland',
	'74':'KBV',
	'78':'Mecklenburg-Vorpommern',
	'83':'Brandenburg',
	'88':'Sachsen-Anhalt',
	'98':'Sachsen'
}
# Personenkreis / Untersuchungskategorie : 4123
kvdt_Personenkreis_Untersuchungskategorie_map = {
	'01':'Besch�digter',
	'02':'Schwerbesch�digter',
	'03':'Angeh�riger',
	'04':'Hinterbliebener',
	'05':'Pflegeperson',
	'06':'Tauglichkeitsuntersuchung',
	'07':'�rztl. Versorgung',
	'08':'Bewerber',
	'09':'Erstuntersuchung',
	'10':'Nachuntersuchung',
	'11':'Erg�nzungsuntersuchung',
	'12':'Verfolgte'
}
#Unfall, Unfallfolgen : 4202
kvdt_Unfallfolgen_map = {
	'1':'ja'
}
#beleg�rztliche Behandlung : 4221
kvdt_belegaerztliche_Behandlung_map = {
	'1':'kurativ',
	'2':'pr�ventiv',
	'3':'sonstige Hilfen',
	'4':'bei beleg�rztlicher Behandlung'
}
# anerkannte Psychotherapie : 4234
kvdt_anerkannte_Psychotherapie_map = {
	'1':'ja'
}
# Abkl�rung somatischer Ursachen : 4236
kvdt_somatische_Ursachen_map = {
	'1':'ja'
}
# GNR-Zusatzkennzeichen f�r poststation�r erbrachte Leistungen : 5024
kvdt_Zusatzkennzeichen_poststationaere_Leistungen_map = {
	'N':'poststation�re Leistung'	
}
# Diagnosensicherheit : 6003
kvdt_Diagnosensicherheit_map = {
	'V':'Verdacht auf / zum Ausschluss von',
	'Z':'Zustand nach',
	'A':'ausgeschlossen'
}
# Seitenlokalisation : 6004
kvdt_Seitenlokalisation_map = {
	'R':'rechts',
	'L':'Links',
	'B':'beiderseits'
}
# Empf�nger : 9102
kvdt_Empfaenger_map = {
	'01':'Schleswig-Holstein',
	'02':'Hamburg',
	'03':'Bremen',
	'06':'Aurich',
	'07':'Braunschweig',
	'08':'G�ttingen',
	'09':'Hannover',
	'10':'Hildesheim',
	'11':'L�neburg',
	'12':'Oldenburg',
	'13':'Osnabr�ck',
	'14':'Stade',
	'15':'Verden',
	'16':'Wilhelmshaven',
	'18':'Dortmund',
	'19':'M�nster',
	'20':'KV Westfalen Lippe',
	'21':'Aachen',
	'24':'D�sseldorf',
	'25':'Duisburg',
	'27':'K�ln',
	'28':'Linker Niederrhein',
	'31':'Ruhr',
	'37':'Bergisch-Land',
	'39':'Darmstadt',
	'40':'Frankfurt/Main',
	'41':'Giessen',
	'42':'Kassel',
	'43':'Limburg',
	'44':'Marburg',
	'45':'Wiesbaden',
	'47':'Koblenz',
	'48':'Rheinhessen',
	'49':'Pfalz',
	'50':'Trier',
	'52':'Karlsruhe',
	'53':'Mannheim',
	'54':'Pforzheim',
	'56':'Baden-Baden',
	'57':'Freiburg',
	'58':'Konstanz',
	'59':'Offenburg',
	'61':'Nord-W�rtemberg',
	'62':'S�d-W�rtemberg',
	'63':'M�nchen Sadt u. Land',
	'64':'Oberbayern',
	'65':'Oberfranken',
	'66':'Mittelfranken',
	'67':'Unterfranken',
	'68':'Oberpfalz',
	'69':'Niederbayern',
	'70':'Schwaben',
	'72':'Berlin',
	'73':'Saarland',
	'78':'Mecklenburg-Vorpommern',
	'79':'Postdam',
	'80':'Cottbus',
	'81':'Frankfurt/Oder',
	'85':'Magdeburg',
	'86':'Halle',
	'87':'Dessau',
	'89':'Erfurt',
	'90':'Gera',
	'91':'Suhl',
	'94':'Chemnitz',
	'95':'Dresden',
	'96':'Leipzig',
	'99':'Bundesknappschaft'
}
# Facharztstatus Operateur / Assistent : 2750/2752
kvdt_Facharztstatus_map = {
	'0':'nein',
	'1':'ja'	
}
# An�sthesie erbracht : 2761
kvdt_Anaesthesie_erbracht_map = {
	'1':'vom Operateur',
	'2':'vom An�sthesisten'
}
# Blutung : 2770-2776,2720-2726
kvdt_Zwischenfall_map = {
	'0':'nein',
	'1':'intraoperativ',
	'2':'postoperativ bis zum 12. Tag EIGENBEFUND',
	'3':'postoperativ bis zum 12. Tag FREMDBEFUND'
}
# Revisionseingriff erforderlich : 2780
kvdt_Revisionseingriff_erforderlich_map = {
	'1':'ja'
}
# Histologie : 2781,2729
kvdt_Histologie_map = {
	'0':'nein',
	'1':'ja'
}
# station�re Weiterbehandlung erforderlich : 2782
kvdt_stationaere_Weiterbehandlung_map = {
	'1':'unmittelbare Aufnahme zur Weiterbehandlung',
	'2':'station�re Aufnahme zur Weiterbehandlung bis zum 12.Tag'
}
# station�re Aufnahme : 2731
kvdt_stationaere_Aufnahme_map = {
	'0':'nein',
	'1':'unmittelbare Aufnahme zur Weiterbehandlung',
	'2':'station�re Aufnahme zur Weiterbehandlung bis zum 12.Tag'
}
# Indikationsschl�ssel : 2706
kvdt_Indikationsschluessel_map = {
	'0':'keine Angabe'
}
# Komplikation : 2727
kvdt_Komplikation_map = {
	'0':'keine Komplikation'
}
# Erfolgsbeurteilung hinsichtlich Indikationsstellung : 2728
kvdt_Erfolgsbeurteilung_Indikation_map = {
	'1':'gut',
	'2':'mittel',
	'3':'schlecht',
	'4':'nicht beurteilbar'
}
# Revisionseingriff: 2730
kvdt_Revisionseingriff_map = {
	'0':'nein',
	'1':'erforderlich'
}
# Angaben zu implantierten Materialien : 2732
kvdt_Implantat_map = {
	'00':'keine Implantation',
	'01':'Herzschrittmachertyp AAI-R',
	'02':'Herzschrittmachertyp VVI-R',
	'03':'Herzschrittmachertyp DDD-R',
	'04':'Herzschrittmachertyp DVI-R',
	'05':'Herzschrittmachertyp DDI-R',
	'06':'Herzschrittmachertyp VDD-R',
	'09':'sonstiger Herzschrittmachertyp',
	'11':'PMMA-Linse',
	'12':'Silicon-Linse',
	'13':'Acryl-Linse'
}
# Operierte Seite : 2742
kvdt_operierte_Seite_map = {
	'0':'keine Angabe',
	'1':'links',
	'2':'rechts',
	'3':'beidseitig'
}
# Art der An�sthesie gem�� Klassifikation Strukturvertrag : 2744
kvdt_Anaesthesie_Art_map = {
	'1':'Intubationsnarkose',
	'2':'Spinalan�sthesie',
	'3':'Maskennarkose',
	'4':'Stand-By',
	'5':'Plexusan�sthesie',
	'6':'Periduralan�sthesie',
	'7':'intraven�se Region',
	'8':'Lokalan�sthesie',
	'9':'Retrobulb�r-/Peribulb�ran�sthesie'
}
# Kurart : 4261
kvdt_Kurart_map = {
	'1':'Ambulante Vorsorgeleistung zur Krankheitsverh�tung',
	'2':'Ambulante Vorsorgeleistung bei bestehenden Krankheiten',
	'3':'Ambulante Vorsorgeleistung f�r Kinder'
}
# Packungsgr��e bei Kassenrezept und Privatrezept : 0917,0918
kvdt_Packungsgroesse_map = {
	'N1':'Kleine Packung',
	'N2':'Mittlere Packung',
	'N3':'Gro�e Packung',
	'kA':'keine Angabe'
}
# Heilmittel : 0925
#kvdt_Heilmittel_map = {
#	'01':'Massagetherapie',
#	'02':'Bewegungstherapie',
#	'03':'Krankengymnastik',
#	'04':'Elektrotherapie',
#	'06':'Thermotherapie(W�rme- und K�ltetherapie)',
#	'08':'Kohlens�ureb�der',
#	'09':'Inhalalationtherapie',
#	'10':'Traktionsbehandlung',
#	'20':'Stimmtherapie',
#	'25':'Sprechtherapie',
#	'30':'Sprachtherapie',
#	'35':'Sprech- und/oder Sprachtherapie bei Kindern und Jugendlichen',
#	'40':'Besch�ftigungs- und Arbeitstherapie (Ergotherapie)',
#	'90':'Sonstiges',
#}

# Kennzeichnung geb�hrenpflichtig, aut idem, noctu
kvdt_Kennzeichnung_map = {
	'0':'nein',
	'1':'ja'
}
#--------------------------------------------------------------
xdt_map_of_content_maps = {
	'0202': xdt_Praxistyp_map,
	'0917': kvdt_Packungsgroesse_map,
	'0918': kvdt_Packungsgroesse_map,
#	'0925': kvdt_Heilmittel_map,
	'0953': kvdt_Packungsgroesse_map,
	'0960': kvdt_Kennzeichnung_map,
	'0961': kvdt_Kennzeichnung_map,
	'0962': kvdt_Kennzeichnung_map,
	'2706': kvdt_Indikationsschluessel_map,
	'2720': kvdt_Zwischenfall_map,
	'2721': kvdt_Zwischenfall_map,
	'2722': kvdt_Zwischenfall_map,
	'2723': kvdt_Zwischenfall_map,
	'2724': kvdt_Zwischenfall_map,
	'2725': kvdt_Zwischenfall_map,
	'2726': kvdt_Zwischenfall_map,
	'2727': kvdt_Komplikation_map,
	'2728': kvdt_Erfolgsbeurteilung_Indikation_map,
	'2729': kvdt_Histologie_map,
	'2730': kvdt_Revisionseingriff_map,
	'2731': kvdt_stationaere_Aufnahme_map,
	'2732': kvdt_Implantat_map,
	'2742': kvdt_operierte_Seite_map,
	'2744': kvdt_Anaesthesie_Art_map,
	'2750': kvdt_Facharztstatus_map,
	'2752': kvdt_Facharztstatus_map,
	'2761': kvdt_Anaesthesie_erbracht_map,
	'2770': kvdt_Zwischenfall_map,
	'2771': kvdt_Zwischenfall_map,
	'2772': kvdt_Zwischenfall_map,
	'2773': kvdt_Zwischenfall_map,
	'2774': kvdt_Zwischenfall_map,
	'2775': kvdt_Zwischenfall_map,
	'2776': kvdt_Zwischenfall_map,
	'2780': kvdt_Revisionseingriff_erforderlich_map,
	'2781': kvdt_Histologie_map,
	'2782': kvdt_stationaere_Weiterbehandlung_map,
	'3108': xdt_Versichertenart_map,
	'3110': map_gender_xdt2gm,
	'3116': kvdt_KV_Bereich_map,
	'3674': kvdt_Diagnosensicherheit_map,
	'3675': kvdt_Seitenlokalisation_map,
	'4106': xdt_Kostentraegeruntergruppe_map,
	'4107': xdt_Abrechnungsart_map,
	'4113': xdt_Ost_West_Status_map,
	'4121': xdt_Gebuehrenordnung_map,
	'4122': xdt_Abrechnungsgebiet_map,
	'4123': kvdt_Personenkreis_Untersuchungskategorie_map,
	'4201': xdt_Ursache_des_Leidens_map,
	'4202': kvdt_Unfallfolgen_map,
	'4210': xdt_Ankreuzfeld_map,
	'4211': xdt_Ankreuzfeld_map,
	'4212': xdt_Ankreuzfeld_map,
	'4213': xdt_Ankreuzfeld_map,
	'4221': kvdt_belegaerztliche_Behandlung_map,
	'4234': kvdt_anerkannte_Psychotherapie_map,
	'4236': kvdt_somatische_Ursachen_map,
	'4239': xdt_Scheinuntergruppe_map,
	'4230': xdt_gesetzlicher_Abzug_map,
	'4236': xdt_Klasse_stationaere_Behandlung_map,
	'4261': kvdt_Kurart_map,
	'4580': xdt_Rechnungsart_map,
	'4608': xdt_Abdingungserklaerung_map,
	'4613': xdt_Anlage_erforderlich_map,
	'4520': xdt_Alkoholeinfluss_map,
	'4522': xdt_Blutentnahme_map,
	'4554': xdt_Arbeitsunfall_map,
	'4560': xdt_arbeitsfaehig_map,
	'4570': xdt_Heilbehandlung_erforderlich_map,
	'4571': xdt_Besondere_Heilbehandlung_durch_map,
	'4581': xdt_Allgemeine_Heilbehandlung_durch_map,
	'4582': xdt_AU_3Tage_map,
	'5024': kvdt_Zusatzkennzeichen_poststationaere_Leistungen_map,
	'6003': kvdt_Diagnosensicherheit_map,
	'6004': kvdt_Seitenlokalisation_map,
	'6288': kvdt_Diagnosensicherheit_map,
	'6289': kvdt_Seitenlokalisation_map,
	'6293': kvdt_Diagnosensicherheit_map,
	'6294': kvdt_Seitenlokalisation_map,
	'8000': xdt_packet_type_map,
	'8401': xdt_Befundstatus_map,
	'8418': xdt_Teststatus_map,
	'8443': xdt_Resistenzmethode_map,
	'8447': xdt_Resistenzinterpretation_map,
	'9102': kvdt_Empfaenger_map,
	'9106': xdt_character_code_map,
	'9132': kvdt_enthaltene_Datenpakete_map,
	'9600': xdt_Archivierungsart_map
}
#--------------------------------------------------------------
def xdt_8date2iso(date=None):
	"""DDMMYYYY -> YYYY-MM-DD"""
	return '%s-%s-%s' % (date[-4:], date[2:4], date[:2])
#==============================================================
# $Log: gmXdtMappings.py,v $
# Revision 1.26  2004-06-25 12:37:20  ncq
# - eventually fix the import gmI18N issue
#
# Revision 1.25  2004/06/20 15:38:58  ncq
# - if epydoc can't handle a locally undefined _() it is broken
#
# Revision 1.24  2004/06/20 06:49:21  ihaywood
# changes required due to Epydoc's OCD
#
# Revision 1.23  2004/06/18 13:34:58  ncq
# - map a few more line types
#
# Revision 1.22  2004/06/09 14:36:17  ncq
# - cleanup
#
# Revision 1.21  2004/05/27 13:40:21  ihaywood
# more work on referrals, still not there yet
#
# Revision 1.20  2004/05/18 20:37:03  ncq
# - update befundstatus/teststatus maps
#
# Revision 1.19  2004/05/11 08:06:49  ncq
# - xdt_8date2iso()
#
# Revision 1.18  2004/04/21 15:27:38  ncq
# - map 8407 to string for ldt import
#
# Revision 1.17  2004/04/19 12:43:44  ncq
# - add Befundstatus mapping xdt <-> GnuMed
#
# Revision 1.16  2004/03/20 19:45:49  ncq
# - rename gender map
#
# Revision 1.15  2003/11/19 12:30:22  shilbert
# - corrected typos
#
# Revision 1.14  2003/11/17 10:56:34  sjtan
#
# synced and commiting.
#
# Revision 1.1  2003/10/23 06:02:38  sjtan
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.13  2003/04/03 14:59:36  ncq
# - lots more maps ...
#
# Revision 1.12  2003/03/26 07:44:40  ncq
# - near-complete maps now
#
# Revision 1.11  2003/03/24 23:49:34  ncq
# - a huge heap of new mappings by Basti
#
# Revision 1.10  2003/02/19 15:57:57  ncq
# - better strings
#
# Revision 1.9  2003/02/19 15:23:44  ncq
# - a whole bunch of new mappings by Basti
#
# Revision 1.8  2003/02/19 12:27:42  ncq
# - map_of_maps -> map_of_content_maps
#
# Revision 1.7  2003/02/19 12:26:47  ncq
# - map of maps
#
# Revision 1.6  2003/02/17 23:31:02  ncq
# - added some patient related mappings
#
# Revision 1.5  2003/02/14 01:49:17  ncq
# - better strings
#
# Revision 1.4  2003/02/13 15:42:54  ncq
# - changed some strings
#
# Revision 1.3  2003/02/13 15:26:09  ncq
# - added mappings for content translation of Satzidentifikation
#
# Revision 1.2  2003/02/13 12:21:53  ncq
# - comment
#
# Revision 1.1  2003/02/13 12:21:26  ncq
# - first check in
#
