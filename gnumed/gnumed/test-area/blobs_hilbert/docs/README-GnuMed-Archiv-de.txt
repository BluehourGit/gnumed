# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/blobs_hilbert/docs/Attic/README-GnuMed-Archiv-de.txt,v $
# $Revision: 1.4 $
#------------------------------------------------------------------------

Sie lesen gerade eine Vorversion des Installationshandbuchs zu GNUmedArchiv

Inhalt :
--------

1.  Voraussetzung
2.  Installation
3.  Starten
4.  Loslegen
5.  Praxisprogrammanbindung


##############################
1.   Installation Voraussetzung
##############################

Sie sind dabei, GNUmedArchiv zu installieren. GNUmedArchiv ist in der Programmiersprache Python geschrieben.
Daher muss auf dem System Python installiert sein. Zus�tzlich m�ssen noch andere Pakete
installiert sein. Die folgende Anleitung wurde mit Suse 8.0 getestet.Andere Distributionen
sollten auch funktionieren.Die Installation umfasst die Installation auf dem Client bzw. Arbeitsplatz
und die Installation der Datenbank auf dem Server.Damit GNUmed/Archive l�uft, m�ssen von Ihrem System
einige Voraussetzungen erf�llt werden.

Sie brauchen:

auf dem Client
--------------

	Python
	------

	Linux )	Bei Linux kann man sich entscheiden ob man Python von den Quellen installiert oder auf
		die Pakete von Distributionen zur�ckgreift.

		Suse 8.0 ) Folgende Pakete m�ssen installiert werden. Dazu kann man yast2 benutzen.
			python ; python-devel ; python-doc ;

		Andere ) Man kann auch von den Quellen installieren. Diese k�nnen von
			http://www.python.org/ftp/python/2.2.1/Python-2.2.1.tgz heruntergeladen werden.

	Windows ) F�r Windows gibt es einen komfortablen Installer.

		http://www.python.org/ftp/python/2.2.1/Python-2.2.1.exe

	Mac ) 	http://www.python.org/2.2.1/mac.html oder http://www.cwi.nl/~jack/macpython.html


	WxWindows - www.wxwindows.org
	---------
	Linux )	Suse 8.0 ) Folgende Pakete beschafft man sich bei www.sourceforge.net
			http://prdownloads.sourceforge.net/wxwindows/wxGTK-2.3.2-1.i386.rpm
			http://prdownloads.sourceforge.net/wxwindows/wxGTK-devel-2.3.2-1.i386.rpm
			http://prdownloads.sourceforge.net/wxwindows/wxGTK-gl-2.3.2-1.i386.rpm

		Andere )Man kann auch alles von Quellen installieren
			http://prdownloads.sourceforge.net/wxwindows/wxGTK-2.3.2.tar.gz

	Windows )F�r Windows gibt es einen komfortablen Installer.
			http://prdownloads.sourceforge.net/wxwindows/wxMSW-2.2.9.zip

	Wxpython - www.wxpython.org
	--------

	Linux )	Voraussetzung f�r wxpython sind "glib" und "gtk+". Die sind oft schon installiert
		Bei Suse kann man yast2 aufrufen und nach "glib" und "gtk" suchen. Wenn links vom Paketnamen
		ein "i" steht, ist es bereits installiert.

		Suse 8.0 ) Bei mir ist installiert : gtk ; gtk-devel ; gtkmm ; gtkmm-devel ; python-gtk ;
			wxGTK ; wxGTK-devel ; wxGTK-gl

			Ich habe folgende Pakete von Sourceforge heruntergeladen :

			http://prdownloads.sourceforge.net/wxpython/wxPython-2.3.2.1-1-Py22.i386.rpm?download
			http://prdownloads.sourceforge.net/wxpython/wxPython-gl-2.3.2.1-1-Py22.i386.rpm?download
			http://prdownloads.sourceforge.net/wxpython/wxPython-tools-2.3.2.tar.gz?download

		Andere )Man kann auch alles von Quellen installieren
			http://prdownloads.sourceforge.net/wxpython/wxPython-docs-2.3.2.tar.gz?download
			http://prdownloads.sourceforge.net/wxpython/wxPython-2.3.2.1.tar.gz

	Windows )F�r Windows gibt es einen komfortablen Installer.
		http://prdownloads.sourceforge.net/wxpython/wxPython-2.3.2.1-Py22.exe

	Scanner-Anbindung
	-----------------
	Linux   - http://www.mostang.com/sane/        - scannen unter Linux

	Windows - http://twainmodule.sourceforge.net/ - damit man von Python aus Scannen kann (Windows)


	PythonImagingLibrary
	--------------------
	http://www.pythonware.com - PIL 1.1.3

	mx-tools
	-------------------
	http://www.egenix.com/files/python/ - muss zur Python-Version passen



Server
------
	Python
	------

	Linux )	Bei Linux kann man sich entscheiden ob man Python von den Quellen installiert oder auf
		die Pakete von Distributionen zur�ckgreift.

		Suse 8.0 ) Folgende Pakete m�ssen installiert werden. Dazu kann man yast2 benutzen.
			python ; python-devel ; python-doc ;

		Andere ) Man kann auch von den Quellen installieren. Diese k�nnen von
			http://www.python.org/ftp/python/2.2.1/Python-2.2.1.tgz heruntergeladen werden.

	Windows ) F�r Windows gibt es einen komfortablen Installer.

		http://www.python.org/ftp/python/2.2.1/Python-2.2.1.exe

	Mac ) 	http://www.python.org/2.2.1/mac.html oder http://www.cwi.nl/~jack/macpython.html


	Posgresql-Datenbank
	---------
	Linux ) Suse 8.0 ) Von der CD oder aus dem Netz (http://www.postgresql.org) muss das Paket postgresql
			installiert werden. Zus�tzlich habe ich noch folgende Pakete installliert :
			postgresl-devel ; postgresql-libs ; postgresql-server


	Python-Schnittstelle f�r PostgreSQL
	---------

	Linux )   http://prdownloads.sourceforge.net/pypgsql/pypgsql-2.2.tar.gz?download
			Die Datei enth�lt eine Datei namens "readme" in der die Installation beschrieben ist.
			Man muss evtl. die Datei setup.py an das eigene System anpassen bevor es kompiliert wird.
			Wichtig sind dabei die Pfade zu den entsprechenden Bibliotheken.

	Windows ) Auch f�r dieses Paket gibt es einen Installer
			http://prdownloads.sourceforge.net/pypgsql/pyPgSQL-2.1.win32-py2.2.exe?download

	mx-tools
	-------------------
	http://www.egenix.com/files/python/ - muss zur Python-Version passen


#############################
2.   Installation
#############################
Client
------
	GNU/Linux )
	Entpacken Sie das Archiv 'gnumed-archive-client.tgz' in ein Verzeichnis Ihrer Wahl.
	F�hren Sie dann in diesem Verzeichnis das Installationsskript 'install.sh' aus.

	Windows )
	F�hren Sie das Installationsprogramm [setup.exe] aus.

	Wenn Sie GNUmedArchive nicht im Standardpfad installieren, m�ssen Sie die
	Dateien 'run-scanner.bat' , 'run-indexer.bat' und 'run-viewer.bat' entsprechend anpassen.
	Diese Dateien befinden sich im Installationsverzeichnis.

	Der Eintrag zur Sprachwahl befindet sich in den Dateien 'run-scanner.bat', 'run-indexer.bat'
	und 'run-indexer.bat'. F�r die deutsche Oberfl�che entfernen Sie bitte die Zeichenkette
	'REM' vor dem Eintrag 'set LANG=de_DE@EURO'.

	Sollte 'python.exe' auf Ihrem System nicht im Standardverzeichnis ' c:\python22' installiert
	sein, muss der richtige Pfad in die genannten *.bat-Dateien Eingetragen werden.

	Nicht vergessen, die Datei gnumed-archive.conf auf den Clients anzupassen damit
	die Datenbank auch erreicht wird. Diese Datei kann an verschiedenen Stellen abgelegt werden.

	GNU/Linux )
	Im Idealfall erzeugt man ein Verzeichnis '.gnumed' im Home-Verzeichnis des ausf�hrenden
	Benutzers und kopiert die Datei gnumed-archive.conf in dieses
	Verzeichnis.

	Windows )
	In Windows ist es ratsam die Datei 'gnumed-archive.conf' ins selbe Verzeichnis wie die Programm-Dateien
	zu legen. Das ist automatisch der Fall wenn man GNUmedArchive via 'setup.exe' installiert.

	Eine Beispielkonfiguration (gnumed-archive.conf) findet sich im Archiv 'gnumed-archive-client.tgz' bzw.
	'setup.exe'
Server
-------

	GNUmed/Archive greift auf einen PostgreSQL-Server zu. Der l�uft z.B unter
	Linux. Es ist wohl auch m�glich den Server unter Windows laufen zu lassen. Diese
	Methode wird aber von uns nicht unterst�tzt. Mehr Infos dazu im Netz unter den
	Schlagworten 'running PostgreSQL under Windows' oder im GNUmed Handbuch.
	PostgreSQL ist jetzt auch f�r das Netzwerkbetriebssystem Novell erschienen und
	kann daher auch auf diesem Betriebssystem eingesetzt werden.

	Entpacken Sie das Archiv 'gnumed-archive-server.tgz' in ein Verzeichnis Ihrer Wahl.
	F�r die Installation ben�tigen Sie root-Zugriff auf Ihr System.

	Passen Sie nun die Datei'german-doc_types.sql' an Ihre individuellen Bed�rfnisse an.
	Diese Datei enth�lt die Eintr�ge f�r die Befundtypen die sp�ter beim Zuordnen der
	eingescannten Befunde ben�tigt werden.

	Bsp.:

	INSERT INTO doc_type(id, name) values(101,'Befundtyp1');
	INSERT INTO doc_type(id, name) values(102,'Befundtyp2');
	INSERT INTO doc_type(id, name) values(103,'Befundtypx');
	usw.

	Die Zahl vor dem Befundtyp muss einmalig sein. Das bedeutet,
	das keine Zahl doppelt vergeben werden darf. Daher muss auch
	sichergestellt werden, dass die Zahl nicht bereits in der Datei
	'gmBlobs.sql' verwendet wird. Man schaut sich also die Datei 'gmBlobs.sql' an, schaut nach
	der gr��ten Zahl und addiert dazu '1'. Diese Zahl ist dann die Zahl vor dem ersten Eintrag
	in der Datei'german-doc_types.sql'. Bei den folgenden Eintr�gen wird einfach hochgez�hlt.


	Jetzt ist es an der Zeit sich zu �berlegen welche Benutzer mit welchen Rechten im
	Archiv arbeiten d�rfen bzw. schreibend und/oder lesend zugreifen d�rfen. Will man
	nur Testbenutzer anlegen muss nichts angepasst werden. Daf�r reichen die Voreinstellungen
	in der Datei 'bootstrap-gm_db_system.conf'. Will man eigene Benutzer einrichten, erledigt man
	das am Besten mit einer eigenen Konfigurationsdatei. Man erzeugt beispielsweise eine
	neue Datei 'users.conf'. Dort tr�gt man dann eigene Gruppen und Benutzer ein. Diese Datei muss
	ein betsimmtes Format haben. Man orientiert sich am Besten am Format der Datei
	'bootstrap-gm_db_system.conf'.

	Ist alles soweit eingestellt, f�hrt man das Installationsskript 'install.sh' aus und
	folgt den Anweisungen.

	L�uft die Installation ohne Fehler durch, erhalten Sie am Ende weitere Anweisungen
	was noch zu tun ist damit beispielsweise automatisch die angelieferten
	Befunde in die Datenbank gespeichert werden.
	
	Falls bei der Installation Fehler auftreten, ist es ratsam, einen Blick in das Fehlerprotokoll
	zu werfen. F�r den Fall, dass auch das nicht zum Ziel f�hrt kann eine Nachricht an die Mailing-Liste
	weiterhelfen. Bitte nicht vergessen, das Fehlerprotokoll anzuh�ngen.

	Passen Sie nun den Abschnitt [import] in der Konfigurationsdatei 'gnumed-archive.conf' an Ihre Bed�rfnisse an.
#################
3.Starten
#################
Client
------
	GNU/Linux )

		'run-scanner.sh'
		'run-indexer.sh'
		'run-viewer.sh'

	MS Windows(TM)
		Im Startmen� wurden entsprechende Verkn�pfungen angelegt

Server
------
	GNU/Linux )
		'run-importer.sh'

	Idealerweise legt man einen cron-job an der zu festgelegten Zeiten die Befunde
	in die Datenbank schiebt.

###############################
4.  Loslegen
###############################
    Das Dokumentenarchiv besteht aus vier Teilprogrammen.
    1) Scan-Modul
    2) Index-Modul
    3) Datenbank-Importer
    4) Betrachter

    und so ist der Ablauf ...

Teil 1: Erfassung
------------------------
Ein Stapel Befunde wird fortlaufend eingescannt. Mehrseitige
Dokumente behalten ihren inneren Zusammenhang. Das
Scanprogramm folgt dabei einem logischen Ablauf.

Schritt 1: Einscannen der Bl�tter. Hierbei wird jeder Scanner
mit TWAIN-Schnittstelle unter Microsoft Windows sowie jeder
mit SANE-Schnittstelle unter GNU/Linux unterst�tzt.

Schritt 2: Optional �ndern der Reihenfolge der Seiten. Dieser
Schritt ist nur notwendig wenn die Seiten nicht in der
nat�rlichen Reihenfolge eingescannt wurden.

Schritt 3: Ist ein Befund vollst�ndig erfasst, wird dieser
gespeichert. Dadurch wird auf dem Bildschirm ein eindeutiges
Identifikationsk�rzel (Paginiernummer) angezeigt. Diese Kennung
muss auf dem Befund vermerkt werden. Sie stellt den
einfachsten Zusammenhang zwischen Papierbefund und
digitalisierter Version her.

Dann kann der n�chste Befund erfasst werden.

Die Oberfl�che des Programms ist speziell f�r diesen
Arbeitsablauf optimiert und enth�lt nur die die wichtigsten
Bedienelemente. Auf den Einsatz einer Maus kann verzichtet
werden. F�r eine sp�tere Version ist geplant, die Kennung als
Barcode und im Klartext auf den Originalbefund zu drucken.
Daf�r kann die freie Software GNUBarcode verwendet werden.

Teil 2: Zuordnung
------------------------
Dieses Programm dient der Zuordnung der gescannten Dokumente zu
einem Patienten. Die meisten kommerziellen Praxisprogramme
lassen f�r Fremdprogramme keinen direkten Zugriff auf die
elektronische Karteikarte zu. Man kann aber die
GDT/BDT-Schnittstelle nutzen, sofern das Praxisprogramm dies
unterst�tzt. Beispielsweise kann das Zuordnungsprogramm an
TurboMed als externes Programm angebunden werden. Bei Aufruf
werden die Stammdaten des aktuellen Patienten als BDT-Datei
�bergeben und vom Zuordnungsprogramm gelesen. Dieser Umweg
entf�llt beim Einsatz des Praxisprogramms GNUmed. Hier k�nnte
der zugeordnete Befund direkt in der elektronischen Kartei
vermerkt werden.

Auch die Zuordnungssoftware folgt wieder einem logischen
Ablauf.

Schritt 1: Laden des Befunds via Identifikationsk�rzel
(Paginiernummer) auf dem Befund. Diese muss in das
entsprechende Feld eingetippt werden. Zuk�nftig ist hier das
Einlesen via Barcode-Scanner vorgesehen. Doch auch ohne
Barcode-Scanner ist das Eintippen der Dokumentenkennung durch
ein intelligentes Eingabefeld sehr komfortabel. Bei Eingabe
einiger Zeichen werden automatisch alle noch nicht
zugeordneten Dokumente angeboten, deren Paginiernummer mit
diesen Zeichen beginnt. Weiteres Tippen grenzt die
Dokumentenauswahl immer mehr ein. Jederzeit kann das
gew�nschte Dokument aus der Liste gew�hlt werden. So reichen
oft drei oder vier Zeichen aus, bis die Kennung eindeutig ist.

Schritt 2: Nach dem Laden der Befundseiten sind beschreibende
Felder auszuf�llen. Dazu z�hlen Erstellungsdatum des Dokuments,
ein kurzer Kommentar, die Angabe des Befundtyps und ein Feld
f�r beliebig lange Anmerkungen. Von �bergeordneter Bedeutung
ist die Angabe des Befundtyps. Dieser mu� aus einer vorher
festzulegenden Liste ausgew�hlt werden. Dieser Liste k�nnen
jederzeit weitere Typen hinzugef�gt werden. Diese relativ
starre Vorgabe bietet sp�ter deutlich h�heren Nutzwert bei der
Auswahl von Dokumenten zur Ansicht.

Schritt 3: Sind alle Felder erfa�t, werden diese gespeichert.
Ein Skript �bertr�gt nun im Hintergrund vollautomatisch die
indizierten Dokumente in die Datenbank. Dies kann bei gro�en
Datenmengen auch erst Nachts geschehen. Somit kann eine
zus�tzliche Belastung des Netzwerkes w�hrend des Praxisbetriebs
vermieden werden. Auf Wunsch wird es m�glich sein, die
Beweiskraft der eingescannten Dokumente mittels eines digitalen
Notarservice (z.B. GNotary) zu erh�hen.

Teil 3: Nutzung

Das Befundanzeigeprogramm wird entweder direkt aus GNUmed oder
aus einem herk�mmlichen Praxisprogramm aufgerufen und zeigt
alle Befunde des aktuellen Patienten als Baumstruktur an. Die
eigentliche Darstellung der Befundseiten wird an Programme des
jeweiligen Betriebssystems delegiert. Dadurch ist das
Anzeigeprogramm nicht auf bestimmmte Dateitypen beschr�nkt. Es
k�nnen alle Dateitypen angezeigt werden, f�r die das
installierte Betriebssystem Anzeigeprogramme anbietet. Somit
k�nnen Grafik- ebenso wie Videodateien, Texte oder Audiodaten
zur Anzeige bzw. zu Geh�r gebracht werden. Die beim Indizieren
erhobenen Metadaten erlauben einen effektiven Umgang mit den
Befunden. Befunde k�nnen nach Typen, Erstellungsdatum bzw.
-zeitr�umen sowie nach Kommentaren gefiltert werden. Damit ist
es z.B. m�glich, alle Sonographiebefunde eines Patienten f�r
einen bestimmten Zeitraum zu selektieren. Diese Funktionalit�t
ist noch in der Entwicklung. Es ist nat�rlich m�glich,
ausgew�hlte Dokumente zur�ck an das Praxisprogramm zu
�bergeben, beispielsweise zum Erstellen eines Arztbriefes.


#########################################
5. Praxisprogrammanbindung
#########################################

GNU/Linux
	GNUmed - GNUmedArchive ist Bestandteil von GNUmed und wird direkt als Plugin in das Programm integriert.

DOS
	Turbomed - Das Programm GNUmed/Archive soll direkt aus Turbomed heraus gestartet werden.
	Also m�ssen 'run-scanner.bat','run-indexer.bat','run-viewer.bat gestartet werden. Die Erfahrung
	zeigt, dass die DOS-Box von Turbomed keine Verzeichnisangaben honoriert. Also m�ssen wir eine Batch-
	Datei erzeugen die wiederum die gew�nsche Batchdatei aufruft. Diese wird als externes Programm in der
	Turbomeddatei '289.gdt' eingetragen. Was man wie einzutragen hat, findet man im Turbomed-Handbuch im
	Kapitel 'GDT'

	Bei mir sieht die Datei so aus :

	[289.gdt]

	1
	2
	Befunde zuordnen #c:\gmtmp\pat_idx.dat#c:\Progra~1\gnumed~1\client\index.bat###
	3
	Befunde scannen #c:\gmtmp\pat_idx.dat#c:\Progra~1\gnumed~1\client\scan.bat###
	Befunde zuordnen #c:\gmtmp\pat_idx.dat#c:\Progra~1\gnumed~1\client\index.bat###
	4
	Befunde zuordnen #d:\gmtmp\pat_idx.dat#d:\Progra~1\gnumed~1\client\index.bat###
	Befunde anschauen #c:\gmtmp\pat_idx.dat#c:\Progra~1\gnumed~1\client\view.bat###

	Dadurch k�nnen die Arbeitsstationen 2,3 und 4 das Zuordnungsprogramm aus der Karteikarte heraus aufrufen.
	An Station 3 kann zus�tzlich das Scanprogramm aufgerufen werden. Der Scan-Eintrag ist nur da sinnvoll wo
	auch ein Scanner oder eine Kamera angeschlossen ist.
	An Station 4 k�nnen dann die Befunde auch wieder angeschaut werden.

	Der Anteil "c:\gmtmp\pat_idx.dat" ist variabel. Der Eintrag "patient file" im Abschnitt [index] und [viewer]
	der Konfigurationsdatei gnumed-archive.conf muss auf diese Stelle zeigen. Unter MSDOS (auch im DOS-Fenster) darf
	diese Zeichenkette maximal 8+3 Zeichen lang sein. Sonst m�ssen die entsprechend verk�rzten Namen
	angegebenen werden. Das funktioniert aber nicht immer und sollte vermieden werden.

	Bsp.
	c:\program files\gnumedarchiv\archivgnumed.bat  -> c:\progra~2\gnumed~1\archiv~1.bat

	Das Scan-Teilprogramm ist ja unabh�ngig vom Patienten und kann daher einfach als
	externes Programm angelegt werden. Es kann dann mit Strg-P aufgerufen werden. Man
	schaue sich den Abschnitt Fremdprogramme im Turbomed-Handbuch an.

	Die Programme werden in der Datei '289.BMN' definiert.


#------------------------------------------------------------------------
$Log: README-GnuMed-Archiv-de.txt,v $
Revision 1.4  2003-01-19 13:44:09  ncq
- new Englisch installation manual
- fixes for German

Revision 1.3  2002/12/22 22:25:04  ncq
- Windows install: setup.exe

Revision 1.2  2002/12/03 10:16:59  ncq
- lots of changes by Basti according to current state of affairs

Revision 1.1  2002/09/17 09:16:57  ncq
- added those files

