-- WorkLifeOS Database Schema
-- Comprehensive schema for all modules

-- ============================================
-- 1. USER MANAGEMENT
-- ============================================
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(150),
    timezone VARCHAR(50) DEFAULT 'UTC',
    role VARCHAR(50) DEFAULT 'user', -- user, admin, executive
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- ============================================
-- 2. SCHEDULING SYSTEM
-- ============================================
CREATE TABLE calendars (
    calendar_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    calendar_name VARCHAR(150),
    color_code VARCHAR(7), -- Hex color
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE events (
    event_id SERIAL PRIMARY KEY,
    calendar_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    location VARCHAR(255),
    timezone VARCHAR(50),
    event_type VARCHAR(50), -- meeting, deadline, personal, etc.
    attendees TEXT, -- JSON format: [{"email": "...", "status": "pending/accepted/declined"}]
    reminder_minutes INT DEFAULT 15, -- Minutes before event
    is_recurring BOOLEAN DEFAULT FALSE,
    recurrence_pattern VARCHAR(50), -- daily, weekly, monthly, yearly
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (calendar_id) REFERENCES calendars(calendar_id) ON DELETE CASCADE
);

CREATE TABLE meeting_conflicts (
    conflict_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    event_id_1 INT NOT NULL,
    event_id_2 INT NOT NULL,
    conflict_type VARCHAR(50), -- overlap, back-to-back, timezone_issue
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_resolved BOOLEAN DEFAULT FALSE,
    resolution_note TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (event_id_1) REFERENCES events(event_id),
    FOREIGN KEY (event_id_2) REFERENCES events(event_id)
);

-- ============================================
-- 3. TASK MANAGEMENT
-- ============================================
CREATE TABLE tasks (
    task_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    priority VARCHAR(20), -- low, medium, high, urgent
    status VARCHAR(50) DEFAULT 'todo', -- todo, in_progress, completed, blocked, cancelled
    due_date DATE,
    due_time TIME,
    category VARCHAR(100),
    assigned_to INT, -- Can be assigned to another user
    parent_task_id INT, -- For task dependencies
    estimated_hours DECIMAL(5, 2),
    actual_hours DECIMAL(5, 2),
    urgency_score INT DEFAULT 0, -- Calculated based on Eisenhower Matrix
    importance_score INT DEFAULT 0,
    progress_percentage INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_to) REFERENCES users(user_id),
    FOREIGN KEY (parent_task_id) REFERENCES tasks(task_id) ON DELETE SET NULL
);

CREATE TABLE task_dependencies (
    dependency_id SERIAL PRIMARY KEY,
    blocking_task_id INT NOT NULL,
    blocked_task_id INT NOT NULL,
    dependency_type VARCHAR(50), -- must_complete, must_start_before, must_start_after
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (blocking_task_id) REFERENCES tasks(task_id) ON DELETE CASCADE,
    FOREIGN KEY (blocked_task_id) REFERENCES tasks(task_id) ON DELETE CASCADE,
    UNIQUE(blocking_task_id, blocked_task_id)
);

CREATE TABLE task_history (
    history_id SERIAL PRIMARY KEY,
    task_id INT NOT NULL,
    user_id INT NOT NULL,
    old_status VARCHAR(50),
    new_status VARCHAR(50),
    old_priority VARCHAR(20),
    new_priority VARCHAR(20),
    change_description TEXT,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ============================================
-- 4. INFORMATION HUB (Notes & Documents)
-- ============================================
CREATE TABLE note_categories (
    category_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    category_name VARCHAR(100),
    color_code VARCHAR(7),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE notes (
    note_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    category_id INT,
    tags TEXT, -- JSON array: ["tag1", "tag2"]
    is_pinned BOOLEAN DEFAULT FALSE,
    is_archived BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES note_categories(category_id) ON DELETE SET NULL
);

CREATE TABLE note_attachments (
    attachment_id SERIAL PRIMARY KEY,
    note_id INT NOT NULL,
    file_name VARCHAR(255),
    file_path TEXT,
    file_type VARCHAR(50),
    file_size INT, -- in bytes
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (note_id) REFERENCES notes(note_id) ON DELETE CASCADE
);

-- ============================================
-- 5. EXPENSE TRACKING
-- ============================================
CREATE TABLE expense_categories (
    expense_category_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    category_name VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE expenses (
    expense_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    category_id INT NOT NULL,
    expense_date DATE NOT NULL,
    payment_method VARCHAR(50), -- cash, credit_card, bank_transfer, cheque
    vendor_name VARCHAR(150),
    status VARCHAR(50) DEFAULT 'pending', -- pending, approved, rejected, reimbursed
    receipt_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES expense_categories(expense_category_id)
);

CREATE TABLE invoices (
    invoice_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    client_name VARCHAR(150) NOT NULL,
    client_email VARCHAR(150),
    invoice_date DATE NOT NULL,
    due_date DATE NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    status VARCHAR(50) DEFAULT 'draft', -- draft, sent, viewed, paid, overdue, cancelled
    description TEXT,
    notes TEXT,
    pdf_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    paid_date DATE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE invoice_items (
    item_id SERIAL PRIMARY KEY,
    invoice_id INT NOT NULL,
    description VARCHAR(255),
    quantity DECIMAL(8, 2),
    rate DECIMAL(10, 2),
    amount DECIMAL(10, 2),
    FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id) ON DELETE CASCADE
);

-- ============================================
-- 6. HABIT TRACKER
-- ============================================
CREATE TABLE habits (
    habit_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    habit_name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(50), -- health, productivity, learning, fitness, etc.
    frequency VARCHAR(50), -- daily, weekly, specific_days
    target_count INT DEFAULT 1, -- e.g., drink 8 glasses of water
    target_unit VARCHAR(50), -- glasses, minutes, km, pages, etc.
    start_date DATE NOT NULL,
    goal_date DATE,
    color_code VARCHAR(7),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE habit_logs (
    log_id SERIAL PRIMARY KEY,
    habit_id INT NOT NULL,
    log_date DATE NOT NULL,
    value INT DEFAULT 1, -- How many times completed
    notes TEXT,
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (habit_id) REFERENCES habits(habit_id) ON DELETE CASCADE,
    UNIQUE(habit_id, log_date)
);

CREATE TABLE habit_streaks (
    streak_id SERIAL PRIMARY KEY,
    habit_id INT NOT NULL,
    start_date DATE,
    end_date DATE,
    streak_count INT DEFAULT 0,
    is_current_streak BOOLEAN DEFAULT TRUE,
    longest_streak INT DEFAULT 0,
    FOREIGN KEY (habit_id) REFERENCES habits(habit_id) ON DELETE CASCADE
);

-- ============================================
-- 7. LOCAL SERVICES DIRECTORY
-- ============================================
CREATE TABLE service_categories (
    service_category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    icon_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE service_providers (
    provider_id SERIAL PRIMARY KEY,
    business_name VARCHAR(200) NOT NULL,
    category_id INT NOT NULL,
    description TEXT,
    phone_number VARCHAR(20),
    email VARCHAR(150),
    website VARCHAR(255),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    average_rating DECIMAL(3, 2) DEFAULT 0,
    total_reviews INT DEFAULT 0,
    price_range VARCHAR(50), -- budget, moderate, premium
    business_hours TEXT, -- JSON format
    availability_status VARCHAR(50) DEFAULT 'available',
    service_area VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES service_categories(service_category_id)
);

CREATE TABLE service_reviews (
    review_id SERIAL PRIMARY KEY,
    provider_id INT NOT NULL,
    user_id INT NOT NULL,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    review_date DATE NOT NULL,
    helpful_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (provider_id) REFERENCES service_providers(provider_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE service_bookings (
    booking_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    provider_id INT NOT NULL,
    booking_date DATE NOT NULL,
    booking_time TIME,
    service_type VARCHAR(100),
    duration_minutes INT,
    notes TEXT,
    status VARCHAR(50) DEFAULT 'pending', -- pending, confirmed, cancelled, completed
    cost DECIMAL(10, 2),
    payment_status VARCHAR(50) DEFAULT 'unpaid', -- unpaid, paid
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (provider_id) REFERENCES service_providers(provider_id) ON DELETE CASCADE
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_events_user_calendar ON events(calendar_id);
CREATE INDEX idx_events_start_time ON events(start_time);
CREATE INDEX idx_tasks_user_status ON tasks(user_id, status);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_notes_user_category ON notes(user_id, category_id);
CREATE INDEX idx_expenses_user_date ON expenses(user_id, expense_date);
CREATE INDEX idx_habits_user_active ON habits(user_id, is_active);
CREATE INDEX idx_providers_category_location ON service_providers(category_id, city);
CREATE INDEX idx_services_rating ON service_providers(average_rating DESC);
