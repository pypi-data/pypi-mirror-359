"""
Utilitaire pour récupérer la fréquence CPU maximale de manière fiable sur différentes plateformes.
"""

import platform
import subprocess
import psutil
import re
from typing import Optional, Dict, Any, List
import os


def get_cpu_current_frequency() -> float:
    """
    Récupère la fréquence actuelle du CPU en MHz.
    
    Essaie plusieurs méthodes dans l'ordre:
    1. psutil (si disponible et fiable)
    2. Méthodes spécifiques au système d'exploitation
    
    Returns:
        Fréquence actuelle en MHz, ou 0 si impossible à déterminer
    """
    # Essayer psutil d'abord
    freq = _get_current_freq_from_psutil()
    if freq and freq > 0:
        return freq
    
    # Essayer les méthodes spécifiques à l'OS
    system = platform.system()
    
    if system == "Windows":
        freq = _get_current_freq_windows()
        if freq:
            return freq
    elif system == "Linux":
        freq = _get_current_freq_linux()
        if freq:
            return freq
    elif system == "Darwin":  # macOS
        freq = _get_current_freq_macos()
        if freq:
            return freq
    
    return 0.0


def _get_current_freq_from_psutil() -> Optional[float]:
    """Récupère la fréquence actuelle via psutil si disponible."""
    try:
        import psutil
        cpu_freq = psutil.cpu_freq()
        if cpu_freq and cpu_freq.current > 0:
            return cpu_freq.current
    except (ImportError, AttributeError):
        pass
    return None


def _get_current_freq_windows() -> Optional[float]:
    """Récupère la fréquence actuelle sur Windows."""
    # Méthode 1: PowerShell avec performance counters (plus précis)
    try:
        ps_command = r"""
        # Essayer les compteurs de performance
        try {
            $perfCounter = Get-Counter '\Processor Information(_Total)\% Processor Performance' -ErrorAction Stop
            $perfValue = $perfCounter.CounterSamples[0].CookedValue
            
            # Obtenir la fréquence max de base
            $cpu = Get-CimInstance Win32_Processor
            $maxSpeed = $cpu.MaxClockSpeed
            
            # Si on n'a pas la fréquence max, l'extraire du nom
            if (-not $maxSpeed -or $maxSpeed -eq 0 -or $maxSpeed -eq 2500) {
                $name = $cpu.Name
                if ($name -match '(\d+\.?\d*)\s*GHz') {
                    $maxSpeed = [int]([double]$matches[1] * 1000)
                }
            }
            
            # Calculer la fréquence actuelle
            if ($maxSpeed -gt 0) {
                $currentSpeed = [int](($perfValue / 100) * $maxSpeed)
                Write-Output $currentSpeed
            }
        } catch {
            # Fallback sur CurrentClockSpeed
            $cpu = Get-CimInstance Win32_Processor
            Write-Output $cpu.CurrentClockSpeed
        }
        """
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_command],
            capture_output=True,
            text=True,
            shell=True
        )
        if result.returncode == 0 and result.stdout.strip():
            mhz = float(result.stdout.strip())
            if mhz > 0:
                return mhz
    except (subprocess.SubprocessError, OSError, ValueError):
        pass
    
    # Méthode 2: wmic standard
    try:
        result = subprocess.run(
            ["wmic", "cpu", "get", "CurrentClockSpeed", "/value"],
            capture_output=True,
            text=True,
            shell=True
        )
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if line.startswith('CurrentClockSpeed='):
                    mhz = int(line.split('=')[1])
                    if mhz > 0:
                        return float(mhz)
    except (subprocess.SubprocessError, OSError, ValueError):
        pass
    
    # Méthode 3: Utiliser les compteurs de performance directement
    try:
        # typeperf pour obtenir le % de performance du processeur
        result = subprocess.run(
            ["typeperf", "-sc", "1", "\\Processor Information(_Total)\\% Processor Performance"],
            capture_output=True,
            text=True,
            shell=True
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if ',' in line and not line.startswith('"'):
                    parts = line.split(',')
                    if len(parts) >= 2:
                        try:
                            perf_percent = float(parts[1].strip('"'))
                            # Il nous faut la fréquence max pour calculer
                            max_freq = _get_freq_windows()
                            if max_freq:
                                return (perf_percent / 100.0) * max_freq
                        except ValueError:
                            pass
    except (subprocess.SubprocessError, OSError, ValueError):
        pass
    
    return None


def _get_current_freq_linux() -> Optional[float]:
    """Récupère la fréquence actuelle sur Linux."""
    # Méthode 1: /sys/devices/system/cpu/
    try:
        # Essayer scaling_cur_freq (fréquence actuelle)
        cpu_cur_freq_path = "/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq"
        if os.path.exists(cpu_cur_freq_path):
            with open(cpu_cur_freq_path, 'r') as f:
                khz = int(f.read().strip())
                return khz / 1000.0  # Convertir KHz en MHz
    except (OSError, IOError):
        pass
    
    # Méthode 2: /proc/cpuinfo (moyenne de tous les cœurs)
    try:
        with open('/proc/cpuinfo', 'r') as f:
            content = f.read()
            
            cpu_mhz_values = []
            for line in content.split('\n'):
                if line.startswith('cpu MHz'):
                    try:
                        mhz = float(line.split(':')[1].strip())
                        cpu_mhz_values.append(mhz)
                    except (IndexError, ValueError):
                        pass
            
            if cpu_mhz_values:
                # Retourner la moyenne
                return sum(cpu_mhz_values) / len(cpu_mhz_values)
    except (OSError, IOError):
        pass
    
    # Méthode 3: cpupower
    try:
        result = subprocess.run(
            ['cpupower', 'frequency-info', '-f'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            # Extraire la fréquence de la sortie
            for line in result.stdout.split('\n'):
                if 'current CPU frequency' in line:
                    # Format: "current CPU frequency is 2.40 GHz."
                    match = re.search(r'(\d+\.?\d*)\s*(MHz|GHz)', line)
                    if match:
                        value = float(match.group(1))
                        unit = match.group(2)
                        if unit == 'GHz':
                            return value * 1000.0
                        else:
                            return value
    except (subprocess.SubprocessError, OSError, ValueError):
        pass
    
    return None


def _get_current_freq_macos() -> Optional[float]:
    """Récupère la fréquence actuelle sur macOS."""
    try:
        # sysctl pour obtenir la fréquence actuelle
        result = subprocess.run(
            ['sysctl', '-n', 'hw.cpufrequency'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            hz = int(result.stdout.strip())
            return hz / 1_000_000.0  # Convertir Hz en MHz
    except (subprocess.SubprocessError, OSError, ValueError):
        pass
    
    # macOS moderne peut ne pas exposer la fréquence actuelle facilement
    # Utiliser powermetrics (nécessite sudo)
    try:
        result = subprocess.run(
            ['powermetrics', '-n', '1', '-i', '1', '--samplers', 'cpu_power'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            # Parser la sortie pour trouver la fréquence
            for line in result.stdout.split('\n'):
                if 'CPU Average frequency' in line:
                    match = re.search(r'(\d+)\s*MHz', line)
                    if match:
                        return float(match.group(1))
    except (subprocess.SubprocessError, OSError, ValueError):
        pass
    
    return None


def get_cpu_max_frequency() -> float:
    """
    Récupère la fréquence maximale du CPU en MHz.
    
    Essaie plusieurs méthodes dans l'ordre:
    1. psutil (si disponible et fiable)
    2. Méthodes spécifiques au système d'exploitation
    3. Extraction depuis le nom du processeur
    
    Returns:
        Fréquence maximale en MHz, ou 0 si impossible à déterminer
    """
    # Essayer psutil d'abord
    freq = _get_freq_from_psutil()
    if freq and freq != 2500:  # 2500 est souvent une valeur par défaut incorrecte
        return freq
    
    # Essayer les méthodes spécifiques à l'OS
    system = platform.system()
    
    if system == "Windows":
        freq = _get_freq_windows()
        if freq:
            return freq
    elif system == "Linux":
        freq = _get_freq_linux()
        if freq:
            return freq
    elif system == "Darwin":  # macOS
        freq = _get_freq_macos()
        if freq:
            return freq
    
    # En dernier recours, essayer d'extraire du nom du processeur
    freq = _get_freq_from_processor_name()
    if freq:
        return freq
    
    return 0.0


def _get_freq_from_psutil() -> Optional[float]:
    """Récupère la fréquence via psutil si disponible."""
    try:
        import psutil
        cpu_freq = psutil.cpu_freq()
        if cpu_freq and cpu_freq.max > 0:
            return cpu_freq.max
    except (ImportError, AttributeError):
        pass
    return None


def _get_freq_windows() -> Optional[float]:
    """Récupère la fréquence maximale sur Windows via WMI."""
    # Méthode 1: PowerShell avec CIM (plus moderne et fiable)
    try:
        ps_command = r"""
        $cpu = Get-CimInstance -ClassName Win32_Processor
        $maxSpeed = $cpu.MaxClockSpeed
        if ($maxSpeed) { 
            Write-Output $maxSpeed 
        } else {
            # Essayer d'extraire depuis le nom
            $name = $cpu.Name
            if ($name -match '(\d+\.?\d*)\s*GHz') {
                $ghz = [double]$matches[1]
                Write-Output ([int]($ghz * 1000))
            } elseif ($name -match '(\d+)\s*MHz') {
                Write-Output $matches[1]
            }
        }
        """
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_command],
            capture_output=True,
            text=True,
            shell=True
        )
        if result.returncode == 0 and result.stdout.strip():
            mhz = float(result.stdout.strip())
            if mhz > 0 and mhz != 2500:  # Ignorer la valeur par défaut
                return mhz
    except (subprocess.SubprocessError, OSError, ValueError):
        pass
    
    # Méthode 2: wmic avec extraction du nom si nécessaire
    try:
        result = subprocess.run(
            ["wmic", "cpu", "get", "Name,MaxClockSpeed", "/value"],
            capture_output=True,
            text=True,
            shell=True
        )
        if result.returncode == 0:
            max_speed = None
            cpu_name = None
            
            for line in result.stdout.strip().split('\n'):
                if line.startswith('MaxClockSpeed='):
                    try:
                        max_speed = int(line.split('=')[1])
                    except (ValueError, IndexError):
                        pass
                elif line.startswith('Name='):
                    cpu_name = line.split('=', 1)[1]
            
            # Si on a une fréquence valide et différente de 2500
            if max_speed and max_speed > 0 and max_speed != 2500:
                return float(max_speed)
            
            # Sinon, extraire du nom
            if cpu_name:
                match = re.search(r'(\d+\.?\d*)\s*GHz', cpu_name, re.IGNORECASE)
                if match:
                    return float(match.group(1)) * 1000
                match = re.search(r'(\d+)\s*MHz', cpu_name, re.IGNORECASE)
                if match:
                    return float(match.group(1))
    except (subprocess.SubprocessError, OSError, ValueError):
        pass
    
    # Méthode 3: Registre Windows
    if platform.system() == "Windows":
        try:
            import winreg
            key_path = r"HARDWARE\DESCRIPTION\System\CentralProcessor\0"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                mhz, _ = winreg.QueryValueEx(key, "~MHz")
                if mhz > 0:
                    return float(mhz)
        except (ImportError, OSError, WindowsError):
            pass
    
    return None


def _get_freq_linux() -> Optional[float]:
    """Récupère la fréquence maximale sur Linux."""
    # Méthode 1: /sys/devices/system/cpu/
    try:
        # Essayer cpuinfo_max_freq d'abord (plus précis)
        cpu_max_freq_path = "/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq"
        if os.path.exists(cpu_max_freq_path):
            with open(cpu_max_freq_path, 'r') as f:
                khz = int(f.read().strip())
                return khz / 1000.0  # Convertir KHz en MHz
    except (OSError, IOError):
        pass
    
    # Méthode 2: /proc/cpuinfo
    try:
        with open('/proc/cpuinfo', 'r') as f:
            content = f.read()
            
            # Chercher "cpu MHz" max
            cpu_mhz_values = []
            for line in content.split('\n'):
                if line.startswith('cpu MHz'):
                    try:
                        mhz = float(line.split(':')[1].strip())
                        cpu_mhz_values.append(mhz)
                    except (IndexError, ValueError):
                        pass
            
            if cpu_mhz_values:
                return max(cpu_mhz_values)
    except (OSError, IOError):
        pass
    
    # Méthode 3: lscpu
    try:
        result = subprocess.run(['lscpu'], capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'CPU max MHz:' in line:
                    mhz = float(line.split(':')[1].strip())
                    return mhz
                elif 'CPU MHz:' in line and 'max' not in line:
                    # Fallback si pas de max MHz
                    mhz = float(line.split(':')[1].strip())
                    if mhz > 0:
                        return mhz
    except (subprocess.SubprocessError, OSError, ValueError):
        pass
    
    return None


def _get_freq_macos() -> Optional[float]:
    """Récupère la fréquence maximale sur macOS."""
    try:
        # sysctl pour obtenir la fréquence
        result = subprocess.run(
            ['sysctl', '-n', 'hw.cpufrequency_max'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            hz = int(result.stdout.strip())
            return hz / 1_000_000.0  # Convertir Hz en MHz
    except (subprocess.SubprocessError, OSError, ValueError):
        pass
    
    try:
        # Alternative: sysctl hw.cpufrequency
        result = subprocess.run(
            ['sysctl', '-n', 'hw.cpufrequency'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            hz = int(result.stdout.strip())
            return hz / 1_000_000.0
    except (subprocess.SubprocessError, OSError, ValueError):
        pass
    
    return None


def _get_freq_from_processor_name() -> Optional[float]:
    """Extrait la fréquence du nom du processeur."""
    try:
        processor_name = platform.processor()
        if not processor_name:
            return None
        
        # Patterns pour extraire la fréquence
        # Ex: "Intel(R) Core(TM) i7-8700K CPU @ 3.70GHz"
        #     "AMD Ryzen 9 5900X 12-Core Processor @ 3.7GHz"
        patterns = [
            r'@\s*(\d+\.?\d*)\s*GHz',  # @ 3.70GHz
            r'(\d+\.?\d*)\s*GHz',       # 3.70GHz n'importe où
            r'@\s*(\d+)\s*MHz',         # @ 3700MHz
            r'(\d+)\s*MHz'              # 3700MHz n'importe où
        ]
        
        for pattern in patterns:
            match = re.search(pattern, processor_name, re.IGNORECASE)
            if match:
                value = float(match.group(1))
                # Si c'est en GHz, convertir en MHz
                if 'ghz' in pattern.lower():
                    return value * 1000.0
                else:
                    return value
    except (AttributeError, ValueError):
        pass
    
    return None


def get_cpu_frequencies_per_core() -> List[float]:
    """
    Récupère les fréquences actuelles par cœur CPU.
    
    Returns:
        Liste des fréquences en MHz pour chaque cœur, ou liste vide si non disponible
    """
    frequencies = []
    
    # Essayer psutil d'abord
    try:
        import psutil
        per_cpu_freq = psutil.cpu_freq(percpu=True)
        if per_cpu_freq:
            return [freq.current for freq in per_cpu_freq if freq.current > 0]
    except (ImportError, AttributeError):
        pass
    
    system = platform.system()
    
    if system == "Linux":
        # Lire depuis /sys/devices/system/cpu/
        cpu_count = os.cpu_count() or 0
        for i in range(cpu_count):
            try:
                freq_path = f"/sys/devices/system/cpu/cpu{i}/cpufreq/scaling_cur_freq"
                if os.path.exists(freq_path):
                    with open(freq_path, 'r') as f:
                        khz = int(f.read().strip())
                        frequencies.append(khz / 1000.0)  # KHz vers MHz
            except (OSError, IOError):
                continue
        
        # Alternative: /proc/cpuinfo
        if not frequencies:
            try:
                with open('/proc/cpuinfo', 'r') as f:
                    for line in f:
                        if line.startswith('cpu MHz'):
                            try:
                                mhz = float(line.split(':')[1].strip())
                                frequencies.append(mhz)
                            except (IndexError, ValueError):
                                pass
            except (OSError, IOError):
                pass
    
    return frequencies


def get_cpu_info() -> Dict[str, Any]:
    """
    Récupère des informations détaillées sur le CPU.
    
    Returns:
        Dictionnaire contenant les informations CPU
    """
    info = {
        "max_frequency": get_cpu_max_frequency(),
        "processor_name": platform.processor() or "Unknown",
        "architecture": platform.machine() or "Unknown",
        "system": platform.system()
    }
    
    # Ajouter le nombre de cœurs si psutil est disponible
    try:
        info["physical_cores"] = psutil.cpu_count(logical=False)
        info["logical_cores"] = psutil.cpu_count(logical=True)
    except ImportError:
        pass
    
    return info