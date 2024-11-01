import pkgutil
import re
import sys
from typing import List, Optional, Tuple

import questionary
from dotenv import load_dotenv
from peewee import PostgresqlDatabase
from peewee_migrate import Router, router

load_dotenv(dotenv_path=".env")


class ExtendedRouter(Router):
    def show(self, module: str) -> Optional[Tuple[str, str]]:
        """
        Show the suggested migration that will be created, without actually creating it.

        :param module: The module to scan & diff against.
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
        Get all migrations that have been applied.
        """
        return [mm.name for mm in self.model.select().order_by(self.model.id)]


def main(*args: str) -> None:
    """
    Main function for running migrations.
    Args are fed directly from sys.argv.
    """
    from linkpulse import models
    from linkpulse.utilities import get_db

    db = get_db()
    router = ExtendedRouter(
        database=db,
        migrate_dir="linkpulse/migrations",
        ignore=[models.BaseModel._meta.table_name],
    )
    auto = "linkpulse.models"

    current = router.all_migrations()
    if len(current) == 0:
        diff = router.diff

        if len(diff) == 0:
            print(
                "No migrations found, no pending migrations to apply. Creating initial migration."
            )

            migration = router.create("initial", auto=auto)
            if not migration:
                print("No changes detected. Something went wrong.")
            else:
                print(f"Migration created: {migration}")
                router.run(migration)

    diff = router.diff
    if len(diff) > 0:
        print(
            "Note: Selecting a migration will apply all migrations up to and including the selected migration."
        )
        print(
            "e.g. Applying 004 while only 001 is applied would apply 002, 003, and 004."
        )

        choice = questionary.select(
            "Select highest migration to apply:", choices=diff
        ).ask()
        if choice is None:
            print(
                "For safety reasons, you won't be able to create migrations without applying the pending ones."
            )
            if len(current) == 0:
                print(
                    "Warn: No migrations have been applied globally, which is dangerous. Something may be wrong."
                )
            return

        result = router.run(choice)
        print(f"Done. Applied migrations: {result}")
        print("Warning: You should commit and push any new migrations immediately!")
    else:
        print("No pending migrations to apply.")

    migration_available = router.show(auto)
    if migration_available is not None:
        print("A migration is available to be applied:")
        migrate_text, rollback_text = migration_available

        print("MIGRATION:")
        for line in migrate_text.split("\n"):
            if line.strip() == "":
                continue
            print("\t" + line)
        print("ROLLBACK:")
        for line in rollback_text.split("\n"):
            if line.strip() == "":
                continue
            print("\t" + line)

        if questionary.confirm("Do you want to create this migration?").ask():
            print(
                'Lowercase letters and underscores only (e.g. "create_table", "remove_ipaddress_count").'
            )
            migration_name: Optional[str] = questionary.text(
                "Enter migration name",
                validate=lambda text: re.match("^[a-z_]+$", text) is not None,
            ).ask()

            if migration_name is None:
                return

            migration = router.create(migration_name, auto=auto)
            if migration:
                print(f"Migration created: {migration}")
                if len(router.diff) == 1:
                    if questionary.confirm(
                        "Do you want to apply this migration immediately?"
                    ).ask():
                        router.run(migration)
                        print("Done.")
                        print("!!! Commit and push this migration file immediately!")
            else:
                print("No changes detected. Something went wrong.")
                return
    else:
        print("No database changes detected.")

    if len(current) > 5:
        if questionary.confirm(
            "There are more than 5 migrations applied. Do you want to merge them?",
            default=False,
        ).ask():
            print("Merging migrations...")
            router.merge(name="initial")
            print("Done.")

            print("!!! Commit and push this merged migration file immediately!")

    # Testing Code:


"""
    print(router.print('linkpulse.models'))

    # Create migration
    print("Creating migration")
    migration = router.create('test', auto='linkpulse.models')
    if migration is None:
        print("No changes detected")
    else:
        print(f"Migration Created: {migration}")

        # Run migration/migrations
        router.run(migration)

    Run all unapplied migrations
    print("Running all unapplied migrations")
    applied = router.run()
    print(f"Applied migrations: {applied}")
"""
