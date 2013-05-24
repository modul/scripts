/*
 * Display given or current date with 
 * decimal (fraction of a day) and conventional local time.
 *
 * usage: 
 * time [no arguments] 
 * time YYYY/MM/DD.fraction 
 * time YYYY/MM/DD [HH:MM[:SS]]
 *
 * 
 * All rights reversed.
 * 2013 Remo Giermann <mo@liberejo.de>
 *
 * 
 */

#include <stdio.h>
#include <time.h>
#include <string.h>

char *fractdate(struct tm *dt)
{
	static char date[18];
	float fract_day = dt->tm_mday + (float) (dt->tm_sec + 60*dt->tm_min + 3600*dt->tm_hour)/86400;
	sprintf(date, "%4u/%02u/%.5f", dt->tm_year+1900, dt->tm_mon+1, fract_day);
	return date;
}

int main(int argc, char *argv[])
{
	static const char wday_name[][4] = {
		"Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"};
	time_t now = time(NULL);
	struct tm *dt = localtime(&now);
	int fraction = 0;

	if (argc >= 2) {
		char timeset = 1;
		if (strchr(argv[1], '/')) {
			if (sscanf(argv[1], "%u/%u/%u.%u", &dt->tm_year, &dt->tm_mon, &dt->tm_mday, &fraction) == 4) {
				dt->tm_sec  = (fraction * 864)/1000;
				dt->tm_min  = dt->tm_sec/60;
				dt->tm_sec  = dt->tm_sec%60;
				dt->tm_hour = dt->tm_min/60;
				dt->tm_min  = dt->tm_min%60;
			}
			else if (argc >= 3 &&
				sscanf(argv[2], "%u:%u:%u", &dt->tm_hour, &dt->tm_min, &dt->tm_sec));
			else
				timeset = 0;

			dt->tm_year -= 1900;
			dt->tm_mon  -= 1;
		}
		else if (strchr(argv[1], ':') && 
			sscanf(argv[1], "%u:%u:%u", &dt->tm_hour, &dt->tm_min, &dt->tm_sec));
		else {
			printf("usage: time {[HH:MM[:SS]] | [YYYY/MM/DD.FFFFF] | [YYYY/MM/DD [HH:MM[:SS]]]}\n");
			return 23;
		}

		now = mktime(dt);
		if (timeset) {
			now += (dt->tm_isdst==0?3600:0);
			dt = localtime(&now);
		}
	}

	printf("%s %s %02u:%02u:%02u %s\n", 
			fractdate(dt), wday_name[dt->tm_wday], 
			dt->tm_hour, dt->tm_min, dt->tm_sec, dt->tm_zone);
	
	return 0;
}
