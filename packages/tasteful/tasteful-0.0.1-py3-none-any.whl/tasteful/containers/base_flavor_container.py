from dependency_injector import containers, providers


# https://python-dependency-injector.ets-labs.org/providers/inject_self.html
class ServiceDispatcher:
    """Service dispatcher for base flavor container."""

    def __init__(self, container: containers.Container):
        self.container = container

    def get_services(self):
        """Get all factory services from the container."""
        for provider in self.container.traverse(types=[providers.Factory]):
            yield provider()


class RepositoryDispatcher:
    def __init__(self, container: containers.Container) -> None:
        self.container = container

    def get_repository(self):
        """Get the repository."""
        for provider in self.container.traverse(types=[providers.Factory]):
            yield provider()


class BaseFlavorContainer(containers.DeclarativeContainer):
    """Container for base flavor dependencies."""

    __self__ = providers.Self()

    services_factory = providers.Factory()
    repository_factory = providers.Factory()

    services = providers.Singleton(ServiceDispatcher, __self__)
    repository = providers.Singleton(RepositoryDispatcher, __self__)
