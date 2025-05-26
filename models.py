from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Association tables for many-to-many relationships
professor_subject = db.Table('professor_subject',
    db.Column('professor_id', db.Integer, db.ForeignKey('professors.id'), primary_key=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subjects.id'), primary_key=True)
)

degree_subject = db.Table('degree_subject',
    db.Column('degree_id', db.Integer, db.ForeignKey('degrees.id'), primary_key=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subjects.id'), primary_key=True)
)

# Base User model (superclass)
class User(db.Model, UserMixin):
    """
    Base User model with authentication capabilities.
    Attributes:
        id (int): Primary key
        username (str): Unique username
        email (str): Unique email address
        password_hash (str): Hashed password
        created_at (datetime): Account creation timestamp
        user_type (str): Type of user (for polymorphic behavior)
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_type = db.Column(db.String(50))  # Used for polymorphic behavior

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': user_type
    }

    def set_password(self, password):
        """Set the user's password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the stored hash"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        """
        Returns a string representation of the User object.

        The returned string includes the class name and the username attribute,
        which is useful for debugging and logging purposes.

        Returns:
            str: A string in the format '<User username>'.
        """
        return f'<User {self.username}>'

# Professor model (subclass)
class Professor(User):
    """
    Represents a Professor user, inheriting from the User model.
    Attributes:
        __tablename__ (str): The name of the database table for professors.
        id (int): Primary key, references the users table.
        department (str): The department to which the professor belongs.
        subjects (list): List of subjects taught by the professor.
    """
    __tablename__ = 'professors'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    department = db.Column(db.String(100), nullable=True)
    
    # Relationship with subjects
    subjects = db.relationship('Subject', 
                             secondary=professor_subject,
                             backref=db.backref('professors', lazy='dynamic'),
                             lazy='dynamic')

    __mapper_args__ = {
        'polymorphic_identity': 'professor',
    }

    def __repr__(self):
        return f'<Professor {self.username} - {self.department}>'

class Subject(db.Model):
    """
    Represents a subject/course in the university.
    Attributes:
        id (int): Primary key
        code (str): Unique subject code (e.g., 'CS101')
        name (str): Name of the subject
        credits (int): Number of credits
        description (str): Description of the subject
        degrees (list): List of degrees that include this subject
        lab_guides (list): List of lab guides associated with this subject
        weekly_topics (list): List of weekly topics for this subject
    """
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    credits = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)

    # Relationship with degrees
    degrees = db.relationship('Degree',
                            secondary=degree_subject,
                            backref=db.backref('subjects', lazy='dynamic'),
                            lazy='dynamic')
    
    # Relationship with lab guides
    lab_guides = db.relationship('LabGuide', backref='subject', lazy='dynamic')

    # Relationship with weekly topics
    weekly_topics = db.relationship('WeeklyTopic', backref='subject', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Subject {self.code} - {self.name}>'

class Degree(db.Model):
    """
    Represents a degree program in the university.
    Attributes:
        id (int): Primary key
        code (str): Unique degree code (e.g., 'CS')
        name (str): Name of the degree
        description (str): Description of the degree program
        duration (int): Duration in semesters
        subjects (list): List of subjects in this degree
    """
    __tablename__ = 'degrees'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    duration = db.Column(db.Integer, nullable=False)  # Duration in semesters

    def __repr__(self):
        return f'<Degree {self.code} - {self.name}>'

class Laboratory(db.Model):
    """
    Represents a physical laboratory in the university.
    Attributes:
        id (int): Primary key
        name (str): Name of the laboratory
        code (str): Unique laboratory code
        location (str): Physical location/building
        capacity (int): Maximum number of students
        equipment (str): Description of available equipment
        is_active (bool): Whether the laboratory is currently in use
        created_at (datetime): When the laboratory was added to the system
        updated_at (datetime): When the laboratory information was last updated
        lab_guides (list): List of lab guides created in this laboratory
    """
    __tablename__ = 'laboratories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    equipment = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with lab guides
    lab_guides = db.relationship('LabGuide', backref='laboratory', lazy='dynamic')

    def __repr__(self):
        return f'<Laboratory {self.code} - {self.name}>'

    @property
    def is_available(self):
        """Check if the laboratory is available for use"""
        return self.is_active

    def deactivate(self):
        """Deactivate the laboratory"""
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def activate(self):
        """Activate the laboratory"""
        self.is_active = True
        self.updated_at = datetime.utcnow()

class LabGuide(db.Model):
    """
    Represents a laboratory guide for a subject.
    Attributes:
        id (int): Primary key
        title (str): Title of the lab guide
        content (str): The actual content of the lab guide
        lab_number (int): The number of the lab (e.g., Lab 1, Lab 2)
        created_at (datetime): When the lab guide was created
        updated_at (datetime): When the lab guide was last updated
        subject_id (int): Foreign key to the associated subject
        weekly_topic_id (int): Foreign key to the associated weekly topic
        created_by_id (int): Foreign key to the professor who created it
        status (str): Status of the lab guide (draft, published, archived)
        difficulty_level (str): Difficulty level of the lab (beginner, intermediate, advanced)
        estimated_duration (int): Estimated duration in minutes
        laboratory_id (int): Foreign key to the assigned laboratory
    """
    __tablename__ = 'lab_guides'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)  # Using Text for large content
    lab_number = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    weekly_topic_id = db.Column(db.Integer, db.ForeignKey('weekly_topics.id'), nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('professors.id'), nullable=False)
    
    # Additional metadata
    status = db.Column(db.String(20), nullable=False, default='draft')  # draft, published, archived
    difficulty_level = db.Column(db.String(20), nullable=False, default='intermediate')  # beginner, intermediate, advanced
    estimated_duration = db.Column(db.Integer, nullable=True)  # in minutes
    
    # Relationships
    created_by = db.relationship('Professor', backref=db.backref('created_lab_guides', lazy='dynamic'))
    weekly_topic = db.relationship('WeeklyTopic', backref=db.backref('lab_guides', lazy='dynamic'))
    laboratory_id = db.Column(db.Integer, db.ForeignKey('laboratories.id'), nullable=True)

    def __repr__(self):
        return f'<LabGuide {self.lab_number} - {self.title}>'

    @property
    def is_published(self):
        return self.status == 'published'

    @property
    def is_draft(self):
        return self.status == 'draft'

    def publish(self):
        """Publish the lab guide"""
        self.status = 'published'
        self.updated_at = datetime.utcnow()

    def archive(self):
        """Archive the lab guide"""
        self.status = 'archived'
        self.updated_at = datetime.utcnow()

class WeeklyTopic(db.Model):
    """
    Represents a weekly topic in a subject.
    Attributes:
        id (int): Primary key
        week_number (int): Week number in the semester
        title (str): Title of the topic
        description (str): Detailed description of what will be covered
        subject_id (int): Foreign key to the associated subject
    """
    __tablename__ = 'weekly_topics'
    id = db.Column(db.Integer, primary_key=True)
    week_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)

    def __repr__(self):
        return f'<WeeklyTopic Week {self.week_number} - {self.title}>' 