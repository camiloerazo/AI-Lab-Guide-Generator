# Lab Guide AI - Intelligent Laboratory Guide Generation System

![Lab Guide AI](static/images/logou.png)

## 🚀 Overview

Lab Guide AI is a sophisticated full-stack web application designed to revolutionize the creation and management of laboratory guides for educational institutions. Leveraging the power of artificial intelligence and modern web technologies, this system streamlines the process of generating, managing, and distributing laboratory guides while maintaining high educational standards.

## ✨ Key Features

- 🤖 **AI-Powered Guide Generation**
  - Utilizes OpenRouter's Llama Maverick model for intelligent content generation
  - Context-aware guide creation based on subject matter and difficulty level
  - Customizable templates and formatting options
  - Spanish language support for educational content

- 👥 **Role-Based Access Control**
  - Professor accounts with subject management capabilities
  - Student accounts with guide access
  - Secure authentication and authorization system
  - Profile management and customization

- 📚 **Subject & Topic Management**
  - Create and manage academic subjects
  - Organize weekly topics and learning objectives
  - Associate laboratory guides with specific topics
  - Track laboratory assignments and schedules

- 📝 **Laboratory Guide Features**
  - Dynamic content generation with AI assistance
  - Customizable difficulty levels and duration estimates
  - PDF export functionality with professional formatting
  - Version control and editing capabilities

- 🎨 **Modern User Interface**
  - Responsive design using Bootstrap 5
  - Intuitive navigation and user experience
  - Professional layout with university branding
  - Mobile-friendly interface

## 🛠️ Technical Stack

### Backend
- **Framework**: Flask 3.0.2
- **Database**: SQLAlchemy 2.0.27 with SQLite
- **Authentication**: Flask-Login
- **Database Migrations**: Flask-Migrate
- **PDF Generation**: ReportLab
- **AI Integration**: OpenRouter API (Llama Maverick)

### Frontend
- **Templating**: Jinja2 3.1.3
- **CSS Framework**: Bootstrap 5.1.3
- **JavaScript**: Vanilla JS with Bootstrap Bundle
- **Responsive Design**: Mobile-first approach

### Development & Deployment
- **Version Control**: Git
- **Environment Management**: Python Virtual Environment
- **Dependency Management**: pip/requirements.txt
- **Security**: Werkzeug 3.0.1 for security features

## 🏗️ Architecture

The application follows a modular architecture with clear separation of concerns:

```
lab-guide-ai/
├── app.py              # Main application entry point
├── models.py           # Database models and relationships
├── ai_config.py        # AI integration and configuration
├── lab_guide_format.py # Guide formatting and structure
├── static/            # Static assets (CSS, images, etc.)
├── templates/         # HTML templates
├── migrations/        # Database migrations
└── instance/          # Instance-specific files
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone [repository-url]
   cd lab-guide-ai
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   # Windows
   set OPENROUTER_API_KEY=your-api-key
   # Linux/Mac
   export OPENROUTER_API_KEY=your-api-key
   ```

5. Initialize the database:
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

6. Run the application:
   ```bash
   flask run
   ```

## 🔒 Security Features

- Secure password hashing and storage
- CSRF protection
- Session management
- Role-based access control
- Input validation and sanitization
- Secure API key management

## 📚 API Documentation

The application provides several RESTful endpoints:

- `/api/subjects/<id>/weekly-topics` - Get weekly topics for a subject
- `/lab_guide/<id>` - View lab guide details
- `/lab_guide/<id>/pdf` - Download lab guide as PDF

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- Your Name - Initial work

## 🙏 Acknowledgments

- OpenRouter for providing the AI capabilities
- Flask community for the excellent web framework
- Bootstrap team for the frontend framework 