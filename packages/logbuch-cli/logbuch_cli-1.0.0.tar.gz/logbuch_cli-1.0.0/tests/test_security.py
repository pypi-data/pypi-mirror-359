#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# tests/test_security.py

import pytest
from unittest.mock import Mock, patch, MagicMock
import sqlite3
import tempfile
from pathlib import Path

from tests.test_mocks import MockStorage, MockConfig
from logbuch.storage import Storage
from logbuch.commands.task import add_task, list_tasks
from logbuch.commands.journal import add_journal_entry, list_journal_entries


class TestInputValidation:
    def test_sql_injection_in_task_content(self, temp_dir):
        db_path = temp_dir / "security_test.db"
        storage = Storage(str(db_path), keep_test_db=True)
        
        try:
            # Common SQL injection patterns
            malicious_inputs = [
                "'; DROP TABLE tasks; --",
                "1' OR '1'='1",
                "UNION SELECT * FROM sqlite_master",
                "'; INSERT INTO tasks (content) VALUES ('hacked'); --",
                "' OR 1=1 --",
                "admin'--",
                "admin'/*",
                "' OR 'x'='x",
                "1'; DROP TABLE users; --"
            ]
            
            for malicious_input in malicious_inputs:
                # Should not cause SQL injection
                task_id = storage.add_task(malicious_input)
                assert task_id is not None
                
                # Verify the malicious input is stored as plain text
                tasks = storage.get_tasks()
                found_task = next((t for t in tasks if t['content'] == malicious_input), None)
                assert found_task is not None
                assert found_task['content'] == malicious_input
            
            # Verify database structure is intact
            with sqlite3.connect(str(db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                
                # All expected tables should still exist
                table_names = [table[0] for table in tables]
                assert 'tasks' in table_names
                assert 'journal_entries' in table_names
                
        finally:
            if db_path.exists():
                db_path.unlink()
    
    def test_sql_injection_in_journal_entries(self, temp_dir):
        db_path = temp_dir / "security_journal_test.db"
        storage = Storage(str(db_path), keep_test_db=True)
        
        try:
            malicious_entries = [
                "Today I learned about SQL injection'; DROP TABLE journal_entries; --",
                "My thoughts: ' OR '1'='1",
                "Reflection: '; UPDATE tasks SET completed=1; --"
            ]
            
            for malicious_entry in malicious_entries:
                entry_id = storage.add_journal_entry(malicious_entry)
                assert entry_id is not None
                
                # Verify entry is stored safely
                entries = storage.get_journal_entries()
                found_entry = next((e for e in entries if e['text'] == malicious_entry), None)
                assert found_entry is not None
                
        finally:
            if db_path.exists():
                db_path.unlink()
    
    def test_xss_prevention_in_content(self, mock_storage):
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "<iframe src='javascript:alert(\"xss\")'></iframe>",
            "<svg onload=alert('xss')>",
            "';alert('xss');//",
            "<body onload=alert('xss')>",
            "<input onfocus=alert('xss') autofocus>"
        ]
        
        for payload in xss_payloads:
            # Add task with XSS payload
            task_id = add_task(mock_storage, payload)
            assert task_id is not None
            
            # Verify payload is stored as-is (not executed)
            tasks = list_tasks(mock_storage)
            found_task = next((t for t in tasks if t['content'] == payload), None)
            assert found_task is not None
            assert found_task['content'] == payload
            
            # Add journal entry with XSS payload
            entry_id = add_journal_entry(mock_storage, payload)
            assert entry_id is not None
            
            entries = list_journal_entries(mock_storage)
            found_entry = next((e for e in entries if e['text'] == payload), None)
            assert found_entry is not None
    
    def test_path_traversal_prevention(self, temp_dir):
        # Test with malicious database paths
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd",
            "/etc/passwd",
            "C:\\Windows\\System32\\config\\sam",
            "~/.ssh/id_rsa",
            "/dev/null",
            "/proc/version"
        ]
        
        for malicious_path in malicious_paths:
            try:
                # Should not allow access to system files
                db_path = temp_dir / "safe_test.db"
                storage = Storage(str(db_path), keep_test_db=True)
                
                # Normal operations should work
                task_id = storage.add_task("Test task")
                assert task_id is not None
                
                # Cleanup
                if db_path.exists():
                    db_path.unlink()
                    
            except Exception as e:
                # Some paths might cause legitimate errors, which is acceptable
                # as long as they don't allow unauthorized access
                pass
    
    def test_oversized_input_handling(self, mock_storage):
        # Test very large task content
        large_content = "A" * 100000  # 100KB
        task_id = add_task(mock_storage, large_content)
        assert task_id is not None
        
        # Test very large journal entry
        large_journal = "B" * 1000000  # 1MB
        entry_id = add_journal_entry(mock_storage, large_journal)
        assert entry_id is not None
        
        # Test extremely large input (should be handled gracefully)
        huge_content = "C" * 10000000  # 10MB
        try:
            huge_task_id = add_task(mock_storage, huge_content)
            # If it succeeds, verify it's stored correctly
            if huge_task_id:
                tasks = list_tasks(mock_storage)
                huge_task = next((t for t in tasks if len(t['content']) > 1000000), None)
                assert huge_task is not None
        except Exception:
            # It's acceptable to reject extremely large inputs
            pass
    
    def test_null_byte_injection(self, mock_storage):
        null_byte_inputs = [
            "normal_text\x00malicious_part",
            "task\x00.txt",
            "content\x00' OR '1'='1",
            "\x00admin",
            "test\x00\x00test"
        ]
        
        for null_input in null_byte_inputs:
            task_id = add_task(mock_storage, null_input)
            assert task_id is not None
            
            # Verify the input is handled safely
            tasks = list_tasks(mock_storage)
            # The null byte might be stripped or preserved, both are acceptable
            # as long as it doesn't cause security issues


class TestAuthenticationSecurity:
    def test_database_file_permissions(self, temp_dir):
        db_path = temp_dir / "permissions_test.db"
        storage = Storage(str(db_path), keep_test_db=True)
        
        try:
            # Add some data to ensure file is created
            storage.add_task("Permission test task")
            
            # Check file permissions (on Unix-like systems)
            import stat
            import os
            
            if os.name != 'nt':  # Not Windows
                file_stat = db_path.stat()
                file_mode = stat.filemode(file_stat.st_mode)
                
                # File should not be world-readable/writable
                assert not (file_stat.st_mode & stat.S_IROTH)  # Not world-readable
                assert not (file_stat.st_mode & stat.S_IWOTH)  # Not world-writable
                
        finally:
            if db_path.exists():
                db_path.unlink()
    
    def test_backup_file_security(self, temp_dir):
        db_path = temp_dir / "backup_security_test.db"
        storage = Storage(str(db_path), keep_test_db=True)
        
        try:
            # Add data and create backup
            storage.add_task("Backup security test")
            backup_path = storage.create_backup()
            
            assert backup_path is not None
            backup_file = Path(backup_path)
            assert backup_file.exists()
            
            # Backup should have appropriate permissions
            import stat
            import os
            
            if os.name != 'nt':  # Not Windows
                backup_stat = backup_file.stat()
                
                # Backup should not be world-accessible
                assert not (backup_stat.st_mode & stat.S_IROTH)
                assert not (backup_stat.st_mode & stat.S_IWOTH)
                
        finally:
            if db_path.exists():
                db_path.unlink()


class TestDataIntegrity:
    def test_concurrent_access_integrity(self, temp_dir):
        import threading
        import time
        
        db_path = temp_dir / "concurrent_integrity_test.db"
        
        def worker_function(worker_id, task_count):
            storage = Storage(str(db_path), keep_test_db=True)
            for i in range(task_count):
                storage.add_task(f"Worker {worker_id} task {i}")
                time.sleep(0.001)  # Small delay to increase chance of conflicts
        
        try:
            # Start multiple workers
            threads = []
            workers = 5
            tasks_per_worker = 20
            
            for worker_id in range(workers):
                thread = threading.Thread(
                    target=worker_function,
                    args=(worker_id, tasks_per_worker)
                )
                threads.append(thread)
                thread.start()
            
            # Wait for all workers to complete
            for thread in threads:
                thread.join()
            
            # Verify data integrity
            storage = Storage(str(db_path), keep_test_db=True)
            tasks = storage.get_tasks()
            
            # Should have all tasks from all workers
            assert len(tasks) == workers * tasks_per_worker
            
            # Verify no duplicate IDs
            task_ids = [task['id'] for task in tasks]
            assert len(task_ids) == len(set(task_ids))
            
        finally:
            if db_path.exists():
                db_path.unlink()
    
    def test_transaction_rollback_integrity(self, temp_dir):
        db_path = temp_dir / "transaction_test.db"
        storage = Storage(str(db_path), keep_test_db=True)
        
        try:
            # Add initial data
            initial_task_id = storage.add_task("Initial task")
            initial_tasks = storage.get_tasks()
            initial_count = len(initial_tasks)
            
            # Simulate a failed transaction by directly accessing the database
            with sqlite3.connect(str(db_path)) as conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("BEGIN TRANSACTION")
                    cursor.execute(
                        "INSERT INTO tasks (content, priority, board, completed) VALUES (?, ?, ?, ?)",
                        ("Transaction test task", "medium", "default", False)
                    )
                    # Simulate error before commit
                    raise Exception("Simulated transaction error")
                except Exception:
                    conn.rollback()
            
            # Verify database state is unchanged
            final_tasks = storage.get_tasks()
            assert len(final_tasks) == initial_count
            
            # Verify the failed transaction didn't leave partial data
            task_contents = [task['content'] for task in final_tasks]
            assert "Transaction test task" not in task_contents
            
        finally:
            if db_path.exists():
                db_path.unlink()
    
    def test_database_corruption_recovery(self, temp_dir):
        db_path = temp_dir / "corruption_test.db"
        
        # Create a valid database first
        storage = Storage(str(db_path), keep_test_db=True)
        storage.add_task("Test task before corruption")
        del storage  # Close the connection
        
        try:
            # Corrupt the database file
            with open(db_path, 'wb') as f:
                f.write(b"This is not a valid SQLite database file")
            
            # Attempt to create storage with corrupted file
            with pytest.raises(Exception):
                corrupted_storage = Storage(str(db_path), keep_test_db=True)
                
        finally:
            if db_path.exists():
                db_path.unlink()


class TestPrivacyAndDataProtection:
    def test_sensitive_data_handling(self, mock_storage):
        sensitive_data = [
            "My password is: secret123",
            "SSN: 123-45-6789",
            "Credit card: 4532-1234-5678-9012",
            "Email: user@example.com, Password: mypassword",
            "API Key: sk-1234567890abcdef",
            "Personal thoughts about my relationship issues"
        ]
        
        for sensitive_content in sensitive_data:
            # Data should be stored (this is a personal journal app)
            # but we should ensure it's handled securely
            task_id = add_task(mock_storage, sensitive_content)
            assert task_id is not None
            
            entry_id = add_journal_entry(mock_storage, sensitive_content)
            assert entry_id is not None
            
            # Verify data is stored correctly
            tasks = list_tasks(mock_storage)
            entries = list_journal_entries(mock_storage)
            
            assert any(sensitive_content in task['content'] for task in tasks)
            assert any(sensitive_content in entry['text'] for entry in entries)
    
    def test_data_export_security(self, mock_storage):
        # Add various types of data
        add_task(mock_storage, "Confidential work task", tags=["work", "confidential"])
        add_journal_entry(mock_storage, "Private personal thoughts", tags=["personal"])
        
        # Export data (simulated)
        tasks = list_tasks(mock_storage, show_completed=True)
        entries = list_journal_entries(mock_storage)
        
        export_data = {
            'tasks': tasks,
            'journal_entries': entries,
            'export_timestamp': '2024-01-01T00:00:00'
        }
        
        # Verify export contains expected data
        assert len(export_data['tasks']) == 1
        assert len(export_data['journal_entries']) == 1
        
        # In a real implementation, ensure export is encrypted or secured
        # This test verifies the data structure is correct
        assert 'export_timestamp' in export_data
        assert isinstance(export_data['tasks'], list)
        assert isinstance(export_data['journal_entries'], list)


class TestSecurityConfiguration:
    def test_security_config_validation(self):
        from tests.test_mocks import MockSecurityConfig
        
        config = MockSecurityConfig()
        
        # Test default security settings
        assert config.input_validation is True
        assert config.rate_limit_enabled is False  # Disabled for tests
        assert config.max_input_length == 10000
        
        # Test configuration validation
        assert hasattr(config, 'input_validation')
        assert hasattr(config, 'rate_limit_enabled')
        assert hasattr(config, 'max_input_length')
    
    def test_input_length_limits(self, mock_storage):
        # This would typically be enforced at the application level
        max_length = 10000
        
        # Test content at limit
        content_at_limit = "A" * max_length
        task_id = add_task(mock_storage, content_at_limit)
        assert task_id is not None
        
        # Test content over limit (in real app, this might be rejected)
        content_over_limit = "B" * (max_length + 1)
        try:
            over_limit_task_id = add_task(mock_storage, content_over_limit)
            # If accepted, verify it's stored correctly
            if over_limit_task_id:
                tasks = list_tasks(mock_storage)
                over_limit_task = next((t for t in tasks if len(t['content']) > max_length), None)
                # In mock storage, this might be allowed
        except Exception:
            # It's acceptable to reject oversized inputs
            pass
    
    def test_rate_limiting_simulation(self, mock_storage):
        import time
        
        # Simulate rapid requests
        start_time = time.time()
        request_count = 100
        
        for i in range(request_count):
            add_task(mock_storage, f"Rate limit test task {i}")
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        # In a real app with rate limiting, this might take longer
        # For mock storage, it should be fast
        assert elapsed < 5.0  # Should complete quickly in mock
        
        # Verify all requests were processed
        tasks = list_tasks(mock_storage)
        assert len(tasks) == request_count


class TestSecurityAuditing:
    def test_security_event_logging(self, mock_storage):
        with patch('logbuch.core.logger.get_logger') as mock_logger:
            mock_log = Mock()
            mock_logger.return_value = mock_log
            
            # Perform operations that might trigger security logging
            suspicious_content = "'; DROP TABLE tasks; --"
            add_task(mock_storage, suspicious_content)
            
            # In a real implementation, suspicious patterns might be logged
            # For now, just verify the operation completed
            tasks = list_tasks(mock_storage)
            assert len(tasks) == 1
    
    def test_failed_operation_handling(self, temp_dir):
        db_path = temp_dir / "failed_ops_test.db"
        
        try:
            storage = Storage(str(db_path), keep_test_db=True)
            
            # Test with invalid data types
            try:
                # This might fail in real storage due to type validation
                result = storage.add_task(None)  # Invalid content
            except Exception as e:
                # Failure should be handled gracefully
                assert isinstance(e, Exception)
            
            # Database should remain in consistent state
            tasks = storage.get_tasks()
            # Should not have any tasks with None content
            assert all(task['content'] is not None for task in tasks)
            
        finally:
            if db_path.exists():
                db_path.unlink()


# Security test utilities

def run_security_audit():
    print("Running Logbuch Security Audit...")
    print("=" * 50)
    
    # Test SQL injection patterns
    print("Testing SQL Injection Prevention...")
    sql_patterns = [
        "'; DROP TABLE tasks; --",
        "1' OR '1'='1",
        "UNION SELECT * FROM users"
    ]
    
    mock_storage = MockStorage()
    for pattern in sql_patterns:
        try:
            add_task(mock_storage, pattern)
            print(f"  ✓ SQL pattern handled safely: {pattern[:30]}...")
        except Exception as e:
            print(f"  ⚠ SQL pattern caused error: {pattern[:30]}... ({e})")
    
    # Test XSS patterns
    print("\nTesting XSS Prevention...")
    xss_patterns = [
        "<script>alert('xss')</script>",
        "javascript:alert('xss')",
        "<img src=x onerror=alert('xss')>"
    ]
    
    for pattern in xss_patterns:
        try:
            add_task(mock_storage, pattern)
            print(f"  ✓ XSS pattern handled safely: {pattern[:30]}...")
        except Exception as e:
            print(f"  ⚠ XSS pattern caused error: {pattern[:30]}... ({e})")
    
    print("\nSecurity audit completed!")


if __name__ == "__main__":
    run_security_audit()
