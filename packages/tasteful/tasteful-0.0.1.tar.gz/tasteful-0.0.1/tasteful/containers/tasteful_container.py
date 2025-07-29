from dependency_injector import containers, providers
from tasteful.base_flavor import BaseFlavor


class TastefulContainer(containers.DeclarativeContainer):
    """Declares Tasteful Container."""

    # Flavors related
    flavors = providers.Singleton(BaseFlavor)
