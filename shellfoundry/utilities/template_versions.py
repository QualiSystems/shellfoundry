import ast
import requests
import shellfoundry.exceptions as exc

VERSIONS_URL = 'https://api.github.com/repos/{}/{}/branches'
NAME_PLACEHOLDER = 'name'


class TemplateVersions(object):
    def __init__(self, url_user, url_repo):
        self.template_repo = [url_user, url_repo]

    def get_versions_of_template(self):
        '''
        Get all versions (branches) of a given template.
        Raises HTTPError on request fail, NoVersionsHaveBeenFoundException when no versions have been found
        :return: List filled with version names (e.g. 1.0, 1.1, 2.0...)
        '''
        response = requests.get(VERSIONS_URL.format(*self.template_repo))
        if response.status_code != requests.codes.ok:
            raise requests.HTTPError('Failed to receive versions from host')

        response_arr = ast.literal_eval(response.text)
        branches = [d[NAME_PLACEHOLDER] for d in response_arr]
        branches.sort(reverse=True)
        if not self.has_versions(branches):
            raise exc.NoVersionsHaveBeenFoundException("No versions has been found for this template")
        return branches

    @staticmethod
    def has_versions(branches):
        first_branch = next(iter(branches or []), None)
        return first_branch is not None
