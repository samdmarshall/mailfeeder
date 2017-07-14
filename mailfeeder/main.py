import os
import sys
import uuid
import email
import argparse
import datetime
import ConfigParser

import notmuch
import PyRSS2Gen

def flatten_body(msg):
    body = ""
    data = msg.get_payload()
    if type(data) == list:
        for item in data:
            body += flatten_body(item)
    else:
        body += data
    body = body.replace('=\n', '')
    return body

def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        '--configuration',
        help='configuration file to use',
        action='store',
    )
    parser.add_argument(
        'output',
        help='directory to write feeds into',
        metavar='<feed directory>',
        action='store',
    )

    args = parser.parse_args()

    configuration = ConfigParser.ConfigParser()
    configuration.read(args.configuration)
    os.environ['NOTMUCH_CONFIG'] = os.path.expanduser(configuration.get('settings', 'notmuch_config'))
    database = notmuch.Database()

    for name in configuration.sections():
        if name == 'settings': continue
        
        message_query = notmuch.Query(database, configuration.get(name, 'query'))
        message_query.set_sort(notmuch.Query.SORT.NEWEST_FIRST)
        messages = message_query.search_messages()
        feed_items = []
        for message in messages:
            item_contents = ""
            for file_path in message.get_filenames():
                msg = email.message_from_file(open(file_path, 'r'))
                item_contents += "\n"
                item_contents += flatten_body(msg)
            item = PyRSS2Gen.RSSItem(
                title = message.get_header("Subject"),
                description = item_contents,
                guid = PyRSS2Gen.Guid(message.get_message_id()),
            )
            feed_items.append(item)

        feed = PyRSS2Gen.RSS2(
            title = configuration.get(name, 'name'),
            link = configuration.get('settings', 'root') + '/' + name + '.xml',
            description = configuration.get(name, 'description'),
            lastBuildDate = datetime.datetime.now(),
            items = feed_items
        )

        feed_path = os.path.join(args.output, name+'.xml')
        feed.write_xml(open(feed_path, 'w+'))
    

if __name__ == '__main__':
    main()
