# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/blobs_hilbert/docs/Attic/README-GnuMed-Archiv-de.txt,v $
# $Revision: 1.1 $
#------------------------------------------------------------------------

Sie lesen gerade eine Vorversion des Installationshandbuchs zu GnumedArchiv

Inhalt :
--------
--> F�r alle die das nicht zum ersten Mal machen, ist Variante 1 gedacht.

--> Wer es ausf�hrlich braucht, liest bitte Variante 2

--> Abschlie�end ein Abschnitt Praxisprogrammanbindung


##########
         #
   #     #
  ##     #
 # #     #
   #     #
   # *   #
##########

Herzlichen Gl�ckwusch ! Sie sind dabei, das Dokumentenarchiv 'GnumedArchiv' auszuprobieren.

0.  Voraussetzungen
1.  Vorbereitung
2.  Installation
3.  Starten

###############################
0.  Voraussetzungen
###############################
Medituaxarchiv basiert auf Python. Man ben�tigt daher folgende Pakete aus dem Internet oder von
der GNU/Linux-CD.

Python
------
GNU/Linux   -   Python2.2.1 http://www.python.org/ftp/python/2.2.1/Python-2.2.1.tgz
Windows -   Python2.2.1 http://www.python.org/ftp/python/2.2.1/Python-2.2.1.exe
Mac     -               http://www.python.org/2.2.1/mac.html

Wxpython
--------
http://www.wxpython.org -- immer passend zur Pythonversion und zum Betriebssystem

WxWindows
---------
http://www.wxwindows.org

Posgresql-Datenbank
---------
Im Idealfall von einer GNU/Linux-CD oder http://www.postgresql.org

Scanner-Anbindung
-----------------
Windows - http://twainmodule.sourceforge.net/ - damit man von Python aus Scannen kann (Windows)
GNU/Linux   - http://www.mostang.com/sane/        - scannen unter GNU/Linux

PythonImagingLibrary
--------------------
http://www.pythonware.com

GNUmed - entweder komplett oder Teile
------
http://savannah.gnu.org/projects/gnumed/

mx-tools
--------
http://www.egenix.com/files/python/ - muss zur Python-Version passen

#############################
1.  Vorbereitung
#############################

1.1 alle ben�tigten Pakete installieren

1.2 Datenbank aufsetzen.
Wir verwenden PostgreSQL. Im GnumedArchiv-Paket befindet sich Dateien mit der Datenbank-Tabellen-Struktur.
Mit Hilfe dieser Datei wird die Datenbank f�r das Archiv erzeugt.  Alternativ
kann man auch komplett vorkonfigurierte Hardware+Software bei "Le-pc Leipzig" bestellen. Die Installation
der GNUmed-Datenbank ist auch gleichzeitig f�r das GnumedArchiv nutzbar. Die Programme teilen sich die Datenbank.

!!! Nicht vergessen die Datei gnumed-archiv.conf auf den clients anzupassen damit
die Datenbak auch erreicht wird.
##############################
2.  Installation GnumedArchiv
##############################

2.1 Das Dokumentenarchiv braucht nicht installiert zu werden. Wenn man dieses Dokument liest, hat man das Paket wahrscheinlich schon entpackt.
Windows - in ein beliebiges Verzeichnis entpacken.

GNU/Linux - irgendwo hin - evtl. m�ssen symbolische Links angepasst werden damit alle Module von GNUmed gefunden werden.
      - deshalb am Besten CVS-Version auschecken.

	Vorausgesetzt man ist mit dem Internet verbunden, gibt man auf der Konsole folgendes ein :
	Wenn nach einem Passwort gefragt wird, einfach mit Enter-Taste best�tigen.

	cvs -d:pserver:anoncvs@subversions.gnu.org:/cvsroot/gnumed login

	cvs -z3 -d:pserver:anoncvs@subversions.gnu.org:/cvsroot/gnumed co gnumed

	Damit werden die Quellen aus dem Internet geladen und im aktuellen Verzeichnis ein Unterverzeichnis
	gnumed erstellt.

	Im Unterverzeichnis test-area im CVS findet sich das GnumedArchiv.


    2.2 Die Konfigurationsdatei des GnumedArchiv (gnumed-archiv.conf) muss irgendwo liegen wo sie auch gefunden
	werden kann.
	Windows - z.B. im selben Verzeichnis wie die *.bat-Dateien
	GNU/Linux   - z.B '~/.gnumed/gnumed-archiv.conf'

	Die Konfigurationsdatei muss an das eigene System angepasst werden.

###############################
3.  Loslegen
###############################
    Das Dokumentenarchiv besteht aus vier Teilprogrammen.
    1) Scan-Modul
    2) Index-Modul
    3) Datenbank-Importer
    4) Betrachter

    und so ist der Ablauf ...

Teil 1: Erfassung

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


#########################################################################

##########
   ##    #
  #  #   #
    #    #
   #     #
  #### * #
         #
##########


0.  Voraussetzungen
1.  Vorbereitung
2.  Installation
3.  Starten

###############################
0.  Voraussetzungen
###############################

Python
------

GNU/Linux )	Bei GNU/Linux kann man sich entscheiden ob man Python von den Quellen installiert oder auf
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
GNU/Linux )	Suse 8.0 ) Folgende Pakete beschafft man sich bei www.sourceforge.net
		http://prdownloads.sourceforge.net/wxwindows/wxGTK-2.3.2-1.i386.rpm
		http://prdownloads.sourceforge.net/wxwindows/wxGTK-devel-2.3.2-1.i386.rpm
		http://prdownloads.sourceforge.net/wxwindows/wxGTK-gl-2.3.2-1.i386.rpm

	Andere )Man kann auch alles von Quellen installieren
		http://prdownloads.sourceforge.net/wxwindows/wxGTK-2.3.2.tar.gz

Windows )F�r Windows gibt es einen komfortablen Installer.
		http://prdownloads.sourceforge.net/wxwindows/wxMSW-2.2.9.zip

Wxpython - www.wxpython.org
--------

GNU/Linux )	Voraussetzung f�r wxpython sind "glib" und "gtk+". Die sind oft schon installiert
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


Posgresql-Datenbank
---------
GNU/Linux ) Suse 8.0 ) Von der CD oder aus dem Netz  muss das Paket postgresql
		installiert werden. Zus�tzlich habe ich noch folgende Pakete installiert :

		postgresl-devel ; postgresql-libs ; postgresql-server

Python-Schnittstelle f�r PostgreSQL
---------

GNU/Linux )   http://prdownloads.sourceforge.net/pypgsql/pypgsql-2.2.tar.gz?download
	Die Datei enth�lt eine readme in der die Installation beschrieben ist.
	Man muss die Datei setup.py an das eigene system anpassen bevor es kompiliert wird.

Windows ) Auch f�r dieses Paket gibt es einen Installer
		http://prdownloads.sourceforge.net/pypgsql/pyPgSQL-2.1.win32-py2.2.exe?download


Scanner-Anbindung
-----------------
GNU/Linux   - http://www.mostang.com/sane/        - scannen unter GNU/Linux

Windows - http://twainmodule.sourceforge.net/ - damit man von Python aus Scannen kann (Windows)


PythonImagingLibrary
--------------------
    http://www.pythonware.com

mx-tools
-------------------
    http://www.egenix.com/files/python/ - muss zur Python-Version passen

GnumedArchiv
--------------------
Im Netz unter www.openmed.org

GNU/Linux	- dist.tgz

Windows - GnumedArchiv.exe


################
1. Installation
################
GnumedArchiv

Sie sind dabei, GnumedArchiv zu installieren. GnumedArchiv ist in der Programmiersprache Python geschrieben.
Daher muss auf dem System Python installiert sein. Zus�tzlich m�ssen noch andere Pakete
installiert sein. Die folgende Anleitung wurde mit Suse 8.0 getestet.Andere Distributionen
sollten auch funktionieren.

GNU/Linux ) entpacken Sie die Datei dist.tgz in ein Verzeichnis Ihrer Wahl

Windows ) F�hren Sie das Installationsprogramm aus indem sie gnumedarchiv.exe ausf�hren.
	  Wenn Sie GnumedArchiv nicht im Standardpfad installieren, m�ssen Sie die Datei
	  gnumed-archiv.conf entsprechende anpassen. In dieser Datei werden auch die Einstallungen
	  f�r die Verbindung zur Datenbank vorgenommen.

############
PostgreSQL

Vorrausgesetzt alle Pakete sind wie oben beschrieben installiert, erzeugt man
nun die Datenank f�r GnumedArchiv. Bei der Installation von PostgreSQL wird ein
Benutzer namens "postgres" erzeugt. Dieser Benutzer "postgres" kann
Benutzer f�r die Gnumed-Datenbank anlegen.

Die Postgresql-Datenbank l�uft unter GNU/Linux und diversen anderen Unix-Derivaten.
Es ist auf m�glich, die Datenbank unter Windows laufen zu lassen.
Davon raten wir aber ausdr�cklich ab.

auf der Konsole auf dem GNU/linux-Server werden folgende Kommandos eingegeben:

Voraussetzung ist, dass PostgreSQL gestartet ist. Das funktioniert bei
jeder Linux-Distribution anders.
Bei Suse 8.0 lautet der Befehl : "rcpostgresql restart"

1.) su root              # wechselt den aktive Benutzer zu root
2.) su postgres          # wechselt den aktive Benutzer zu postgres
3.) createuser $Arzt1    # erzeugt einen Datenbanknutzer "Arzt1"
4.) createdb gnumed      # erzeugt eine Datenbank mit dem Namen "gnumed"

Jetzt muss die Datenbank noch mit Inhalten gef�llt werden.
Dazu wechselt man in das Verzeichnis gnumed/gnumed/gnumed/server/sql

5.) psql gnumed
6.) \i gmconfiguration.sql
7.) \i gnumed.sql        # usw. mit allen die dort liegen au�er gmBlobs.sql

f�r GnumedArchiv muss die Datei gmBlobs.sql an die individuellen
Bed�rfnisse angepasst werden.
Bsp.:

INSERT INTO doc_type(id, name) values(101,'Befundtyp1');
INSERT INTO doc_type(id, name) values(102,'Entlassung Chirurgie');
usw.

8.) \i gmBlobs.sql
9.) exit          # dadurch wird wieder zu root-Benutzer gewechselt
10.) rcpostgresql restart

!!! Nicht vergessen die Datei gnumed-archiv.conf auf den clients anzupassen damit
die Datenbank auch erreicht werden kann.

###############################
3.  Loslegen
###############################
    GNU/Linux )
    	man wechselt jetzt in das Unterverzeichnis /dist/client/
    	und f�hrt die entsprechenden Shell-Skripte (*.sh) zum Starten der einzelnen Programme aus.

    Windows ) bei der Installation wuden Verkn�pfungen im Startmen� erzeugt.


    Das Dokumentenarchiv besteht aus drei Teilprogrammen.
    1) Scan-Modul
    2) Index-Modul
    3) Betrachter

    und so ist der Ablauf ...

Teil 1: Erfassung

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
4. Praxisprogrammanbindung
#########################################

GNU/Linux   - Gnumed 

GnumedArchiv ist Bestandteil von Gnumed und wird direkt in das Programm integriert.


DOS - Turbomed

Die Verkn�pfung 'run-indexer.bat' soll direkt aus Turbomed gestartet werden. Dazu wird
'run-indexer.bat' als externes Programm in der Turbomeddatei '289.gdt' eingetragen.
Was man wie einzutragen hat, findet man im Turbomed-Handbuch im Kapitel 'GDT'

Bei mir sieht die Datei so aus :

[289.gdt]

1
2
Befunde zuordnen #c:\temp\archiv.bdt#c:\Programme\gnumedarchiv\client\run-indexer.bat###
3
Befunde zuordnen #c:\temp\archiv.bdt#c:\Programme\gnumedarchiv\client\run-indexer.bat###
4
Befunde zuordnen #d:\temp\archiv.bdt#d:\Programme\gnumedarchiv\client\run-indexer.bat###

Dadurch k�nnen die Arbeitsstationen 2,3 und 4 das Zuornungsprogramm aus der Karteikarte heraus aufrufen.

Der Anteil "c:\temp\archiv.bdt ist variabel. Der Eintrag "patient_file" im Abschnitt [metadata] der
Konfigurationsdatei gnumed-archiv.conf muss auf diese Stelle zeigen. Unter MSDOS (auch im DOS-Fenster) darf
diese Zeichenkette maximal 8.3 Zeichen lang sein. Sonst m�ssen die entsprechend verk�rzten Namen
angegebene werden. 

Bsp.
c:\temp\archivturbomed.bat  -> c:\temp\archiv~1.bat

#------------------------------------------------------------------------
$Log: README-GnuMed-Archiv-de.txt,v $
Revision 1.1  2002-09-17 09:16:57  ncq
- added those files

