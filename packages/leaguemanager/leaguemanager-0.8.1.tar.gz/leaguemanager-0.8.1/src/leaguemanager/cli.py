"""CLI for League Manager tool."""

import json
from typing import Annotated, Optional

import typer
from advanced_alchemy.exceptions import DuplicateKeyError
from rich import print
from rich.prompt import Prompt
from sqlalchemy import delete
from sqlalchemy.orm import Session

from leaguemanager import models
from leaguemanager.core import get_settings
from leaguemanager.db import register_sqlite
from leaguemanager.db.cli.alembic_cli import db_app
from leaguemanager.dependency.cli_callbacks import (
    provide_manager_service,
    provide_sync_db_session,
)
from leaguemanager.services import (
    FixtureService,
    LeagueService,
    OrganizationService,
    SeasonService,
    TeamMembershipService,
    TeamService,
)

from . import __app_name__, __version__

settings = get_settings()
register_sqlite()

app = typer.Typer()


def _version_callback(value: bool) -> None:
    if value:
        print(f"{__app_name__} v{__version__}")
        raise typer.Exit()


@app.command(help="Populate the database with synthetic data.")
def populate(
    season_service: Annotated[
        Optional[SeasonService], typer.Argument(callback=provide_manager_service, parser=SeasonService)
    ] = None,
    league_service: Annotated[
        Optional[LeagueService], typer.Argument(callback=provide_manager_service, parser=LeagueService)
    ] = None,
    team_service: Annotated[
        Optional[TeamService], typer.Argument(callback=provide_manager_service, parser=TeamService)
    ] = None,
    team_membership_service: Annotated[
        Optional[TeamMembershipService],
        typer.Argument(callback=provide_manager_service, parser=TeamMembershipService),
    ] = None,
    organization_service: Annotated[
        Optional[OrganizationService],
        typer.Argument(callback=provide_manager_service, parser=OrganizationService),
    ] = None,
) -> None:
    if (settings.APP_DIR / "example_data.json").exists():
        with open(settings.APP_DIR / "example_data.json") as _data:
            data = json.load(_data)
    elif not (settings.SYNTH_DATA_DIR / "example_data.json").exists():
        data_file = Prompt.ask("Please provide the path to the data directory: ")
        try:
            with open(data_file) as _data:
                data = json.load(_data)
        except FileNotFoundError:
            print(f"File {data_file} does not exist.")
            return
    else:
        with open(settings.SYNTH_DATA_DIR / "example_data.json") as _data:
            data = json.load(_data)
    try:
        org = organization_service.create(data["organization"], auto_commit=True)
        for league in data["leagues"]:
            league["organization_id"] = org.id
            league_service.create(league, auto_commit=True)
        for season in data["seasons"]:
            _league = league_service.get_one(name=season["league"])
            season["league_id"] = _league.id
            season_service.create(
                season,
                auto_commit=True,
            )
        for team in data["teams"]:
            _team_membership = team_membership_service.create(
                {"label": f"{team['name']} - {team['season']}"},
                auto_commit=True,
            )
            team["team_membership_id"] = _team_membership.id
            team.pop("season", None)  # Remove season key if it exists

        for team in data["teams"]:
            team_service.create(
                team,
                auto_commit=True,
            )
    except DuplicateKeyError:
        print("[red]Data already exists in the database. Will not create any data...[/red]")
        return

    print(
        "✨ [green]Successfully created data![/green] ✨",
        f"\nCreated {season_service.count()} Seasons",
        f"\nCreated {league_service.count()} Leagues",
        f"\nCreated {team_service.count()} Teams",
        f"\nCreated {organization_service.count()} Organization",
    )
    return


@app.command(help="Check the counts of data in each table.")
def check(
    session: Annotated[Optional[Session], typer.Argument(callback=provide_sync_db_session, parser=Session)] = None,
    season_service: Annotated[
        Optional[SeasonService], typer.Argument(callback=provide_manager_service, parser=SeasonService)
    ] = None,
    league_service: Annotated[
        Optional[LeagueService], typer.Argument(callback=provide_manager_service, parser=LeagueService)
    ] = None,
    team_service: Annotated[
        Optional[TeamService], typer.Argument(callback=provide_manager_service, parser=TeamService)
    ] = None,
    organization_service: Annotated[
        Optional[OrganizationService],
        typer.Argument(callback=provide_manager_service, parser=OrganizationService),
    ] = None,
    all: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="Check all seasons, leagues, and teams.",
    ),
) -> None:
    if all:
        print(
            "✨ [green]These are the counts of data in each table[/green] ✨",
            f"\n{season_service.count()} Seasons",
            f"\n{league_service.count()} Leagues",
            f"\n{team_service.count()} Teams",
            f"\n{organization_service.count()} Organization",
        )
    else:
        model = Prompt.ask("Please provide the model name to check (i.e. Season): ")
        try:
            _models = session.query(getattr(models, model)).all()
            print(f"Found {session.query(getattr(models, model)).count()} {model}s.")
            for m in _models:
                if m.name:
                    print(f">> {m.name}")
        except AttributeError:
            print(f"Model [green]{model}[/green] does not exist.")
    return


@app.command(name="delete", help="Delete data from the database.")
def _delete(
    session: Annotated[Optional[Session], typer.Argument(callback=provide_sync_db_session, parser=Session)] = None,
    all: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="Delete all seasons, leagues, teams, and organization.",
    ),
) -> None:
    if all:
        session.execute(delete(models.Season))
        session.execute(delete(models.League))
        session.execute(delete(models.Team))
        session.execute(delete(models.Organization))
        session.commit()
        print("⛔ [yellow]Removed all Seasons, Leagues, Teams, and Organizations.[/yellow]⛔")
    else:
        model = Prompt.ask("Please provide the model name to delete (i.e. Season): ")
        try:
            session.execute(delete(getattr(models, model.title())))
            session.commit()
        except AttributeError:
            print(f"Model [green]{model.title()}[/green] does not exist.")
        print(f"⛔ [yellow]Removed all data in the {model.title()} table.[/yellow]⛔")
    return


@app.callback(no_args_is_help=True, help="League Manager CLI.")
def main(
    ctx: typer.Context,
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            "-V",
            callback=_version_callback,
            is_eager=True,
            help="Show the version and exit.",
        ),
    ] = None,
):
    """League Manager CLI."""
    return


# This creates an app for Typer, adding the above commands.
# This enables us to add the `db_app`, which is a Click group from Advanced Alchemy.
app = typer.main.get_command(app)
app.add_command(db_app)
