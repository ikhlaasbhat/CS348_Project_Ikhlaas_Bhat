from datetime import date, time, timedelta
from random import randint, choice, sample
from server import app
from models import db, Job, Applicant, Recruiter, Interviewer, Application, Interview


def populate_sample_data():
    with app.app_context():

        db.session.query(Interview).delete()
        db.session.query(Application).delete()
        db.session.query(Job).delete()
        db.session.query(Applicant).delete()
        db.session.query(Interviewer).delete()
        db.session.query(Recruiter).delete()

        recruiters = [
            Recruiter(name="Alice Johnson", email="alice.johnson@example.com", phone_number="123-456-7890"),
            Recruiter(name="Bob Smith", email="bob.smith@example.com", phone_number="234-567-8901"),
            Recruiter(name="Cathy Lee", email="cathy.lee@example.com", phone_number="345-678-9012")
        ]
        db.session.add_all(recruiters)
        db.session.commit()

        job_titles = ["Software Engineer", "Data Analyst", "Project Manager", "Marketing Specialist", "HR Coordinator",
                      "Sales Associate", "UX Designer", "DevOps Engineer", "Technical Writer", "IT Support"]
        job_locations = ["New York", "San Francisco", "Chicago", "Austin", "Boston"]
        statuses = ["Open/Accepting Applications", "Closed - Still Deciding", "Closed & Decided"]
        jobs = []

        for title in job_titles:
            recruiter = choice(recruiters)
            job = Job(
                title=title,
                description=f"{title} at {choice(job_locations)}.",
                location=choice(job_locations),
                posted_date=date.today() - timedelta(days=randint(10, 50)),
                status=choice(statuses),
                recruiter_id=recruiter.recruiter_id
            )
            jobs.append(job)
        db.session.add_all(jobs)
        db.session.commit()

        # Create sample applicants
        applicant_names = ["John Doe", "Jane Smith", "Emily Brown", "Michael Davis", "Sarah Wilson", "David Clark",
                           "Laura Lewis", "James Taylor", "Sophia Martin", "Daniel White"]
        applicants = []

        for name in applicant_names:
            applicant = Applicant(
                name=name,
                email=f"{name.lower().replace(' ', '.')}@example.com",
                phone_number=f"555-01{randint(10, 99)}"
            )
            applicants.append(applicant)
        db.session.add_all(applicants)
        db.session.commit()

        applications = []
        for job in jobs:
            num_applicants = randint(4, 10)
            selected_applicants = sample(applicants, num_applicants)
            for applicant in selected_applicants:
                application = Application(
                    job_id=job.job_id,
                    applicant_id=applicant.applicant_id,
                    application_date=job.posted_date + timedelta(days=randint(1, 15)),
                    status=choice(["Incomplete", "In Review", "Accepted", "Rejected"])
                )
                applications.append(application)
        db.session.add_all(applications)
        db.session.commit()

        interviewer_names = ["Sarah Parker", "James Lee", "Olivia Scott", "Matthew Harris", "Ethan Johnson"]
        interviewers = []

        for name in interviewer_names:
            interviewer = Interviewer(
                name=name,
                email=f"{name.lower().replace(' ', '.')}@example.com",
                phone_number=f"555-09{randint(10, 99)}"
            )
            interviewers.append(interviewer)
        db.session.add_all(interviewers)
        db.session.commit()

        interviews = []
        for application in applications:
            if choice([True, False, True]): 
                interviewer = choice(interviewers)
                interview = Interview(
                    application_id=application.application_id,
                    interviewer_id=interviewer.interviewer_id,
                    interview_date=application.application_date + timedelta(days=randint(1, 7)),
                    interview_time=time(hour=randint(9, 17), minute=0),
                    status=choice(["Awaiting Interview", "Complete", "No Show"])
                )
                interviews.append(interview)
        db.session.add_all(interviews)
        db.session.commit()

        print("Sample data has been populated successfully.")

if __name__ == "__main__":
    populate_sample_data()
