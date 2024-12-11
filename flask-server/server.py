from flask import Flask, request, jsonify
from models import db, Job, Applicant, Recruiter, Interviewer, Application, Interview
from flask_migrate import Migrate
from sqlalchemy.sql import text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ikh:password@localhost/jobtracker'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)


# Recruiter view endpoint
@app.route('/recruitersView', methods=['GET'])
def get_recruiters_view():
    recruiters = Recruiter.query.all()
    return jsonify([{
        "recruiter_id": recruiter.recruiter_id,
        "name": recruiter.name,
        "email": recruiter.email,
        "phone_number": recruiter.phone_number
    } for recruiter in recruiters])

# Interview view endpoint
@app.route('/interviewsView', methods=['GET'])
def get_interviews_view():
    # ORM
    interviews = Interview.query.all()
    return jsonify([{
        "interview_id": interview.interview_id,
        "application_id": interview.application_id,
        "interviewer_id": interview.interviewer_id,
        "interview_date": interview.interview_date.strftime('%Y-%m-%d'),
        "interview_time": interview.interview_time.strftime('%H:%M:%S'),
        "status": interview.status
    } for interview in interviews])

# Interviewer view endpoint
@app.route('/interviewersView', methods=['GET'])
def get_interviewers_view():
    # ORM
    interviewers = Interviewer.query.all()
    return jsonify([{
        "interviewer_id": interviewer.interviewer_id,
        "name": interviewer.name,
        "email": interviewer.email,
        "phone_number": interviewer.phone_number
    } for interviewer in interviewers])

# Applicant view endpoint
@app.route('/applicantsView', methods=['GET'])
def get_applicants_view():
    applicants = Applicant.query.all()
    return jsonify([{
        "applicant_id": applicant.applicant_id,
        "name": applicant.name,
        "email": applicant.email,
        "phone_number": applicant.phone_number
    } for applicant in applicants])

# Fetch all jobs - include recruiter name
@app.route('/jobView', methods=['GET'])
def fetch_jobs():
    # ORM
    jobs = Job.query.join(Recruiter, Job.recruiter_id == Recruiter.recruiter_id).add_columns(
        Job.job_id, Job.title, Job.description, Job.location, Job.posted_date, Job.status,
        Recruiter.name.label("recruiter_name")
    ).all()

    return jsonify([
        {
            "job_id": job.job_id,
            "title": job.title,
            "description": job.description,
            "location": job.location,
            "posted_date": job.posted_date.strftime('%Y-%m-%d'),
            "status": job.status,
            "recruiter_name": job.recruiter_name
        }
        for job in jobs
    ])

# Fetch all recruiters for dropdown
@app.route('/recruitersDropdown', methods=['GET'])
def fetch_recruiters():
    recruiters = Recruiter.query.all()
    return jsonify([
        {
            "recruiter_id": recruiter.recruiter_id,
            "name": recruiter.name
        }
        for recruiter in recruiters
    ])

# Add a new job
@app.route('/addJob', methods=['POST'])
def add_job():
    data = request.json
    new_job = Job(
        title=data['title'],
        description=data['description'],
        location=data['location'],
        posted_date=data['posted_date'],
        status=data['status'],
        recruiter_id=data['recruiter_id']
    )
    db.session.add(new_job)
    db.session.commit()

    return jsonify({
        "job_id": new_job.job_id,
        "title": new_job.title,
        "description": new_job.description,
        "location": new_job.location,
        "posted_date": new_job.posted_date.strftime('%Y-%m-%d'),
        "status": new_job.status,
        "recruiter_id": new_job.recruiter_id
    }), 201

# Edit a job
@app.route('/editJob/<int:job_id>', methods=['PUT'])
def edit_job(job_id):
    data = request.json
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    job.title = data.get('title', job.title)
    job.description = data.get('description', job.description)
    job.location = data.get('location', job.location)
    job.posted_date = data.get('posted_date', job.posted_date)
    job.status = data.get('status', job.status)
    job.recruiter_id = data.get('recruiter_id', job.recruiter_id)

    db.session.commit()
    return jsonify({"message": "Job updated successfully!"})

# Delete a job and its related applications/interviews
@app.route('/deleteJob/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    applications = Application.query.filter_by(job_id=job_id).all()
    for application in applications:
        interviews = Interview.query.filter_by(application_id=application.application_id).all()
        for interview in interviews:
            db.session.delete(interview)
        db.session.delete(application)
    db.session.commit()
    db.session.delete(job)
    db.session.commit()
    return jsonify({"message": "Job and related data deleted successfully!"})



@app.route('/applicationView', methods=['GET'])
def get_application_view():
    # PREPARED STATEMENT - Base query to fetch application data
    base_query = """
    SELECT 
        a.application_id, a.applicant_id, app.name AS applicant_name,
        a.job_id, j.title AS job_title, j.location AS job_location, 
        j.posted_date, j.recruiter_id, r.name AS recruiter_name,
        a.status AS application_status, a.application_date,
        i.interview_date, i.interview_time, ir.name AS interviewer_name
    FROM applications a
    LEFT JOIN applicants app ON a.applicant_id = app.applicant_id
    LEFT JOIN jobs j ON a.job_id = j.job_id
    LEFT JOIN recruiters r ON j.recruiter_id = r.recruiter_id
    LEFT JOIN interviews i ON a.application_id = i.application_id
    LEFT JOIN interviewers ir ON i.interviewer_id = ir.interviewer_id
    """

    filters = []
    params = {}

    job_id = request.args.get('job_id')
    applicant_id = request.args.get('applicant_id')
    recruiter_id = request.args.get('recruiter_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if job_id:
        filters.append("a.job_id = :job_id")
        params['job_id'] = job_id

    if applicant_id:
        filters.append("a.applicant_id = :applicant_id")
        params['applicant_id'] = applicant_id

    if recruiter_id:
        filters.append("j.recruiter_id = :recruiter_id")
        params['recruiter_id'] = recruiter_id

    if start_date and end_date:
        filters.append("a.application_date BETWEEN :start_date AND :end_date")
        params['start_date'] = start_date
        params['end_date'] = end_date
    elif start_date:
        filters.append("a.application_date >= :start_date")
        params['start_date'] = start_date
    elif end_date:
        filters.append("a.application_date <= :end_date")
        params['end_date'] = end_date

    if filters:
        base_query += " WHERE " + " AND ".join(filters)

    # PREPARED STATEMENT EXECUTION
    stmt = text(base_query)
    results = db.session.execute(stmt, params).fetchall()

    application_data = [
        {
            "application_id": row[0],
            "applicant_id": row[1],
            "applicant_name": row[2],
            "job_id": row[3],
            "job_title": row[4],
            "job_location": row[5],
            "posted_date": row[6].strftime('%Y-%m-%d') if row[6] else None,
            "recruiter_id": row[7],
            "recruiter_name": row[8],
            "application_status": row[9],
            "application_date": row[10].strftime('%Y-%m-%d') if row[10] else None,
            "interview_date": row[11].strftime('%Y-%m-%d') if row[11] else None,
            "interview_time": row[12].strftime('%H:%M') if row[12] else None,
            "interviewer_name": row[13]
        }
        for row in results
    ]

    statistics = {}
    if job_id:
        # Number of applications to this job
        application_count = db.session.execute(text("""
            SELECT COUNT(*) 
            FROM applications
            WHERE job_id = :job_id
            AND (:start_date IS NULL OR application_date >= :start_date)
            AND (:end_date IS NULL OR application_date <= :end_date)
        """), {'job_id': job_id, 'start_date': start_date, 'end_date': end_date}).scalar()

        # Average # of days between post date and application date
        avg_days_after_posting = db.session.execute(text("""
            SELECT AVG(DATE_PART('day', application_date::timestamp - posted_date::timestamp))
            FROM applications
            JOIN jobs ON applications.job_id = jobs.job_id
            WHERE applications.job_id = :job_id
            AND (:start_date IS NULL OR application_date >= :start_date)
            AND (:end_date IS NULL OR application_date <= :end_date)
        """), {'job_id': job_id, 'start_date': start_date, 'end_date': end_date}).scalar()

        # Number of interviews for the job
        num_interviews = db.session.execute(text("""
            SELECT COUNT(*)
            FROM interviews
            WHERE application_id IN (
                SELECT application_id
                FROM applications
                WHERE job_id = :job_id
                AND (:start_date IS NULL OR application_date >= :start_date)
                AND (:end_date IS NULL OR application_date <= :end_date)
            )
        """), {'job_id': job_id, 'start_date': start_date, 'end_date': end_date}).scalar()

        statistics = {
            "Application Count": application_count,
            "Average Days after Posting": avg_days_after_posting,
            "Number of Interviews": num_interviews
        }

    elif applicant_id:
        # Number of jobs applied to
        job_count = db.session.execute(text("""
            SELECT COUNT(DISTINCT job_id)
            FROM applications
            WHERE applicant_id = :applicant_id
            AND (:start_date IS NULL OR application_date >= :start_date)
            AND (:end_date IS NULL OR application_date <= :end_date)
        """), {'applicant_id': applicant_id, 'start_date': start_date, 'end_date': end_date}).scalar()

        # Number of in-progress applications
        num_in_progress = db.session.execute(text("""
            SELECT COUNT(*)
            FROM applications
            WHERE applicant_id = :applicant_id
            AND status IN ('Incomplete', 'In Review')
            AND (:start_date IS NULL OR application_date >= :start_date)
            AND (:end_date IS NULL OR application_date <= :end_date)
        """), {'applicant_id': applicant_id, 'start_date': start_date, 'end_date': end_date}).scalar()

        # Success rate (percentage) of completed applications (complete / accepted)

        completed_applications = db.session.execute(text("""
            SELECT COUNT(*)
            FROM applications
            WHERE applicant_id = :applicant_id
            AND status IN ('Accepted', 'Rejected')
            AND (:start_date IS NULL OR application_date >= :start_date)
            AND (:end_date IS NULL OR application_date <= :end_date)
        """), {'applicant_id': applicant_id, 'start_date': start_date, 'end_date': end_date}).scalar()

        accepted_applications = db.session.execute(text("""
            SELECT COUNT(*)
            FROM applications
            WHERE applicant_id = :applicant_id
            AND status = 'Accepted'
            AND (:start_date IS NULL OR application_date >= :start_date)
            AND (:end_date IS NULL OR application_date <= :end_date)
        """), {'applicant_id': applicant_id, 'start_date': start_date, 'end_date': end_date}).scalar()

        success_rate = (
            f"{accepted_applications}/{completed_applications} "
            f"({(accepted_applications / completed_applications * 100):.2f}%)"
            if completed_applications > 0
            else "No completed applications"
        )

        statistics = {
            "Total Job Application Count": job_count,
            "Applications in Progress": num_in_progress,
            "Success Rate of Completed Applications": success_rate
        }

    elif recruiter_id:
        # Number of distinct jobs the recruiter is responsible for
        distinct_jobs = db.session.execute(text("""
            SELECT COUNT(DISTINCT a.job_id)
            FROM applications a LEFT JOIN jobs j ON a.job_id = j.job_id
            WHERE recruiter_id = :recruiter_id
            AND (:start_date IS NULL OR application_date >= :start_date)
            AND (:end_date IS NULL OR application_date <= :end_date)
        """), {'recruiter_id': recruiter_id, 'start_date': start_date, 'end_date': end_date}).scalar()

        # Number of in-progress and completed applications for those jobs

        num_in_progress = db.session.execute(text("""
            SELECT COUNT(*)
            FROM applications
            WHERE job_id IN (SELECT job_id FROM jobs WHERE recruiter_id = :recruiter_id)
            AND status IN ('Incomplete', 'In Review')
            AND (:start_date IS NULL OR application_date >= :start_date)
            AND (:end_date IS NULL OR application_date <= :end_date)
        """), {'recruiter_id': recruiter_id, 'start_date': start_date, 'end_date': end_date}).scalar()

        num_completed = db.session.execute(text("""
            SELECT COUNT(*)
            FROM applications
            WHERE job_id IN (SELECT job_id FROM jobs WHERE recruiter_id = :recruiter_id)
            AND status IN ('Accepted', 'Rejected')
            AND (:start_date IS NULL OR application_date >= :start_date)
            AND (:end_date IS NULL OR application_date <= :end_date)
        """), {'recruiter_id': recruiter_id, 'start_date': start_date, 'end_date': end_date}).scalar()

        # Number of distinct applicants for the recruiter's jobs
        distinct_applicants = db.session.execute(text("""
            SELECT COUNT(DISTINCT applicant_id)
            FROM applications
            WHERE job_id IN (SELECT job_id FROM jobs WHERE recruiter_id = :recruiter_id)
            AND (:start_date IS NULL OR application_date >= :start_date)
            AND (:end_date IS NULL OR application_date <= :end_date)
        """), {'recruiter_id': recruiter_id, 'start_date': start_date, 'end_date': end_date}).scalar()

        # Total number of applications associated with the recruiter's jobs
        total_applications = db.session.execute(text("""
            SELECT COUNT(*)
            FROM applications
            WHERE job_id IN (SELECT job_id FROM jobs WHERE recruiter_id = :recruiter_id)
            AND (:start_date IS NULL OR application_date >= :start_date)
            AND (:end_date IS NULL OR application_date <= :end_date)
        """), {'recruiter_id': recruiter_id, 'start_date': start_date, 'end_date': end_date}).scalar()

        avg_applications_per_job = total_applications / distinct_jobs if distinct_jobs > 0 else 0

        statistics = {
            "Total Applications": total_applications,
            "Average Applications per Job": avg_applications_per_job,
            "Distinct Jobs": distinct_jobs,
            "Jobs in Progress": num_in_progress,
            "Completed Jobs": num_completed,
            "Distinct Applicants Associated": distinct_applicants
        }

    return jsonify({
        "applications": application_data,
        "statistics": statistics
    })


# Fetch dropdown options for filters
@app.route('/getJobs', methods=['GET'])
def fetch_job_idname():
    jobs = Job.query.all()
    return jsonify([{"id": job.job_id, "name": job.title} for job in jobs])

@app.route('/getRecruiters', methods=['GET'])
def fetch_recruiters_idname():
    recruiters = Recruiter.query.all()
    return jsonify([{"id": recruiter.recruiter_id, "name": recruiter.name} for recruiter in recruiters])

@app.route('/getApplicants', methods=['GET'])
def fetch_applicants_idname():
    applicants = Applicant.query.all()
    return jsonify([{"id": applicant.applicant_id, "name": applicant.name} for applicant in applicants])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
