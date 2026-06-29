from fastapi import FastAPI
from pydantic import BaseModel
app = FastAPI(title="TritonPlan API")
# to run docker you do docker compose up --build
# right now we are using a simple pyuthon dictionary as a storage so ndata will disappear everytime we refresh but its just for learning
student_courses = {}
class CompletedCoursesRequest(BaseModel):
    courses:list[str]
    quarter: str
    year:int
# basemodel tells the function that it will be json, so the class will expect a json structure
@app.get("/health")
def health() -> dict[str, str]:# arrow tells coder what it function should return
    return {"status": "ok", "service": "tritonplan-backend"}

# simple get api request, the URL basicallyt is the get request and you can run the url to see it
@app.get("/completed_courses")
def completed_courses() -> list[dict[str, str]]:
    return [
        {"code":"DSC 10", "title":"Principles of Data Science"},
        {"code":"DSC 20", "title":"Programming and Basic Data Structures for Data Science"},
        {"code":"DSC 30", "title":"Data Structures and Algorithms for Data Science"},
        {"code":"DSC 40A", "title":"Theoretical Foundations of Data Science I"},
        {"code":"DSC 40B", "title":"Theoretical Foundations of Data Science II"},

    ]
# same thing, but this time inputting the url will give it a variable which will be used in the function
@app.get("/students/{student_name}/completed-courses")
def get_completed_courses(student_name: str):
    return {
        "student_name":student_name,
        "completed_courses": student_courses.get(student_name, [])
    }
# this time we are putting the variables inside, browser url are just for get requests
# but we can use http://localhost:8000/docs fast apis docs instead and tryu it out
@app.post("/students/{student_name}/completed-courses")
def add_completed_courses(student_name: str, request:CompletedCoursesRequest ):
    student_courses[student_name] = {
        "complete_record": request.courses,
        "quarter": request.quarter,
        "year":request.year,
     }

    return {
        "student_name": student_name,

        "completed_courses":student_courses[student_name]
    }