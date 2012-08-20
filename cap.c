/* 
 * Print Cellular Automata output in netpbm format.
 * 
 * All rights reversed.
 * 2012 Remo Giermann <mo@liberejo.d>
 *
 */
#include <stdio.h>
#include <stdlib.h>

#define W 1000

void usage(const char *p)
{
	printf("Usage: %s [-h|--help] [black|white] [rRULE] [wWIDTH] [OUTFILE]\n", p);
	exit(0);
}

void pbm(int *u, size_t w, size_t h, FILE *o, int b, const char *desc)
{
	int x, y;
	fprintf(o, "P1\n# %s\n%u %u\n", desc, w, h);
	for (y=0; y<h; y++) {
		for (x=0; x<w; x++)
			fprintf(o, "%u ", u[y*w+x]?b:!b);
		fputc(10, o);
	}
}

int ca(int *u, size_t w, size_t max, int rule)
{
	int x, t;
	for (t=0; t<max-1; t++) {
		for (x=0; x<w; x++) {
			int l = x==0? 0: u[t*w+x-1];
			int c = u[t*w+x];
			int r = x==w-1? 0: u[t*w+x+1];
			int n = (l<<2)|(c<<1)|(r<<0);
			u[(t+1)*w+x] = (rule&(1<<n))>>n;
		}
		if (u[t*w] && u[t*w+w-1]) break;
	}
	return t+1;
}

int main(int argc, const char **argv)
{
	int t, *u, b=1, w=W, r=30, h=0;
	FILE *out = stdout;
	char c[32];
	while (--argc > 0) {
		if (strcmp(argv[argc], "-h") == 0 || strcmp(argv[argc], "--help") == 0) 
			usage(argv[0]);
		else if (strcmp(argv[argc], "black") == 0) b = 0;
		else if (strcmp(argv[argc], "white") == 0) b = 1;
		else if (sscanf(argv[argc], "%c%u", c, &t) == 2 && *c == 'r' || *c == 'w') {
			if (*c == 'r') r = t;
			else if (*c == 'w') w = t;
		}
		else if (!(out = fopen(argv[argc], "w"))) {
			perror(argv[argc]); usage(argv[0]);
		}
	}

	h = w*3/2;
	u = malloc(w*h*sizeof(int));
	u[w/2] = 1;

	sprintf(c, "CA rule %u", r);
	t = ca(u, w, h, r);
	pbm(u, w, t, out, b, c);

	return 0;
}
