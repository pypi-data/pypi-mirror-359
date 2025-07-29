from typing import Optional, Tuple, List, Dict, Any
from dataclasses import dataclass
from qiskit_ibm_runtime import QiskitRuntimeService


@dataclass
class BackendInfo:
    """Information about an IBM Quantum backend."""
    
    backend: Any
    name: str
    qubits: int
    operational: bool
    pending_jobs: int
    simulator: bool
    processor_type: Optional[str] = None
    backend_version: Optional[str] = None
    coupling_map_size: Optional[int] = None


def list_and_select_backend() -> Tuple[Optional[QiskitRuntimeService], Optional[Any]]:
    """
    List available IBM Quantum backends and let user select one.
    
    Returns:
        Tuple of (service, backend) or (None, None) if failed/cancelled
    """
    
    print("\n🚀 Connecting to IBM Quantum...")
    
    try:
        service = QiskitRuntimeService()
        print("✅ Service connection established")
        
        # Get available backends
        backends = service.backends()
        print(f"📡 Available backends: {len(backends)} found\n")
        
        # Parse backend information
        backend_infos = _parse_backends(backends)
        real_backends = [b for b in backend_infos if not b.simulator]
        simulators = [b for b in backend_infos if b.simulator]
        
        # Display options
        _display_backends(real_backends, simulators)
        
        # User selection
        selected_backend = _get_user_selection(real_backends + simulators)
        
        if selected_backend:
            return service, selected_backend.backend
        else:
            return None, None
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        print("💡 Make sure to authenticate first:")
        print("   QiskitRuntimeService.save_account(token='your_token_here')")
        return None, None


def _parse_backends(backends) -> List[BackendInfo]:
    """Parse backend list into BackendInfo objects."""
    
    backend_infos = []
    
    for backend in backends:
        try:
            config = backend.configuration()
            status = backend.status()
            
            # Extract coupling map size
            coupling_size = None
            if hasattr(config, 'coupling_map') and config.coupling_map:
                coupling_size = len(config.coupling_map)
            
            backend_info = BackendInfo(
                backend=backend,
                name=backend.name,
                qubits=getattr(config, 'n_qubits', 0),
                operational=getattr(status, 'operational', True),
                pending_jobs=getattr(status, 'pending_jobs', 0),
                simulator=backend.name.startswith('simulator') or 'simulator' in backend.name.lower(),
                processor_type=getattr(config, 'processor_type', None),
                backend_version=getattr(config, 'backend_version', None),
                coupling_map_size=coupling_size
            )
            
            backend_infos.append(backend_info)
            
        except Exception:
            # Skip backends we can't query
            continue
    
    return backend_infos


def _display_backends(real_backends: List[BackendInfo], simulators: List[BackendInfo]) -> None:
    """Display formatted backend lists."""
    
    # Display real quantum computers
    print("🔬 REAL QUANTUM COMPUTERS:")
    print("-" * 50)
    
    for i, info in enumerate(real_backends):
        status_emoji = "🟢" if info.operational else "🔴"
        queue_info = f"Queue: {info.pending_jobs}" if info.operational else "OFFLINE"
        print(f"{i+1:2d}. {info.name:<20} {info.qubits:>3} qubits  {status_emoji} {queue_info}")
    
    # Display simulators
    if simulators:
        print(f"\n🖥️  SIMULATORS:")
        print("-" * 50)
        sim_start_idx = len(real_backends)
        for i, info in enumerate(simulators):
            idx = sim_start_idx + i + 1
            print(f"{idx:2d}. {info.name:<20} {info.qubits:>3} qubits  🖥️  Simulator")


def _get_user_selection(all_backends: List[BackendInfo]) -> Optional[BackendInfo]:
    """Handle user selection interface."""
    
    print("\n" + "="*60)
    
    while True:
        try:
            choice = input(f"👆 Select backend (1-{len(all_backends)}) or 'q' to quit: ").strip()
            
            if choice.lower() in ['exit', 'quit', 'q']:
                print("👋 Selection cancelled")
                return None
                
            choice_idx = int(choice) - 1
            
            if 0 <= choice_idx < len(all_backends):
                selected = all_backends[choice_idx]
                
                # Show selection details
                print(f"\n🎯 Selected: {selected.name}")
                print(f"   📊 Qubits: {selected.qubits}")
                print(f"   🔄 Status: {'Operational' if selected.operational else 'Offline'}")
                if selected.operational and not selected.simulator:
                    print(f"   ⏳ Queue: {selected.pending_jobs} jobs")
                
                # Warn if offline
                if not selected.operational:
                    confirm = input("⚠️  Backend is offline. Continue anyway? (y/n): ")
                    if confirm.lower() != 'y':
                        continue
                
                return selected
            else:
                print(f"❌ Please enter a number between 1 and {len(all_backends)}")
                
        except ValueError:
            print("❌ Please enter a valid number")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            return None


def get_backend_details(backend) -> bool:
    """
    Display detailed information about a selected backend.
    
    Args:
        backend: IBM Quantum backend object
        
    Returns:
        True if details were successfully retrieved, False otherwise
    """
    
    try:
        config = backend.configuration()
        status = backend.status()
        
        print(f"\n📋 BACKEND DETAILS:")
        print(f"   🏷️  Name: {backend.name}")
        print(f"   🔬 Qubits: {config.n_qubits}")
        print(f"   🔄 Status: {'Operational' if status.operational else 'Offline'}")
        
        if hasattr(status, 'pending_jobs'):
            print(f"   ⏳ Queue: {status.pending_jobs} jobs")
            
        if hasattr(config, 'processor_type'):
            print(f"   ⚙️  Type: {config.processor_type}")
            
        if hasattr(config, 'backend_version'):
            print(f"   🔖 Version: {config.backend_version}")
            
        # Show coupling map size if available
        if hasattr(config, 'coupling_map') and config.coupling_map:
            print(f"   🔗 Connections: {len(config.coupling_map)} edges")
            
        return True
        
    except Exception as e:
        print(f"   ⚠️  Could not get detailed info: {e}")
        return False


def check_authentication() -> bool:
    """
    Quick check if IBM Quantum authentication is working.
    
    Returns:
        True if authentication is working, False otherwise
    """
    
    try:
        service = QiskitRuntimeService()
        backends = service.backends()
        print(f"✅ Authentication working - {len(backends)} backends available")
        return True
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        setup_authentication()
        return False


def setup_authentication() -> None:
    """Guide user through IBM Quantum authentication setup."""
    
    print("🔐 IBM QUANTUM AUTHENTICATION SETUP")
    print("="*50)
    print("1. Go to: https://quantum-computing.ibm.com/")
    print("2. Log in to your IBM Quantum account")
    print("3. Go to Account Settings")
    print("4. Copy your API token")
    print("5. Run this command:")
    print("   from qiskit_ibm_runtime import QiskitRuntimeService")
    print("   QiskitRuntimeService.save_account(token='paste_your_token_here')")
    print("\nThen run your experiment again!")