-- Disable the enforcement of foreign key constraints.
PRAGMA foreign_keys = OFF;

DROP TABLE IF EXISTS todo;
DROP TABLE IF EXISTS user;

-- Enable the enforcement of foreign key constraints.
PRAGMA foreign_keys = ON;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL COLLATE RTRIM,
  password TEXT NOT NULL
);

CREATE TABLE todo (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_by INTEGER NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  task TEXT NOT NULL COLLATE NOCASE,   -- collating sequence NOCASE
  description TEXT NOT NULL COLLATE NOCASE,
  --  SQLite does not have a separate Boolean storage class. Instead, Boolean values are stored as integers 0 (false) and 1 (true).
  completed INTEGER NOT NULL DEFAULT 0,
  completed_at TIMESTAMP,
  FOREIGN KEY (created_by) REFERENCES user (id)
);
