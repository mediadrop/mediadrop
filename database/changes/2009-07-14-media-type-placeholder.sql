ALTER TABLE `media`
  MODIFY COLUMN `type` ENUM('audio','video','placeholder') NOT NULL DEFAULT 'placeholder';
