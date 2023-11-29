// set a type Course that contains all the data relevant to a course for displaying in rows for table
export type Course = {
    subject: string;
    catalog_number: number;
    title_long: string;
    description: string;
}

export type CourseInfo = {
    title: string;  
    description: string;
}

export type SemesterForm = {
    id: number
    year: number;
    active: boolean;
    period_id: number;
    catalog: File | null;
}