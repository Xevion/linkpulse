import pkgutil
import sys
from typing import Any, List, Optional
from dotenv import load_dotenv
from peewee_migrate import Router, router

load_dotenv(dotenv_path=".env")

class ExtendedRouter(Router):
    def show(self, module: str) -> Optional[str]:
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
                        m for _, m, ispkg in pkgutil.iter_modules([f"{router.CURDIR}"]) if ispkg
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

def main(*args):
    """
    Main function for running migrations.
    Args are fed directly from sys.argv.
    """
    from linkpulse import models
    db = models.BaseModel._meta.database
    router = ExtendedRouter(database=db, migrate_dir='linkpulse/migrations')
    
    # TODO: Show unapplied migrations before applying all
    # TODO: Suggest merging migrations if many are present + all applied
    # TODO: Show prepared migration before naming (+ confirmation option for pre-provided name)


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