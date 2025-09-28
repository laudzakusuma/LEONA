"""
Monitoring and analytics for LEONA
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time
from functools import wraps
from typing import Dict, Any, List
import json
import asyncio
from datetime import datetime, timedelta
import psutil
import GPUtil

# Prometheus metrics
request_count = Counter('leona_requests_total', 'Total requests', ['method', 'endpoint'])
response_time = Histogram('leona_response_duration_seconds', 'Response time', ['endpoint'])
active_users = Gauge('leona_active_users', 'Number of active users')
memory_usage = Gauge('leona_memory_usage_bytes', 'Memory usage in bytes')
cpu_usage = Gauge('leona_cpu_usage_percent', 'CPU usage percentage')
gpu_usage = Gauge('leona_gpu_usage_percent', 'GPU usage percentage')
model_inference_time = Histogram('leona_model_inference_seconds', 'Model inference time', ['model'])
agent_execution_time = Histogram('leona_agent_execution_seconds', 'Agent execution time', ['agent'])
websocket_connections = Gauge('leona_websocket_connections', 'Active WebSocket connections')
error_rate = Counter('leona_errors_total', 'Total errors', ['error_type'])

class PerformanceMonitor:
    """Monitor LEONA's performance and health"""
    
    def __init__(self):
        self.metrics = {}
        self.alerts = []
        self.thresholds = {
            'response_time': 2.0,  # seconds
            'memory_usage': 80,    # percent
            'cpu_usage': 90,        # percent
            'error_rate': 0.05      # 5% error rate
        }
        
        # Start monitoring background task
        asyncio.create_task(self._monitor_loop())
    
    def track_request(self, method: str, endpoint: str):
        """Track incoming request"""
        request_count.labels(method=method, endpoint=endpoint).inc()
    
    def track_response_time(self, endpoint: str, duration: float):
        """Track response time"""
        response_time.labels(endpoint=endpoint).observe(duration)
        
        # Check threshold
        if duration > self.thresholds['response_time']:
            self._create_alert('high_response_time', {
                'endpoint': endpoint,
                'duration': duration
            })
    
    def track_model_inference(self, model: str, duration: float):
        """Track model inference time"""
        model_inference_time.labels(model=model).observe(duration)
    
    def track_agent_execution(self, agent: str, duration: float):
        """Track agent execution time"""
        agent_execution_time.labels(agent=agent).observe(duration)
    
    def track_error(self, error_type: str):
        """Track errors"""
        error_rate.labels(error_type=error_type).inc()
    
    async def _monitor_loop(self):
        """Background monitoring loop"""
        while True:
            try:
                # Update system metrics
                self._update_system_metrics()
                
                # Check for anomalies
                await self._check_anomalies()
                
                # Clean old alerts
                self._clean_old_alerts()
                
                await asyncio.sleep(10)  # Monitor every 10 seconds
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                await asyncio.sleep(10)
    
    def _update_system_metrics(self):
        """Update system resource metrics"""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_usage.set(cpu_percent)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_usage.set(memory.used)
        
        # GPU usage (if available)
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu_percent = gpus[0].load * 100
                gpu_usage.set(gpu_percent)
        except:
            pass
        
        # Update internal metrics
        self.metrics['cpu'] = cpu_percent
        self.metrics['memory'] = memory.percent
        self.metrics['timestamp'] = datetime.now()
    
    async def _check_anomalies(self):
        """Check for performance anomalies"""
        
        # Check CPU usage
        if self.metrics.get('cpu', 0) > self.thresholds['cpu_usage']:
            self._create_alert('high_cpu_usage', {
                'usage': self.metrics['cpu']
            })
        
        # Check memory usage
        if self.metrics.get('memory', 0) > self.thresholds['memory_usage']:
            self._create_alert('high_memory_usage', {
                'usage': self.metrics['memory']
            })
    
    def _create_alert(self, alert_type: str, details: Dict[str, Any]):
        """Create performance alert"""
        alert = {
            'type': alert_type,
            'details': details,
            'timestamp': datetime.now(),
            'severity': self._get_severity(alert_type)
        }
        
        self.alerts.append(alert)
        
        # Log critical alerts
        if alert['severity'] == 'critical':
            print(f"🚨 CRITICAL ALERT: {alert_type} - {details}")
    
    def _get_severity(self, alert_type: str) -> str:
        """Determine alert severity"""
        critical_types = ['high_error_rate', 'system_failure']
        warning_types = ['high_cpu_usage', 'high_memory_usage', 'high_response_time']
        
        if alert_type in critical_types:
            return 'critical'
        elif alert_type in warning_types:
            return 'warning'
        else:
            return 'info'
    
    def _clean_old_alerts(self):
        """Remove alerts older than 24 hours"""
        cutoff = datetime.now() - timedelta(hours=24)
        self.alerts = [a for a in self.alerts if a['timestamp'] > cutoff]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status"""
        recent_alerts = [a for a in self.alerts 
                        if (datetime.now() - a['timestamp']).seconds < 300]
        
        if any(a['severity'] == 'critical' for a in recent_alerts):
            status = 'critical'
        elif any(a['severity'] == 'warning' for a in recent_alerts):
            status = 'degraded'
        else:
            status = 'healthy'
        
        return {
            'status': status,
            'metrics': self.metrics,
            'recent_alerts': recent_alerts,
            'uptime': self._get_uptime()
        }
    
    def _get_uptime(self) -> str:
        """Get system uptime"""
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        
        days = uptime.days
        hours = uptime.seconds // 3600
        minutes = (uptime.seconds % 3600) // 60
        
        return f"{days}d {hours}h {minutes}m"
    
    def get_metrics_export(self) -> bytes:
        """Export metrics in Prometheus format"""
        return generate_latest()

# Decorator for timing functions
def monitor_performance(endpoint: str = None):
    """Decorator to monitor function performance"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start
                
                if endpoint:
                    response_time.labels(endpoint=endpoint).observe(duration)
                
                return result
            except Exception as e:
                error_rate.labels(error_type=type(e).__name__).inc()
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start
                
                if endpoint:
                    response_time.labels(endpoint=endpoint).observe(duration)
                
                return result
            except Exception as e:
                error_rate.labels(error_type=type(e).__name__).inc()
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator