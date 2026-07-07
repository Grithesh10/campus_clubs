from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    roll_number = db.Column(db.String(30), unique=True, nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    department = db.Column(db.String(100), nullable=False)

    year = db.Column(db.String(20), nullable=False)

    password = db.Column(db.String(200), nullable=False)


class Club(db.Model):
    __tablename__ = "clubs"

    id = db.Column(db.Integer, primary_key=True)

    club_name = db.Column(db.String(100), nullable=False)

    category = db.Column(db.String(100), nullable=False)

    description = db.Column(db.Text)

    logo = db.Column(db.String(255))


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)

    event_name = db.Column(db.String(100), nullable=False)

    club_name = db.Column(db.String(100), nullable=False)

    event_date = db.Column(db.String(30), nullable=False)

    venue = db.Column(db.String(150), nullable=False)

    description = db.Column(db.Text)


class Registration(db.Model):
    __tablename__ = "registrations"

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.id"),
        nullable=False
    )

    student_name = db.Column(db.String(100), nullable=False)

    roll_number = db.Column(db.String(30), nullable=False)

    email = db.Column(db.String(120), nullable=False)

    club_name = db.Column(db.String(100), nullable=False)

    event_name = db.Column(db.String(100), nullable=False)