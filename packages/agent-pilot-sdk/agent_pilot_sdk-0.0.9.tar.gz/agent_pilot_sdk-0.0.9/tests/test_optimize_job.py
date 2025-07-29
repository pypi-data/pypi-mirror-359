import pytest
from unittest.mock import patch

from agent_pilot.optimize.models import (
    OptimizeDataRecord,
    OptimizeJobInfo,
    OptimizeProgress,
    OptimizeResult,
    OptimizeServiceStartOptimizeResult,
    OptimizeServiceProgressResult,
    OptimizeJobInfoPayload,
    OptimizeReport,
    OptimizeState,
)
from agent_pilot.optimize.optimize_job import OptimizeJob, create, resume


@pytest.fixture
def mock_config():
    with patch("agent_pilot.optimize.optimize_job.OptimizeJob._loaded_api_config") as mock_config_instance:
        mock_config_instance.api_key = "default_api_key"
        mock_config_instance.api_url = "http://default.api.url"
        mock_config_instance.local_debug = False
        yield mock_config_instance


class TestOptimizeJob:
    @patch("agent_pilot.optimize.optimize_job.optimize_service_start")
    def test_create_optimize_job_success(self, mock_start, mock_config):
        mock_start.return_value = OptimizeServiceStartOptimizeResult(
            TaskId="task-1", Version="v1", OptimizeJobId="job-123"
        )
        job = OptimizeJob.create_optimize_job("task-1", "v1")
        assert job.job_id == "job-123"
        assert job.task_id == "task-1"
        assert job.base_version == "v1"
        mock_start.assert_called_once_with(
            task_id="task-1", version="v1", api_key="default_api_key", api_url="http://default.api.url"
        )

    @patch("agent_pilot.optimize.optimize_job.optimize_service_start")
    def test_create_optimize_job_failure(self, mock_start, mock_config):
        mock_start.side_effect = Exception("API Error")
        with pytest.raises(RuntimeError, match="(?s)Starting optimization failed:.*API Error"):
            OptimizeJob.create_optimize_job("task-1", "v1")

    @patch("agent_pilot.optimize.optimize_job.optimize_service_get_progress")
    def test_get_job_info_success(self, mock_get_progress, mock_config):
        job = OptimizeJob(task_id="task-1", base_version="v1", job_id="job-123")
        expected_progress = OptimizeProgress(
            ProgressPercent=100.0,
            TotalCnt=100,
            BetterCnt=0,
            WorseCnt=0,
            UnchangedCnt=0,
            InitFullscoreCnt=100,
            FullscoreCntList=[100],
            InitAverageScore=50.0,
            AverageScoreList=[5.0],
            OptimizeTokenConsumption=100,
            OptimalPrompt="optimal prompt",
        )
        job_info = OptimizeJobInfoPayload(
            JobId="job-123",
            Version="v1",
            CreatedTime="2025-07-01 00:00:00",
            UpdatedTime="2025-07-02 00:00:00",
            State=OptimizeState.SUCCESS.value,
            OptimizedVersion="v2",
        )
        mock_get_progress.return_value = OptimizeServiceProgressResult(JobInfo=job_info, Progress=expected_progress)

        job_info = job.get_job_info()

        assert job_info.job_id == "job-123"
        assert job_info.state == OptimizeState.SUCCESS
        assert job_info.progress == expected_progress
        assert job_info.optimized_version == "v2"
        mock_get_progress.assert_called_once_with(
            optimize_job_id="job-123", api_key="default_api_key", api_url="http://default.api.url"
        )

    def test_get_job_info_missing_credentials(self, mock_config):
        job = OptimizeJob(task_id="task-1", base_version="v1", job_id="job-123")
        job.api_key = None
        with pytest.raises(RuntimeError, match="API key or API URL is not set"):
            job.get_job_info()

    @patch("agent_pilot.optimize.optimize_job.optimize_service_get_report")
    @patch.object(OptimizeJob, "get_job_info")
    def test_get_report_success(self, mock_get_job_info, mock_get_report, mock_config):
        job = OptimizeJob(task_id="task-1", base_version="v1", job_id="job-123")
        data_record = OptimizeDataRecord(record_id="record-1")
        base_result = OptimizeResult(records=[data_record], prompt="base prompt", metric="metric", avg_score=4.0)
        opt_result = OptimizeResult(records=[data_record], prompt="optimal prompt", metric="metric", avg_score=5.0)
        mock_get_report.return_value = OptimizeReport(base=base_result, opt=opt_result)

        report = job.get_report(ref_version="v2")

        assert report.base == base_result
        assert report.opt == opt_result
        mock_get_report.assert_called_once_with(
            task_id="task-1",
            base_version="v1",
            ref_version="v2",
            api_key="default_api_key",
            api_url="http://default.api.url",
        )
        mock_get_job_info.assert_not_called()

    @patch("agent_pilot.optimize.optimize_job.optimize_service_get_report")
    @patch.object(OptimizeJob, "get_job_info")
    def test_get_report_fetches_ref_version(self, mock_get_job_info, mock_get_report, mock_config):
        job = OptimizeJob(task_id="task-1", base_version="v1", job_id="job-123")
        mock_job_info = OptimizeJobInfo(job_id="job-123", state=OptimizeState.SUCCESS, optimized_version="v3")
        mock_get_job_info.return_value = mock_job_info
        data_record = OptimizeDataRecord(record_id="record-1")
        base_result = OptimizeResult(records=[data_record], prompt="base prompt", metric="metric", avg_score=4.0)
        opt_result = OptimizeResult(records=[data_record], prompt="optimal prompt", metric="metric", avg_score=5.0)
        mock_get_report.return_value = OptimizeReport(base=base_result, opt=opt_result)

        job.get_report()

        mock_get_job_info.assert_called_once()
        mock_get_report.assert_called_once_with(
            task_id="task-1",
            base_version="v1",
            ref_version="v3",
            api_key="default_api_key",
            api_url="http://default.api.url",
        )


@patch("agent_pilot.optimize.optimize_job.OptimizeJob.create_optimize_job")
def test_create_function(mock_create_job):
    mock_create_job.return_value = "mock_job"
    result = create("task-1", "v1", api_key="key", api_url="url")
    assert result == "mock_job"
    mock_create_job.assert_called_once_with("task-1", "v1", "key", "url")


def test_resume_function():
    job = resume("task-1", "v1", "job-123", api_key="key", api_url="url")
    assert isinstance(job, OptimizeJob)
    assert job.task_id == "task-1"
    assert job.base_version == "v1"
    assert job.job_id == "job-123"
    assert job.api_key == "key"
    assert job.api_url == "url"
