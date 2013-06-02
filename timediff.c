/*
 * Calculate time difference between now and a given date (and time).
 * 
 * All rights reversed.
 * 2013 Remo Giermann <mo@liberejo.de>
 * 
 */

#include <stdio.h>
#include <time.h>

#define plural(x) (x==0? 's' :(x==1? 0 : 's'))

int main(int argc, const char *argv[])
{
	time_t now = time(NULL);
	time_t then = 0;
	struct tm *dt = localtime(&now);
	int weeks, days, hours, minutes, seconds;

	if (argc < 2 || sscanf(argv[1], "%u/%u/%u", &dt->tm_year, &dt->tm_mon, &dt->tm_mday) < 3) {
		printf("usage: %s YYYY/MM/DD [HH:MM[:SS]]\n", argv[0]);
		return 1;
	}
	else {
		if (argc > 2)
			sscanf(argv[2], "%u:%u:%u", &dt->tm_hour, &dt->tm_min, &dt->tm_sec);
	}

	dt->tm_year -= 1900;
	dt->tm_mon  -= 1;
	then = mktime(dt);

	seconds = then<now? now-then : then-now;
	minutes = seconds/60;
	seconds = seconds%60;
	hours   = minutes/60;
	minutes = minutes%60;
	days    = hours/24;
	hours   = hours%24;

	printf("%u day%c %u hour%c %u minute%c %u second%c %s\n", 
			days, plural(days), 
			hours, plural(hours),
			minutes, plural(minutes), 
			seconds, plural(seconds), 
			then<now?"ago":"to go");

	return 0;
}
