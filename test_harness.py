import pytest
from task_analyzer import task_analyzer, TaskValidationError


def test_cenario_sucesso_calculo_metricas():
    tasks = [
        {
            "id": 101, "status": "Concluída", "prioridade": "Alta",
            "data_criacao": "2026-03-01T08:00:00",
            "data_conclusao": "2026-03-01T11:00:00", # 3 horas
            "data_prevista": "2026-03-01T12:00:00"
        },
        {
            "id": 102, "status": "Concluída", "prioridade": "Baixa",
            "data_criacao": "2026-03-01T08:00:00",
            "data_conclusao": "2026-03-01T14:00:00", # 6 horas
            "data_prevista": "2026-03-01T10:00:00"
        }
    ]
    result = task_analyzer(tasks)
    assert result["total_tarefas"] == 2
    assert result["concluidas"] == 2
    assert result["tempo_medio_horas"] == 4.5
    assert result["tempo_medio_prioridade"]["Alta"] == 3.0
    assert result["tempo_medio_prioridade"]["Baixa"] == 6.0


def test_cenario_excecao_datas_inconsistentes():
    tasks = [
        {
            "id": 999, "status": "Concluída", "prioridade": "Alta",
            "data_criacao": "2026-03-01T12:00:00",
            "data_conclusao": "2026-03-01T08:00:00" # Erro: Conclusão antes da criação
        }
    ]
    with pytest.raises(TaskValidationError) as excinfo:
        task_analyzer(tasks)
    assert "Inconsistência cronológica no ID 999" in str(excinfo.value)

# Cenário 3: Caso de Borda - Entrada Vazia
def test_caso_borda_entrada_vazia():
    result = task_analyzer([])
    assert result["total_tarefas"] == 0
    assert result["concluidas"] == 0
    assert result["tempo_medio_horas"] == 0.0


def test_caso_borda_apenas_pendentes():
    tasks = [
        {
            "id": 201, "status": "Pendente", "prioridade": "Alta",
            "data_criacao": "2026-03-01T08:00:00",
            "data_prevista": "2026-03-02T18:00:00"
        }
    ]
    result = task_analyzer(tasks)
    assert result["total_tarefas"] == 1
    assert result["pendentes"] == 1
    assert result["concluidas"] == 0
    assert result["tempo_medio_horas"] == 0.0