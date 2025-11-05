-- =====================================================
-- Migration 001: Core Gamification System (XP & Levels)
-- Date: 2025-10-31
-- Description: Creates tables for XP system, levels, and progression tracking
-- =====================================================

USE ignis;

-- =====================================================
-- 1. USER PROGRESSION TABLE
-- =====================================================
-- Tracks XP, level, and prestige for each user
CREATE TABLE IF NOT EXISTS user_progression (
    user_id BIGINT PRIMARY KEY,
    total_xp BIGINT DEFAULT 0,
    current_level INT DEFAULT 1,
    prestige_level INT DEFAULT 0,
    last_xp_gain TIMESTAMP NULL,
    last_level_up TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_level (current_level),
    INDEX idx_total_xp (total_xp),
    INDEX idx_prestige (prestige_level),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- 2. XP EVENTS TABLE
-- =====================================================
-- Logs all XP gains for analytics and audit
CREATE TABLE IF NOT EXISTS xp_events (
    event_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    xp_amount INT NOT NULL,
    source VARCHAR(50) NOT NULL,  -- voice, message, quest, achievement, event, manual, etc.
    details JSON NULL,  -- Additional context (voice_duration, message_count, etc.)
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_source (source),
    INDEX idx_user_timestamp (user_id, timestamp),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- 3. DAILY XP LIMITS TABLE
-- =====================================================
-- Tracks daily XP caps per source to prevent farming
CREATE TABLE IF NOT EXISTS daily_xp_limits (
    user_id BIGINT NOT NULL,
    source VARCHAR(50) NOT NULL,  -- voice, message, etc.
    date DATE NOT NULL,
    xp_gained INT DEFAULT 0,
    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, source, date),
    INDEX idx_date (date),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- 4. LEVEL REWARDS TABLE (Optional - for future)
-- =====================================================
-- Defines rewards given at each level
CREATE TABLE IF NOT EXISTS level_rewards (
    level INT PRIMARY KEY,
    xp_bonus INT DEFAULT 0,
    points_bonus INT DEFAULT 0,
    reward_type VARCHAR(50) NULL,  -- achievement, badge, role, etc.
    reward_value VARCHAR(255) NULL,
    description TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert default level rewards (example)
INSERT INTO level_rewards (level, xp_bonus, points_bonus, description) VALUES
(1, 0, 0, 'Starting level'),
(5, 50, 25, 'First milestone'),
(10, 100, 50, 'Double digits!'),
(25, 250, 125, 'Quarter century'),
(50, 500, 250, 'Half century milestone'),
(100, 1000, 500, 'Century achievement')
ON DUPLICATE KEY UPDATE description=VALUES(description);

