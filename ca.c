/*
 * Cellular Automata Printer
 *
 * Usage: binary-name [RULE INITAL] 
 * where RULE sets the CA rule (def. 30)
 * and  INITIAL the initial hex start pattern 
 * (def. 0x100000000 i.e. a centered 1).
 *
 * All rights reversed.
 * 2012 Remo Giermann <mo@liberejo.de>
 */

#include <stdio.h>

int main(int argc, const char *argv[])
{
	long i, r=30, w=1L<<32;
	if (argc == 3) {
		sscanf(argv[1], "%u", &r);
		sscanf(argv[2], "%x", &w);
	}
	while (1) {
		long g = 0;
		for (i=1; i<sizeof(long)*8-1; i++) {
			long pat = (w&(7L<<(i-1)))>>(i-1);
			g |= (r&(1L<<pat))<<(i-pat);
			putchar(w&(1L<<i)?'X':' ');
		}
		putchar(10);
		usleep(10000);
		w = g;
	}
}
