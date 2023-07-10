import argparse
from datetime import datetime
import json
import traceback
from urllib.request import urlopen
import zstandard

def yield_lines(url):
    resp = urlopen(url)
    reader = zstandard.ZstdDecompressor(max_window_size=2**31).stream_reader(resp)
    buffer = ''
    while True:
        try:
            chunk = reader.read(2**10).decode()
            if not chunk:
                break
            lines = (buffer + chunk).split("\n")
            for line in lines[:-1]:
                yield line
            buffer = lines[-1]      
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            print(line)
            break
    yield from buffer.split('\n')
        
def fetch_by_subreddit(kind, handle, subreddits, month, year, local_path):
    ct = 0
    lines = 0
    prefix = local_path if 'file:///' + local_path else "https://files.pushshift.io/reddit"
    for line in yield_lines("%s/%s/R%s_%s-%s.zst" % 
                            (prefix, kind, 'S' if kind=='submissions' else 'C', year, month)):
        lines += 1
        try:
            if len(line.strip()) > 0:
                j = json.loads(line)
                if len(subreddits) == 0 or ('subreddit' in j and j['subreddit'].lower() in subreddits):
                    ct += 1
                    if ct % 500 == 0:
                        print('.....matched %d/%d' % (ct, lines), end='\r')
                    handle.write(line)
                    handle.write("\n")
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            print(line)
    print('.....matched %d/%d' % (ct, lines), end='\r')            
    print()
    return ct, lines
        
def main():
    parser = argparse.ArgumentParser(description = "Fetch reddit posts from pushshift.io",
                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
 
    parser.add_argument("-o", "--output", type = str,
                        metavar = "FILE", default = 'out',
                        help = "File name prefix to write output file.")
    parser.add_argument("-b", "--begin", type = str,
                        metavar = "year-month", default = '2005-06',
                        help = "year-month to start crawl from (e.g., 2006-01).")
    parser.add_argument("-e", "--end", type = str,
                        metavar = "year-month", default = '',
                        help = "year-month to end crawl to (e.g., 2006-12). If empty, crawl to today.")
    parser.add_argument("-s", "--subreddits", default='',
                        help="comma separated list of subreddits to collect (e.g., news,politics)")
    parser.add_argument("-p", "--posts", default=True, action="store_true",
                        help="Collect posts.")
    parser.add_argument('--no-posts', dest='posts', action='store_false',
                        help="Don't collect posts.")
    parser.add_argument("-c", "--comments", default=True, action="store_true",
                        help="Collect comments.")
    parser.add_argument('--no-comments', dest='comments', action='store_false',
                        help="Don't collect comments.")
    parser.add_argument("-l", "--local-path", type = str,
                        metavar = "FILE", default = None,
                        help = "Rather than fetch from pushshift, extract from a local mirror specified by this path (e.g., ./reddit)")


    args = parser.parse_args()
    begin = args.begin
    end = args.end
    subreddits = [] if len(args.subreddits.strip()) == 0 else args.subreddits.strip().split(',')
    outfile = args.output
    post_handle = open('%s-posts.json' % outfile, 'w')
    comment_handle = open('%s-comments.json' % outfile, 'w')
    year_s, month_s = begin.split('-')
    if end == '':
        year_e = str(datetime.now().year)
        month_e = str(datetime.now().month).zfill(2)
        end = '%s-%s' % (year_e, month_e)
    else:
        year_e, month_e = end.split('-')
    year, month = year_s, month_s
    print('collecting subreddits %s from %s-%s to %s-%s' % (subreddits, year_s, month_s, year_e, month_e))
    matched_posts = 0
    total_posts = 0
    matched_comments = 0
    total_comments = 0
    while True:
        print('%s-%s' % (month, year))
        if args.posts:
            print('...fetching posts')
            mp, tp = fetch_by_subreddit('submissions', post_handle, subreddits, month, year, args.local_path)
            matched_posts += mp
            total_posts += tp
        if args.comments:
            print('...fetching comments')
            mc, tc = fetch_by_subreddit('comments', comment_handle, subreddits, month, year, args.local_path)
            matched_comments += mc
            total_comments += tc
        print('\nin total, matched %d/%d posts and %d/%d comments\n' % 
              (matched_posts, total_posts, matched_comments, total_comments))
        month = int(month)+1
        if month > 12:
            month = 1
            year = int(year) + 1
        month = str(month).zfill(2)
        if '%s-%s' % (year, month) > end:
            break

 
if __name__ == "__main__":
    # calling the main function
    main()