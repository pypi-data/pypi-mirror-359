from typing import List, Dict, Any, Optional
from .selector import BackendInfo


def format_backend_status(backend_info: BackendInfo) -> str:
    """
    Format backend status for display.
    
    Args:
        backend_info: BackendInfo object
        
    Returns:
        Formatted status string
    """
    
    if backend_info.simulator:
        return "🖥️  Simulator"
    elif backend_info.operational:
        return f"🟢 Online (Queue: {backend_info.pending_jobs})"
    else:
        return "🔴 Offline"


def get_backend_performance(backend_info: BackendInfo) -> Dict[str, Any]:
    """
    Calculate backend performance metrics.
    
    Args:
        backend_info: BackendInfo object
        
    Returns:
        Dictionary of performance metrics
    """
    
    # Simple scoring based on availability and queue
    if backend_info.simulator:
        score = 100  # Simulators always available
    elif not backend_info.operational:
        score = 0    # Offline backends unusable
    else:
        # Score based on queue length (lower is better)
        base_score = 100
        queue_penalty = min(backend_info.pending_jobs * 2, 80)  # Max 80% penalty
        score = max(base_score - queue_penalty, 20)  # Min 20% score
    
    return {
        'score': score,
        'operational': backend_info.operational,
        'queue_length': backend_info.pending_jobs,
        'qubits': backend_info.qubits,
        'type': 'simulator' if backend_info.simulator else 'hardware'
    }


def recommend_backend(backend_infos: List[BackendInfo], min_qubits: int = 1) -> Optional[BackendInfo]:
    """
    Recommend the best backend based on performance metrics.
    
    Args:
        backend_infos: List of BackendInfo objects
        min_qubits: Minimum number of qubits required
        
    Returns:
        Recommended BackendInfo or None if no suitable backend found
    """
    
    # Filter by minimum qubits
    suitable_backends = [b for b in backend_infos if b.qubits >= min_qubits]
    
    if not suitable_backends:
        return None
    
    # Score each backend
    scored_backends = []
    for backend in suitable_backends:
        performance = get_backend_performance(backend)
        scored_backends.append((backend, performance['score']))
    
    # Sort by score (highest first)
    scored_backends.sort(key=lambda x: x[1], reverse=True)
    
    return scored_backends[0][0] if scored_backends else None