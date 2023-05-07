"""Database module."""
from contextlib import asynccontextmanager
from config.settings import get_settings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import async_scoped_session
from asyncio import current_task
from sqlalchemy.ext.declarative import declarative_base

settings = get_settings()


class SqlAlchemy:

    def __init__(self, database_url: str, metadata=None):
        self.db = create_async_engine(database_url, echo=settings.debug)
        self.session = self.create_scoped_session()
        self.Model = self.make_declarative_base(metadata)

    @staticmethod
    def make_declarative_base(metadata=None):
        """Creates the declarative base that all models will inherit from.

        :param model: base model class (or a tuple of base classes) to pass
            to :func:`~sqlalchemy.ext.declarative.declarative_base`. Or a class
            returned from ``declarative_base``, in which case a new base class
            is not created.
        :param metadata: :class:`~sqlalchemy.MetaData` instance to use, or
            none to use SQLAlchemy's default.

        .. versionchanged 2.3.0::
            ``model`` can be an existing declarative base in order to support
            complex customization such as changing the metaclass.
        """
        model = declarative_base(
            name='Model',
            metadata=metadata,
        )
        return model

    def create_scoped_session(self, options=None):
        """Create a :class:`~sqlalchemy.orm.scoping.scoped_session`
        on the factory from :meth:`create_session`.
        """
        if options is None:
            options = {}
        return async_scoped_session(
            self.create_session(options), scopefunc=current_task
        )

    @property
    def metadata(self):
        """The metadata associated with ``db.Model``."""
        return self.Model.metadata

    def create_session(self, options):
        """Create the session factory used by :meth:`create_scoped_session`.

        The factory **must** return an object that SQLAlchemy recognizes as a session,
        or registering session events may raise an exception.

        Valid factories include a :class:`~sqlalchemy.orm.session.Session`
        class or a :class:`~sqlalchemy.orm.session.sessionmaker`.

        The default implementation creates a ``sessionmaker`` for :class:`AsyncSession`.

        :param options: dict of keyword arguments passed to session class
        """
        return sessionmaker(self.db, class_=AsyncSession, **options)


@asynccontextmanager
async def in_transaction(async_session: async_scoped_session) -> AsyncSession:
    """
    Transaction context manager.

    You can run your code inside ``async with in_transaction() as tx:``
    statement to run it into one transaction. If error occurs transaction
    will rollback.
    """
    session = async_session()
    await session.begin()
    try:
        yield session
        await session.commit()
    except BaseException:
        await session.rollback()
        raise
    finally:
        await session.close()


db = SqlAlchemy(settings.database_url)


async def db_session():
    """Return session."""
    async with in_transaction(db.session) as session:
        yield session
