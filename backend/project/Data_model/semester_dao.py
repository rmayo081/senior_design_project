from Data_model.models import Semester, db
from flask import current_app

# Retrieve every Semester and its courses from the db
def get_all() -> list[Semester] or None:
    
    return Semester.query.all()
    
# Retrieve every Semester that fits filter from the db
def get_by_filter(expression : bool) -> list[Semester] or None:
    
    return Semester.query.filter(expression).all()    

# Retrieve a Semester by its id
def get_by_id(id : int) -> Semester or None:
    
    return Semester.query.get(id)

# Insert a new Semester into the db. Returns True if successful, False otherwise.
def insert_semester(semester : Semester) -> bool:
    
        # Probably should add some sort of error checking here
        db.session.add(semester)
        db.session.commit()
        return True

# Updates a semester in the db. Searches for a Semester with a matching id to ensure it already exists in the db
def update_semester(semester : Semester) -> bool:
    
    saved_semester = get_by_id(semester.id)
    
    if saved_semester is None:
        return False
    
    db.session.merge(semester)
    db.session.commit()
    
    return True
    
# Removes a semester from the db by its id
def delete_semester(semester : Semester):
    semester = Semester.query.get_or_404(semester.id)

    db.session.delete(semester)
    db.session.commit() 
    