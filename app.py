import json
import os
from flask import Flask, render_template, request, redirect, url_for, flash

# Flask App Initialization
app = Flask(__name__)
app.secret_key = 'secret'
COURSE_FILE = 'course_catalog.json'

sample_input =  {
    "code": "CS 203",
    "name": "Software and Tools for AI",
    "instructor": "Prof. Mayank Singh",
    "semester": "Fall 2025",
    "schedule": "Mon, Wed, Fri 10:00-11:00 AM",
    "classroom": "AB 7/109",
    "prerequisites": "Basic Python, Linux",
    "grading": "50% Assignment, 50% Quiz",
    "description": ""
}


# Utility Functions
def load_courses():
    """Load courses from the JSON file."""
    if not os.path.exists(COURSE_FILE):
        return []  # Return an empty list if the file doesn't exist
    with open(COURSE_FILE, 'r') as file:
        return json.load(file)


def save_courses(data):
    """Save new course data to the JSON file."""
    courses = load_courses()  # Load existing courses
    courses.append(data)  # Append the new course
    with open(COURSE_FILE, 'w') as file:
        json.dump(courses, file, indent=4)


# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/catalog')
def course_catalog():
    courses = load_courses()
    return render_template('course_catalog.html', courses=courses)


@app.route('/course/<code>')
def course_details(code):
    courses = load_courses()
    course = next((course for course in courses if course['code'] == code), None)
    if not course:
        flash(f"No course found with code '{code}'.", "error")
        return redirect(url_for('course_catalog'))
    return render_template('course_details.html', course=course)

@app.route('/add_course', methods=['GET', 'POST'])
def add_course():
    if request.method == 'POST':
        
        if(request.form['code'] == "" or request.form['name'] == "" or request.form['instructor'] == "" or request.form['semester'] == "" or request.form['schedule'] == "" or request.form['classroom'] == "" or request.form['prerequisites'] == "" or request.form['grading'] == ""):
            flash("Please fill all the fields.", "error")
            return redirect(url_for('add_course'))
        
        data = {
            'code': request.form['code'],
            'name': request.form['name'],
            'description': request.form['description'],
            'instructor': request.form['instructor'],
            'credits': request.form['credits'],
            'semester': request.form['semester'],
            'classroom': request.form['classroom'],
            "schedule": request.form['schedule'],
            "prerequisites": request.form['prerequisites'],
            "grading": request.form['grading'],
            "description": request.form['description']
        }
        save_courses(data)
        flash(f"Course '{data['code']}' added successfully.", "success")
        return redirect(url_for('course_catalog'))
    return render_template('add_courses.html')   



if __name__ == '__main__':
    app.run(debug=True)
