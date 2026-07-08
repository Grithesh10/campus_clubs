import os
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename

from models import db, Club, Event, Registration, Student

app = Flask(__name__)

app.secret_key = "campusclubportal"

UPLOAD_FOLDER = "static/uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":

            session.clear()
            session["admin"] = True

            return redirect(url_for("dashboard"))

        return render_template(
            "login.html",
            error="Invalid Username or Password"
        )

    return render_template("login.html")
@app.route("/about")
def about():
    return render_template("about.html")
@app.route("/contact")
def contact():
    return render_template("contact.html")
@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))
@app.route("/")
def home():
    return render_template("landing.html")
@app.route("/dashboard")
def dashboard():

    if "admin" not in session:
        return redirect(url_for("login"))

    club_count = Club.query.count()
    event_count = Event.query.count()
    registration_count = Registration.query.count()

    latest_clubs = Club.query.order_by(Club.id.desc()).limit(5).all()
    latest_events = Event.query.order_by(Event.id.desc()).limit(5).all()
    latest_registrations = Registration.query.order_by(
        Registration.id.desc()
    ).limit(5).all()

    return render_template(
        "index.html",
        clubs=club_count,
        events=event_count,
        registrations=registration_count,
        latest_clubs=latest_clubs,
        latest_events=latest_events,
        latest_registrations=latest_registrations
    )

@app.route("/student-register", methods=["GET", "POST"])
def student_register():

    if request.method == "POST":

        if Student.query.filter_by(
            roll_number=request.form["roll_number"]
        ).first():

            return render_template(
                "student_register.html",
                error="Roll Number already exists"
            )

        if Student.query.filter_by(
            email=request.form["email"]
        ).first():

            return render_template(
                "student_register.html",
                error="Email already exists"
            )

        student = Student(

            name=request.form["name"],

            roll_number=request.form["roll_number"],

            email=request.form["email"],

            department=request.form["department"],

            year=request.form["year"],

            password=request.form["password"]

        )

        db.session.add(student)

        db.session.commit()

        return redirect(url_for("student_login"))

    return render_template("student_register.html")
@app.route("/student-login", methods=["GET", "POST"])
def student_login():

    if request.method == "POST":

        student = Student.query.filter_by(
            roll_number=request.form["roll_number"],
            password=request.form["password"]
        ).first()

        if student:

            session.clear()
            session["student"] = student.id

            return redirect(url_for("student_dashboard"))

        return render_template(
            "student_login.html",
            error="Invalid Roll Number or Password"
        )

    return render_template("student_login.html")
@app.route("/student-dashboard")
def student_dashboard():

    if "student" not in session:
        return redirect(url_for("student_login"))

    student = Student.query.get(session["student"])

    clubs = Club.query.all()

    events = Event.query.all()

    return render_template(
        "student_dashboard.html",
        student=student,
        clubs=clubs,
        events=events
    )
@app.route("/clubs")
def clubs():

    if "admin" not in session and "student" not in session:
        return redirect(url_for("login"))

    search = request.args.get("search")

    if search:

        all_clubs = Club.query.filter(
            Club.club_name.contains(search)
        ).all()

    else:

        all_clubs = Club.query.all()

    return render_template(
        "clubs.html",
        clubs=all_clubs
    )
@app.route("/club/<int:id>")
def club_details(id):

    if "admin" not in session and "student" not in session:
        return redirect(url_for("login"))

    club = Club.query.get_or_404(id)

    events = Event.query.filter_by(
        club_name=club.club_name
    ).all()

    return render_template(
        "club_details.html",
        club=club,
        events=events
    )
@app.route("/add-club", methods=["GET", "POST"])
def add_club():

    if "admin" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        print("POST RECEIVED")
        print(request.form)
    

    

        if "logo" in request.files:

            logo = request.files["logo"]

            if logo.filename != "":

                filename = secure_filename(logo.filename)

                logo.save(
                    os.path.join(
                        app.config["UPLOAD_FOLDER"],
                        filename
                    )
                )

        club = Club(

            club_name=request.form["club_name"],

            category=request.form["category"],

            description=request.form["description"],

            logo=filename

        )

        db.session.add(club)

        db.session.commit()

        return redirect(url_for("clubs"))

    return render_template("add_club.html")
@app.route("/edit-club/<int:id>", methods=["GET", "POST"])
def edit_club(id):

    if "admin" not in session:
        return redirect(url_for("login"))

    club = Club.query.get_or_404(id)

    if request.method == "POST":

        club.club_name = request.form["club_name"]

        club.category = request.form["category"]

        club.description = request.form["description"]

        if "logo" in request.files:

            logo = request.files["logo"]

            if logo.filename != "":

                filename = secure_filename(logo.filename)

                logo.save(
                    os.path.join(
                        app.config["UPLOAD_FOLDER"],
                        filename
                    )
                )

                club.logo = filename

        db.session.commit()

        return redirect(url_for("clubs"))

    return render_template(
        "edit_club.html",
        club=club
    )
@app.route("/delete-club/<int:id>")
def delete_club(id):

    if "admin" not in session:
        return redirect(url_for("login"))

    club = Club.query.get_or_404(id)

    db.session.delete(club)

    db.session.commit()

    return redirect(url_for("clubs"))
@app.route("/events")
def events():

    if "admin" not in session and "student" not in session:
        return redirect(url_for("login"))

    all_events = Event.query.all()

    return render_template(
        "events.html",
        events=all_events
    )
@app.route("/add-event", methods=["GET", "POST"])
def add_event():

    if "admin" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        event = Event(

            event_name=request.form["event_name"],

            club_name=request.form["club_name"],

            event_date=request.form["event_date"],

            venue=request.form["venue"],

            description=request.form["description"]

        )

        db.session.add(event)
        db.session.commit()

        return redirect(url_for("events"))

    clubs = Club.query.all()

    return render_template(
        "add_event.html",
        clubs=clubs
    )
@app.route("/edit-event/<int:id>", methods=["GET", "POST"])
def edit_event(id):

    if "admin" not in session:
        return redirect(url_for("login"))

    event = Event.query.get_or_404(id)

    if request.method == "POST":

        event.event_name = request.form["event_name"]
        event.club_name = request.form["club_name"]
        event.event_date = request.form["event_date"]
        event.venue = request.form["venue"]
        event.description = request.form["description"]

        db.session.commit()

        return redirect(url_for("events"))

    clubs = Club.query.all()

    return render_template(
        "edit_event.html",
        event=event,
        clubs=clubs
    )
@app.route("/delete-event/<int:id>")
def delete_event(id):

    if "admin" not in session:
        return redirect(url_for("login"))

    event = Event.query.get_or_404(id)

    db.session.delete(event)
    db.session.commit()

    return redirect(url_for("events"))
@app.route("/register", methods=["GET", "POST"])
def register():

    if "student" not in session:
        return redirect(url_for("student_login"))

    student = Student.query.get(session["student"])

    if request.method == "POST":

        registration = Registration(

            student_name=student.name,

            roll_number=student.roll_number,

            email=student.email,

            club_name=request.form["club_name"],

            event_name=request.form["event_name"]

        )

        db.session.add(registration)
        db.session.commit()

        return redirect(url_for("student_dashboard"))

    clubs = Club.query.all()
    events = Event.query.all()

    return render_template(
        "register.html",
        student=student,
        clubs=clubs,
        events=events
    )
@app.route("/registrations")
def registrations():

    if "admin" not in session:
        return redirect(url_for("login"))

    all_registrations = Registration.query.all()

    return render_template(
        "registrations.html",
        registrations=all_registrations
    )
if __name__ == "__main__":
    app.run(debug=True)