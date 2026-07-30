"""Initial tables

Revision ID: 001
Revises:
Create Date: 2026-01-01 00:00:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'audit_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('url', sa.String(2048), nullable=False),
        sa.Column('site_name', sa.String(255)),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('max_pages', sa.Integer, default=10),
        sa.Column('pages_crawled', sa.Integer, default=0),
        sa.Column('total_violations', sa.Integer, default=0),
        sa.Column('critical_violations', sa.Integer, default=0),
        sa.Column('compliance_score', sa.Float),
        sa.Column('error_message', sa.Text),
        sa.Column('started_at', sa.DateTime(timezone=True)),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        'audit_pages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('audit_jobs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('url', sa.String(2048), nullable=False),
        sa.Column('title', sa.String(512)),
        sa.Column('violation_count', sa.Integer, default=0),
        sa.Column('critical_count', sa.Integer, default=0),
        sa.Column('warning_count', sa.Integer, default=0),
        sa.Column('compliance_score', sa.Float),
        sa.Column('crawled_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        'violations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('page_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('audit_pages.id', ondelete='CASCADE'), nullable=False),
        sa.Column('wcag_criterion', sa.String(50), nullable=False),
        sa.Column('wcag_level', sa.String(5), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('element', sa.Text),
        sa.Column('fix_suggestion', sa.Text),
        sa.Column('help_url', sa.String(512)),
    )
    op.create_index('ix_audit_jobs_status', 'audit_jobs', ['status'])
    op.create_index('ix_violations_severity', 'violations', ['severity'])

def downgrade() -> None:
    op.drop_table('violations')
    op.drop_table('audit_pages')
    op.drop_table('audit_jobs')
