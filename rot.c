#define rot(a) \
(a>='a'&&a<='m'? a+13: a>='A'&&a<='M'? a+13: \
 a>='N'&&a<='Z'? a-13: a>='n'&&a<='z'? a-13: \
 a>='!'&&a<= 39? a+ 7: a>='('&&a<='/'? a- 7: \
 a>='0'&&a<='4'? a+ 5: a>='5'&&a<='9'? a- 5: \
 a>=':'&&a<='<'? a+ 3: a>='='&&a<='@'? a- 3: a)
int main() { char c; while((c=getchar())>0) putchar(rot(c)); return 0;}
