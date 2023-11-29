# Import necessary modules and classes
from flask import request, send_from_directory
from schemas import (
    ProgramPostSchema,
    ProgramSchema,
    DepartmentListSchema,
    ProgramPutSchema,
)
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from datetime import datetime
import os
import json
from pathlib import Path
import Data_model.program_dao as prog_dao
import Data_model.showing_dao as show_dao
import Data_model.theme_dao as theme_dao
from werkzeug.exceptions import NotFound
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from dateutil import parser
from Data_model.permissions import (
    authenticated_permission,
    superuser_permission,
    ccg_permission,
)

# Create a Blueprint for the program API with a specified URL prefix
program_router = Blueprint("program_api", __name__, url_prefix="/program")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
DIR = Path(__file__, "../..").resolve()
IMAGE_DIR = DIR.joinpath("image_uploads/")


# Define a class for handling program-related requests
@program_router.route("/")
class HandleProgram(MethodView):
    # Define a method to handle GET requests
    @program_router.response(200, ProgramSchema(many=True))
    def get(self):
        # Get the 'display' parameter from the URL
        display = request.args.get("display")

        # Check URL parameters for upcoming or past programs
        if display == "upcoming":
            today = datetime.now()
            programs = filter_programs(prog_dao.Showing.datetime >= today)
            return programs
        elif display == "past":
            today = datetime.now()
            programs = filter_programs(prog_dao.Showing.datetime < today)
            return programs
        else:
            # If URL param is not set or an incorrect value, get all programs
            programs = prog_dao.get_all()
            return programs

    # Define a method to handle POST requests
    @program_router.arguments(ProgramPostSchema, location="form")
    @program_router.response(200, ProgramSchema)
    def post(self, program_data):
        try:
            # Extract showings from program data
            showings = json.loads(program_data.pop("showings"))
            new_prg = prog_dao.Program(**program_data)
            new_prg.showings = []

            # Process each showing and add it to the program
            for show in showings:
                show["datetime"] = parser.parse(show["datetime"])
                new_show = show_dao.Showing(**show)
                new_prg.showings.append(new_show)

            # Upload program image if provided
            if "image" in request.files:
                filename = upload_file(request.files["image"], IMAGE_DIR)

                new_prg.image_filename = filename

            # Insert the new program into the database
            prog_dao.insert(new_prg)

            # Classify program themes and commit changes
            theme_dao.classify_program(new_prg, commit=True)

            return new_prg
        except SQLAlchemyError:
            abort(422, message="An SQL error occured during the operation")


# Route to retrieve Departments that the frontend is allowed to use
@program_router.route("/departments/")
class GetDepartments(MethodView):
    @program_router.response(200, DepartmentListSchema)
    def get(self):
        # Get a list of department values and return as response
        res = DepartmentListSchema()
        res.departments = [str(d.value) for d in prog_dao.Department]
        return res


# Define a class for handling specific program IDs
@program_router.route("/<int:programid>/")
class HandleProgramID(MethodView):
    # Define a method to handle GET requests for a specific program ID
    @program_router.response(200, ProgramSchema)
    def get(self, programid):
        res = prog_dao.get_by_id(programid)
        return res

    # Define a method to handle PUT requests for a specific program ID
    @program_router.arguments(ProgramPutSchema)
    @program_router.response(200, ProgramSchema)
    def put(self, program_data: dict, programid):
        try:
            # Extract showings from program data
            showings: list[dict] = program_data.pop("showings")

            # Update the program without modifying showings yet
            result = prog_dao.update(program_data, programid)

            # Parse each showing in the request data and check their states
            for show in showings:
                # Grab this showing's state if it is set
                state = show.pop("state") if show.get("state") else None

                # Add a new showing to the program
                if state == "new":
                    dt = show.pop("datetime") # Remove the datetime string as it must be parsed first
                    new_show = show_dao.Showing(**show)
                    new_show.datetime = parser.parse(dt)
                    show_dao.add_show_to_program(new_show, programid)

                # Update an existing showing
                elif state == "modified":
                    id = show.pop("id")
                    show_dao.update(show, id)

            return result
        except SQLAlchemyError:
            abort(422)

    # Define a method to handle DELETE requests for a specific program ID
    @program_router.response(200)
    def delete(self, programid):
        prg = prog_dao.get_by_id(programid)
        filename = prg.image_filename
        if filename is not None and os.path.exists(IMAGE_DIR.joinpath(filename)):
            os.remove(IMAGE_DIR.joinpath(filename))
            # Path.unlink(IMAGE_DIR.joinpath(filename))
        prog_dao.delete(programid)

        return


# Define a class for handling program images
@program_router.route("/<int:programid>/image/")
class ProgramImage(MethodView):
    def get(self, programid):
        # Get the program and its image filename
        program = prog_dao.get_by_id(programid)
        filename = program.image_filename

        # If no image is stored, return a 404 error
        if filename is None:
            abort(404, message="no stored image")

        # Return the stored image file
        return send_from_directory(IMAGE_DIR, filename, mimetype="image/gif")


# Define a function to filter programs based on a given expression
def filter_programs(expression: bool) -> list[prog_dao.Program]:
    programs = {}

    # Get showings based on the provided expression
    showings: list[prog_dao.Showing] = show_dao.get_showing_by_datetime_expression(
        expression
    )

    # Organize programs based on unique IDs from showings
    for show in showings:
        if programs.get(show.program_id) is None:
            prg: prog_dao.Program = prog_dao.get_by_id(show.program_id)
            programs[prg.id] = prg

    return list(programs.values())


# Define a function to upload a file to a specified location
def upload_file(file: FileStorage, location: str):
    if file.filename == "":
        return None
    if file and allowed_file(file.filename):
        sfilename = secure_filename(file.filename)
        file.save(os.path.join(location, sfilename))
        return sfilename
    return None


# Define a function to check if a given filename has an allowed extension
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
