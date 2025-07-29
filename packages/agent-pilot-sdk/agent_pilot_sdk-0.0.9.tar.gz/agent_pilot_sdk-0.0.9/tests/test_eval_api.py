import pytest
from unittest.mock import patch, MagicMock
from pydantic import ValidationError

from agent_pilot.eval.api import evaluate, generate_criteria
from agent_pilot.eval.models import EvaluationResult, InputResponseExample, Metric


@pytest.fixture
def mock_config():
    with patch("agent_pilot.eval.api.get_config") as mock_get_config:
        mock_config_instance = MagicMock()
        mock_config_instance.api_key = "default_api_key"
        mock_config_instance.api_url = "http://default.api.url"
        mock_get_config.return_value = mock_config_instance
        yield mock_get_config


class TestEvaluate:
    @patch("agent_pilot.eval.api.eval_service_input_response_evaluate")
    def test_evaluate_success(self, mock_eval_service, mock_config):
        example_data = {"example_id": "1", "input": "test input", "response": "test response"}
        metric_data = {"criteria": "test criteria"}
        mock_eval_service.return_value = EvaluationResult(example_id="1", results=[])

        result = evaluate(example_data, metric_data)

        assert isinstance(result, EvaluationResult)
        mock_eval_service.assert_called_once()
        _, called_kwargs = mock_eval_service.call_args
        assert isinstance(called_kwargs["input_response_example"], InputResponseExample)
        assert isinstance(called_kwargs["metric_prompt"], Metric)
        assert called_kwargs["api_key"] == "default_api_key"
        assert called_kwargs["api_url"] == "http://default.api.url"

    def test_evaluate_invalid_example(self, mock_config):
        example_data = {"example_id": "1"}  # Missing required fields
        metric_data = {"criteria": "test criteria"}

        with pytest.raises(ValidationError):
            evaluate(example_data, metric_data)

    def test_evaluate_invalid_metric(self, mock_config):
        example_data = {"example_id": "1", "input": "test input", "response": "test response"}
        metric_data = {"name": "test_metric"}  # Missing required field

        with pytest.raises(ValidationError):
            evaluate(example_data, metric_data)

    @patch("agent_pilot.eval.api.eval_service_input_response_evaluate")
    def test_evaluate_api_error(self, mock_eval_service, mock_config):
        example_data = {"example_id": "1", "input": "test input", "response": "test response"}
        metric_data = {"criteria": "test criteria"}
        mock_eval_service.side_effect = Exception("API Error")

        with pytest.raises(RuntimeError, match="(?s)Evaluation failed:.*API Error"):
            evaluate(example_data, metric_data)

    @patch("agent_pilot.eval.api.eval_service_input_response_evaluate")
    def test_evaluate_with_custom_credentials(self, mock_eval_service, mock_config):
        example_data = {"example_id": "1", "input": "test input", "response": "test response"}
        metric_data = {"criteria": "test criteria"}
        mock_eval_service.return_value = EvaluationResult(example_id="1", results=[])

        evaluate(example_data, metric_data, api_key="custom_key", api_url="http://custom.url")

        _, called_kwargs = mock_eval_service.call_args
        assert called_kwargs["api_key"] == "custom_key"
        assert called_kwargs["api_url"] == "http://custom.url"


class TestGenerateCriteria:
    @patch("agent_pilot.eval.api.eval_service_criteria_generation")
    def test_generate_criteria_success(self, mock_criteria_service, mock_config):
        examples_data = [
            {"example_id": "1", "input": "in1", "response": "out1"},
            {"example_id": "2", "input": "in2", "response": "out2"},
        ]
        mock_criteria_service.return_value = "Generated Criteria"

        result = generate_criteria(examples_data)

        assert result == "Generated Criteria"
        mock_criteria_service.assert_called_once()
        _, called_kwargs = mock_criteria_service.call_args
        assert isinstance(called_kwargs["input_response_examples"], list)
        assert all(isinstance(ex, InputResponseExample) for ex in called_kwargs["input_response_examples"])
        assert called_kwargs["api_key"] == "default_api_key"
        assert called_kwargs["api_url"] == "http://default.api.url"

    def test_generate_criteria_invalid_example(self, mock_config):
        examples_data = [{"example_id": "1"}]  # Missing required fields

        with pytest.raises(ValidationError):
            generate_criteria(examples_data)

    @patch("agent_pilot.eval.api.eval_service_criteria_generation")
    def test_generate_criteria_api_error(self, mock_criteria_service, mock_config):
        examples_data = [{"example_id": "1", "input": "in1", "response": "out1"}]
        mock_criteria_service.side_effect = Exception("API Error")

        with pytest.raises(RuntimeError, match="(?s)Criteria generation failed:.*API Error"):
            generate_criteria(examples_data)

    @patch("agent_pilot.eval.api.eval_service_criteria_generation")
    def test_generate_criteria_with_custom_credentials(self, mock_criteria_service, mock_config):
        examples_data = [{"example_id": "1", "input": "in1", "response": "out1"}]
        mock_criteria_service.return_value = "Generated Criteria"

        generate_criteria(examples_data, api_key="custom_key", api_url="http://custom.url")

        _, called_kwargs = mock_criteria_service.call_args
        assert called_kwargs["api_key"] == "custom_key"
        assert called_kwargs["api_url"] == "http://custom.url"

    @patch("agent_pilot.eval.api.eval_service_criteria_generation")
    def test_generate_criteria_empty_list(self, mock_criteria_service, mock_config):
        examples_data = []
        mock_criteria_service.return_value = "Generated Criteria for empty"

        result = generate_criteria(examples_data)

        assert result == "Generated Criteria for empty"
        mock_criteria_service.assert_called_once_with(
            input_response_examples=[], api_key="default_api_key", api_url="http://default.api.url"
        )
