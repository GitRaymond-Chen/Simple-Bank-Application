-- Simple Bank Database Schema
-- Run this file to create the database tables in MySQL:
--   mysql -u root -p bankdb < sql/schema.sql

CREATE TABLE users (
  user_id    INT PRIMARY KEY AUTO_INCREMENT,
  name       VARCHAR(100),
  email      VARCHAR(100) UNIQUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE accounts (
  account_id   INT PRIMARY KEY AUTO_INCREMENT,
  user_id      INT,
  balance      DECIMAL(10,2) DEFAULT 0,
  account_type VARCHAR(50),
  created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE transactions (
  txn_id     INT PRIMARY KEY AUTO_INCREMENT,
  account_id INT,
  txn_type   VARCHAR(20),
  amount     DECIMAL(10,2),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);
