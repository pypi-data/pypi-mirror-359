from typing import List, Type

from dependency_injector import providers
from fastapi import FastAPI, Security

from tasteful.base_flavor import BaseFlavor
from tasteful.containers.tasteful_container import TastefulContainer


class TastefulApp:
    def __init__(
        self,
        title: str,
        version: str,
        flavors: List[Type[BaseFlavor]],
        authentication_backends: list[Security],  # type: ignore
    ):
        self.app = FastAPI(
            title=title, version=version, dependencies=authentication_backends
        )
        self.container = TastefulContainer()
        self.app.container = self.container  # type: ignore
        self.flavors = flavors
        self.register_flavors()

    def register_flavors(self) -> None:
        """Register all flavors with the app."""
        for flavor_class in self.flavors:
            self.container.flavors.override(
                providers.Singleton(
                    flavor_class,
                    name=flavor_class.name,
                    prefix=flavor_class.prefix,
                    tags=flavor_class.tags,
                    services=flavor_class.services,
                    repository=flavor_class.repository,
                )
            )
            injected_flavor = self.container.flavors()
            self.app.include_router(injected_flavor.router)
