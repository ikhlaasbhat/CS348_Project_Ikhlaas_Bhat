from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy import Index

db = SQLAlchemy()

# Status types
job_status_enum = ENUM('Open/Accepting Applications', 'Closed - Still Deciding', 'Closed & Decided', name='job_status_enum', create_type=True)
application_status_enum = ENUM('Incomplete', 'In Review', 'Rejected', 'Accepted', name='application_status_enum', create_type=True)
interview_status_enum = ENUM('Awaiting Interview', 'Complete', 'No Show', name='interview_status_enum', create_type=True)

class Job(db.Model):
    __tablename__ = 'jobs'
    job_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100))
    posted_date = db.Column(db.Date, nullable=False)
    status = db.Column(job_status_enum, nullable=False)
    recruiter_id = db.Column(db.Integer, db.ForeignKey('recruiters.recruiter_id'), nullable=False)


    __table_args__ = (
        Index('ix_jobs_recruiter_id', 'recruiter_id'),  # INDEX on recruiter_id - Optimizes filtering by recruiter
        Index('ix_jobs_posted_date', 'posted_date')  # INDEX on job posted date - Optimizes date range queries for jobs
    )

class Applicant(db.Model):
    __tablename__ = 'applicants'
    applicant_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)

class Recruiter(db.Model):
    __tablename__ = 'recruiters'
    recruiter_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)

class Interviewer(db.Model):
    __tablename__ = 'interviewers'
    interviewer_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)

class Application(db.Model):
    __tablename__ = 'applications'
    application_id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.job_id'), nullable=False)
    applicant_id = db.Column(db.Integer, db.ForeignKey('applicants.applicant_id'), nullable=False)
    application_date = db.Column(db.Date, nullable=False)
    status = db.Column(application_status_enum, nullable=False)

    interview = db.relationship('Interview', uselist=False, back_populates='application')

    __table_args__ = (
        Index('ix_applications_job_id', 'job_id'),  # INDEX on job_id - Optimizes filtering applications by job
        Index('ix_applications_applicant_id', 'applicant_id'),  # INDEX on applicant_id - Optimizes filtering applications by applicant
        Index('ix_applications_application_date', 'application_date'),  # INDEX on application date - Optimizes date range queries
        Index('ix_applications_status', 'status')  # INDEX on status - Optimizes filtering applications by application status
    )

class Interview(db.Model):
    __tablename__ = 'interviews'
    interview_id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.application_id'), nullable=False, unique=True)
    interviewer_id = db.Column(db.Integer, db.ForeignKey('interviewers.interviewer_id'), nullable=False)
    interview_date = db.Column(db.Date, nullable=False)
    interview_time = db.Column(db.Time, nullable=False)
    status = db.Column(interview_status_enum, nullable=False)

    application = db.relationship('Application', back_populates='interview')

    __table_args__ = (
        Index('ix_interviews_application_id', 'application_id'),  # INDEX - Optimizes joining interviews with applications
        Index('ix_interviews_interviewer_id', 'interviewer_id'),  # INDEX - Optimizes filtering by interviewer_id
        Index('ix_interviews_interview_date', 'interview_date')  # INDEX - Optimizes date range queries for interviews
    )
