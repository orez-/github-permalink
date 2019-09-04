import argparse
import json
import re
import shutil
import subprocess
import sys

import dateparser
import requests


def _fetch_commits_before_hub(url):
    try:
        result = subprocess.run(
            ['hub', 'api', url, '-H', 'Accept: application/vnd.github.cloak-preview'],
            check=True,
            capture_output=True,
            encoding='utf8',
        )
    except subprocess.CalledProcessError as exc:
        print(exc.stdout)
        print(exc.stderr)
        sys.exit(1)
    return json.loads(result.stdout)


def _fetch_commits_before_api(url):
    response = requests.get(url, headers={"Accept": "application/vnd.github.cloak-preview"})
    try:
        response.raise_for_status()
    except Exception:
        print(response.text)
        sys.exit(1)
    return response.json()


def fetch_commits_before(repo, timestamp):
    url = f'https://api.github.com/search/commits?q=committer-date:<{timestamp}+repo:{repo}&sort=committer-date'
    if shutil.which('hub'):
        return _fetch_commits_before_hub(url)
    return _fetch_commits_before_api(url)


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
