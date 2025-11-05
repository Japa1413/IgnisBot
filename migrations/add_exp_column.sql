-- Migration: Add exp column to users table
-- Date: 2025-11-05

-- Check if column exists, if not add it
SET @dbname = DATABASE();
SET @tablename = "users";
SET @columnname = "exp";
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (TABLE_SCHEMA = @dbname)
      AND (TABLE_NAME = @tablename)
      AND (COLUMN_NAME = @columnname)
  ) > 0,
  "SELECT 'Column exp already exists.' AS message;",
  CONCAT("ALTER TABLE ", @tablename, " ADD COLUMN exp INT DEFAULT 0 AFTER points;")
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Also add path column if it doesn't exist
SET @columnname = "path";
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (TABLE_SCHEMA = @dbname)
      AND (TABLE_NAME = @tablename)
      AND (COLUMN_NAME = @columnname)
  ) > 0,
  "SELECT 'Column path already exists.' AS message;",
  CONCAT("ALTER TABLE ", @tablename, " ADD COLUMN path VARCHAR(50) DEFAULT 'pre_induction' AFTER exp;")
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Update existing rows: set exp = points (for backward compatibility)
UPDATE users SET exp = COALESCE(points, 0) WHERE exp IS NULL OR exp = 0;

-- Add indexes if they don't exist
CREATE INDEX IF NOT EXISTS idx_exp ON users(exp DESC);
CREATE INDEX IF NOT EXISTS idx_rank ON users(`rank`);

