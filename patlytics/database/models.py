from patlytics.database import db
from datetime import datetime


class TimestampMixin:
    ctime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    utime = db.Column(db.DateTime, onupdate=datetime.utcnow,
                      default=datetime.utcnow)


company_product = db.Table('company_product',
                           db.Column("ctime", db.DateTime,
                                     nullable=False, default=datetime.utcnow),
                           db.Column('company_id', db.Integer, db.ForeignKey(
                               'company.id', ondelete='CASCADE'), primary_key=True),
                           db.Column('product_id', db.Integer, db.ForeignKey(
                               'product.id', ondelete='CASCADE'), primary_key=True)
                           )


class Company(TimestampMixin, db.Model):
    """Company model representing business entities"""
    __tablename__ = 'company'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True, index=True)

    product = db.relationship(
        'Product',
        secondary="company_product",
        back_populates='company',
        lazy='dynamic'
    )


class Product(TimestampMixin, db.Model):
    """Product model representing products that can belong to multiple companies"""
    __tablename__ = 'product'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)

    company = db.relationship(
        'Company',
        secondary="company_product",
        back_populates='product',
        lazy='dynamic'
    )


class Patent(TimestampMixin, db.Model):
    """Patent model for storing patent information"""
    __tablename__ = 'patent'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patent_id = db.Column(db.Integer, unique=True, nullable=False, index=True)
    title = db.Column(db.String(500), nullable=False)


class User(TimestampMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    hashed_password = db.Column(db.String(128), nullable=False)

    reports = db.relationship(
        'Report',
        back_populates='user',
        lazy='dynamic',
        cascade="all, delete-orphan"
    )


class Report(TimestampMixin, db.Model):
    __tablename__ = 'report'

    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(
        db.Integer,
        db.ForeignKey('user.id', ondelete='CASCADE'),
        nullable=False
    )
    patent_id = db.Column(
        db.Integer,
        db.ForeignKey('patent.patent_id'),
        nullable=False
    )
    company_id = db.Column(
        db.Integer,
        db.ForeignKey('company.id', ondelete='CASCADE'),
        nullable=False
    )
    input_company = db.Column(db.String(200), nullable=False)
    analysis_results = db.Column(db.JSON, nullable=False)

    user = db.relationship(
        'User',
        back_populates='reports'
    )
    patent = db.relationship(
        'Patent',
        backref=db.backref(
            'reports',
            lazy='dynamic',
            cascade="all, delete-orphan"
        )
    )
    company = db.relationship(
        'Company',
        backref=db.backref(
            'reports',
            lazy='dynamic',
            cascade="all, delete-orphan"
        )
    )
