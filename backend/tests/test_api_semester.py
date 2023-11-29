from flask import Flask
from flask.testing import FlaskClient
import json
from Data_models import Semester, Course, Period

BASE_URL = "/v1/program/"

def test_get(client: FlaskClient):
    resp = client.get(BASE_URL)
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)
    assert len(resp.get_json()) == 0
    
    # make period, pass id to semester
    p1 = Period()
    
    
    s1 = Semester()
    s1.year = "2023"
    