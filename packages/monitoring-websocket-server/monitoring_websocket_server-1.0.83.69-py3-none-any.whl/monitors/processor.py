"""
Moniteur de processeur système.
Surveillance de l'utilisation du CPU et de ses caractéristiques.
"""

import logging
import time
from typing import Optional, List, Tuple, Dict, Any

import psutil

from .base import BaseMonitor
from ..core.models import ProcessorInfo
from ..core.exceptions import InvalidIntervalError

# Import de notre utilitaire de fréquence CPU
try:
    from ..utils.cpu_freq import get_cpu_max_frequency, get_cpu_current_frequency
except ImportError:
    get_cpu_max_frequency = None
    get_cpu_current_frequency = None


class ProcessorMonitor(BaseMonitor):
    """Moniteur pour surveiller l'utilisation du processeur."""

    def __init__(self, interval: float = 0.05) -> None:
        """Initialiser le moniteur de processeur.

        Args:
            interval: Intervalle de mesure en secondes.
        """
        super().__init__("Processor")
        self._interval: float = self._validate_interval(interval)
        self._last_check: Optional[ProcessorInfo] = None
        self._logger = logging.getLogger(__name__)
        
        # Variables pour la mesure non-bloquante du CPU
        self._last_cpu_times: Optional[Any] = None
        self._last_cpu_check_time: Optional[float] = None
        self._last_per_cpu_times: Optional[List[Any]] = None
        
        # Liste des attributs CPU pour éviter l'utilisation de dir()
        self._cpu_time_attrs: List[str] = ['user', 'nice', 'system', 'idle', 'iowait', 
                                            'irq', 'softirq', 'steal', 'guest', 'guest_nice']

    @property
    def interval(self) -> float:
        """Retourner l'intervalle de mesure.

        Returns:
            Intervalle en secondes.
        """
        return self._interval

    @interval.setter
    def interval(self, new_interval: float) -> None:
        """Définir l'intervalle de mesure.

        Args:
            new_interval: Nouvel intervalle en secondes.

        Raises:
            InvalidIntervalError: Si l'intervalle est invalide.
        """
        self._interval = self._validate_interval(new_interval)

    @property
    def last_check(self) -> Optional[ProcessorInfo]:
        """Retourner les dernières informations processeur récupérées.

        Returns:
            Dernières informations processeur ou None.
        """
        return self._last_check

    @staticmethod
    def _validate_interval(interval: float) -> float:
        """Valider l'intervalle de mesure.

        Args:
            interval: Intervalle à valider.

        Returns:
            Intervalle validé.

        Raises:
            InvalidIntervalError: Si l'intervalle est invalide.
        """
        if interval <= 0:
            raise InvalidIntervalError("L'intervalle doit être positif")
        if interval > 10.0:
            raise InvalidIntervalError("L'intervalle ne doit pas dépasser 10 secondes")
        return interval

    def _do_initialize(self) -> None:
        """Initialiser le moniteur de processeur.

        Raises:
            Exception: Si psutil n'est pas disponible.
        """
        try:
            # Test des fonctionnalités CPU
            psutil.cpu_count()
            
            # Initialiser la mesure non-bloquante du CPU
            # Premier appel pour initialiser les valeurs de référence
            psutil.cpu_percent(interval=None)
            psutil.cpu_percent(interval=None, percpu=True)
            
            # Stocker les temps CPU initiaux pour le calcul manuel
            self._last_cpu_times = psutil.cpu_times()
            self._last_per_cpu_times = psutil.cpu_times(percpu=True)
            self._last_cpu_check_time = time.time()
            
        except Exception as e:
            raise Exception(f"Impossible d'accéder aux informations processeur: {e}")

    def _collect_data(self) -> ProcessorInfo:
        """Collecter les informations actuelles sur le processeur.

        Returns:
            Informations détaillées sur le processeur.

        Raises:
            Exception: En cas d'erreur de collecte.
        """
        current_time = time.time()

        try:
            # Utilisation CPU non-bloquante
            if self._last_cpu_check_time is None:
                # Première mesure, utiliser psutil sans intervalle
                per_core_usage = psutil.cpu_percent(interval=None, percpu=True)
                cpu_percent = psutil.cpu_percent(interval=None)
                
                # Si les valeurs sont nulles (première mesure), utiliser un fallback rapide
                if cpu_percent == 0:
                    # Utiliser une mesure avec un intervalle très court comme fallback
                    cpu_percent = psutil.cpu_percent(interval=0.01)
                    per_core_usage = psutil.cpu_percent(interval=0.01, percpu=True)
                
                # Initialiser les temps de référence
                self._last_cpu_times = psutil.cpu_times()
                self._last_per_cpu_times = psutil.cpu_times(percpu=True)
                self._last_cpu_check_time = current_time
            else:
                # Utiliser psutil sans intervalle (non-bloquant)
                cpu_percent = psutil.cpu_percent(interval=None)
                per_core_usage = psutil.cpu_percent(interval=None, percpu=True)
                
                # Si psutil retourne 0 (pas assez de temps écoulé), calculer manuellement
                if cpu_percent == 0 or not per_core_usage or all(v == 0 for v in per_core_usage):
                    per_core_usage = self._calculate_cpu_percent_manual(percpu=True)
                    cpu_percent = self._calculate_cpu_percent_manual(percpu=False)
                
                # Mettre à jour les temps de référence
                self._last_cpu_times = psutil.cpu_times()
                self._last_per_cpu_times = psutil.cpu_times(percpu=True)
                self._last_cpu_check_time = current_time

            # Information CPU
            core_count = psutil.cpu_count(logical=False) or 0
            logical_count = psutil.cpu_count(logical=True) or 0

            # Fréquences CPU
            try:
                freq_info = psutil.cpu_freq()
                freq_current = freq_info.current if freq_info else 0.0
                freq_max = freq_info.max if freq_info else 0.0
                
                # Utiliser notre fonction améliorée pour la fréquence max si nécessaire
                if get_cpu_max_frequency and (freq_max == 2500 or freq_max == 0 or freq_max is None):
                    better_freq = get_cpu_max_frequency()
                    if better_freq > 0:
                        freq_max = better_freq
                
                # Utiliser notre fonction améliorée pour la fréquence actuelle si nécessaire
                if get_cpu_current_frequency and (freq_current == 0 or freq_current is None):
                    better_current = get_cpu_current_frequency()
                    if better_current > 0:
                        freq_current = better_current
                        
            except (AttributeError, OSError):
                freq_current = 0.0
                freq_max = 0.0

        except Exception as e:
            raise Exception(f"Erreur lors de la récupération des données processeur: {e}")

        proc_info = ProcessorInfo(
            usage_percent=cpu_percent,
            core_count=core_count,
            logical_count=logical_count,
            frequency_current=float(freq_current) if freq_current is not None else 0.0,
            frequency_max=float(freq_max) if freq_max is not None else 0.0,
            per_core_usage=per_core_usage,
            timestamp=current_time
        )

        self._last_check = proc_info
        return proc_info

    def get_processor_info(self) -> ProcessorInfo:
        """Récupérer les informations actuelles sur le processeur.

        Méthode publique pour compatibilité avec l'ancien code.

        Returns:
            Informations détaillées sur le processeur.
        """
        return self.get_data()

    def get_usage_percentage(self) -> float:
        """Récupérer uniquement le pourcentage d'utilisation CPU.

        Returns:
            Pourcentage d'utilisation.
        """
        processor_info = self.get_data()
        return processor_info.usage_percent

    def get_core_usage(self) -> List[float]:
        """Récupérer l'utilisation par cœur.

        Returns:
            Liste des pourcentages par cœur.
        """
        processor_info = self.get_data()
        return processor_info.per_core_usage

    def get_core_count(self) -> int:
        """Récupérer le nombre de cœurs physiques.

        Returns:
            Nombre de cœurs physiques.
        """
        processor_info = self.get_data()
        return processor_info.core_count

    def get_logical_count(self) -> int:
        """Récupérer le nombre de processeurs logiques.

        Returns:
            Nombre de processeurs logiques.
        """
        processor_info = self.get_data()
        return processor_info.logical_count

    def get_frequency_info(self) -> Tuple[float, float]:
        """Récupérer les informations de fréquence.

        Returns:
            Tuple contenant (fréquence actuelle, fréquence maximale).
        """
        processor_info = self.get_data()
        return processor_info.frequency_current, processor_info.frequency_max

    def is_cpu_critical(self, threshold: float = 95.0) -> bool:
        """Vérifier si l'utilisation CPU est critique.

        Args:
            threshold: Seuil critique en pourcentage.

        Returns:
            True si critique.
        """
        return self.get_usage_percentage() > threshold

    def is_cpu_warning(self, threshold: float = 80.0) -> bool:
        """Vérifier si l'utilisation CPU nécessite une alerte.

        Args:
            threshold: Seuil d'alerte en pourcentage.

        Returns:
            True si alerte nécessaire.
        """
        return self.get_usage_percentage() > threshold

    def get_load_distribution(self) -> Dict[str, Any]:
        """Analyser la distribution de la charge sur les cœurs.

        Returns:
            Statistiques de distribution de charge.
        """
        core_usage = self.get_core_usage()
        
        return {
            "min_usage": min(core_usage),
            "max_usage": max(core_usage),
            "avg_usage": sum(core_usage) / len(core_usage),
            "std_deviation": self._calculate_std_dev(core_usage),
            "balanced": max(core_usage) - min(core_usage) < 20.0  # Seuil d'équilibre
        }

    @staticmethod
    def _calculate_std_dev(values: List[float]) -> float:
        """Calculer l'écart-type d'une liste de valeurs.

        Args:
            values: Liste de valeurs.

        Returns:
            Écart-type.
        """
        if not values:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5

    def _calculate_cpu_percent_manual(self, percpu: bool = False) -> Any:
        """Calculer manuellement le pourcentage CPU basé sur les temps CPU.

        Args:
            percpu: Si True, retourne les pourcentages par CPU.

        Returns:
            Pourcentage(s) d'utilisation CPU.
        """
        try:
            if percpu:
                current_times = psutil.cpu_times(percpu=True)
                if not self._last_per_cpu_times:
                    return [0.0] * len(current_times)
                
                percents = []
                for i, (current, last) in enumerate(zip(current_times, self._last_per_cpu_times)):
                    # Calculer le delta total en utilisant la liste pré-définie
                    total_delta = 0
                    idle_delta = 0
                    
                    for attr in self._cpu_time_attrs:
                        if hasattr(current, attr) and hasattr(last, attr):
                            try:
                                current_val = getattr(current, attr)
                                last_val = getattr(last, attr)
                                delta = current_val - last_val
                                total_delta += delta
                                if attr == 'idle':
                                    idle_delta = delta
                            except (AttributeError, TypeError):
                                continue
                    
                    if total_delta <= 0:
                        percents.append(0.0)
                    else:
                        busy_delta = total_delta - idle_delta
                        percents.append(min(100.0, max(0.0, (busy_delta / total_delta) * 100)))
                
                return percents
            else:
                current_times = psutil.cpu_times()
                if not self._last_cpu_times:
                    return 0.0
                
                # Calculer le delta total en utilisant la liste pré-définie
                total_delta = 0
                idle_delta = 0
                
                for attr in self._cpu_time_attrs:
                    if hasattr(current_times, attr) and hasattr(self._last_cpu_times, attr):
                        try:
                            current_val = getattr(current_times, attr)
                            last_val = getattr(self._last_cpu_times, attr)
                            delta = current_val - last_val
                            total_delta += delta
                            if attr == 'idle':
                                idle_delta = delta
                        except (AttributeError, TypeError):
                            continue
                
                if total_delta <= 0:
                    return 0.0
                
                busy_delta = total_delta - idle_delta
                return min(100.0, max(0.0, (busy_delta / total_delta) * 100))
                
        except (AttributeError, ZeroDivisionError, TypeError, ValueError) as e:
            # En cas d'erreur, retourner des valeurs par défaut
            self._logger.debug(f"Erreur dans le calcul CPU manuel: {e}")
            if percpu:
                return [0.0] * psutil.cpu_count()
            else:
                return 0.0
