# Imports
import json
import os
import logging

# Flask App
from flask import Flask, render_template, request, redirect, url_for, flash
from flask.logging import default_handler

# OpenTelemetry trace-related components for setting up distributed tracing
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider, StatusCode
from opentelemetry.sdk.trace.export import (BatchSpanProcessor)
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

# Flask App Initialization
app = Flask(__name__)
app.logger.removeHandler(default_handler)
logging.basicConfig(level=logging.INFO)

# Trace  Provider Initialisation
resource = Resource.create({"service.name": "Course-App"})
provider = TracerProvider(resource=resource)
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)
processor = BatchSpanProcessor(jaeger_exporter)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("my.tracer.name")
FlaskInstrumentor().instrument_app(app)

# Constant Declarations
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
    """
        Route for the home page.

        This route renders the home page by returning the `index.html` template. It 
        also generates a span for the request to trace the home page visit.

        Returns:
            str: The rendered HTML for the home page.
    """
    with tracer.start_as_current_span("Request") as span:
        span.set_attribute("request method", str(request.method))
        span.set_attribute("ip address", str(request.remote_addr))
        span.set_attribute("metadata", str(list(sample_input.keys())))
        
        
    with tracer.start_as_current_span("Rendering HTML") as span:
        output = render_template('index.html')
        span.set_status(StatusCode.OK)
        return output

@app.route('/catalog')
def course_catalog():
    """
        Route for displaying the course catalog.

        This route loads the list of courses and renders the `course_catalog.html` template.
        It traces the request and rendering of the catalog page.

        Returns:
            str: The rendered HTML for the course catalog page, or an error message.
    """
    with tracer.start_as_current_span("Request") as span:
        span.set_attribute("request method", str(request.method))
        span.set_attribute("ip address", str(request.remote_addr))
        span.set_attribute("metadata", str(list(sample_input.keys())))
    courses = load_courses()
    with tracer.start_as_current_span("Rendering Catalog") as span:
        try:
            span.set_attribute("courses", str(courses))
            output = render_template('course_catalog.html', courses=courses)
            span.set_status(StatusCode.OK)
            return output
        except Exception:
            span.set_status(StatusCode.ERROR)
            return "Error rendering catalog"


@app.route('/course/<code>')
def course_details(code):
    """
    Route for displaying the details of a specific course.

    This route retrieves the course details using the course code and renders 
    the `course_details.html` template. If the course is not found, it flashes an error 
    and redirects the user to the course catalog.

    Args:
        code (str): The course code (e.g., "CS 203") to look up.

    Returns:
        str: The rendered HTML for the course details, or a redirection to the catalog.
    """
    with tracer.start_as_current_span("Request") as span:
        span.set_attribute("request method", str(request.method))
        span.set_attribute("ip address", str(request.remote_addr))
        span.set_attribute("metadata", str(list(sample_input.keys())))
    
    with tracer.start_as_current_span("Viewing Course") as span:
        courses = load_courses()
        course = next((course for course in courses if course['code'] == code), None)
        span.set_attribute("code", code)
        if not course:
            flash(f"No course found with code '{code}'.", "error")
            span.set_status(StatusCode.ERROR)
            logging.error(f"No course found with code '{code}'.")
            return redirect(url_for('course_catalog'))
        span.set_status(StatusCode.OK)
        logging.info(f"Course '{code}' given.")
    return render_template('course_details.html', course=course)

@app.route('/add_course', methods=['GET', 'POST'])
def add_course():
    """
    Route for adding a new course to the catalog.

    This route displays a form to add a new course and handles the form submission.
    If the form is submitted successfully, the course is saved, and the user is redirected 
    to the course catalog. Otherwise, an error is flashed.

    Returns:
        str: The rendered HTML for the add course form, or a redirection to the catalog.
    """
    with tracer.start_as_current_span("Request") as span:
        span.set_attribute("request method", str(request.method))
        span.set_attribute("ip address", str(request.remote_addr))
        span.set_attribute("metadata", str(list(sample_input.keys())))

    with tracer.start_as_current_span("Adding Course") as span:
        span.set_attribute("request", str(request.method))
        if request.method == 'POST':
            span.set_attribute("form", str(request.form))
            if(request.form['code'] == "" or request.form['name'] == "" or request.form['instructor'] == "" or request.form['semester'] == "" or request.form['schedule'] == "" or request.form['classroom'] == "" or request.form['prerequisites'] == "" or request.form['grading'] == ""):
                flash("Please fill all the fields.", "error")
                span.set_status(StatusCode.UNSET)
                logging.error("Please fill all the fields.")
                return redirect(url_for('add_course'))
            
            data = {
                'code': request.form['code'],
                'name': request.form['name'],
                'description': request.form['description'],
                'instructor': request.form['instructor'],
                'semester': request.form['semester'],
                'classroom': request.form['classroom'],
                "schedule": request.form['schedule'],
                "prerequisites": request.form['prerequisites'],
                "grading": request.form['grading'],
                "description": request.form['description']
            }
            save_courses(data)
            flash(f"Course '{data['code']}' added successfully.", "success")
            logging.info(f"Course '{data['code']}' added successfully.")
            span.set_status(StatusCode.OK)
            return redirect(url_for('course_catalog'))  
        if request.method  == "GET":
            return render_template('add_courses.html')   



if __name__ == '__main__':
    app.run(debug=True)
