import os
import sys
import argparse
import datetime
import ConfigParser

import notmuch
import PyRSS2Gen

def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        '--configuration',
        help='configuration file to use',
        action='store',
    )
    parser.add_argument(
        'mailbox',
        help='directory containing the notmuch mail database',
        metavar='<notmuch db path>',
        action='store',
    )
    parser.add_argument(
        'output',
        help='directory to write feeds into',
        metavar='<feed directory>',
        action='store',
    )

    args = parser.parse_args()

    configuration = ConfigParser.ConfigParser(args.configuration)
    database = notmuch.Database(args.mailbox)

    for (name, options) in configurion.items():
        if name == 'settings': continue
        
        message_query = notmuch.Query(database, configuration.get(name, 'query')).search_messages()
        feed_items = []
        for message in message_query:
            print(message)

        feed = PyRSS2Gen.RSS2(
            title = configuration.get(name, 'name'),
            link = configuration.get('settings', 'root') + '/' + name + '.xml',
            description = configuration.get(name, 'description'),
            lastBuildDate = datetime.datetime.now(),
            items = feed_items
        )

        print(feed)
#        feed_path = os.path.join(args.output, name+'.xml')
#        feed.write_xml(open(feed_path, 'w+'))
    

if __name__ == '__main__':
    main()
