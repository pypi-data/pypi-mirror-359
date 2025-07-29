import os

from typing import Generator


from db_work_template.db.model import Documento
from sqlmodel import Session, create_engine, select

from dotenv import load_dotenv

load_dotenv(override=True)


DATABASE_URL_MYSQL = os.getenv("DATABASE_URL_MYSQL")
BASEAPI = os.getenv("BASEAPI")
BASEPORTAL = os.getenv("BASEPORTAL")
engine = create_engine(DATABASE_URL_MYSQL + BASEAPI)
my_sql_hml = create_engine(DATABASE_URL_MYSQL + BASEPORTAL)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def get_session_hml() -> Generator[Session, None, None]:
    with Session(my_sql_hml) as session:
        return session


def update_escrituracao_status(session: Session, status: bool, mensagem: str, _id: int):
    stmt = select(Documento).where(Documento.id == _id)
    result = session.exec(stmt).first()
    if result:
        try:
            result.status_escrit = status
            result.descri_escrit = mensagem
            session.commit()
            return True
        except Exception as e:
            raise e
    else:
        return False
