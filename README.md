# reddit-dl
download reddit data from pushshift.io

## Installation
```
git clone https://github.com/tapilab/reddit-dl.git
cd reddit-dl
pip install -r requirements.txt
```

## Usage
```
% python dl.py --help
usage: dl.py [-h] [-o FILE] [-b year-month] [-e year-month] [-s SUBREDDITS] [-p] [--no-posts] [-c] [--no-comments]

Fetch reddit posts from pushshift.io

optional arguments:
  -h, --help            show this help message and exit
  -o FILE, --output FILE
                        File name prefix to write output file. (default: out)
  -b year-month, --begin year-month
                        year-month to start crawl from (e.g., 2006-01). (default: 2005-06)
  -e year-month, --end year-month
                        year-month to end crawl to (e.g., 2006-12). If empty, crawl to today. (default: )
  -s SUBREDDITS, --subreddits SUBREDDITS
                        comma separated list of subreddits to collect (e.g., news,politics) (default: )
  -p, --posts           Collect posts. (default: True)
  --no-posts            Don't collect posts. (default: True)
  -c, --comments        Collect comments. (default: True)
  --no-comments         Don't collect comments. (default: True)
```

E.g., get `politics` and `features` subreddits from Dec 2008-Jan 2009:

```
% python3 dl.py -b 2008-12 -e 2009-01 -s politics,features
collecting subreddits ['politics', 'features'] from 2008-12 to 2009-01
12-2008
...fetching posts
.....matched 14226/283916
...fetching comments
.....matched 67176/850360

in total, matched 14226/283916 posts and 67176/850360 comments

01-2009
...fetching posts
.....matched 18327/331061
...fetching comments
.....matched 86497/1051650

in total, matched 32553/614977 posts and 153673/1902010 comments

% wc -l out-*
  153673 out-comments.json
   32553 out-posts.json
  186226 total
```

E.g., just `politics` posts (no comments) for Jan 2009:

```
% python3 dl.py -b 2009-01 -e 2009-01 --no-comments -s politics         
collecting subreddits ['politics'] from 2009-01 to 2009-01
01-2009
...fetching posts
.....matched 18327/331061

in total, matched 18327/331061 posts and 0/0 comments

% wc -l out-*                                                  
       0 out-comments.json
   18327 out-posts.json
   18327 total
```