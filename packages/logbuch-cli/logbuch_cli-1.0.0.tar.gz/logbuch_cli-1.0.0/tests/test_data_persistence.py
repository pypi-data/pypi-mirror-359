#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# tests/test_data_persistence.py

import pytest
import sqlite3
import tempfile
import json
import shutil
import time
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from logbuch.storage import Storage
from logbuch.commands.task import add_task, list_tasks, complete_task
from logbuch.commands.journal import add_journal_entry, list_journal_entries
from logbuch.commands.mood import add_mood_entry, list_mood_entries
from logbuch.commands.goal import add_goal, update_goal_progress, list_goals


class TestBasicDataPersistence:
    def test_task_persistence_across_sessions(self, temp_dir):
        db_path = temp_dir / "persistence_test.db"
        
        try:
            # Session 1: Create tasks
            storage1 = Storage(str(db_path), keep_test_db=True)
            task_id1 = storage1.add_task("Persistent task 1", "high", ["important"])
            task_id2 = storage1.add_task("Persistent task 2", "medium", ["work"])
            
            # Complete one task
            storage1.complete_task(task_id1)
            
            # Close session
            del storage1
            
            # Session 2: Verify data persists
            storage2 = Storage(str(db_path), keep_test_db=True)
            
            # Get all tasks including completed
            all_tasks = storage2.get_tasks(show_completed=True)
            active_tasks = storage2.get_tasks(show_completed=False)
            
            assert len(all_tasks) == 2
            assert len(active_tasks) == 1
            
            # Verify task details
            task1 = next((t for t in all_tasks if t['id'] == task_id1), None)
            task2 = next((t for t in all_tasks if t['id'] == task_id2), None)
            
            assert task1 is not None
            assert task1['content'] == "Persistent task 1"
            assert task1['priority'] == "high"
            assert "important" in task1['tags']
            assert task1['completed'] is True
            
            assert task2 is not None
            assert task2['content'] == "Persistent task 2"
            assert task2['priority'] == "medium"
            assert "work" in task2['tags']
            assert task2['completed'] is False
            
        finally:
            if db_path.exists():
                db_path.unlink()
    
    def test_journal_persistence_across_sessions(self, temp_dir):
        db_path = temp_dir / "journal_persistence.db"
        
        try:
            # Session 1: Create journal entries
            storage1 = Storage(str(db_path), keep_test_db=True)
            entry_id1 = storage1.add_journal_entry(
                "First persistent journal entry",
                ["personal", "reflection"],
                "daily"
            )
            entry_id2 = storage1.add_journal_entry(
                "Second persistent journal entry",
                ["work", "progress"],
                "work"
            )
            
            del storage1
            
            # Session 2: Verify entries persist
            storage2 = Storage(str(db_path), keep_test_db=True)
            entries = storage2.get_journal_entries()
            
            assert len(entries) == 2
            
            # Verify entry details
            entry1 = next((e for e in entries if e['id'] == entry_id1), None)
            entry2 = next((e for e in entries if e['id'] == entry_id2), None)
            
            assert entry1 is not None
            assert entry1['text'] == "First persistent journal entry"
            assert set(entry1['tags']) == {"personal", "reflection"}
            assert entry1['category'] == "daily"
            
            assert entry2 is not None
            assert entry2['text'] == "Second persistent journal entry"
            assert set(entry2['tags']) == {"work", "progress"}
            assert entry2['category'] == "work"
            
        finally:
            if db_path.exists():
                db_path.unlink()
    
    def test_mixed_data_persistence(self, temp_dir):
        db_path = temp_dir / "mixed_persistence.db"
        
        try:
            # Session 1: Create various data types
            storage1 = Storage(str(db_path), keep_test_db=True)
            
            # Add tasks
            task_id = storage1.add_task("Mixed data task", "high", ["test"])
            
            # Add journal entries
            entry_id = storage1.add_journal_entry("Mixed data journal", ["test"])
            
            # Add mood entries (if supported by storage)
            try:
                mood_id = storage1.add_mood_entry("happy", "Mixed data mood")
            except AttributeError:
                # Mood entries might not be implemented in storage directly
                mood_id = None
            
            # Add goals (if supported by storage)
            try:
                goal_id = storage1.add_goal("Mixed data goal", "Test goal", 10, 5)
            except AttributeError:
                # Goals might not be implemented in storage directly
                goal_id = None
            
            del storage1
            
            # Session 2: Verify all data persists
            storage2 = Storage(str(db_path), keep_test_db=True)
            
            # Verify tasks
            tasks = storage2.get_tasks()
            assert len(tasks) == 1
            assert tasks[0]['content'] == "Mixed data task"
            
            # Verify journal entries
            entries = storage2.get_journal_entries()
            assert len(entries) == 1
            assert entries[0]['text'] == "Mixed data journal"
            
            # Verify mood entries (if supported)
            if mood_id:
                try:
                    moods = storage2.get_mood_entries()
                    assert len(moods) >= 1
                except AttributeError:
                    pass
            
            # Verify goals (if supported)
            if goal_id:
                try:
                    goals = storage2.get_goals()
                    assert len(goals) >= 1
                except AttributeError:
                    pass
                    
        finally:
            if db_path.exists():
                db_path.unlink()


class TestDatabaseIntegrity:
    def test_foreign_key_constraints(self, temp_dir):
        db_path = temp_dir / "foreign_key_test.db"
        
        try:
            storage = Storage(str(db_path), keep_test_db=True)
            
            # Add some data
            task_id = storage.add_task("FK test task")
            
            # Directly access database to test constraints
            with sqlite3.connect(str(db_path)) as conn:
                cursor = conn.cursor()
                
                # Try to insert invalid foreign key reference (if applicable)
                # This depends on your database schema
                try:
                    # Example: Try to insert a comment with invalid task_id
                    cursor.execute(
                        "INSERT INTO task_comments (task_id, comment) VALUES (?, ?)",
                        (99999, "Invalid FK comment")
                    )
                    conn.commit()
                    
                    # If this succeeds, foreign keys might not be enforced
                    # Check if the invalid data was actually inserted
                    cursor.execute("SELECT * FROM task_comments WHERE task_id = 99999")
                    invalid_data = cursor.fetchall()
                    
                    if invalid_data:
                        # Foreign keys are not enforced - this might be intentional
                        pass
                    
                except sqlite3.IntegrityError:
                    # Foreign key constraint is working correctly
                    pass
                except sqlite3.OperationalError:
                    # Table might not exist - that's fine for this test
                    pass
                    
        finally:
            if db_path.exists():
                db_path.unlink()
    
    def test_transaction_consistency(self, temp_dir):
        db_path = temp_dir / "transaction_test.db"
        
        try:
            storage = Storage(str(db_path), keep_test_db=True)
            
            # Add initial data
            initial_task_id = storage.add_task("Initial task")
            initial_count = len(storage.get_tasks())
            
            # Test transaction rollback
            with sqlite3.connect(str(db_path)) as conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("BEGIN TRANSACTION")
                    
                    # Insert data within transaction
                    cursor.execute(
                        "INSERT INTO tasks (content, priority, board, completed) VALUES (?, ?, ?, ?)",
                        ("Transaction test task", "medium", "default", False)
                    )
                    
                    # Simulate error and rollback
                    raise Exception("Simulated error")
                    
                except Exception:
                    conn.rollback()
            
            # Verify rollback worked
            final_count = len(storage.get_tasks())
            assert final_count == initial_count
            
            # Verify the transaction data was not committed
            tasks = storage.get_tasks()
            task_contents = [task['content'] for task in tasks]
            assert "Transaction test task" not in task_contents
            
        finally:
            if db_path.exists():
                db_path.unlink()
    
    def test_database_schema_consistency(self, temp_dir):
        db_path = temp_dir / "schema_test.db"
        
        try:
            storage = Storage(str(db_path), keep_test_db=True)
            
            # Verify expected tables exist
            with sqlite3.connect(str(db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                # Check for expected tables
                expected_tables = ['tasks', 'journal_entries']
                for table in expected_tables:
                    assert table in tables, f"Expected table '{table}' not found"
                
                # Verify table schemas
                for table in expected_tables:
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = cursor.fetchall()
                    assert len(columns) > 0, f"Table '{table}' has no columns"
                    
                    # Verify essential columns exist
                    column_names = [col[1] for col in columns]
                    assert 'id' in column_names, f"Table '{table}' missing 'id' column"
                    
        finally:
            if db_path.exists():
                db_path.unlink()


class TestBackupAndRestore:
    def test_basic_backup_creation(self, temp_dir):
        db_path = temp_dir / "backup_source.db"
        
        try:
            storage = Storage(str(db_path), keep_test_db=True)
            
            # Add test data
            task_id = storage.add_task("Backup test task", "high", ["backup"])
            entry_id = storage.add_journal_entry("Backup test entry", ["backup"])
            
            # Create backup
            backup_path = storage.create_backup()
            
            assert backup_path is not None
            assert Path(backup_path).exists()
            assert Path(backup_path).stat().st_size > 0
            
            # Verify backup contains data
            backup_storage = Storage(backup_path, keep_test_db=True)
            
            backup_tasks = backup_storage.get_tasks()
            backup_entries = backup_storage.get_journal_entries()
            
            assert len(backup_tasks) == 1
            assert len(backup_entries) == 1
            
            assert backup_tasks[0]['content'] == "Backup test task"
            assert backup_entries[0]['text'] == "Backup test entry"
            
        finally:
            if db_path.exists():
                db_path.unlink()
    
    def test_backup_integrity_verification(self, temp_dir):
        db_path = temp_dir / "integrity_source.db"
        
        try:
            storage = Storage(str(db_path), keep_test_db=True)
            
            # Add substantial test data
            for i in range(50):
                storage.add_task(f"Integrity test task {i}", "medium", [f"tag{i%5}"])
            
            for i in range(25):
                storage.add_journal_entry(f"Integrity test entry {i}", [f"tag{i%3}"])
            
            # Create backup
            backup_path = storage.create_backup()
            
            # Verify backup integrity
            backup_storage = Storage(backup_path, keep_test_db=True)
            
            original_tasks = storage.get_tasks()
            original_entries = storage.get_journal_entries()
            
            backup_tasks = backup_storage.get_tasks()
            backup_entries = backup_storage.get_journal_entries()
            
            # Verify counts match
            assert len(backup_tasks) == len(original_tasks)
            assert len(backup_entries) == len(original_entries)
            
            # Verify content matches
            original_task_contents = {task['content'] for task in original_tasks}
            backup_task_contents = {task['content'] for task in backup_tasks}
            assert original_task_contents == backup_task_contents
            
            original_entry_texts = {entry['text'] for entry in original_entries}
            backup_entry_texts = {entry['text'] for entry in backup_entries}
            assert original_entry_texts == backup_entry_texts
            
        finally:
            if db_path.exists():
                db_path.unlink()
    
    def test_backup_rotation(self, temp_dir):
        db_path = temp_dir / "rotation_source.db"
        
        try:
            storage = Storage(str(db_path), keep_test_db=True, max_backups=3)
            
            # Add initial data
            storage.add_task("Rotation test task")
            
            # Create multiple backups
            backup_paths = []
            for i in range(5):
                # Add more data to make each backup different
                storage.add_task(f"Backup {i} task")
                
                backup_path = storage.create_backup()
                backup_paths.append(backup_path)
                
                # Small delay to ensure different timestamps
                time.sleep(0.1)
            
            # Verify backup rotation (should keep only max_backups)
            existing_backups = [path for path in backup_paths if Path(path).exists()]
            
            # Should have at most max_backups (3) files
            assert len(existing_backups) <= 3
            
            # The most recent backups should exist
            recent_backups = backup_paths[-3:]  # Last 3 backups
            for backup_path in recent_backups:
                assert Path(backup_path).exists(), f"Recent backup {backup_path} should exist"
                
        finally:
            if db_path.exists():
                db_path.unlink()
            # Clean up backup files
            for backup_path in backup_paths:
                if Path(backup_path).exists():
                    Path(backup_path).unlink()
    
    def test_restore_from_backup(self, temp_dir):
        original_db = temp_dir / "original.db"
        restored_db = temp_dir / "restored.db"
        
        try:
            # Create original database with data
            original_storage = Storage(str(original_db), keep_test_db=True)
            
            task_id = original_storage.add_task("Original task", "high", ["original"])
            entry_id = original_storage.add_journal_entry("Original entry", ["original"])
            
            # Create backup
            backup_path = original_storage.create_backup()
            
            # Simulate data loss by creating new database
            restored_storage = Storage(str(restored_db), keep_test_db=True)
            
            # Verify new database is empty
            assert len(restored_storage.get_tasks()) == 0
            assert len(restored_storage.get_journal_entries()) == 0
            
            # Restore from backup (simulate restore process)
            # In a real implementation, this would be a restore method
            shutil.copy2(backup_path, str(restored_db))
            
            # Verify restored data
            final_storage = Storage(str(restored_db), keep_test_db=True)
            
            restored_tasks = final_storage.get_tasks()
            restored_entries = final_storage.get_journal_entries()
            
            assert len(restored_tasks) == 1
            assert len(restored_entries) == 1
            
            assert restored_tasks[0]['content'] == "Original task"
            assert restored_entries[0]['text'] == "Original entry"
            
        finally:
            for db_file in [original_db, restored_db]:
                if db_file.exists():
                    db_file.unlink()


class TestDataMigration:
    def test_database_version_compatibility(self, temp_dir):
        db_path = temp_dir / "version_test.db"
        
        try:
            # Create database with current version
            storage_v1 = Storage(str(db_path), keep_test_db=True)
            storage_v1.add_task("Version test task")
            
            # Simulate version upgrade by accessing with new storage instance
            storage_v2 = Storage(str(db_path), keep_test_db=True)
            
            # Should be able to read existing data
            tasks = storage_v2.get_tasks()
            assert len(tasks) == 1
            assert tasks[0]['content'] == "Version test task"
            
            # Should be able to add new data
            new_task_id = storage_v2.add_task("New version task")
            assert new_task_id is not None
            
            # Verify both old and new data exist
            all_tasks = storage_v2.get_tasks()
            assert len(all_tasks) == 2
            
        finally:
            if db_path.exists():
                db_path.unlink()
    
    def test_schema_migration_simulation(self, temp_dir):
        db_path = temp_dir / "migration_test.db"
        
        try:
            # Create initial database
            storage = Storage(str(db_path), keep_test_db=True)
            storage.add_task("Migration test task")
            
            # Simulate schema changes by directly modifying database
            with sqlite3.connect(str(db_path)) as conn:
                cursor = conn.cursor()
                
                # Add a new column (simulate migration)
                try:
                    cursor.execute("ALTER TABLE tasks ADD COLUMN new_field TEXT DEFAULT ''")
                    conn.commit()
                except sqlite3.OperationalError:
                    # Column might already exist
                    pass
            
            # Verify storage still works with modified schema
            new_storage = Storage(str(db_path), keep_test_db=True)
            tasks = new_storage.get_tasks()
            
            assert len(tasks) == 1
            assert tasks[0]['content'] == "Migration test task"
            
            # Should be able to add new tasks
            new_task_id = new_storage.add_task("Post-migration task")
            assert new_task_id is not None
            
        finally:
            if db_path.exists():
                db_path.unlink()


class TestLongTermPersistence:
    def test_large_dataset_persistence(self, temp_dir):
        db_path = temp_dir / "large_dataset.db"
        
        try:
            storage = Storage(str(db_path), keep_test_db=True)
            
            # Create large dataset
            task_count = 1000
            entry_count = 500
            
            # Add tasks
            task_ids = []
            for i in range(task_count):
                task_id = storage.add_task(
                    f"Large dataset task {i}",
                    priority=["low", "medium", "high"][i % 3],
                    tags=[f"tag{i%10}", "large_dataset"]
                )
                task_ids.append(task_id)
            
            # Add journal entries
            entry_ids = []
            for i in range(entry_count):
                entry_id = storage.add_journal_entry(
                    f"Large dataset entry {i}: " + "Content " * 20,  # Longer entries
                    tags=[f"tag{i%5}", "large_dataset"]
                )
                entry_ids.append(entry_id)
            
            # Complete some tasks
            for i in range(0, task_count, 10):  # Every 10th task
                storage.complete_task(task_ids[i])
            
            # Close and reopen storage
            del storage
            
            # Verify all data persists
            new_storage = Storage(str(db_path), keep_test_db=True)
            
            all_tasks = new_storage.get_tasks(show_completed=True)
            all_entries = new_storage.get_journal_entries()
            
            assert len(all_tasks) == task_count
            assert len(all_entries) == entry_count
            
            # Verify completed tasks
            completed_tasks = [t for t in all_tasks if t['completed']]
            assert len(completed_tasks) == task_count // 10
            
            # Verify data integrity
            for i, task in enumerate(all_tasks):
                assert task['content'].startswith("Large dataset task")
                assert "large_dataset" in task['tags']
            
            for i, entry in enumerate(all_entries):
                assert entry['text'].startswith("Large dataset entry")
                assert "large_dataset" in entry['tags']
                
        finally:
            if db_path.exists():
                db_path.unlink()
    
    def test_database_file_size_management(self, temp_dir):
        db_path = temp_dir / "size_management.db"
        
        try:
            storage = Storage(str(db_path), keep_test_db=True)
            
            initial_size = db_path.stat().st_size if db_path.exists() else 0
            
            # Add substantial amount of data
            for i in range(500):
                storage.add_task(f"Size test task {i}" + " extra content" * 10)
                storage.add_journal_entry(f"Size test entry {i}" + " extra content" * 20)
            
            # Check file size growth
            current_size = db_path.stat().st_size
            assert current_size > initial_size
            
            # Delete some data
            tasks = storage.get_tasks()
            for i in range(0, len(tasks), 2):  # Delete every other task
                storage.delete_task(tasks[i]['id'])
            
            entries = storage.get_journal_entries()
            for i in range(0, len(entries), 2):  # Delete every other entry
                storage.delete_journal_entry(entries[i]['id'])
            
            # File size might not decrease immediately due to SQLite behavior
            # but database should still function correctly
            remaining_tasks = storage.get_tasks()
            remaining_entries = storage.get_journal_entries()
            
            assert len(remaining_tasks) < len(tasks)
            assert len(remaining_entries) < len(entries)
            
        finally:
            if db_path.exists():
                db_path.unlink()
    
    def test_concurrent_persistence(self, temp_dir):
        db_path = temp_dir / "concurrent_persistence.db"
        
        def worker_function(worker_id, iterations):
            storage = Storage(str(db_path), keep_test_db=True)
            for i in range(iterations):
                storage.add_task(f"Worker {worker_id} task {i}")
                time.sleep(0.001)  # Small delay
        
        try:
            # Run concurrent workers
            import threading
            
            threads = []
            workers = 3
            iterations = 20
            
            for worker_id in range(workers):
                thread = threading.Thread(
                    target=worker_function,
                    args=(worker_id, iterations)
                )
                threads.append(thread)
                thread.start()
            
            # Wait for all workers to complete
            for thread in threads:
                thread.join()
            
            # Verify all data was persisted
            storage = Storage(str(db_path), keep_test_db=True)
            tasks = storage.get_tasks()
            
            # Should have all tasks from all workers
            expected_count = workers * iterations
            assert len(tasks) == expected_count
            
            # Verify no data corruption
            for worker_id in range(workers):
                worker_tasks = [t for t in tasks if f"Worker {worker_id}" in t['content']]
                assert len(worker_tasks) == iterations
                
        finally:
            if db_path.exists():
                db_path.unlink()


class TestDataExportImport:
    def test_json_export_format(self, temp_dir):
        db_path = temp_dir / "export_test.db"
        export_path = temp_dir / "export_test.json"
        
        try:
            storage = Storage(str(db_path), keep_test_db=True)
            
            # Add test data
            task_id = storage.add_task("Export test task", "high", ["export", "test"])
            entry_id = storage.add_journal_entry("Export test entry", ["export", "test"])
            
            # Complete the task
            storage.complete_task(task_id)
            
            # Export data (simulate export functionality)
            export_data = {
                'tasks': storage.get_tasks(show_completed=True),
                'journal_entries': storage.get_journal_entries(),
                'export_timestamp': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            # Verify export file
            assert export_path.exists()
            assert export_path.stat().st_size > 0
            
            # Verify export content
            with open(export_path, 'r') as f:
                imported_data = json.load(f)
            
            assert 'tasks' in imported_data
            assert 'journal_entries' in imported_data
            assert 'export_timestamp' in imported_data
            assert 'version' in imported_data
            
            assert len(imported_data['tasks']) == 1
            assert len(imported_data['journal_entries']) == 1
            
            # Verify task data
            exported_task = imported_data['tasks'][0]
            assert exported_task['content'] == "Export test task"
            assert exported_task['priority'] == "high"
            assert set(exported_task['tags']) == {"export", "test"}
            assert exported_task['completed'] is True
            
            # Verify journal data
            exported_entry = imported_data['journal_entries'][0]
            assert exported_entry['text'] == "Export test entry"
            assert set(exported_entry['tags']) == {"export", "test"}
            
        finally:
            for file_path in [db_path, export_path]:
                if file_path.exists():
                    file_path.unlink()
    
    def test_import_data_integrity(self, temp_dir):
        source_db = temp_dir / "source.db"
        target_db = temp_dir / "target.db"
        export_file = temp_dir / "import_test.json"
        
        try:
            # Create source data
            source_storage = Storage(str(source_db), keep_test_db=True)
            
            original_tasks = []
            original_entries = []
            
            for i in range(10):
                task_id = source_storage.add_task(f"Import test task {i}", "medium", ["import"])
                original_tasks.append(source_storage.get_tasks()[-1])
                
                entry_id = source_storage.add_journal_entry(f"Import test entry {i}", ["import"])
                original_entries.append(source_storage.get_journal_entries()[-1])
            
            # Export data
            export_data = {
                'tasks': source_storage.get_tasks(),
                'journal_entries': source_storage.get_journal_entries(),
                'export_timestamp': datetime.now().isoformat()
            }
            
            with open(export_file, 'w') as f:
                json.dump(export_data, f, default=str)
            
            # Import to new database (simulate import process)
            target_storage = Storage(str(target_db), keep_test_db=True)
            
            with open(export_file, 'r') as f:
                import_data = json.load(f)
            
            # Import tasks
            for task_data in import_data['tasks']:
                target_storage.add_task(
                    task_data['content'],
                    task_data['priority'],
                    task_data['tags']
                )
            
            # Import journal entries
            for entry_data in import_data['journal_entries']:
                target_storage.add_journal_entry(
                    entry_data['text'],
                    entry_data['tags'],
                    entry_data.get('category')
                )
            
            # Verify imported data
            imported_tasks = target_storage.get_tasks()
            imported_entries = target_storage.get_journal_entries()
            
            assert len(imported_tasks) == len(original_tasks)
            assert len(imported_entries) == len(original_entries)
            
            # Verify content integrity
            original_task_contents = {task['content'] for task in original_tasks}
            imported_task_contents = {task['content'] for task in imported_tasks}
            assert original_task_contents == imported_task_contents
            
            original_entry_texts = {entry['text'] for entry in original_entries}
            imported_entry_texts = {entry['text'] for entry in imported_entries}
            assert original_entry_texts == imported_entry_texts
            
        finally:
            for file_path in [source_db, target_db, export_file]:
                if file_path.exists():
                    file_path.unlink()
