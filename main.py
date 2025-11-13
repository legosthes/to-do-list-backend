from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
from datetime import datetime
from typing import Annotated

app = FastAPI()


class ToDo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    item: str = Field(max_length=200)
    is_completed: bool = Field(default=False)
    created_at: str = Field(default_factory=datetime.now, nullable=False)
    updated_at: str = Field(default_factory=datetime.now, nullable=False)


sqlite_file_name = "todolist.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/todos/")
def read_todos(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[ToDo]:
    todos = session.exec(select(ToDo).offset(offset).limit(limit)).all()
    return todos


@app.post("/todos/")
def create_todo(todo: ToDo, session: SessionDep) -> ToDo:
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo
