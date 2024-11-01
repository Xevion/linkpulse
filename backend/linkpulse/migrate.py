import pkgutil
import re
import sys
from typing import List, Optional, Tuple

import questionary
import structlog
from dotenv import load_dotenv
from peewee_migrate import Router, router

logger = structlog.get_logger()
load_dotenv(dotenv_path=".env")


class ExtendedRouter(Router):
    """
    The original Router class from peewee_migrate didn't have all the functions I needed, so several functions are added here

    Added
        - show: Show the suggested migration that will be created, without actually creating it
        - all_migrations: Get all migrations that have been applied
    """

    def show(self, module: str) -> Optional[Tuple[str, str]]:
        """
        Show the suggested migration that will be created, without actually creating it

        :param module: The module to scan & diff against
        """
        migrate = rollback = ""

        # Need to append the CURDIR to the path for import to work.
        sys.path.append(f"{ router.CURDIR }")
        models = module if isinstance(module, list) else [module]
        if not all(router._check_model(m) for m in models):
            try:
                modules = models
                if isinstance(module, bool):
                    modules = [
                        m
                        for _, m, ispkg in pkgutil.iter_modules([f"{router.CURDIR}"])
                        if ispkg
                    ]
                models = [m for module in modules for m in router.load_models(module)]

            except ImportError:
                self.logger.exception("Can't import models module: %s", module)
                return None

        if self.ignore:
            models = [m for m in models if m._meta.name not in self.ignore]  # type: ignore[]

        for migration in self.diff:
            self.run_one(migration, self.migrator, fake=True)

        migrate = router.compile_migrations(self.migrator, models)
        if not migrate:
            self.logger.warning("No changes found.")
            return None

        rollback = router.compile_migrations(self.migrator, models, reverse=True)

        return migrate, rollback

    def all_migrations(self) -> List[str]:
        """
        Get all migrations that have been applied
        """
        return [mm.name for mm in self.model.select().order_by(self.model.id)]


def main(*args: str) -> None:
    """
    Main function for running migrations.
    Args are fed directly from sys.argv.
    """
    from linkpulse.utilities import get_db

    from linkpulse import models

    db = get_db()
    router = ExtendedRouter(
        database=db,
        migrate_dir="linkpulse/migrations",
        ignore=[models.BaseModel._meta.table_name],
    )
    target_models = "linkpulse.models"  # The module to scan for models & changes

    current = router.all_migrations()
    if len(current) == 0:
        diff = router.diff

        if len(diff) == 0:
            logger.info(
                "No migrations found, no pending migrations to apply. Creating initial migration."
            )

            migration = router.create("initial", auto=target_models)
            if not migration:
                logger.error("No changes detected. Something went wrong.")
            else:
                logger.info(f"Migration created: {migration}")
                router.run(migration)

    diff = router.diff
    if len(diff) > 0:
        logger.info(
            "Note: Selecting a migration will apply all migrations up to and including the selected migration."
        )
        logger.info(
            "e.g. Applying 004 while only 001 is applied would apply 002, 003, and 004."
        )

        choice = questionary.select(
            "Select highest migration to apply:", choices=diff
        ).ask()
        if choice is None:
            logger.warning(
                "For safety reasons, you won't be able to create migrations without applying the pending ones."
            )
            if len(current) == 0:
                logger.warning(
                    "Warn: No migrations have been applied globally, which is dangerous. Something may be wrong."
                )
            return

        result = router.run(choice)
        logger.info(f"Done. Applied migrations: {result}")
        logger.warning("You should commit and push any new migrations immediately!")
    else:
        logger.info("No pending migrations to apply.")

    # Inspects models and might generate a migration script
    migration_available = router.show(target_models)

    if migration_available is not None:
        logger.info("A migration is available to be applied:")
        migrate_text, rollback_text = migration_available

        def _reformat_text(text: str) -> str:
            # Remove empty lines
            text = [line for line in text.split("\n") if line.strip() != ""]
            # Add line numbers, indent, ensure it starts on a new line
            return "\n" + "\n".join([f"{i:02}:\t{line}" for i, line in enumerate(text)])

        logger.info("Migration Content", content=_reformat_text(migrate_text))
        logger.info("Rollback Content", content=_reformat_text(rollback_text))

        if questionary.confirm("Do you want to create this migration?").ask():
            logger.info(
                'Minimum length 9, lowercase letters and underscores only (e.g. "create_table", "remove_ipaddress_count").'
            )
            migration_name: Optional[str] = questionary.text(
                "Enter migration name",
                validate=lambda text: re.match("^[a-z_]{9,}$", text) is not None,
            ).ask()

            if migration_name is None:
                return

            migration = router.create(migration_name, auto=target_models)
            if migration:
                logger.info(f"Migration created: {migration}")

                if len(router.diff) == 1:
                    if questionary.confirm(
                        "Do you want to apply this migration immediately?"
                    ).ask():
                        router.run(migration)
                        logger.info("Done.")
                        logger.warning(
                            "!!! Commit and push this migration file immediately!"
                        )
            else:
                raise RuntimeError(
                    "Changes anticipated with show() but no migration created with create(), model definition may have reverted."
                )
    else:
        logger.info("No database changes detected.")

    if len(current) > 5:
        if questionary.confirm(
            "There are more than 5 migrations applied. Do you want to merge them?",
            default=False,
        ).ask():
            logger.info("Merging migrations...")
            router.merge(name="initial")
            logger.info("Done.")

            logger.warning("Commit and push this merged migration file immediately!")
