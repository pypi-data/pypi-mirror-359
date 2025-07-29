from sqlalchemy.orm import Session
from tasteful.repositories.base_repository import BaseRepository


class SqlAlchemyRepository(BaseRepository):
    """Declare an SqlAlchemyRepository."""

    def __init__(self, session: Session) -> None:
        self.session = session
