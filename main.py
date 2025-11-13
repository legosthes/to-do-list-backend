from fastapi import Depends, FastAPI, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
from datetime import datetime
from typing import Annotated, Optional
import uuid

app = FastAPI()


class ToDoBase(SQLModel):
    item: str = Field(max_length=200)
    is_completed: bool = Field(default=False)


class ToDo(ToDoBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.now,
        nullable=False,
        sa_column_kwargs={"onupdate": datetime.now},
    )


class ToDoCreate(ToDoBase):
    """Model for creating a new todo."""

    pass


class ToDoRead(ToDoBase):
    """Model for reading a todo."""

    id: str
    created_at: datetime
    updated_at: datetime


class ToDoUpdate(SQLModel):
    """Model for updating a todo."""

    item: Optional[str] = None
    is_completed: Optional[bool] = None


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
def create_todo(todo: ToDoCreate, session: SessionDep) -> ToDo:
    todo_item = ToDo.from_orm(todo)
    session.add(todo_item)
    session.commit()
    session.refresh(todo_item)
    return todo
