from datetime import datetime
from typing import Any

class TaskValidationError(Exception):
    """Exceção customizada para erros de validação nas tarefas."""
    pass

def parse_datetime(date_str: str) -> datetime:
    """Converte string ISO para objeto datetime."""
    try:
        
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except ValueError:
        raise ValueError(f"Formato de data inválido: {date_str}")

def task_analyzer(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    """Processa uma lista de tarefas e calcula métricas consolidadas."""
    total_tasks = len(tasks)
    completed_tasks = 0
    pending_tasks = 0
    delayed_tasks = 0
    
    total_hours = 0.0
    priority_hours = {"Alta": 0.0, "Média": 0.0, "Baixa": 0.0}
    priority_counts = {"Alta": 0, "Média": 0, "Baixa": 0}

    for task in tasks:
        # Contagem de status
        if task["status"] == "Concluída":
            completed_tasks += 1
            
            # Validação cronológica (Regra de Negócio Exigida)
            created_at = parse_datetime(task["data_criacao"])
            completed_at = parse_datetime(task["data_conclusao"])
            
            if completed_at < created_at:
                raise TaskValidationError(
                    f"Inconsistência cronológica no ID {task['id']}: "
                    f"Conclusão ({completed_at}) anterior à criação ({created_at})."
                )
            
           
            duration = (completed_at - created_at).total_seconds() / 3600
            total_hours += duration
            
            priority = task.get("prioridade", "Baixa")
            if priority in priority_hours:
                priority_hours[priority] += duration
                priority_counts[priority] += 1
                
        elif task["status"] == "Pendente":
            pending_tasks += 1
            
        
        if "data_prevista" in task:
            due_date = parse_datetime(task["data_prevista"])
            current_date = parse_datetime(task.get("data_conclusao")) if task["status"] == "Concluída" else datetime.now()
            # Se tem timezone, tornamos o datetime.now() compatível. Para simplificar no Colab, checamos datas tz-naive.
            if current_date.tzinfo is None and due_date.tzinfo is not None:
                current_date = current_date.astimezone()
                
            if current_date > due_date:
                delayed_tasks += 1

    
    avg_total_time = total_hours / completed_tasks if completed_tasks > 0 else 0.0
    avg_priority_time = {
        p: (priority_hours[p] / priority_counts[p] if priority_counts[p] > 0 else 0.0)
        for p in priority_hours
    }
    delay_rate = (delayed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0

    return {
        "total_tarefas": total_tasks,
        "concluidas": completed_tasks,
        "pendentes": pending_tasks,
        "tempo_medio_horas": round(avg_total_time, 2),
        "tempo_medio_prioridade": {k: round(v, 2) for k, v in avg_priority_time.items()},
        "taxa_atraso_percentual": round(delay_rate, 2)
    }