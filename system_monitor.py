"""
JARVIS System Monitor Module
Provides real-time system monitoring and status reporting
"""

import psutil
import platform
import time
import threading
from datetime import datetime

class SystemMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.alerts = []
        self.monitoring = False
        
    def get_uptime(self):
        """Get system uptime"""
        uptime = time.time() - self.start_time
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        return f"{hours} hours, {minutes} minutes"
    
    def get_cpu_info(self):
        """Get detailed CPU information"""
        cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
        cpu_freq = psutil.cpu_freq()
        
        info = {
            'usage': sum(cpu_percent) / len(cpu_percent),
            'per_core': cpu_percent,
            'cores': psutil.cpu_count(),
            'frequency': cpu_freq.current if cpu_freq else 0
        }
        return info
    
    def get_memory_info(self):
        """Get detailed memory information"""
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        info = {
            'total': mem.total / (1024**3),  # GB
            'available': mem.available / (1024**3),
            'used': mem.used / (1024**3),
            'percent': mem.percent,
            'swap_total': swap.total / (1024**3),
            'swap_used': swap.used / (1024**3),
            'swap_percent': swap.percent
        }
        return info
    
    def get_disk_info(self):
        """Get disk information"""
        partitions = psutil.disk_partitions()
        disks = []
        
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disks.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total': usage.total / (1024**3),
                    'used': usage.used / (1024**3),
                    'free': usage.free / (1024**3),
                    'percent': usage.percent
                })
            except:
                pass
        
        return disks
    
    def get_network_info(self):
        """Get network information"""
        net_io = psutil.net_io_counters()
        
        info = {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv,
            'errin': net_io.errin,
            'errout': net_io.errout
        }
        return info
    
    def get_battery_info(self):
        """Get battery information"""
        battery = psutil.sensors_battery()
        
        if battery:
            return {
                'percent': battery.percent,
                'plugged': battery.power_plugged,
                'time_left': battery.secsleft if battery.secsleft > 0 else None
            }
        return None
    
    def get_processes(self, limit=10):
        """Get top processes by CPU usage"""
        processes = []
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append({
                    'pid': p.info['pid'],
                    'name': p.info['name'],
                    'cpu': p.info['cpu_percent'] or 0,
                    'memory': p.info['memory_percent'] or 0
                })
            except:
                pass
        
        # Sort by CPU and get top N
        processes.sort(key=lambda x: x['cpu'], reverse=True)
        return processes[:limit]
    
    def get_system_info(self):
        """Get comprehensive system information"""
        uname = platform.uname()
        
        info = {
            'system': uname.system,
            'node': uname.node,
            'release': uname.release,
            'version': uname.version,
            'machine': uname.machine,
            'processor': uname.processor,
            'uptime': self.get_uptime()
        }
        return info
    
    def get_full_status(self):
        """Get complete system status"""
        return {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'system': self.get_system_info(),
            'cpu': self.get_cpu_info(),
            'memory': self.get_memory_info(),
            'disks': self.get_disk_info(),
            'network': self.get_network_info(),
            'battery': self.get_battery_info()
        }
    
    def format_status_report(self):
        """Format status as JARVIS-style report"""
        status = self.get_full_status()
        
        report = "Sir, here is the system status report:\n\n"
        report += f"System: {status['system']['node']}\n"
        report += f"OS: {status['system']['system']} {status['system']['release']}\n"
        report += f"Uptime: {status['system']['uptime']}\n\n"
        
        report += f"CPU: {status['cpu']['usage']:.1f}% "
        report += f"({status['cpu']['cores']} cores)\n"
        
        report += f"Memory: {status['memory']['used']:.1f}GB / {status['memory']['total']:.1f}GB "
        report += f"({status['memory']['percent']:.1f}%)\n"
        
        if status['disks']:
            for disk in status['disks']:
                report += f"Disk {disk['mountpoint']}: {disk['used']:.1f}GB / {disk['total']:.1f}GB "
                report += f"({disk['percent']:.1f}%)\n"
        
        if status['battery']:
            bat = status['battery']
            report += f"Battery: {bat['percent']}%"
            if bat['plugged']:
                report += " (Charging)"
            report += "\n"
        
        return report
    
    def check_alerts(self):
        """Check for system alerts"""
        alerts = []
        
        # CPU alert
        cpu = psutil.cpu_percent(interval=1)
        if cpu > 90:
            alerts.append(f"WARNING: CPU usage at {cpu}%")
        
        # Memory alert
        mem = psutil.virtual_memory()
        if mem.percent > 90:
            alerts.append(f"WARNING: Memory usage at {mem.percent}%")
        
        # Disk alert
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                if usage.percent > 90:
                    alerts.append(f"WARNING: Disk {partition.mountpoint} at {usage.percent}%")
            except:
                pass
        
        # Battery alert
        battery = psutil.sensors_battery()
        if battery and not battery.power_plugged and battery.percent < 15:
            alerts.append(f"WARNING: Battery at {battery.percent}% - Please charge")
        
        return alerts
    
    def start_monitoring(self, interval=60):
        """Start background monitoring"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring = False
    
    def _monitor_loop(self, interval):
        """Background monitoring loop"""
        while self.monitoring:
            alerts = self.check_alerts()
            if alerts:
                self.alerts.extend(alerts)
            time.sleep(interval)


# Singleton instance
monitor = SystemMonitor()

# Convenience functions
def get_status():
    """Get quick status summary"""
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    return {
        'cpu': cpu,
        'memory': mem.percent,
        'battery': psutil.sensors_battery().percent if psutil.sensors_battery() else 100
    }

def format_short_status():
    """Get short status string"""
    status = get_status()
    battery = psutil.sensors_battery()
    bat_str = f" | Battery: {battery.percent}%" if battery else ""
    return f"CPU: {status['cpu']}% | Memory: {status['memory']}%{bat_str}"