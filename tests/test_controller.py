import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone, timedelta
import math
from src.controllers.experiment_manager import ExperimentManager
from src.database.models import Experiment

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

    @patch('src.controllers.experiment_manager.SessionLocal')
    def test_delete_failed_experiments_removes_failed_status(self, mock_session, manager):
        """Testa se remove experimentos com status 'failed'"""
        mock_db = MagicMock()
        mock_session.return_value = mock_db

        # Simula query retornando experimentos 'failed'
        mock_query = mock_db.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.delete.return_value = 2  # 2 experimentos removidos

        result = manager.delete_failed_experiments()

        assert result is True
        assert mock_db.commit.called

    @patch('src.controllers.experiment_manager.SessionLocal')
    def test_delete_failed_experiments_removes_stale_running(self, mock_session, manager):
        """Testa se remove experimentos 'running' há mais de 30 minutos"""
        mock_db = MagicMock()
        mock_session.return_value = mock_db

        # Mock para experimentos antigos
        old_time = datetime.now(timezone.utc) - timedelta(minutes=45)
        stale_exp = MagicMock()
        stale_exp.status = 'running'
        stale_exp.created_at = old_time
        stale_exp.best_fitness = None

        mock_db.query.return_value.filter.return_value.delete.return_value = 1
        mock_db.query.return_value.filter.return_value.all.return_value = []
        mock_db.query.return_value.all.return_value = []

        result = manager.delete_failed_experiments()

        assert result is True

    @patch('src.controllers.experiment_manager.SessionLocal')
    def test_delete_failed_experiments_removes_null_fitness(self, mock_session, manager):
        """Testa se remove experimentos com best_fitness NULL"""
        mock_db = MagicMock()
        mock_session.return_value = mock_db

        null_exp = MagicMock()
        null_exp.best_fitness = None
        null_exp.status = 'completed'

        # Mock das queries
        mock_db.query.return_value.filter.return_value.delete.return_value = 0
        mock_db.query.return_value.filter.return_value.all.return_value = [null_exp]
        mock_db.query.return_value.all.return_value = []

        result = manager.delete_failed_experiments()

        assert result is True
        assert mock_db.delete.called

    @patch('src.controllers.experiment_manager.SessionLocal')
    def test_delete_failed_experiments_removes_nan_fitness(self, mock_session, manager):
        """Testa se remove experimentos com best_fitness NaN ou Inf"""
        mock_db = MagicMock()
        mock_session.return_value = mock_db

        nan_exp = MagicMock()
        nan_exp.best_fitness = float('nan')
        nan_exp.status = 'completed'

        inf_exp = MagicMock()
        inf_exp.best_fitness = float('inf')
        inf_exp.status = 'completed'

        # Mock das queries
        mock_db.query.return_value.filter.return_value.delete.return_value = 0
        mock_db.query.return_value.filter.return_value.all.return_value = []
        mock_db.query.return_value.all.return_value = [nan_exp, inf_exp]

        result = manager.delete_failed_experiments()

        assert result is True
        assert mock_db.delete.call_count >= 2  # Deletou pelo menos 2 experimentos

    @patch('src.controllers.experiment_manager.SessionLocal')
    def test_delete_failed_experiments_handles_errors(self, mock_session, manager):
        """Testa se trata erros corretamente com rollback"""
        mock_db = MagicMock()
        mock_session.return_value = mock_db

        # Simula erro no commit
        mock_db.commit.side_effect = Exception("Database error")
        mock_db.query.return_value.filter.return_value.delete.return_value = 0
        mock_db.query.return_value.filter.return_value.all.return_value = []
        mock_db.query.return_value.all.return_value = []

        result = manager.delete_failed_experiments()

        assert result is False
        assert mock_db.rollback.called

    @patch('src.controllers.experiment_manager.SessionLocal')
    def test_list_experiments_with_pagination(self, mock_session, manager):
        """Testa paginação na listagem de experimentos"""
        mock_db = MagicMock()
        mock_session.return_value = mock_db

        # Mock de experimentos
        mock_exp1 = MagicMock()
        mock_exp1.id = 1
        mock_exp1.status = 'completed'
        mock_exp1.best_fitness = 100.0
        mock_exp1.created_at = datetime.now(timezone.utc)

        mock_exp2 = MagicMock()
        mock_exp2.id = 2
        mock_exp2.status = 'completed'
        mock_exp2.best_fitness = 200.0
        mock_exp2.created_at = datetime.now(timezone.utc)

        # Setup do mock query chain
        mock_query = mock_db.query.return_value
        mock_order = mock_query.order_by.return_value
        mock_limit = mock_order.limit.return_value
        mock_offset = mock_limit.offset.return_value
        mock_offset.all.return_value = [mock_exp1, mock_exp2]

        result = manager.list_experiments(limit=10, offset=5)

        assert len(result) == 2
        assert result[0]['id'] == 1
        assert result[1]['id'] == 2
        # Verifica que limit e offset foram chamados
        mock_order.limit.assert_called_with(10)
        mock_limit.offset.assert_called_with(5)

    @patch('src.controllers.experiment_manager.SessionLocal')
    def test_count_experiments_all(self, mock_session, manager):
        """Testa contagem total de experimentos"""
        mock_db = MagicMock()
        mock_session.return_value = mock_db

        # Mock do count
        mock_query = mock_db.query.return_value
        mock_query.count.return_value = 469

        result = manager.count_experiments()

        assert result == 469
        mock_db.query.assert_called_once()

    @patch('src.controllers.experiment_manager.SessionLocal')
    def test_count_experiments_by_status(self, mock_session, manager):
        """Testa contagem de experimentos filtrado por status"""
        mock_db = MagicMock()
        mock_session.return_value = mock_db

        # Mock do count com filtro
        mock_query = mock_db.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.count.return_value = 450

        result = manager.count_experiments(status='completed')

        assert result == 450
        # Verifica que filter foi chamado
        mock_query.filter.assert_called_once()

    @patch('src.controllers.experiment_manager.SessionLocal')
    def test_get_statistics(self, mock_session, manager):
        """Testa obtenção de estatísticas globais"""
        mock_db = MagicMock()
        mock_session.return_value = mock_db

        # Mock dos queries de contagem
        mock_query = mock_db.query.return_value
        mock_query.count.return_value = 469

        # Mock do filter para status específico
        mock_filter = mock_query.filter.return_value
        mock_filter.count.side_effect = [469, 0, 0, 0]  # completed, failed, running, pending

        # Mock das agregações (min, avg)
        mock_entities = mock_filter.with_entities.return_value
        mock_entities.scalar.side_effect = [128.71, 4399.82, 644.0, 16.57]

        result = manager.get_statistics()

        assert result['total'] == 469
        assert result['completed'] == 469
        assert result['best_fitness'] == 128.71
        assert result['avg_fitness'] == 4399.82
        assert result['avg_generations'] == 644.0
        assert result['avg_execution_time'] == 16.57
