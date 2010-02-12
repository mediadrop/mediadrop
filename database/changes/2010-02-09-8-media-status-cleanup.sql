DELETE FROM media WHERE status LIKE '%trash%';
ALTER TABLE media DROP COLUMN `status`;
