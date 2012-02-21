/*
 * dcal
 * 
 * A discordian calendar and date tool for the commandline.
 *
 *
 *  author: Remo Giermann
 * created: 2010/7/15
 * updates: 2010/7/20 calendar output
 */


#include <stdio.h>
#include <stdlib.h>
#include <string.h> 
#include <time.h>

/*
 * From here on read season == discordian month.
 */

#define G1900 1900
#define D1900 3066
#define YCONV 1166

#define isdiscyear(y) y > D1900
#define isgregyear(y) y > G1900 && y < D1900

// TIB(year)
// get discordian St. Tib's Day (leap year)
// year: gregorian year
// returns 1 if St. Tib's Day
#define TIB(year) (year % 4 == 0 && year % 100 != 0) || ( year % 400 == 0) ? 1 : 0

// YOLD(year)
// get the discordian Year of Our Lady Discord
// year: gregorian year
#define YOLD(year) (year + YCONV)

// YEAR(yold)
// get the gregorian year
// yold: discordian YOLD
#define YEAR(yold) (yold - YCONV)

// SDAY(tm_yday, tm_year)
// get the discordian day of the season 
// tm_yday: days since January 1
#define SDAY(tm_yday) (tm_yday + 1) % 73

// SEASON(tm_yday, tm_year)
// get the discordian season
// tm_yday: days since January 1
#define SEASON(tm_yday) (tm_yday + 1) / 73 

// DAY(tm_yday)
// get the discordian weekday (0...4, Setting Orange...Prickle-Prickle)
// tm_yday: days since January 1
#define DAY(tm_yday) (tm_yday + 1) % 5

#define SM 1
#define BT 2
#define PD 3
#define PP 4
#define SO 0

#define Chs 0
#define Dsc 1
#define Cfn 2
#define Bcy 3
#define Afm 4

#define SNAME(s) s == Chs ? "Chaos" : \
				(s == Dsc ? "Discord" : \
				(s == Cfn ? "Confusion" : \
				(s == Bcy ? "Bureaucracy" : \
				(s == Afm ? "Aftermath" : ""))))

void print_calendar_month(int today, int season, int seasonstart, int yold);
void print_calendar_year(int seasonstarts[], int yold);
void print_calendar_header(int season, int yold);
void print_calendar_days(int today, int shift, int tib);

void usage(const char* name)
{
    printf("USAGE: %s [YEAR]\n", name);
    printf("USAGE: %s [SEASON]\n", name);
    printf("USAGE: %s [YOLD [SEASON]]\n", name);
    printf("USAGE: %s [YEAR MONTH DAY]\n", name);
    printf("USAGE: %s [YOLD SEASON DAY]\n\n", name);
}

int main(int argc, const char *argv[]) 
{
    time_t rawtime;
    struct tm *timeinfo;
    char str[32];
    int yday, year, uyear, month, season, day;
    int seasonstart[5]   = {0, 3, 1, 4, 2}; // how many days after Sweetmorn a season starts

    time(&rawtime);
    timeinfo = localtime(&rawtime);

    if (argc == 1)
    {
        year  = timeinfo->tm_year;
        year += 1900;
        yday  = timeinfo->tm_yday;
        yday -= TIB(year);

        print_calendar_month(SDAY(yday), SEASON(yday), seasonstart[SEASON(yday)], YOLD(year));
    }
    else if (argc == 2)
    {
        if (!strcmp(argv[1], "help") || !strcmp(argv[1],"--help") || !strcmp(argv[1],"-h"))
        {
            usage(argv[0]);
            return 0;
        }
        else
            sscanf(argv[1], "%i", &uyear);

        if (isdiscyear(uyear))
            print_calendar_year(seasonstart, uyear);
        else if (isgregyear(uyear))
            print_calendar_year(seasonstart, YOLD(uyear));
        else if (uyear < 6 && uyear > 0)
            print_calendar_month(0, uyear-1, seasonstart[uyear-1], YOLD(timeinfo->tm_year+1900));
        else
        {
            fprintf(stderr, "ARGUMENT must be greater than 1900 (YEAR, YOLD) or smaller than 6 (SEASON).\n");
            return 1;
        }
    }
    else if (argc == 3)
    {
        sscanf(argv[1], "%i", &uyear);
        sscanf(argv[2], "%i", &season);

        if (isdiscyear(uyear) && season < 6 && season > 0)
            print_calendar_month(0, season-1, seasonstart[season-1], uyear);
        else
        {
            fprintf(stderr, "Date out of range, should be discordian YOLD and SEASON.\n");
            return 1;
        }
    }
    else if (argc == 4)
    {
        sscanf(argv[1], "%i", &uyear);
        sscanf(argv[2], "%i", &month);
        sscanf(argv[3], "%i", &day);

        if (isgregyear(uyear) && month < 13 && month > 0 && day < 32 && day > 0)
        {
            timeinfo->tm_year = uyear - 1900;
            timeinfo->tm_mon = month - 1;
            timeinfo->tm_mday = day;
            mktime(timeinfo);
            year  = timeinfo->tm_year;
            year += 1900;
            yday  = timeinfo->tm_yday;
            if (yday > 0)
                yday -= TIB(year);

            print_calendar_month(SDAY(yday), SEASON(yday), seasonstart[SEASON(yday)], YOLD(year));
        }
        else if (isdiscyear(uyear) && month < 6 && month > 0 && day < 74 && day > 0)
            print_calendar_month(day, month-1, seasonstart[month-1], uyear);
        else 
        {
            fprintf(stderr, "Date out of range, should be gregorian YEAR, MONTH and DAY or discordian YOLD, SEASON and DAY.\n");
            return 1;
        }

    }
    return 0;
}

void print_calendar_month(int today, int season, int seasonstart, int yold)
{
    int tib = 0;
    if (season == Chs && TIB(YEAR(yold)))
        tib = 1;
    print_calendar_header(season, yold);
    print_calendar_days(today, seasonstart, tib);
}

void print_calendar_year(int seasonstarts[], int yold)
{
    int i;
    for (i=0; i < 5; i++)
        print_calendar_month(0, i, seasonstarts[i], yold);
}

void print_calendar_header(int season, int yold)
{
    printf("\n  %s, %i\n", SNAME(season), yold);
    printf(" SM     BT     PD     PP     SO\n");
}

void print_calendar_days(int today, int shift, int tib) 
{
    int i;
    for (i=1; i < 80; i++)
    {
        if ((i - shift) < 1)
            printf("       ");
        else if ((i - shift) > 73)
            break;
        else
        {
            if ((i - shift) == today)
                printf("[%2i] ", i-shift);
            else
                printf("%3i  ", i-shift);
            if (tib == 1 && (i - shift) == 59)
                printf("T ");
            else
                printf("  ");

            if (i%5 == 0 && (i - shift != 73))
                printf("\n");
        }
    }
    printf("\n");
    return;
}
