import os
import re
import sys
from rich import print
from urllib.parse import urlparse

# print(f"parser: {__name__=}")

def parse_url(url: str) -> tuple[str, str]:

    url = url.strip()

    # strip .git
    if url.endswith(".git"):
        url = url[:-4]

    parsed: dict | None = None

    if url.startswith("git@"):  # SSH URL
        # git@host:path/to/repo.git
        SSH_PATTERN = r"git@([^:]+):(.+)"
        match = re.match(SSH_PATTERN, url)
        if match:
            host, path = match.groups()
            parsed = {"domain": host, "repo_path": path}
        # else => None (invalid git@ url)
    elif url.startswith("https://"):  # HTTPS or similar
        url_parsed = urlparse(url)
        path = url_parsed.path.lstrip("/")  # Remove leading '/'
        path = path.rstrip("/")  # Remove trailing '/' => wcl https://github.com/Hammerspoon/Spoons/

        # org/repo/blob/branch/path/to/file, strip blob+ (must have org/repo before blob)
        # PRN if it happens to be that a repo is named blob/tree then we have issues!
        if re.search(r"[^/]+/[^/]+/(blob|tree)/", path):
            path = re.sub(r"/(blob|tree).*", "", path)

        parsed = {"domain": url_parsed.netloc, "repo_path": path}
    elif not re.search(r"\/", url):
        # url = "dotfiles"
        #   => github.com:g0t4/{url}
        parsed = {"domain": "github.com", "repo_path": "g0t4/" + url}
    elif re.search(r"\/", url):
        # url = "g0t4/dotfiles"
        #   => github.com:g0t4/dotfiles
        # 2+ levels (obviously github only has two: org/repo)
        parsed = {"domain": "github.com", "repo_path": url}

    if not parsed:
        print("unable to parse repository url", url, "\n")
        sys.exit(1)

    host_name = parsed["domain"]
    if host_name == "github.com":
        host_name = "github"
    elif host_name == "gitlab.com":
        host_name = "gitlab"
    elif host_name == "bitbucket.org":
        host_name = "bitbucket"

    repo_dir = os.path.expanduser(os.path.join("~/repos", host_name, parsed["repo_path"]))

    always_use_https = parsed["domain"] in ["gitlab.gnome.org", "sourceware.org", "git.kernel.org", "huggingface.co", "git.sr.ht"]
    if always_use_https:
        clone_from = f"https://{parsed["domain"]}/{parsed["repo_path"]}"
    else:
        # prefer ssh for git repos (simple, standard, supports ssh auth)
        clone_from = f"git@{parsed["domain"]}:{parsed["repo_path"]}"

    return repo_dir, clone_from

if __name__ == "__main__":
    from unittest import TestCase

    _test = TestCase()

    repo_dir, _ = parse_url("https://gitlab.com/g0t4/dotfiles.git")
    _test.assertEqual(repo_dir, "/Users/wesdemos/repos/gitlab/g0t4/dotfiles")

    repo_dir, _ = parse_url("https://huggingface.co/datasets/PleIAs/common_corpus/tree/main")
    _test.assertEqual(repo_dir, "/Users/wesdemos/repos/huggingface.co/datasets/PleIAs/common_corpus")

    print("testing done")

