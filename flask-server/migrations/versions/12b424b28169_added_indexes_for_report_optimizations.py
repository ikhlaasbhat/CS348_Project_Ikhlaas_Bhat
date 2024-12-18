"""added indexes for report optimizations

Revision ID: 12b424b28169
Revises: 562068e90f6f
Create Date: 2024-12-11 14:48:40.553065

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '12b424b28169'
down_revision = '562068e90f6f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('applications', schema=None) as batch_op:
        batch_op.create_index('ix_applications_applicant_id', ['applicant_id'], unique=False)
        batch_op.create_index('ix_applications_application_date', ['application_date'], unique=False)
        batch_op.create_index('ix_applications_job_id', ['job_id'], unique=False)
        batch_op.create_index('ix_applications_status', ['status'], unique=False)

    with op.batch_alter_table('interviews', schema=None) as batch_op:
        batch_op.create_index('ix_interviews_application_id', ['application_id'], unique=False)
        batch_op.create_index('ix_interviews_interview_date', ['interview_date'], unique=False)
        batch_op.create_index('ix_interviews_interviewer_id', ['interviewer_id'], unique=False)

    with op.batch_alter_table('jobs', schema=None) as batch_op:
        batch_op.drop_index('ix_recruiter_id')
        batch_op.create_index('ix_jobs_posted_date', ['posted_date'], unique=False)
        batch_op.create_index('ix_jobs_recruiter_id', ['recruiter_id'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('jobs', schema=None) as batch_op:
        batch_op.drop_index('ix_jobs_recruiter_id')
        batch_op.drop_index('ix_jobs_posted_date')
        batch_op.create_index('ix_recruiter_id', ['recruiter_id'], unique=False)

    with op.batch_alter_table('interviews', schema=None) as batch_op:
        batch_op.drop_index('ix_interviews_interviewer_id')
        batch_op.drop_index('ix_interviews_interview_date')
        batch_op.drop_index('ix_interviews_application_id')

    with op.batch_alter_table('applications', schema=None) as batch_op:
        batch_op.drop_index('ix_applications_status')
        batch_op.drop_index('ix_applications_job_id')
        batch_op.drop_index('ix_applications_application_date')
        batch_op.drop_index('ix_applications_applicant_id')

    # ### end Alembic commands ###
