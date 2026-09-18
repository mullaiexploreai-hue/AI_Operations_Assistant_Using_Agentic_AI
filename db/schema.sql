-- SQLite schema for the three IT support tools.
DROP TABLE IF EXISTS support_tickets;
DROP TABLE IF EXISTS knowledge_articles;
DROP TABLE IF EXISTS employees;

CREATE TABLE employees (
    employee_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    email TEXT NOT NULL
);

CREATE TABLE knowledge_articles (
    article_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    keywords TEXT NOT NULL,
    source TEXT NOT NULL
);

CREATE TABLE support_tickets (
    ticket_id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL REFERENCES employees(employee_id),
    issue_summary TEXT NOT NULL,
    category TEXT NOT NULL,
    priority TEXT NOT NULL CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    status TEXT NOT NULL CHECK (status IN ('open', 'in_progress', 'resolved')),
    created_at TEXT NOT NULL
);
