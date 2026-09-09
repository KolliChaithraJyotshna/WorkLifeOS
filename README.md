# 🚀 WorkLifeOS - All-in-One Personal & Business Operations Platform

> An intelligent system that solves real-world productivity gaps through integrated scheduling, task management, finance tracking, habit building, and local service discovery.

## 📋 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [Career Impact](#career-impact)

## 🎯 Overview

WorkLifeOS is a comprehensive platform addressing multiple productivity challenges:

✅ **Scheduling Chaos** → Smart calendar with timezone coordination  
✅ **Information Overload** → Centralized note & document hub  
✅ **Task Overwhelm** → Intelligent prioritization system  
✅ **Financial Tracking** → Automated expense & invoice management  
✅ **Habit Formation** → Accountability tracking system  
✅ **Service Discovery** → Local trusted services directory  

## ✨ Features

### 1. 📅 Scheduling System
- Multi-timezone calendar management
- Automated conflict detection
- Smart meeting coordination
- Recurring event support
- Attendee management with RSVPs
- Custom reminders

### 2. ✅ Task Management
- Eisenhower Matrix prioritization
- Task dependencies & blocking
- Time estimation & tracking
- Progress monitoring
- Team task assignment
- Deadline alerts

### 3. 📝 Information Hub
- Rich text note-taking
- Category organization
- Smart tagging system
- File attachments
- Quick search & archive
- Pin important items

### 4. 💰 Expense Tracking
- Receipt scanning & storage
- Expense categorization
- Invoice generation
- Financial reports
- Reimbursement tracking
- Multi-currency support

### 5. 🎯 Habit Tracker
- Daily habit logging
- Streak counting
- Goal setting & monitoring
- Progress visualization
- Reminders & notifications
- Habit analytics

### 6. 🏪 Local Services Directory
- Service provider database
- Ratings & reviews system
- Location-based search
- Service booking integration
- Availability tracking
- Trusted recommendations

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python (Flask/FastAPI) |
| **Database** | PostgreSQL / SQLite |
| **ORM** | SQLAlchemy |
| **Authentication** | JWT |
| **API** | RESTful Architecture |
| **Testing** | Pytest |
| **Version Control** | Git & GitHub |

## 📁 Project Structure

```
WorkLifeOS/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── models/
│   │   ├── user.py
│   │   ├── calendar.py
│   │   ├── task.py
│   │   ├── note.py
│   │   ├── expense.py
│   │   ├── habit.py
│   │   └── service.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── calendar.py
│   │   ├── tasks.py
│   │   ├── notes.py
│   │   ├── expenses.py
│   │   ├── habits.py
│   │   └── services.py
│   ├── services/
│   │   ├── calendar_service.py
│   │   ├── task_service.py
│   │   ├── expense_service.py
│   │   ├── habit_service.py
│   │   └── notification_service.py
│   └── utils/
│       ├── validators.py
│       ├── helpers.py
│       └── decorators.py
├── database/
│   ├── schema.sql
│   └── migrations/
├── tests/
│   ├── test_auth.py
│   ├── test_calendar.py
│   ├── test_tasks.py
│   └── ...
├── docs/
│   ├── API.md
│   ├── DATABASE.md
│   └── DEPLOYMENT.md
├── requirements.txt
├── .env.example
└── README.md
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- PostgreSQL 12+ (or SQLite for development)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/KolliChaithraJyotshna/WorkLifeOS.git
   cd WorkLifeOS
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup database**
   ```bash
   createdb worklifeos  # For PostgreSQL
   psql worklifeos < database/schema.sql
   ```
   
   Or for SQLite:
   ```bash
   python
   >>> from app import db, create_app
   >>> app = create_app()
   >>> with app.app_context():
   ...     db.create_all()
   ```

5. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

6. **Run the application**
   ```bash
   python run.py
   ```

   Server runs on `http://localhost:5000`

## 📖 Usage

### Example: Creating a Task

```python
from app import create_app, db
from app.models.task import Task

app = create_app()
with app.app_context():
    new_task = Task(
        user_id=1,
        title="Prepare Q4 Report",
        description="Compile quarterly metrics",
        priority="high",
        due_date="2024-09-30",
        urgency_score=9,
        importance_score=9
    )
    db.session.add(new_task)
    db.session.commit()
```

### Example: API Call (Create Event)

```bash
curl -X POST http://localhost:5000/api/events \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "title": "Team Meeting",
    "start_time": "2024-09-15T14:00:00",
    "end_time": "2024-09-15T15:00:00",
    "location": "Conference Room A",
    "timezone": "America/New_York"
  }'
```

## 📚 API Documentation

See [API.md](docs/API.md) for complete endpoint documentation.

### Quick API Reference

**Authentication**
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/refresh` - Refresh token

**Calendar**
- `GET /api/calendars` - List calendars
- `POST /api/events` - Create event
- `GET /api/events?date=2024-09-15` - Get events by date

**Tasks**
- `GET /api/tasks?status=todo` - Get tasks by status
- `POST /api/tasks` - Create task
- `PUT /api/tasks/{id}` - Update task

**Notes**
- `GET /api/notes` - List notes
- `POST /api/notes` - Create note
- `GET /api/notes/search?q=keyword` - Search notes

**Expenses**
- `GET /api/expenses` - List expenses
- `POST /api/expenses` - Create expense
- `POST /api/invoices` - Generate invoice

**Habits**
- `GET /api/habits` - List habits
- `POST /api/habits/{id}/log` - Log habit completion
- `GET /api/habits/{id}/stats` - Get habit statistics

**Services**
- `GET /api/services?category=plumbing&city=NewYork` - Find services
- `POST /api/services/{id}/reviews` - Add review
- `POST /api/services/{id}/book` - Book service

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_calendar.py -v
```

## 🔧 Development

### Code Quality

```bash
# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Add new column"

# Apply migrations
alembic upgrade head
```

## 📖 Documentation

- [Database Documentation](docs/DATABASE.md)
- [API Reference](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Architecture Overview](docs/ARCHITECTURE.md)

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/amazing-feature`
2. Commit changes: `git commit -m 'Add amazing feature'`
3. Push to branch: `git push origin feature/amazing-feature`
4. Open a Pull Request

## 📈 Career Impact

This project demonstrates:

✅ **Full-stack capability** - Database design to API implementation  
✅ **Problem-solving** - Real-world system integration  
✅ **Best practices** - Clean code, testing, documentation  
✅ **Python expertise** - Advanced OOP and design patterns  
✅ **SQL mastery** - Complex queries and schema design  
✅ **Professional readiness** - Production-quality code  

### Ideal For:
- Backend Developer roles
- Python Developer positions
- Operations/Assistant roles requiring tech knowledge
- Freelance/Full-stack Developer portfolios
- Startup technical founder roles

## 📝 License

MIT License - See LICENSE file for details

## 👨‍💻 Author

Built with ❤️ for career growth and real-world impact

---

**Ready to build something amazing? Start with the [Getting Started](#getting-started) section!**
