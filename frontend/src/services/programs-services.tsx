import axios from 'axios';

const API_URL = "/api/v1/program/";

class ProgramService {
  getUpcomingPrograms () {
    return axios.get(API_URL + "?display=upcoming");
  }

  getPastPrograms () {
    return axios.get(API_URL + "?display=past");
  }

  getAllPrograms () {
    return axios.get(API_URL);
  }

  getProgram (id: Number) {
    return axios.get(API_URL + id);
  }

  deleteProgram (id: Number) {
    return axios.delete(API_URL + id + "/");
  }

  uploadProgram (programform: FormData) {
    return axios.post(API_URL, programform, {headers: { "Content-Type": "multipart/form-data" }});
  }

  getDepartments () {
    return axios.get(API_URL + "departments/")
  }
}

export default new ProgramService();