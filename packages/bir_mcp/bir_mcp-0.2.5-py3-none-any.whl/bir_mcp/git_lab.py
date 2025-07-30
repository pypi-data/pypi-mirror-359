import base64
import inspect
import zoneinfo
from typing import Annotated

import fastmcp.tools
import git
import gitlab
import mcp
import pydantic

from bir_mcp.utils import filter_dict_by_keys, format_datetime_for_ai, to_fastmcp_tool

RepoUrlType = Annotated[
    str,
    pydantic.Field(
        description=inspect.cleandoc("""
            The url of a GitLab repo that identifies a project in the following format:
            "https://{base_gitlab_url}/{project_path}/.git", for example:
            "https://gitlab.com/organization/namespace/project/.git"
        """)
    ),
]
BranchType = Annotated[
    str,
    pydantic.Field(description="The branch to fetch files from."),
]


def get_local_repo_metadata(
    repo_path: Annotated[str, pydantic.Field(description="The filesystem path to the repo.")],
) -> dict:
    """Retrieves metadata about the Git repo in the local filesystem, such as branch names and remote urls."""
    repo = git.Repo(repo_path, search_parent_directories=True)
    branch_names = [b.name for b in repo.branches]
    remotes = [{"name": r.name, "urls": list(r.urls)} for r in repo.remotes]
    metadata = {
        "remotes": remotes,
        "branch_names": branch_names,
        "active_branch_name": repo.active_branch.name,
    }
    return metadata


class GitLab:
    def __init__(
        self,
        url: str,
        private_token: str,
        timezone: str = "UTC",
        tag: str = "gitlab",
        max_output_length: int | None = None,
        ssl_verify: bool | str = True,
    ):
        self.gitlab = gitlab.Gitlab(
            url=url,
            private_token=private_token,
            ssl_verify=ssl_verify,
        )
        self.gitlab.auth()
        self.timezone = zoneinfo.ZoneInfo(timezone)
        self.tag = tag
        self.max_output_length = max_output_length

    def get_mcp_tools(self) -> list[fastmcp.tools.FunctionTool]:
        tools = [
            get_local_repo_metadata,
            self.get_project_metadata,
            self.list_all_repo_branch_files,
            self.get_file_content,
            self.search_in_repository,
            self.get_latest_pipeline_info,
        ]
        tools = [
            to_fastmcp_tool(
                tool,
                tags={self.tag},
                annotations=mcp.types.ToolAnnotations(readOnlyHint=True, destructiveHint=False),
                max_output_length=self.max_output_length,
            )
            for tool in tools
        ]
        return tools

    def build_mcp_server(self) -> fastmcp.FastMCP:
        tools = self.get_mcp_tools()
        server = fastmcp.FastMCP(
            name="Bir GitLab MCP server",
            instructions=inspect.cleandoc("""
                GitLab related tools.
            """),
            tools=tools,
        )
        return server

    def extract_project_path_from_url(self, url: str) -> str:
        url = url.removeprefix(self.gitlab.url)
        url = url.removesuffix(".git")
        url = url.strip("/")
        return url

    def get_project_from_url(self, url: str):
        project_path = self.extract_project_path_from_url(url)
        project = self.gitlab.projects.get(project_path)
        return project

    def get_project_metadata(self, repo_url: RepoUrlType) -> dict:
        """
        Retrieves metadata about a GitLab project identified by the repo url,
        such as name, description, last activity, topics (tags), etc.
        """
        project = self.get_project_from_url(repo_url)
        metadata = {
            "name_with_namespace": project.name_with_namespace,
            "topics": project.topics,
            "description": project.description,
            "last_activity_at": format_datetime_for_ai(
                project.last_activity_at, timezone=self.timezone
            ),
            "web_url": project.web_url,
        }
        return metadata

    def list_all_repo_branch_files(
        self,
        repo_url: RepoUrlType,
        branch: BranchType,
    ) -> dict:
        """Recursively lists all files and directories in the repository."""
        project = self.get_project_from_url(repo_url)
        tree = project.repository_tree(ref=branch, get_all=True, recursive=True)
        tree = {"files": [{"path": item["path"], "type": item["type"]} for item in tree]}
        return tree

    def get_file_content(
        self,
        repo_url: RepoUrlType,
        branch: BranchType,
        file_path: Annotated[
            str,
            pydantic.Field(
                description="The path to the file relative to the root of the repository."
            ),
        ],
    ) -> str:
        """Retrieves the text content of a specific file."""
        project = self.get_project_from_url(repo_url)
        file = project.files.get(file_path=file_path, ref=branch)
        content = base64.b64decode(file.content).decode()
        return content

    def search_in_repository(
        self,
        repo_url: RepoUrlType,
        branch: BranchType,
        query: Annotated[
            str,
            pydantic.Field(description="The text query to search for."),
        ],
    ) -> dict:
        """
        Performs a basic search for a text query within the repo's files.
        Doesn't support regex, but is case-insensitive.
        Returns a list of occurences within files, with file path, starting line in the file
        and a snippet of the contextual window in which the query was found.
        For details see the [API docs](https://docs.gitlab.com/api/search/#project-search-api).
        """
        project = self.get_project_from_url(repo_url)
        results = project.search(scope="blobs", search=query, ref=branch)
        results = [
            {
                "file_path": result["path"],
                "starting_line_in_file": result["startline"],
                "snippet": result["data"],
            }
            for result in results
        ]
        results = {
            "query": query,
            "search_results": results,
        }
        return results

    def get_latest_pipeline_info(self, repo_url: RepoUrlType) -> dict:
        """Retrieves the latest pipeline info, such as url, status, duration, commit, jobs, etc."""
        project = self.get_project_from_url(repo_url)
        pipeline = project.pipelines.latest()

        commit = project.commits.get(pipeline.sha)
        commit = filter_dict_by_keys(
            commit.attributes,
            ["title", "author_name", "web_url"],
        )

        jobs = pipeline.jobs.list(all=True)
        jobs = [
            filter_dict_by_keys(
                job.attributes,
                ["name", "status", "stage", "allow_failure", "web_url"],
            )
            for job in jobs
        ]

        info = {
            "web_url": pipeline.web_url,
            "created_at": format_datetime_for_ai(pipeline.created_at, timezone=self.timezone),
            "status": pipeline.status,
            "source": pipeline.source,
            "duration_seconds": pipeline.duration,
            "queued_duration_seconds": pipeline.queued_duration,
            "commit_sha": pipeline.sha,
            "commit": commit,
            "jobs": jobs,
        }
        return info
