import json
import os
from datetime import datetime
from typing import Any
import httpx
from pydantic import SecretStr
from openhands.core.logger import openhands_logger as logger
from openhands.integrations.github.queries import (
    suggested_task_issue_graphql_query,
    suggested_task_pr_graphql_query,
)
from openhands.integrations.service_types import (
    BaseGitService,
    Branch,
    GitService,
    ProviderType,
    Repository,
    RequestMethod,
    SuggestedTask,
    TaskType,
    UnknownException,
    User,
)
from openhands.server.types import AppMode
from openhands.utils.import_utils import get_impl
class GitHubService(BaseGitService, GitService):
    """Default implementation of GitService for GitHub integration.
    TODO: This doesn't seem a good candidate for the get_impl() pattern. What are the abstract methods we should actually separate and implement here?
    This is an extension point in OpenHands that allows applications to customize GitHub
    integration behavior. Applications can substitute their own implementation by:
    1. Creating a class that inherits from GitService
    2. Implementing all required methods
    3. Setting server_config.github_service_class to the fully qualified name of the class
    The class is instantiated via get_impl() in openhands.server.shared.py.
    """
    BASE_URL = 'https://api.github.com'
    token: SecretStr = SecretStr('')
    refresh = False
    def __init__(
        self,
        user_id: str | None = None,
        external_auth_id: str | None = None,
        external_auth_token: SecretStr | None = None,
        token: SecretStr | None = None,
        external_token_manager: bool = False,
        base_domain: str | None = None,
    ):
        self.user_id = user_id
        self.external_token_manager = external_token_manager
        if token:
            self.token = token
        if base_domain and base_domain != 'github.com':
            self.BASE_URL = f'https://{base_domain}/api/v3'
        self.external_auth_id = external_auth_id
        self.external_auth_token = external_auth_token
    @property
    def provider(self) -> str:
        return ProviderType.GITHUB.value
    async def _get_github_headers(self) -> dict:
        """Retrieve the GH Token from settings store to construct the headers."""
        if not self.token:
            self.token = await self.get_latest_token()
        return {
            'Authorization': f'Bearer {self.token.get_secret_value() if self.token else ""}',
            'Accept': 'application/vnd.github.v3+json',
        }
    def _has_token_expired(self, status_code: int) -> bool:
        return status_code == 401
    async def get_latest_token(self) -> SecretStr | None:
        return self.token
    async def _make_request(
        self,
        url: str,
        params: dict | None = None,
        method: RequestMethod = RequestMethod.GET,
    ) -> tuple[Any, dict]:
        try:
            async with httpx.AsyncClient() as client:
                github_headers = await self._get_github_headers()
                response = await self.execute_request(
                    client=client,
                    url=url,
                    headers=github_headers,
                    params=params,
                    method=method,
                )
                if self.refresh and self._has_token_expired(response.status_code):
                    await self.get_latest_token()
                    github_headers = await self._get_github_headers()
                    response = await self.execute_request(
                        client=client,
                        url=url,
                        headers=github_headers,
                        params=params,
                        method=method,
                    )
                response.raise_for_status()
                headers = {}
                if 'Link' in response.headers:
                    headers['Link'] = response.headers['Link']
                return response.json(), headers
        except httpx.HTTPStatusError as e:
            raise self.handle_http_status_error(e)
        except httpx.HTTPError as e:
            raise self.handle_http_error(e)
    async def get_user(self) -> User:
        url = f'{self.BASE_URL}/user'
        response, _ = await self._make_request(url)
        return User(
            id=str(response.get('id', '')),
            login=response.get('login'),
            avatar_url=response.get('avatar_url'),
            company=response.get('company'),
            name=response.get('name'),
            email=response.get('email'),
        )
    async def verify_access(self) -> bool:
        """Verify if the token is valid by making a simple request."""
        url = f'{self.BASE_URL}'
        await self._make_request(url)
        return True
    async def _fetch_paginated_repos(
        self, url: str, params: dict, max_repos: int, extract_key: str | None = None
    ) -> list[dict]:
        """
        Fetch repositories with pagination support.
        Args:
            url: The API endpoint URL
            params: Query parameters for the request
            max_repos: Maximum number of repositories to fetch
            extract_key: If provided, extract repositories from this key in the response
        Returns:
            List of repository dictionaries
        """
        repos: list[dict] = []
        page = 1
        while len(repos) < max_repos:
            page_params = {**params, 'page': str(page)}
            response, headers = await self._make_request(url, page_params)
            page_repos = response.get(extract_key, []) if extract_key else response
            if not page_repos:
                break
            repos.extend(page_repos)
            page += 1
            link_header = headers.get('Link', '')
            if 'rel="next"' not in link_header:
                break
        return repos[:max_repos]
    def parse_pushed_at_date(self, repo):
        ts = repo.get('pushed_at')
        return datetime.strptime(ts, '%Y-%m-%dT%H:%M:%SZ') if ts else datetime.min
    async def get_repositories(self, sort: str, app_mode: AppMode) -> list[Repository]:
        MAX_REPOS = 1000
        PER_PAGE = 100
        all_repos: list[dict] = []
        if app_mode == AppMode.SAAS:
            installation_ids = await self.get_installation_ids()
            for installation_id in installation_ids:
                params = {'per_page': str(PER_PAGE)}
                url = (
                    f'{self.BASE_URL}/user/installations/{installation_id}/repositories'
                )
                installation_repos = await self._fetch_paginated_repos(
                    url, params, MAX_REPOS - len(all_repos), extract_key='repositories'
                )
                all_repos.extend(installation_repos)
                if len(all_repos) >= MAX_REPOS:
                    break
            if sort == 'pushed':
                all_repos.sort(key=self.parse_pushed_at_date, reverse=True)
        else:
            params = {'per_page': str(PER_PAGE), 'sort': sort}
            url = f'{self.BASE_URL}/user/repos'
            all_repos = await self._fetch_paginated_repos(url, params, MAX_REPOS)
        return [
            Repository(
                id=str(repo.get('id')),
                full_name=repo.get('full_name'),
                stargazers_count=repo.get('stargazers_count'),
                git_provider=ProviderType.GITHUB,
                is_public=not repo.get('private', True),
            )
            for repo in all_repos
        ]
    async def get_installation_ids(self) -> list[int]:
        url = f'{self.BASE_URL}/user/installations'
        response, _ = await self._make_request(url)
        installations = response.get('installations', [])
        return [i['id'] for i in installations]
    async def search_repositories(
        self, query: str, per_page: int, sort: str, order: str
    ) -> list[Repository]:
        url = f'{self.BASE_URL}/search/repositories'
        query_with_visibility = f'{query} is:public'
        params = {
            'q': query_with_visibility,
            'per_page': per_page,
            'sort': sort,
            'order': order,
        }
        response, _ = await self._make_request(url, params)
        repo_items = response.get('items', [])
        repos = [
            Repository(
                id=str(repo.get('id')),
                full_name=repo.get('full_name'),
                stargazers_count=repo.get('stargazers_count'),
                git_provider=ProviderType.GITHUB,
                is_public=True,
            )
            for repo in repo_items
        ]
        return repos
    async def execute_graphql_query(
        self, query: str, variables: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute a GraphQL query against the GitHub API."""
        try:
            async with httpx.AsyncClient() as client:
                github_headers = await self._get_github_headers()
                response = await client.post(
                    f'{self.BASE_URL}/graphql',
                    headers=github_headers,
                    json={'query': query, 'variables': variables},
                )
                response.raise_for_status()
                result = response.json()
                if 'errors' in result:
                    raise UnknownException(
                        f'GraphQL query error: {json.dumps(result["errors"])}'
                    )
                return dict(result)
        except httpx.HTTPStatusError as e:
            raise self.handle_http_status_error(e)
        except httpx.HTTPError as e:
            raise self.handle_http_error(e)
    async def get_suggested_tasks(self) -> list[SuggestedTask]:
        """Get suggested tasks for the authenticated user across all repositories.
        Returns:
        - PRs authored by the user.
        - Issues assigned to the user.
        Note: Queries are split to avoid timeout issues.
        """
        user = await self.get_user()
        login = user.login
        tasks: list[SuggestedTask] = []
        variables = {'login': login}
        try:
            pr_response = await self.execute_graphql_query(
                suggested_task_pr_graphql_query, variables
            )
            pr_data = pr_response['data']['user']
            for pr in pr_data['pullRequests']['nodes']:
                repo_name = pr['repository']['nameWithOwner']
                task_type = TaskType.OPEN_PR
                if pr['mergeable'] == 'CONFLICTING':
                    task_type = TaskType.MERGE_CONFLICTS
                elif (
                    pr['commits']['nodes']
                    and pr['commits']['nodes'][0]['commit']['statusCheckRollup']
                    and pr['commits']['nodes'][0]['commit']['statusCheckRollup'][
                        'state'
                    ]
                    == 'FAILURE'
                ):
                    task_type = TaskType.FAILING_CHECKS
                elif any(
                    review['state'] in ['CHANGES_REQUESTED', 'COMMENTED']
                    for review in pr['reviews']['nodes']
                ):
                    task_type = TaskType.UNRESOLVED_COMMENTS
                if task_type != TaskType.OPEN_PR:
                    tasks.append(
                        SuggestedTask(
                            git_provider=ProviderType.GITHUB,
                            task_type=task_type,
                            repo=repo_name,
                            issue_number=pr['number'],
                            title=pr['title'],
                        )
                    )
        except Exception as e:
            logger.info(
                f'Error fetching suggested task for PRs: {e}',
                extra={
                    'signal': 'github_suggested_tasks',
                    'user_id': self.external_auth_id,
                },
            )
        try:
            issue_response = await self.execute_graphql_query(
                suggested_task_issue_graphql_query, variables
            )
            issue_data = issue_response['data']['user']
            for issue in issue_data['issues']['nodes']:
                repo_name = issue['repository']['nameWithOwner']
                tasks.append(
                    SuggestedTask(
                        git_provider=ProviderType.GITHUB,
                        task_type=TaskType.OPEN_ISSUE,
                        repo=repo_name,
                        issue_number=issue['number'],
                        title=issue['title'],
                    )
                )
            return tasks
        except Exception as e:
            logger.info(
                f'Error fetching suggested task for issues: {e}',
                extra={
                    'signal': 'github_suggested_tasks',
                    'user_id': self.external_auth_id,
                },
            )
        return tasks
    async def get_repository_details_from_repo_name(
        self, repository: str
    ) -> Repository:
        url = f'{self.BASE_URL}/repos/{repository}'
        repo, _ = await self._make_request(url)
        return Repository(
            id=str(repo.get('id')),
            full_name=repo.get('full_name'),
            stargazers_count=repo.get('stargazers_count'),
            git_provider=ProviderType.GITHUB,
            is_public=not repo.get('private', True),
        )
    async def get_branches(self, repository: str) -> list[Branch]:
        """Get branches for a repository"""
        url = f'{self.BASE_URL}/repos/{repository}/branches'
        MAX_BRANCHES = 1000
        PER_PAGE = 100
        all_branches: list[Branch] = []
        page = 1
        while page <= 10 and len(all_branches) < MAX_BRANCHES:
            params = {'per_page': str(PER_PAGE), 'page': str(page)}
            response, headers = await self._make_request(url, params)
            if not response:
                break
            for branch_data in response:
                last_push_date = None
                if branch_data.get('commit') and branch_data['commit'].get('commit'):
                    commit_info = branch_data['commit']['commit']
                    if commit_info.get('committer') and commit_info['committer'].get(
                        'date'
                    ):
                        last_push_date = commit_info['committer']['date']
                branch = Branch(
                    name=branch_data.get('name'),
                    commit_sha=branch_data.get('commit', {}).get('sha', ''),
                    protected=branch_data.get('protected', False),
                    last_push_date=last_push_date,
                )
                all_branches.append(branch)
            page += 1
            link_header = headers.get('Link', '')
            if 'rel="next"' not in link_header:
                break
        return all_branches
    async def create_pr(
        self,
        repo_name: str,
        source_branch: str,
        target_branch: str,
        title: str,
        body: str | None = None,
        draft: bool = True,
    ) -> str:
        """
        Creates a PR using user credentials
        Args:
            repo_name: The full name of the repository (owner/repo)
            source_branch: The name of the branch where your changes are implemented
            target_branch: The name of the branch you want the changes pulled into
            title: The title of the pull request (optional, defaults to a generic title)
            body: The body/description of the pull request (optional)
            draft: Whether to create the PR as a draft (optional, defaults to False)
        Returns:
            - PR URL when successful
            - Error message when unsuccessful
        """
        url = f'{self.BASE_URL}/repos/{repo_name}/pulls'
        if not body:
            body = f'Merging changes from {source_branch} into {target_branch}'
        payload = {
            'title': title,
            'head': source_branch,
            'base': target_branch,
            'body': body,
            'draft': draft,
        }
        response, _ = await self._make_request(
            url=url, params=payload, method=RequestMethod.POST
        )
        return response['html_url']
github_service_cls = os.environ.get(
    'OPENHANDS_GITHUB_SERVICE_CLS',
    'openhands.integrations.github.github_service.GitHubService',
)
GithubServiceImpl = get_impl(GitHubService, github_service_cls)