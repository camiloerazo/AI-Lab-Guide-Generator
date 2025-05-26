from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from models import db, User, Professor, Subject, LabGuide, WeeklyTopic, Laboratory
from werkzeug.security import generate_password_hash
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import tempfile
from datetime import datetime
from io import BytesIO

# To use this application, you need to set your OpenRouter API key as an environment variable:
# Windows: set OPENROUTER_API_KEY=your-api-key
# Linux/Mac: export OPENROUTER_API_KEY=your-api-key
# Or set it in your system's environment variables

from ai_config import ai_config  # Import the AI configuration

app = Flask(__name__)
# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Add a secret key for session management
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure secret key in production

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Configure Flask-Migrate
migrate = Migrate(app, db)

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        user_type = request.form.get('user_type', 'user')  # Default to 'user' if not specified
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different one.', 'error')
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please use a different one.', 'error')
            return redirect(url_for('register'))
        
        # Create new user based on type
        if user_type == 'professor':
            department = request.form.get('department')
            user = Professor(
                username=username,
                email=email,
                department=department
            )
        else:
            user = User(username=username, email=email)
        
        # Set password and save user
        user.set_password(password)
        db.session.add(user)
        
        try:
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'error')
            return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page or url_for('home'))
        else:
            flash('Invalid username or password. Please try again.', 'error')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/')
def home():
    # Get all users (includes Professor, Student, etc.)
    users = User.query.all()
    return render_template('index.html', title='Welcome to Flask', users=users)

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard for authenticated users. Provides options to create lab guides, manage subjects (if professor), and edit account data."""
    # For professors, fetch their subjects (if any) so that the dashboard can display or link to them.
    subjects = []
    if hasattr(current_user, "subjects") and (current_user.user_type == "professor"):
        subjects = current_user.subjects.all()
    return render_template("dashboard.html", subjects=subjects, WeeklyTopic=WeeklyTopic)

@app.route('/api/subjects/<int:subject_id>/weekly-topics')
@login_required
def get_weekly_topics(subject_id):
    """API endpoint to get weekly topics for a subject"""
    # Verify the subject exists and the user has access to it
    subject = Subject.query.get_or_404(subject_id)
    if not (current_user.user_type == 'professor' and subject in current_user.subjects):
        return jsonify({'error': 'Unauthorized'}), 403
    
    topics = subject.weekly_topics.order_by(WeeklyTopic.week_number).all()
    return jsonify([{
        'id': topic.id,
        'week_number': topic.week_number,
        'title': topic.title,
        'description': topic.description
    } for topic in topics])

@app.route('/dashboard/create_lab_guide', methods=['GET', 'POST'])
@login_required
def create_lab_guide():
    if current_user.user_type != 'professor':
        flash('Solo los profesores pueden crear guías de laboratorio.', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        subject_id = request.form.get('subject_id')
        weekly_topic_id = request.form.get('weekly_topic_id')
        title = request.form.get('title')
        lab_number = request.form.get('lab_number')
        difficulty_level = request.form.get('difficulty_level')
        estimated_duration = request.form.get('estimated_duration')
        additional_notes = request.form.get('additional_notes', '')
        laboratory_id = request.form.get('laboratory_id')

        # Validate subject ownership
        subject = Subject.query.get_or_404(subject_id)
        if subject not in current_user.subjects:
            flash('No tienes permiso para crear guías para esta materia.', 'error')
            return redirect(url_for('dashboard'))

        # Validate weekly topic association
        weekly_topic = WeeklyTopic.query.get_or_404(weekly_topic_id)
        if weekly_topic.subject_id != int(subject_id):
            flash('El tema semanal seleccionado no pertenece a la materia.', 'error')
            return redirect(url_for('dashboard'))

        try:
            # Generate lab guide content using AI
            content = ai_config.generate_lab_guide(
                subject_name=subject.name,
                topic_title=weekly_topic.title,
                topic_description=weekly_topic.description,
                lab_number=int(lab_number),
                difficulty_level=difficulty_level,
                estimated_duration=int(estimated_duration),
                additional_notes=additional_notes,
                lab_guide_title=title
            )

            if not content:
                flash('Error al generar la guía de laboratorio. Por favor, intente nuevamente.', 'error')
                return redirect(url_for('create_lab_guide'))

            # Convert plain text content to HTML for display
            formatted_content = f"""
<div class="institutional-header">
    <h1>Universidad Cooperativa de Colombia</h1>
    <h2>{current_user.department}</h2>
    <p><strong>Asignatura:</strong> {subject.code} - {subject.name}</p>
    <p><strong>Laboratorio:</strong> {title}</p>
    <p><strong>Docente:</strong> {current_user.username}</p>
    <p><strong>Semestre:</strong> 2024-1</p>
</div>
<hr>
<div class="lab-guide-content">
"""

            # Process the content line by line to convert to HTML
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if not line:  # Empty line
                    formatted_content += '<br>\n'
                elif line.isupper() and len(line) > 3:  # Section title
                    formatted_content += f'<h2>{line}</h2>\n'
                elif line.endswith(':'):  # Subsection title
                    formatted_content += f'<h3>{line}</h3>\n'
                else:  # Regular text
                    formatted_content += f'<p>{line}</p>\n'

            formatted_content += '</div>'

            # Create new lab guide
            lab_guide = LabGuide(
                subject_id=subject_id,
                weekly_topic_id=weekly_topic_id,
                title=title,
                content=formatted_content,
                lab_number=lab_number,
                difficulty_level=difficulty_level,
                estimated_duration=estimated_duration,
                status='draft',
                laboratory_id=laboratory_id if laboratory_id else None,
                created_by_id=current_user.id  # Add the professor's ID as the creator
            )

            db.session.add(lab_guide)
            db.session.commit()

            flash('Guía de laboratorio creada exitosamente.', 'success')
            return redirect(url_for('dashboard'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear la guía de laboratorio: {str(e)}', 'error')
            return redirect(url_for('create_lab_guide'))

    # Get subjects for the current professor using the correct relationship
    subjects = current_user.subjects.all()
    laboratories = Laboratory.query.all()

    return render_template('create_lab_guide.html',
                         subjects=subjects,
                         laboratories=laboratories)

@app.route('/dashboard/manage_subjects', methods=['GET', 'POST'])
@login_required
def manage_subjects():
    """Route for professors to manage their subjects and weekly topics."""
    if not current_user.user_type == 'professor':
        flash('Only professors can manage subjects.', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        action = request.form.get('action')
        
        try:
            if action == 'add_subject':
                # Add new subject
                subject = Subject(
                    code=request.form.get('subject_code'),
                    name=request.form.get('subject_name'),
                    credits=int(request.form.get('credits')),
                    description=request.form.get('description')
                )
                db.session.add(subject)
                # Associate subject with professor
                current_user.subjects.append(subject)
                db.session.commit()
                flash('Subject added successfully!', 'success')

            elif action == 'add_topic':
                # Add new weekly topic
                subject_id = request.form.get('subject_id')
                subject = Subject.query.get_or_404(subject_id)
                
                # Verify subject ownership
                if subject not in current_user.subjects:
                    flash('You do not have permission to modify this subject.', 'error')
                    return redirect(url_for('manage_subjects'))

                topic = WeeklyTopic(
                    week_number=int(request.form.get('week_number')),
                    title=request.form.get('topic_title'),
                    description=request.form.get('topic_description'),
                    subject_id=subject_id
                )
                db.session.add(topic)
                db.session.commit()
                flash('Weekly topic added successfully!', 'success')

            elif action == 'delete_topic':
                # Delete a weekly topic
                topic_id = request.form.get('topic_id')
                topic = WeeklyTopic.query.get_or_404(topic_id)
                
                # Verify subject ownership
                if topic.subject not in current_user.subjects:
                    flash('You do not have permission to delete this topic.', 'error')
                    return redirect(url_for('manage_subjects'))

                db.session.delete(topic)
                db.session.commit()
                flash('Weekly topic deleted successfully!', 'success')

            elif action == 'delete_subject':
                # Delete a subject
                subject_id = request.form.get('subject_id')
                subject = Subject.query.get_or_404(subject_id)
                
                # Verify subject ownership
                if subject not in current_user.subjects:
                    flash('You do not have permission to delete this subject.', 'error')
                    return redirect(url_for('manage_subjects'))

                # Check if subject has any lab guides
                if subject.lab_guides.count() > 0:
                    flash('Cannot delete subject because it has associated lab guides. Please delete the lab guides first.', 'error')
                    return redirect(url_for('manage_subjects'))

                # Remove subject from professor's subjects
                current_user.subjects.remove(subject)
                # Delete all weekly topics associated with the subject
                WeeklyTopic.query.filter_by(subject_id=subject_id).delete()
                # Delete the subject
                db.session.delete(subject)
                db.session.commit()
                flash('Subject and its weekly topics deleted successfully!', 'success')

            else:
                flash('Invalid action.', 'error')

        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'error')

        return redirect(url_for('manage_subjects'))

    # GET request - show the form
    subjects = current_user.subjects.all()
    return render_template('manage_subjects.html', subjects=subjects, WeeklyTopic=WeeklyTopic)

@app.route('/dashboard/edit_account', methods=['GET', 'POST'])
@login_required
def edit_account():
    """Route for users to edit their account data (e.g. change password). Requires authentication."""
    if request.method == "POST":
         # (In a real app, you'd update the user's data, e.g. change password.)
         flash("Account (simulated) updated.", "info")
         return redirect(url_for("dashboard"))
    return render_template("edit_account.html")

@app.route('/lab_guide/<int:guide_id>')
@login_required
def view_lab_guide(guide_id):
    """Route to view a specific lab guide."""
    lab_guide = LabGuide.query.get_or_404(guide_id)
    
    # Check if user has permission to view the guide
    if not (current_user.user_type == 'professor' and lab_guide.subject in current_user.subjects):
        flash('No tienes permiso para ver esta guía de laboratorio.', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('view_lab_guide.html', lab_guide=lab_guide)

@app.route('/lab_guide/<int:guide_id>/delete', methods=['POST'])
@login_required
def delete_lab_guide(guide_id):
    """Route to delete a lab guide."""
    lab_guide = LabGuide.query.get_or_404(guide_id)
    
    # Check if user has permission to delete the guide
    if not (current_user.user_type == 'professor' and lab_guide.subject in current_user.subjects):
        flash('No tienes permiso para eliminar esta guía de laboratorio.', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        db.session.delete(lab_guide)
        db.session.commit()
        flash('Guía de laboratorio eliminada exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar la guía de laboratorio: {str(e)}', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/lab_guide/<int:guide_id>/pdf')
@login_required
def download_lab_guide_pdf(guide_id):
    """Generate and download a PDF version of the lab guide."""
    try:
        lab_guide = LabGuide.query.get_or_404(guide_id)
        
        # Check if user has permission to view the guide
        if not (current_user.user_type == 'professor' and lab_guide.subject in current_user.subjects):
            flash('No tienes permiso para descargar esta guía de laboratorio.', 'error')
            return redirect(url_for('dashboard'))
        
        # Create a BytesIO buffer to store the PDF
        buffer = BytesIO()
        
        # Create the PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2.5*cm,
            leftMargin=2.5*cm,
            topMargin=2.5*cm,
            bottomMargin=2.5*cm
        )
        
        # Create styles
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name='Header',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1,  # Center alignment
            textColor=colors.HexColor('#003366')
        ))
        styles.add(ParagraphStyle(
            name='SubHeader',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=20,
            alignment=1,
            textColor=colors.HexColor('#003366')
        ))
        styles.add(ParagraphStyle(
            name='CustomBodyText',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            leading=14
        ))
        
        # Build the PDF content
        story = []
        
        # Add logo if it exists
        logo_path = os.path.join(os.path.dirname(__file__), 'static', 'images', 'logou.png')
        if os.path.exists(logo_path):
            try:
                img = Image(logo_path)
                # Scale image to reasonable size while maintaining aspect ratio
                img.drawHeight = 2*cm
                img.drawWidth = 2*cm
                img.hAlign = 'CENTER'
                story.append(img)
                story.append(Spacer(1, 20))
            except Exception as e:
                print(f"Error loading logo: {str(e)}")
                flash('Error loading university logo.', 'warning')
        else:
            flash('University logo file not found at {logo_path}.', 'warning')
        
        # Add header information
        story.append(Paragraph("Universidad Cooperativa de Colombia", styles['Header']))
        story.append(Paragraph(current_user.department, styles['SubHeader']))
        story.append(Spacer(1, 20))
        
        # Add subject information
        story.append(Paragraph(f"<b>Asignatura:</b> {lab_guide.subject.code} - {lab_guide.subject.name}", styles['CustomBodyText']))
        story.append(Paragraph(f"<b>Laboratorio:</b> {lab_guide.title}", styles['CustomBodyText']))
        story.append(Paragraph(f"<b>Docente:</b> {current_user.username}", styles['CustomBodyText']))
        story.append(Paragraph(f"<b>Semestre:</b> 2024-1", styles['CustomBodyText']))
        story.append(Spacer(1, 30))
        
        # Add a single line
        story.append(Paragraph("_" * 80, styles['CustomBodyText']))
        story.append(Spacer(1, 20))
        
        # Process the content to remove duplicates and clean up formatting
        content = lab_guide.content
        
        # Remove institutional header section
        if '<div class="institutional-header">' in content:
            content = content.split('<div class="lab-guide-content">')[-1]
        
        # Remove HTML tags and clean up the content
        content = content.replace('<div class="lab-guide-content">', '')
        content = content.replace('</div>', '')
        content = content.replace('<h2>', '\n\n').replace('</h2>', '\n')
        content = content.replace('<h3>', '\n').replace('</h3>', '\n')
        content = content.replace('<p>', '').replace('</p>', '\n')
        content = content.replace('<br>', '\n')
        
        # Remove duplicate lines and clean up spacing
        paragraphs = []
        seen_lines = set()
        for para in content.split('\n'):
            para = para.strip()
            # Also remove lines that consist only of underscores
            if para and para not in seen_lines and not (para.startswith('_') and all(c == '_' for c in para)):
                seen_lines.add(para)
                paragraphs.append(para)
        
        # Add processed content to PDF
        for para in paragraphs:
            story.append(Paragraph(para, styles['CustomBodyText']))
        
        # Add footer with generation date
        story.append(Spacer(1, 30))
        story.append(Paragraph("_" * 80, styles['CustomBodyText']))
        story.append(Paragraph(f"Documento generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}", 
                             ParagraphStyle(
                                 name='Footer',
                                 parent=styles['Normal'],
                                 fontSize=9,
                                 textColor=colors.gray,
                                 alignment=1
                             )))
        
        # Build the PDF
        doc.build(story)
        
        # Get the value of the BytesIO buffer
        pdf = buffer.getvalue()
        buffer.close()
        
        # Create the response
        response = send_file(
            BytesIO(pdf),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'guia_laboratorio_{lab_guide.title.lower().replace(" ", "_")}.pdf'
        )
        
        return response
        
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")  # Debug log
        flash(f'Error al generar el PDF: {str(e)}', 'error')
        return redirect(url_for('view_lab_guide', guide_id=guide_id))

# Create database tables
with app.app_context():
    db.create_all()

    # Only add sample data if DB is empty
    if not User.query.first():
        prof = Professor(
            username='drsmith',
            email='drsmith@university.edu',
            department='AI'
        )
        prof.set_password('password123')  # Set a default password
        db.session.add(prof)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
