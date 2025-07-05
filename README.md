# DiagnoRx - Advanced AI Medical Diagnosis System

A comprehensive Django-based medical diagnosis application that combines patient management, AI-powered diagnosis, and automated report generation.

## Features

### 🏥 **Patient Management**

- Complete patient record creation and management
- Medical history tracking
- File upload support for ECG, Lab, and X-ray reports
- Patient search and filtering capabilities

### 🤖 **AI-Powered Diagnosis**

- Symptom-based diagnosis using machine learning
- Confidence scoring for diagnosis accuracy
- Support for multiple medical report types
- Automated treatment plan generation

### 📊 **Report Generation**

- Automated PDF report generation
- Professional medical report formatting
- Downloadable patient records
- Comprehensive medical summaries

### 🔐 **User Authentication**

- Secure user registration and login
- Role-based access control
- User session management
- Password validation and security

### 📱 **Modern UI/UX**

- Responsive Bootstrap-based interface
- Medical-themed design
- Mobile-friendly layout
- Intuitive navigation

## Technology Stack

- **Backend**: Django 3.2+
- **Frontend**: Bootstrap 5, HTML5, CSS3
- **Database**: SQLite (development), PostgreSQL (production)
- **AI/ML**: scikit-learn, joblib
- **PDF Generation**: ReportLab
- **Image Processing**: Pillow

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd Diagno
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser (optional)**

   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**

   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Open your browser and go to `http://127.0.0.1:8000/`
   - Register a new account or login with existing credentials

## Project Structure

```
Diagno/
├── core/                    # Main application
│   ├── ai_models/          # AI model files
│   ├── static/             # Static files (CSS, JS)
│   ├── templates/          # HTML templates
│   ├── admin.py           # Django admin configuration
│   ├── forms.py           # Patient forms
│   ├── models.py          # Database models
│   ├── urls.py            # URL routing
│   ├── utils.py           # PDF generation utilities
│   └── views.py           # Application views
├── users/                  # User authentication app
│   ├── forms.py           # User registration forms
│   ├── urls.py            # Auth URL routing
│   └── views.py           # Authentication views
├── diagnorx/              # Django project settings
│   ├── settings.py        # Django settings
│   ├── urls.py            # Main URL configuration
│   └── wsgi.py            # WSGI configuration
├── media/                  # Uploaded files
│   ├── ecg_reports/       # ECG report files
│   ├── lab_reports/       # Lab report files
│   └── xray_reports/      # X-ray report files
├── manage.py              # Django management script
├── requirements.txt        # Python dependencies
└── README.md              # Project documentation
```

## Usage

### For Medical Professionals

1. **Login/Register**: Create an account or login to the system
2. **Add Patient**: Fill out the comprehensive patient form with symptoms and medical history
3. **Upload Reports**: Optionally upload ECG, lab, or X-ray reports
4. **Generate Diagnosis**: Submit the form to get AI-powered diagnosis
5. **View Results**: Review diagnosis, confidence score, and treatment plan
6. **Download Reports**: Generate and download PDF medical reports
7. **Track History**: View and search through all patient records

### AI Diagnosis Features

The system provides intelligent diagnosis based on:

- **Symptom Analysis**: Analyzes patient symptoms using pattern recognition
- **Medical History**: Considers patient's medical background
- **Report Integration**: Incorporates uploaded medical reports
- **Confidence Scoring**: Provides accuracy confidence for each diagnosis

### Supported Diagnosis Categories

- Cardiovascular issues
- Respiratory infections
- Neurological conditions
- Gastrointestinal problems
- General consultations

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

### Production Deployment

For production deployment:

1. Set `DEBUG=False` in settings
2. Configure a production database (PostgreSQL recommended)
3. Set up static file serving
4. Configure media file storage
5. Set up proper security measures

## API Endpoints

- `/` - Dashboard (requires authentication)
- `/dashboard/` - Patient form and recent records
- `/prescription/<id>/` - View diagnosis results
- `/history/` - Patient records with search/filter
- `/download-pdf/<id>/` - Download PDF report
- `/users/login/` - User login
- `/users/register/` - User registration
- `/users/logout/` - User logout

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:

- Create an issue in the repository
- Contact the development team
- Check the documentation

## Disclaimer

This is a demonstration system and should not be used for actual medical diagnosis without proper validation and certification. Always consult with qualified medical professionals for real medical decisions.

---

**DiagnoRx** - Advancing medical diagnosis through AI technology.
