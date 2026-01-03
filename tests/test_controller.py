import pytest
from unittest.mock import MagicMock, patch
from src.controllers.experiment_manager import ExperimentManager

class TestExperimentManager:
    @pytest.fixture
    def manager(self):
        return ExperimentManager()

    @patch('src.controllers.experiment_manager.SessionLocal')
    def test_create_experiment(self, mock_session, manager):
        # Mock do DB Session
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        
        config = {'population_size': 50}
        manager.create_experiment(config)
        
        # Verifica se chamou add e commit
        assert mock_db.add.called
        assert mock_db.commit.called
    
    @patch('src.controllers.experiment_manager.threading.Thread')
    def test_run_experiment_background(self, mock_thread, manager):
        manager.run_experiment_background(1)
        assert mock_thread.called
