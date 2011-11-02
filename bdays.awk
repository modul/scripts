#!/usr/bin/awk -f
#
# bdays.awk
# ---------------------------------------
# gibt aus, wer heute oder morgen Geburtstag hat und wie 
# alt die Person wird;
# die Daten kommen aus einer Datei, die wie folgt aufgebaut ist:
# NAME:DD:MM:YYYY
# Benutzung: 
# $ /PATH/TO/bdays.awk < DATEI
# ---------------------------------------
# written by mo
# 08/03/2003
# 

BEGIN {
	FS=":"
	"date +%d" | getline day
	"date +%m" | getline month
	"date +%Y" | getline year
	today = 0
	tomorrow = 0
	
	# Ich muss wissen wieviele Tage der jetzige Monat hat bzw.
	# welches der Letzte ist (deswegen die Variable 'last')
	# Von Januar bis July haben alle ungeraden Monate 31 Tage.
	# Ab August haben alle geraden Monate 31 Tage (Aug, Okt, Dez).
	# Meine Loesung:
	if(month <= 7) {
		if((month % 2) > 0) last = 31
		else last = 30
	}
	else {
		if((month % 2) == 0) last = 31
		else last = 30
	}
	
	print "Heute ist der "day"."month"."year
}

$2 == day && $3 == month {
	print "\033[31m"$1" wird heute "year - $4"!\033[0m"
	today++
}
$2 == (day + 1) && $3 == month {
	print "\033[36m"$1" wird morgen "year - $4"!\033[0m"
	tomorrow++
}
$2 == 01 && day == last && $3 == (month + 1){
	print "\033[36m"$1" wird morgen "year - $4"!\033[0m"
	tomorrow++
}

END { 
	if(today == 0 && tomorrow == 0) print "Keine Geburtstage."
}
