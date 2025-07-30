"""Module de configuration pour le système de monitoring.

Ce module gère la configuration complète du système de monitoring, incluant
le chargement, la validation et la sauvegarde des paramètres depuis/vers
différents formats de fichiers (JSON, YAML).

Classes:
    MonitoringConfig: Dataclass contenant tous les paramètres de configuration
    ConfigurationManager: Gestionnaire principal pour la manipulation des configurations

Le module supporte la validation automatique des paramètres, la vérification
de cohérence des seuils d'alerte et la gestion des chemins de fichiers.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, asdict

from .core.exceptions import ExportError, AlertConfigurationError


@dataclass
class MonitoringConfig:
    """Configuration complète du système de monitoring.
    
    Cette dataclass contient tous les paramètres configurables du système,
    organisés par catégorie (service, moniteurs, export, alertes, etc.).
    
    Attributes:
        monitor_interval: Intervalle entre les collectes de données (secondes)
        export_interval: Intervalle entre les exports de données (secondes)
        max_snapshots_history: Nombre maximum de snapshots à conserver en mémoire
        processor_interval: Intervalle de mise à jour du processeur (secondes)
        disk_path: Chemin du disque à surveiller
        auto_initialize: Initialisation automatique des moniteurs
        export_dir: Répertoire de destination pour les exports
        export_type: Type d'export (json, websocket)
        export_compress: Compression des fichiers exportés
        export_pretty_print: Formatage JSON lisible
        export_date_in_filename: Inclusion de la date dans le nom de fichier
        alert_cooldown_seconds: Temps minimum entre deux alertes identiques
        alert_max_history: Nombre maximum d'alertes à conserver
        alert_enabled: Activation du système d'alertes
        memory_warning_threshold: Seuil d'alerte warning pour la mémoire (%)
        memory_critical_threshold: Seuil d'alerte critique pour la mémoire (%)
        disk_warning_threshold: Seuil d'alerte warning pour le disque (%)
        disk_critical_threshold: Seuil d'alerte critique pour le disque (%)
        log_level: Niveau de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Fichier de log optionnel
        websocket_enabled: Activation du serveur WebSocket
        websocket_host: Adresse d'écoute du serveur WebSocket
        websocket_port: Port d'écoute du serveur WebSocket
        threadsafe_enabled: Activation du mode thread-safe
        data_queue_size: Taille de la queue de données en mode thread-safe
    """
    
    # Configuration du service principal
    monitor_interval: float = 0.5
    export_interval: float = 60.0
    max_snapshots_history: int = 1000
    
    # Configuration des moniteurs
    processor_interval: float = 0.05
    disk_path: str = "/"
    auto_initialize: bool = True
    
    # Configuration de l'export
    export_dir: str = "./monitoring_data"
    export_type: str = "json"
    export_compress: bool = False
    export_pretty_print: bool = True
    export_date_in_filename: bool = True
    
    # Configuration des alertes
    alert_cooldown_seconds: float = 300.0
    alert_max_history: int = 100
    alert_enabled: bool = True
    
    # Seuils d'alerte par défaut
    memory_warning_threshold: float = 80.0
    memory_critical_threshold: float = 90.0
    disk_warning_threshold: float = 85.0
    disk_critical_threshold: float = 95.0
    
    # Configuration du logging
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # Configuration WebSocket
    websocket_enabled: bool = False
    websocket_host: str = "0.0.0.0"
    websocket_port: int = 8765
    
    # Configuration du service thread-safe
    threadsafe_enabled: bool = False
    data_queue_size: int = 100


class ConfigurationManager:
    """Gestionnaire de configuration pour le système de monitoring.
    
    Cette classe fournit une interface complète pour gérer les configurations
    du système, incluant le chargement depuis des fichiers, la validation,
    la mise à jour et la sauvegarde dans différents formats.
    
    Attributes:
        _config: Configuration actuelle (MonitoringConfig ou None)
        _config_file_path: Chemin du fichier de configuration chargé
    
    Methods:
        create_default_config: Crée une configuration par défaut
        load_from_file: Charge une configuration depuis un fichier
        save_to_file: Sauvegarde la configuration vers un fichier
        update_config: Met à jour la configuration actuelle
        get_service_config: Extrait la configuration du service
        get_monitor_config: Extrait la configuration des moniteurs
        get_exporter_config: Extrait la configuration de l'exporteur
        get_alert_config: Extrait la configuration des alertes
        create_example_config_file: Crée un fichier d'exemple
        from_dict: Crée un gestionnaire depuis un dictionnaire
    """

    def __init__(self) -> None:
        """Initialise le gestionnaire de configuration.
        
        Crée un gestionnaire vide sans configuration chargée.
        """
        self._config: Optional[MonitoringConfig] = None
        self._config_file_path: Optional[Path] = None

    @property
    def config(self) -> Optional[MonitoringConfig]:
        """Retourne la configuration actuelle.

        Returns:
            Optional[MonitoringConfig]: Configuration chargée ou None si aucune
                configuration n'est chargée.
        """
        return self._config

    @property
    def config_file_path(self) -> Optional[Path]:
        """Retourne le chemin du fichier de configuration.

        Returns:
            Optional[Path]: Chemin du fichier de configuration chargé ou None
                si la configuration n'a pas été chargée depuis un fichier.
        """
        return self._config_file_path

    @staticmethod
    def create_default_config() -> MonitoringConfig:
        """Crée une configuration par défaut.

        Returns:
            MonitoringConfig: Nouvelle instance de configuration avec toutes
                les valeurs par défaut.
        """
        return MonitoringConfig()

    def load_from_file(self, file_path: Union[str, Path]) -> MonitoringConfig:
        """Charge la configuration depuis un fichier.

        Supporte les formats JSON et YAML. La configuration est validée
        automatiquement après le chargement.

        Args:
            file_path: Chemin du fichier de configuration à charger.

        Returns:
            MonitoringConfig: Configuration chargée et validée.

        Raises:
            FileNotFoundError: Si le fichier spécifié n'existe pas.
            ValueError: Si le format de fichier n'est pas supporté (doit être
                .json, .yaml ou .yml).
            AlertConfigurationError: Si la configuration est invalide ou si une
                erreur survient pendant le chargement.
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Fichier de configuration non trouvé: {file_path}")

        try:
            if file_path.suffix.lower() == '.json':
                config_data = self._load_json(file_path)
            elif file_path.suffix.lower() in ['.yaml', '.yml']:
                config_data = self._load_yaml(file_path)
            else:
                raise ValueError(f"Format de fichier non supporté: {file_path.suffix}")

            # Validation et création de la configuration
            validated_data = self._validate_config_data(config_data)
            self._config = MonitoringConfig(**validated_data)
            self._config_file_path = file_path
            
            return self._config

        except Exception as e:
            raise AlertConfigurationError(f"Erreur lors du chargement de {file_path}: {e}")

    def save_to_file(self, file_path: Union[str, Path], 
                    config: Optional[MonitoringConfig] = None) -> None:
        """Sauvegarde la configuration vers un fichier.

        Le format est déterminé par l'extension du fichier (.json ou .yaml/.yml).
        Le répertoire parent est créé automatiquement si nécessaire.

        Args:
            file_path: Chemin du fichier de destination.
            config: Configuration à sauvegarder. Si None, utilise la
                configuration actuellement chargée.

        Raises:
            ValueError: Si aucune configuration n'est disponible ou si le
                format de fichier n'est pas supporté.
            ExportError: Si une erreur survient pendant la sauvegarde.
        """
        config_to_save = config or self._config
        if config_to_save is None:
            raise ValueError("Aucune configuration à sauvegarder")

        file_path = Path(file_path)
        
        try:
            # Création du répertoire parent si nécessaire
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            config_data = asdict(config_to_save)
            
            if file_path.suffix.lower() == '.json':
                self._save_json(file_path, config_data)
            elif file_path.suffix.lower() in ['.yaml', '.yml']:
                self._save_yaml(file_path, config_data)
            else:
                raise ValueError(f"Format de fichier non supporté: {file_path.suffix}")

            self._config_file_path = file_path

        except Exception as e:
            raise ExportError(f"Erreur lors de la sauvegarde vers {file_path}: {e}")

    @staticmethod
    def _load_json(file_path: Path) -> Dict[str, Any]:
        """Charge un fichier JSON.

        Args:
            file_path: Chemin du fichier JSON à charger.

        Returns:
            Dict[str, Any]: Dictionnaire contenant les données chargées.
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def _load_yaml(file_path: Path) -> Dict[str, Any]:
        """Charge un fichier YAML.

        Args:
            file_path: Chemin du fichier YAML à charger.

        Returns:
            Dict[str, Any]: Dictionnaire contenant les données chargées.

        Raises:
            ImportError: Si PyYAML n'est pas installé dans l'environnement.
        """
        try:
            import yaml
        except ImportError:
            raise ImportError("PyYAML est requis pour charger les fichiers YAML")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}

    @staticmethod
    def _save_json(file_path: Path, data: Dict[str, Any]) -> None:
        """Sauvegarde vers un fichier JSON.

        Le fichier est formaté avec indentation pour une meilleure lisibilité.

        Args:
            file_path: Chemin du fichier JSON de destination.
            data: Dictionnaire contenant les données à sauvegarder.
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def _save_yaml(file_path: Path, data: Dict[str, Any]) -> None:
        """Sauvegarde vers un fichier YAML.

        Args:
            file_path: Chemin du fichier YAML de destination.
            data: Dictionnaire contenant les données à sauvegarder.

        Raises:
            ImportError: Si PyYAML n'est pas installé dans l'environnement.
        """
        try:
            import yaml
        except ImportError:
            raise ImportError("PyYAML est requis pour sauvegarder les fichiers YAML")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

    def _validate_config_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Valide et normalise les données de configuration.

        Vérifie les types, les plages de valeurs et la cohérence des données.
        Les valeurs manquantes sont remplacées par les valeurs par défaut.

        Args:
            data: Dictionnaire contenant les données à valider.

        Returns:
            Dict[str, Any]: Dictionnaire contenant les données validées et
                normalisées.

        Raises:
            ValueError: Si les données sont invalides (types incorrects,
                valeurs hors limites, incohérences).
        """
        # Création d'une configuration par défaut pour comparaison
        default_config = self.create_default_config()
        validated_data = asdict(default_config)

        # Validation de chaque champ
        for key, value in data.items():
            if key in validated_data:
                # Validation spécifique selon le type attendu
                expected_type = type(validated_data[key])
                
                if expected_type == float and isinstance(value, (int, float)):
                    validated_data[key] = float(value)
                elif expected_type == int and isinstance(value, int):
                    validated_data[key] = value
                elif expected_type == bool and isinstance(value, bool):
                    validated_data[key] = value
                elif expected_type == str and isinstance(value, str):
                    validated_data[key] = value
                elif key.endswith('_threshold') and isinstance(value, (int, float)):
                    # Validation des seuils (0-100%)
                    if not 0 <= value <= 100:
                        raise ValueError(f"Le seuil {key} doit être entre 0 et 100")
                    validated_data[key] = float(value)
                elif key.endswith('_interval') and isinstance(value, (int, float)):
                    # Validation des intervalles (>0)
                    if value <= 0:
                        raise ValueError(f"L'intervalle {key} doit être positif")
                    validated_data[key] = float(value)
                else:
                    raise ValueError(f"Type invalide pour {key}: attendu {expected_type.__name__}, reçu {type(value).__name__}")

        # Validations de cohérence
        self._validate_threshold_consistency(validated_data)
        self._validate_paths(validated_data)

        return validated_data

    @staticmethod
    def _validate_threshold_consistency(data: Dict[str, Any]) -> None:
        """Valide la cohérence des seuils d'alerte.

        Vérifie que les seuils warning sont inférieurs aux seuils critiques
        pour chaque type de ressource.

        Args:
            data: Dictionnaire contenant les seuils à valider.

        Raises:
            ValueError: Si un seuil warning est supérieur ou égal au seuil
                critique correspondant.
        """
        threshold_pairs = [
            ("memory_warning_threshold", "memory_critical_threshold"),
            ("disk_warning_threshold", "disk_critical_threshold")
        ]

        for warning_key, critical_key in threshold_pairs:
            warning_value = data.get(warning_key)
            critical_value = data.get(critical_key)
            
            if warning_value and critical_value and warning_value >= critical_value:
                raise ValueError(
                    f"{warning_key} ({warning_value}) doit être inférieur à "
                    f"{critical_key} ({critical_value})"
                )

    @staticmethod
    def _validate_paths(data: Dict[str, Any]) -> None:
        """Valide les chemins de fichiers et répertoires.

        Vérifie l'existence du chemin de disque et crée le répertoire
        d'export s'il n'existe pas.

        Args:
            data: Dictionnaire contenant les chemins à valider.

        Raises:
            ValueError: Si le chemin de disque n'existe pas ou si le
                répertoire d'export ne peut pas être créé.
        """
        # Validation du chemin de disque
        disk_path = data.get("disk_path")
        if disk_path and not Path(disk_path).exists():
            raise ValueError(f"Le chemin de disque n'existe pas: {disk_path}")

        # Validation du répertoire d'export
        export_dir = data.get("export_dir")
        if export_dir:
            try:
                Path(export_dir).mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise ValueError(f"Impossible de créer le répertoire d'export {export_dir}: {e}")

    def update_config(self, **kwargs) -> None:
        """Met à jour la configuration actuelle.

        Les nouveaux paramètres sont validés avant d'être appliqués.

        Args:
            **kwargs: Paramètres de configuration à mettre à jour sous forme
                de paires clé-valeur.

        Raises:
            ValueError: Si aucune configuration n'est chargée ou si les
                nouveaux paramètres sont invalides.
        """
        if self._config is None:
            raise ValueError("Aucune configuration chargée")

        # Validation des nouveaux paramètres
        current_data = asdict(self._config)
        current_data.update(kwargs)
        validated_data = self._validate_config_data(current_data)
        
        # Mise à jour de la configuration
        self._config = MonitoringConfig(**validated_data)

    def get_service_config(self) -> Dict[str, Any]:
        """Retourne la configuration pour le service de monitoring.

        Extrait les paramètres spécifiques au service principal.

        Returns:
            Dict[str, Any]: Dictionnaire contenant les paramètres du service
                (intervalles, historique, répertoire d'export).

        Raises:
            ValueError: Si aucune configuration n'est chargée.
        """
        if self._config is None:
            raise ValueError("Aucune configuration chargée")

        return {
            "monitor_interval": self._config.monitor_interval,
            "export_interval": self._config.export_interval,
            "max_snapshots_history": self._config.max_snapshots_history,
            "export_dir": Path(self._config.export_dir)
        }

    def get_monitor_config(self) -> Dict[str, Any]:
        """Retourne la configuration pour les moniteurs.

        Extrait les paramètres spécifiques aux différents moniteurs.

        Returns:
            Dict[str, Any]: Dictionnaire contenant les paramètres des moniteurs
                organisés par type (processor, disk).

        Raises:
            ValueError: Si aucune configuration n'est chargée.
        """
        if self._config is None:
            raise ValueError("Aucune configuration chargée")

        return {
            "processor": {
                "interval": self._config.processor_interval
            },
            "disk": {
                "path": self._config.disk_path
            },
            "auto_initialize": self._config.auto_initialize
        }

    def get_exporter_config(self) -> Dict[str, Any]:
        """Retourne la configuration pour l'exporteur.

        Extrait les paramètres spécifiques à l'export de données.

        Returns:
            Dict[str, Any]: Dictionnaire contenant les paramètres d'export
                (type, répertoire, compression, formatage).

        Raises:
            ValueError: Si aucune configuration n'est chargée.
        """
        if self._config is None:
            raise ValueError("Aucune configuration chargée")

        return {
            "type": self._config.export_type,
            "output_dir": self._config.export_dir,
            "compress": self._config.export_compress,
            "pretty_print": self._config.export_pretty_print,
            "date_in_filename": self._config.export_date_in_filename
        }

    def get_alert_config(self) -> Dict[str, Any]:
        """Retourne la configuration pour les alertes.

        Extrait les paramètres spécifiques au système d'alertes.

        Returns:
            Dict[str, Any]: Dictionnaire contenant les paramètres d'alertes
                (cooldown, historique, seuils par ressource).

        Raises:
            ValueError: Si aucune configuration n'est chargée.
        """
        if self._config is None:
            raise ValueError("Aucune configuration chargée")

        return {
            "cooldown_seconds": self._config.alert_cooldown_seconds,
            "max_history": self._config.alert_max_history,
            "enabled": self._config.alert_enabled,
            "thresholds": {
                "memory_warning": self._config.memory_warning_threshold,
                "memory_critical": self._config.memory_critical_threshold,
                "disk_warning": self._config.disk_warning_threshold,
                "disk_critical": self._config.disk_critical_threshold
            }
        }

    def create_example_config_file(self, file_path: Union[str, Path]) -> None:
        """Crée un fichier de configuration d'exemple.

        Génère un fichier avec la configuration par défaut.

        Args:
            file_path: Chemin du fichier d'exemple à créer.
        """
        example_config = self.create_default_config()
        self.save_to_file(file_path, example_config)

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'ConfigurationManager':
        """Crée un gestionnaire de configuration à partir d'un dictionnaire.

        Méthode factory pour créer un gestionnaire pré-configuré.

        Args:
            config_dict: Dictionnaire contenant les paramètres de configuration.

        Returns:
            ConfigurationManager: Nouvelle instance de gestionnaire avec la
                configuration chargée et validée.
        """
        manager = cls()
        validated_data = manager._validate_config_data(config_dict)
        manager._config = MonitoringConfig(**validated_data)
        return manager

    def __str__(self) -> str:
        """Retourne une représentation textuelle du gestionnaire.
        
        Returns:
            str: Description lisible de l'état du gestionnaire.
        """
        if self._config:
            return f"ConfigurationManager(loaded from {self._config_file_path})"
        else:
            return "ConfigurationManager(no config loaded)"
