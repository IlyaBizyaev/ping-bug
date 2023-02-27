import asyncio
import uvloop

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import Column, Integer, BigInteger, SmallInteger, Index, func
from sqlalchemy.future import select
from sqlalchemy.orm.decl_api import declarative_base


DB_URL = "mysql+asyncmy://user:password@localhost/database"


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
Base = declarative_base()


class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    message_id = Column(Integer, index=True, nullable=False)
    user_id = Column(BigInteger, index=True, nullable=False)
    feedback = Column(SmallInteger, nullable=False)
    __table_args__ = (
        Index("feedback_message_id_user_id", "message_id", "user_id", unique=True),
    )


class DB:
    def __init__(self):
        self.engine = create_async_engine(DB_URL, pool_pre_ping=True, pool_use_lifo=True)
        self.async_session = async_sessionmaker(self.engine)

    async def get_feedback_count(self, m_id: int, index: int):
        async with self.async_session.begin() as session:  # type: AsyncSession
            statement = select(func.count()).select_from(
                select(Feedback).filter_by(message_id=m_id, feedback=index).subquery()
            )
            return (await session.execute(statement)).scalar()


async def run():
    db = DB()
    
    while True:
        result = await db.get_feedback_count(120, 0)
        print(result)
        await asyncio.sleep(9 * 60 * 60)  # A long period of inactivity.


loop = asyncio.get_event_loop()
loop.run_until_complete(run())
