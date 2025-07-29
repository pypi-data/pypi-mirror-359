from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Annotated as An

from rich.console import Console
from rich.table import Table
from typing_extensions import Doc

from insiders._internal.logger import _logger
from insiders._internal.models import Backlog

if TYPE_CHECKING:
    from insiders._internal.clients.github import GitHub
    from insiders._internal.models import Sponsors


def print_backlog(
    backlog: An[Backlog, Doc("The backlog to print.")],
    labels: An[dict[str, str] | None, Doc("A map of label representations.")] = None,
    limit: An[int, Doc("The maximum number of issues to print.")] = 0,
) -> None:
    """Print the backlog."""
    table = Table(title=f"Backlog ({f'showing {limit} of ' if limit else ''}{len(backlog.issues)} issues)")
    table.add_column("Nº", no_wrap=True)
    table.add_column("Type", no_wrap=True)
    table.add_column("Issue", no_wrap=True)
    table.add_column("Author", no_wrap=True)
    table.add_column("Labels", no_wrap=False)
    table.add_column("Funding", no_wrap=True)
    table.add_column("Upvotes", no_wrap=True)
    table.add_column("Title")

    labels = labels or {}

    for index, issue in enumerate(backlog.issues, 1):
        iid = f"{issue.repository}#{issue.number}"
        issue_type = "PR" if issue.is_pr else "Issue"
        url_path = "pull" if issue.is_pr else "issues"
        url = f"https://github.com/{issue.repository}/{url_path}/{issue.number}"
        table.add_row(
            str(index),
            issue_type,
            f"[link={url}]{iid}[/link]",
            f"[link=https://github.com/{issue.author.name}]{issue.author.name}[/link]",
            "".join(labels.get(label, label) for label in sorted(issue.labels)),
            f"💖{issue.funding}",
            f"👍{len(issue.upvotes)}",
            f"[link={url}]{issue.title}[/link]",
        )
        if index == limit:
            break

    console = Console()
    console.print(table)


def get_backlog(
    github_namespaces: list[str],
    github: GitHub,
    sponsors: Sponsors | None = None,
    issue_labels: set[str] | None = None,
) -> Backlog:
    """Get the backlog."""
    github_users = {beneficiary.user for beneficiary in sponsors.beneficiaries.values()} if sponsors else None
    github_issues = github.get_issues(github_namespaces, github_users, allow_labels=issue_labels)
    _logger.debug(f"Got {len(github_issues)} issues from GitHub")
    return Backlog(issues=list(github_issues.values()))
