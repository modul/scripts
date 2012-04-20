/*
 * blink.c
 *
 * This might let your ThinkLight blink!
 *
 * Usage: blink [COUNT] [DUTY/%] [PERIOD/ms] 
 *
 * author: mo
 * created: 2012/04/08
 *
 */

#include <stdio.h>

#define THINKLIGHT "/sys/class/leds/tpacpi::thinklight/brightness"
#define OFF "0"
#define ON  "255"

#define COUNT 1
#define PERIOD 500
#define DUTY 50

#define light(x, fp) fputs(x, fp); fflush(fp)

int main(int argc, char *argv[])
{
	FILE *fp;
	int i;
	int cnt = COUNT;
	int per = PERIOD;
	int dty = DUTY;

	if (!(fp = fopen(THINKLIGHT, "w"))) { perror(THINKLIGHT); return 1; }
	light(OFF, fp);

	if (argc > 1 && sscanf(argv[1], "%u", &i) == 1) 
		cnt = i;
	if (argc > 2 && sscanf(argv[2], "%u", &i) == 1)
		dty = i > 100 ? 100 : i;
	if (argc > 3 && sscanf(argv[3], "%u", &i) == 1)
		per = i;

	for (i=2*cnt; i>0; i--) {
		if (i%2 == 0) {
			light(ON, fp);
			usleep(10 * per*dty);
		}
		else {
			light(OFF, fp);
			usleep(10 * per*(100-dty));
		}
	}
	return 0;
}
