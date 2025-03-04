import psutil
import platform
from datetime import datetime

class SystemMonitor:
    def get_metrics(self):
        """Get current system metrics."""
        # Get process information
        process_count = len(psutil.pids())
        thread_count = 0
        
        # Count threads across all processes
        for proc in psutil.process_iter(['pid', 'num_threads']):
            try:
                # Check if num_threads is in proc.info and is not None
                if 'num_threads' in proc.info and proc.info['num_threads'] is not None:
                    thread_count += proc.info['num_threads']
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        return {
            'timestamp': datetime.now().isoformat(),
            'cpu': {
                'usage_percent': psutil.cpu_percent(interval=1),
                'cores': psutil.cpu_count(),
                'frequency': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
            },
            'memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'percent': psutil.virtual_memory().percent
            },
            'disk': {
                'total': psutil.disk_usage('/').total,
                'used': psutil.disk_usage('/').used,
                'free': psutil.disk_usage('/').free,
                'percent': psutil.disk_usage('/').percent
            },
            'processes': {
                'count': process_count,
                'threads': thread_count
            },
            'system_info': {
                'system': platform.system(),
                'platform': platform.platform(),
                'processor': platform.processor()
            }
        } 