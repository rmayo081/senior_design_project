import React, { useState, useEffect } from 'react';
import CourseService from "../services/CourseServices.tsx"
import SemesterService from '../services/SemesterService';
import "../css/CoursePage.css"
import { Course, SemesterForm } from "../CourseModels/courseModels.tsx";
import { Modal, ModalButton, ModalNewSemesterBody, DeleteSemesterModalButton, DeleteSemesterBody } from "../components/Modal.tsx";

interface TableBodyRowsProps {
    id: number;
}



const NewSemesterTab: React.FC = () => {

    const [id, setId] = useState<number | null>(null);
    const [semesters, setSemesters] = useState<SemesterForm[] | null>();


    useEffect(() => {

        SemesterService.getSemesters()
            .then((response) => {
                setSemesters(response.data);
            })

    }, []);

    const handleSemesterUpload = (semester: SemesterForm) => {
        setSemesters((previous) => {
            return [semester, ...previous ?? []];
        })
    }

    const handleClick = (id: number) => {
        setId(id);
    };


    return (
        <div className="outer-button-container">
            <div className="btn-group" role="toolbar">
                <ModalButton modalTarget="uploadModal" buttonMessage="Add a semester" />
                <Modal modalTarget="uploadModal" modalTitle="CREATE A NEW SEMESTER" modalBody={<ModalNewSemesterBody handleUpload={handleSemesterUpload} />} />
                {semesters ? semesters.map((semester) => (
                    <button type="button" className="btn btn-default" value={semester.id} onClick={() => handleClick(semester.id)}>{semester.period.period} {semester.year}</button>
                )) : null}
            </div>
            <div className="delete-button-wrapper">
                <DeleteSemesterModalButton modalTarget="DeleteSemesterModal" buttonMessage="Delete a semester" />
                <Modal modalTarget="DeleteSemesterModal" modalTitle="DELETE A SEMESTER" modalBody={<DeleteSemesterBody />} />
            </div>
            {id !== null && <TableBodyRows id={id} />}
        </div >
    )
}

const TableBodyRows: React.FC<TableBodyRowsProps> = ({ id }) => {
    const [course, setCourse] = useState<Course | undefined>(undefined);
    const [courseId, setCourseId] = useState<number | null>(null);
    const [courses, setCourses] = useState<Course[] | null>();
    const [courseTitle, setCourseTitle] = useState<string | undefined>();

    useEffect(() => {
        SemesterService.getCourses(id)
            .then((response) => {
                setCourses((prevCourses) => {
                    console.log(prevCourses);
                    return response.data;
                });
            });
    }, [id]);

    const handleClick = (courseId: number) => {
        setCourseId(courseId);
    };

    const setCourseType = (courseId: number) => {
        if (courses) {
            courses.forEach((course) => {
                if (course.id === courseId) {
                    setCourse(course);
                }
            });
        }
    }

    const setCourseTitleClick = (courseId: number) => {
        if (courses) {
            courses.forEach((course) => {
                if (course.id === courseId) {
                    setCourseTitle(course.title_long);
                }
            });
        }
    };


    return (
        <div>
            <table className="table">
                <thead>
                    <tr>
                        <th scope="col">Course Subject & Number</th>
                        <th scope="col">Course Title</th>
                        <th scope="col">Tags</th>
                    </tr>
                </thead>
                <tbody>
                    {courses && courses.map((course) => (
                        <tr key={course.id} value={course.id} onClick={() => { handleClick(course.id); setCourseTitleClick(course.id); setCourseType(course.id) }} data-toggle="modal" data-target="#courseInfoDisplay">
                            <th scope="row">{course.subject} {course.catalog_number}</th>
                            <td>{course.title_long}</td>
                            <td>{course.catalog_number}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
            <div>
                <nav aria-label="...">
                    <ul class="pagination">
                        <li class="page-item disabled">
                            <span class="page-link">Previous</span>
                        </li>
                        <li class="page-item"><a class="page-link" href="#">1</a></li>
                        <li class="page-item active">
                            <span class="page-link">
                                2
                                <span class="sr-only">(current)</span>
                            </span>
                        </li>
                        <li class="page-item"><a class="page-link" href="#">3</a></li>
                        <li class="page-item">
                            <a class="page-link" href="#">Next</a>
                        </li>
                    </ul>
                </nav>
            </div>
            {courseId !== null && course !== null && (<Modal modalTarget="courseInfoDisplay" modalTitle={courseTitle} modalBody={<ShowClassInfo course={course} />} />)}
        </div >
    );

};

const ShowClassInfo: React.FC<{ course: Course | undefined }> = ({ course }) => {

    // Assuming courseId is available from the course object
    const courseDescription = course?.description || "";


    return (
        <div className="modal-body">
            <p>Instructor:</p>
            <p className="programDescription"> {courseDescription}
            </p>
        </div>
    )
}


const CoursePage: React.FC = () => {


    return (
        <>
            <NewSemesterTab />
        </>
    );
}

export default CoursePage;
