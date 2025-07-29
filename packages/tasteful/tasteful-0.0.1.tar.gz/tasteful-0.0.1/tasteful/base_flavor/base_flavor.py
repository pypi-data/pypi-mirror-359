import re
import inspect

from typing import Any, Type, Union

from dependency_injector import providers
from fastapi import APIRouter

from tasteful.containers.base_flavor_container import BaseFlavorContainer

from ..repositories.base_repository import BaseRepository
from .base_service import BaseService


class BaseFlavor:
    """Base class for creating API flavors that handle routing and endpoint registration.

    A flavor is a collection of related endpoints grouped under a common prefix and tags.
    """

    name: str
    prefix: str
    tags: list[str]
    services: dict[str, Type]
    repository: Union[Type[BaseRepository], None]

    def __init__(
        self,
        name: str = "",
        prefix: str = "",
        tags: list[str] = [],
        services: list[Type[BaseService]] = [],
        repository: Union[Type[BaseRepository], None] = None,
    ):
        """Initialize a new flavor instance."""
        self.name = name
        self.prefix = prefix
        self.tags = tags
        self.services = services
        self.repository = repository
        self.router = APIRouter(tags=self.tags, prefix=self.prefix)
        self.container = BaseFlavorContainer()

        self._register_services()
        self._router_from_controller()

    def _convert_class_name_to_snake_case(self, class_name: str) -> str:
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", class_name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

    def _register_services(self) -> None:
        """Register a service with the flavor's container."""
        for service_class in self.services:
            self.container.services_factory.override(providers.Factory(service_class))
            service_attr_name = self._convert_class_name_to_snake_case(
                service_class.__name__
            )
            setattr(self, service_attr_name, service_class())

    def _router_from_controller(self, **defaults_route_args: Any) -> None:
        """Build a router from a controller instance annotated endpoints).

        Args:
        ----
            defaults_route_args: Default arguments to pass to all routes

        Raises:
        ------
            ValueError: If no endpoints are found in the controller

        """
        # Find all methods that have endpoint definitions attached
        members = inspect.getmembers(
            self, lambda x: hasattr(x, "__endpoint_definitions__")
        )

        # Register each endpoint with the router
        for _, endpoint in members:
            for endpoint_definition in getattr(endpoint, "__endpoint_definitions__"):
                kwargs = {**defaults_route_args, **endpoint_definition.kwargs}

                self.router.add_api_route(
                    endpoint_definition.path,
                    endpoint,
                    methods=[endpoint_definition.method],
                    **kwargs,
                )
