from giturlparse import parse


def construct_template_url(repo_address, branch):
    branch = branch or ''
    user, repo = _parse_repo_url(repo_address)
    download_url = _join_url_all("https://api.github.com/repos", [user, repo, 'zipball', branch])
    return download_url


def _parse_repo_url(url):
    success, user, repo = _try_parse_git_url(url)
    if not success:
        success, user, repo = _try_parse_http_url(url)

    return user, repo


def _try_parse_git_url(url):
    if url.startswith('git@'):
        parsed_repo = parse(url)
        return True, parsed_repo.owner, parsed_repo.repo
    else:
        return False, None, None


def _try_parse_http_url(url):
    if url.startswith('http'):
        fragments = url.split("/")
        return True, fragments[-2], fragments[-1]
    else:
        return False, None, None


def _join_url_all(url, fragments):
    return '/'.join([url] + [fragment for fragment in fragments if fragment])
