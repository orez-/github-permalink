import argparse
import re

import dateparser
import requests


def fetch_commits_before(repo, timestamp):
    response = requests.get(
        f'https://api.github.com/search/commits?q=committer-date:<{timestamp}+repo:{repo}&sort=committer-date',
        headers={"Accept": "application/vnd.github.cloak-preview"},
    )
    response.raise_for_status()
    return response.json()


def get_commit_hash_before(repo, timestamp):
    results = fetch_commits_before(repo, timestamp)
    return results['items'][0]['sha']


def get_url_at_time(url, timestamp):
    match = re.fullmatch(
        r"(?P<front>.*github.com/(?P<repo>[^/]+/[^/]+)/blob/)[^/]+(?P<path>/.*)", url
    )
    sha = get_commit_hash_before(match['repo'], timestamp)
    return f"{match['front']}{sha}{match['path']}"


def normalize_timestamp(timestamp):
    date = dateparser.parse(timestamp)
    return date.strftime("%Y-%m-%d")


def main():
    parser = argparse.ArgumentParser(
        description="convert a GitHub code link into a permalink, retroactively"
    )
    parser.add_argument("url", help="the link to convert")
    parser.add_argument(
        "timestamp", help="the estimated date and time at which the link was created"
    )
    args = parser.parse_args()

    timestamp = normalize_timestamp(args.timestamp)
    print(get_url_at_time(args.url, timestamp))


if __name__ == '__main__':
    main()
