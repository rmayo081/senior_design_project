# Import necessary modules and classes
from Data_model.models import Program, db, Showing, Department, Program_to_Theme, Theme
from flask import current_app
from sqlalchemy.sql.functions import func
from sqlalchemy import or_, BinaryExpression
from dateutil import parser


# Retrieve all programs and their showings from the database
def get_all() -> list[Program] or None:
    return Program.query.all()


# Retrieve a program by its ID
def get_by_id(id: int) -> Program or None:
    return Program.query.get_or_404(
        id, description="No program found with the given ID"
    )


# Search programs by title
def search_by_title(title: str) -> list[Program] | None:
    search_param = "%{}%".format(title)
    return db.session.query(Program).filter(Program.title.like(search_param)).all()


# Insert a new Program into the database
def insert(program: Program):
    db.session.add(program)
    db.session.commit()


# Update a program in the database based on its ID
# The first param must be a dictionary where each key is a field to be updated in the stored Program
def update(program: dict, id: int):
    Program.query.filter(Program.id == id).update(program)
    db.session.commit()

    return Program.query.get(id)


# Remove a program from the database by its ID
def delete(id: int) -> bool:
    Program.query.get_or_404(id)

    # Delete related showings
    Showing.query.filter(Showing.program_id == id).delete()

    # Delete Program_to_Theme relations
    db.session.query(Program_to_Theme).filter(
        Program_to_Theme.columns.program_id == id
    ).delete()

    # Delete the program
    Program.query.filter(Program.id == id).delete()
    db.session.commit()
    return True



'''
Search programs based on various filter parameters
Params:
    title : str -> A string to search for similar titles (i.e. given "Lo" returns programs such as "Lord of the Rings" and "Lost Woods")
    themes : list[int] -> A list of theme ids that a desired program can have. A resulting program can have any 1 or all the themes in this list.
    dates : list[str] -> A list of datetime strings to search showings of a program. A given string specifies a date a potential showing will be on.
    departments : list[str] -> A list of strings as the departments of potential programs that are retrieved
Return Value:
    A list of the Programs that match the given search criteria
'''
def search(**kwargs) -> list[Program]:
    themes: list[int] = kwargs.get("themes") 
    title: str = kwargs.get("title")
    dates: list[str] = kwargs.get("dates")
    departments: list[str] = kwargs.get("departments")

    filters: list[BinaryExpression[bool]] = [] # A list of SQLAlchemy filter expressions
    themes_subquery = None

    # Filter by themes if specified
    if themes:
        themes_subquery = (
            db.session.query(Program_to_Theme.c.program_id)
            .filter(Program_to_Theme.c.theme_id.in_(themes))
            .group_by(Program_to_Theme.c.program_id)
            .having(func.count() == len(themes))
            .subquery()
        )
        filters.append(Program.id.in_(themes_subquery))

    # Filter by departments if specified
    if departments:
        filters.append(Program.department.in_(departments))

    # Filter by dates if specified
    if dates:
        parsed_dates = [parser.parse(d).date() for d in dates]
        filters.append(func.date(Showing.datetime).in_(parsed_dates))

    # Combine the filters to function as an OR statement in SQL
    crit_query = db.session.query(Program).filter(or_(*filters))

    # Further filter by title if specified
    # Operates as an AND SQL statement rather than the OR in previous filters
    if title:
        search_param = "{}%".format(title)
        return crit_query.filter(Program.title.like(search_param)).all()

    return crit_query.all()
