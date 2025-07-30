import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, Mock
import json

from taskcheck.report import (
    get_tasks,
    get_taskwarrior_date,
    get_days_in_constraint,
    generate_report,
    get_task_emoji,
    tostring,
    get_unplanned_tasks
)


class TestDateUtilities:
    @patch('subprocess.run')
    def test_get_taskwarrior_date_valid(self, mock_run, test_taskrc):
        mock_result = Mock()
        mock_result.stdout = "2023-12-05T14:30:00\n"
        mock_run.return_value = mock_result
        
        result = get_taskwarrior_date("today", taskrc=test_taskrc)
        
        assert result == datetime(2023, 12, 5, 14, 30, 0)
        mock_run.assert_called_once()
        # Verify environment was passed
        call_args = mock_run.call_args
        assert 'env' in call_args.kwargs
        assert call_args.kwargs['env']['TASKRC'] == test_taskrc
        
    @patch('subprocess.run')
    def test_get_taskwarrior_date_relative(self, mock_run, test_taskrc):
        # First call fails, second call with "today+" prefix succeeds
        mock_result_fail = Mock()
        mock_result_fail.stdout = "invalid\n"
        
        mock_result_success = Mock()
        mock_result_success.stdout = "2023-12-06T14:30:00\n"
        
        mock_run.side_effect = [mock_result_fail, mock_result_success]
        
        result = get_taskwarrior_date("1day", taskrc=test_taskrc)
        
        assert result == datetime(2023, 12, 6, 14, 30, 0)
        assert mock_run.call_count == 2
        
    def test_get_days_in_constraint(self, test_taskrc):
        with patch('taskcheck.report.get_taskwarrior_date') as mock_date:
            with patch('taskcheck.report.datetime') as mock_datetime:
                # Mock the constraint date (end of week)
                mock_date.return_value = datetime(2023, 12, 7, 0, 0, 0)
                
                # Mock datetime.today() to return an earlier date
                mock_datetime.today.return_value = datetime(2023, 12, 5, 0, 0, 0)
                mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
                
                days = list(get_days_in_constraint("eow", taskrc=test_taskrc))
                
                # Should return days from Dec 5 to Dec 7 (3 days)
                assert len(days) == 3
                assert all(len(day) == 3 for day in days)  # (year, month, day)
                mock_date.assert_called_once_with("eow", taskrc=test_taskrc)


class TestTaskFiltering:
    def test_get_tasks_with_scheduling(self, sample_config):
        tasks_with_scheduling = [
            {
                "id": 1,
                "project": "test",
                "description": "Test task",
                "scheduling": "2023-12-05 - PT2H\n2023-12-06 - PT1H",
                "urgency": 10.0
            },
            {
                "id": 2,
                "project": "other",
                "description": "Another task",
                "scheduling": "2023-12-05 - PT30M",
                "urgency": 5.0
            }
        ]
        
        result = get_tasks(sample_config["report"], tasks_with_scheduling, 2023, 12, 5)
        
        assert len(result) == 2
        assert result[0]["urgency"] >= result[1]["urgency"]  # Sorted by urgency
        
    @patch('subprocess.run')
    def test_get_unplanned_tasks(self, mock_run, sample_config, test_taskrc):
        unplanned_tasks = [
            {
                "id": 3,
                "description": "Unplanned task",
                "urgency": 8.0,
                "due": "20231210T170000Z"
            }
        ]
        
        mock_result = Mock()
        mock_result.stdout = json.dumps(unplanned_tasks)
        mock_run.return_value = mock_result
        
        result = get_unplanned_tasks(sample_config["report"], [], taskrc=test_taskrc)
        
        assert result == unplanned_tasks
        # Verify environment was passed
        call_args = mock_run.call_args
        assert 'env' in call_args.kwargs
        assert call_args.kwargs['env']['TASKRC'] == test_taskrc


class TestStringFormatting:
    def test_tostring_boolean(self):
        assert tostring(True) == "Yes"
        assert tostring(False) == "No"
        
    def test_tostring_datetime(self):
        dt = datetime(2023, 12, 5, 14, 30, 0)
        assert tostring(dt) == "2023-12-05 14:30"
        
    def test_tostring_taskwarrior_date(self):
        tw_date = "20231205T143000Z"
        result = tostring(tw_date)
        assert "2023-12-05 14:30" == result
        
    def test_tostring_regular_string(self):
        assert tostring("hello") == "hello"
        
    def test_tostring_number(self):
        assert tostring(42) == "42"
        assert tostring(3.14) == "3.14"


class TestEmojiGeneration:
    def test_get_task_emoji_keyword_match(self, sample_config):
        task = {"description": "Schedule a meeting with the team"}
        emoji = get_task_emoji(sample_config["report"], task)
        
        assert emoji == ":busts_in_silhouette:"
        
    def test_get_task_emoji_default_keyword(self, sample_config):
        task = {"description": "Write some code for the project"}
        emoji = get_task_emoji(sample_config["report"], task)
        
        assert emoji == ":computer:"
        
    def test_get_task_emoji_random(self, sample_config):
        task = {"description": "Some random task without keywords"}
        emoji = get_task_emoji(sample_config["report"], task)
        
        # Should return some emoji (deterministic based on description)
        assert len(emoji) >= 1
        
        # Same description should give same emoji
        emoji2 = get_task_emoji(sample_config["report"], task)
        assert emoji == emoji2


class TestReportGeneration:
    @patch('taskcheck.report.fetch_tasks')
    @patch('taskcheck.report.get_days_in_constraint')
    @patch('taskcheck.report.get_unplanned_tasks')
    def test_generate_report_basic(self, mock_unplanned, mock_days, mock_fetch, sample_config, test_taskrc):
        mock_fetch.return_value = [
            {
                "id": 1,
                "description": "Test task",
                "scheduling": "2023-12-05 - PT2H",
                "urgency": 10.0,
                "project": "test"
            }
        ]
        mock_days.return_value = [(2023, 12, 5)]
        mock_unplanned.return_value = []
        
        # Should run without error
        generate_report(sample_config, "today", verbose=True, taskrc=test_taskrc)
        
        mock_fetch.assert_called_once_with(test_taskrc)
        mock_days.assert_called_once_with("today", taskrc=test_taskrc)
        
    @patch('taskcheck.report.fetch_tasks')
    @patch('taskcheck.report.get_days_in_constraint')
    @patch('taskcheck.report.get_unplanned_tasks')
    def test_generate_report_with_unplanned(self, mock_unplanned, mock_days, mock_fetch, sample_config, test_taskrc):
        mock_fetch.return_value = []
        mock_days.return_value = [(2023, 12, 5)]
        mock_unplanned.return_value = [
            {
                "id": 2,
                "description": "Unplanned task",
                "urgency": 5.0,
                "project": "urgent"
            }
        ]
        
        # Should run without error
        generate_report(sample_config, "today", verbose=True, taskrc=test_taskrc)
        
        mock_unplanned.assert_called_once_with(sample_config["report"], [], taskrc=test_taskrc)
