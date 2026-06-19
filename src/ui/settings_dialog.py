"""
settings_dialog — App Configuration
====================================
Interactive settings view allowing users to switch models
and update API keys using the Database-backed Model Config.
"""

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QFormLayout,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QComboBox,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QGroupBox,
    QScrollArea
)

from src.core.database import DatabaseManager
from src.core.models import LLM_PROVIDERS

class ModelFetcher(QThread):
    models_ready = pyqtSignal(str, list)

    def __init__(self, task: str, provider: str, api_key: str):
        super().__init__()
        self.task = task
        self.provider = provider
        self.api_key = api_key

    def run(self):
        cls = LLM_PROVIDERS.get(self.provider)
        if cls:
            models = cls.get_available_models(self.api_key)
            self.models_ready.emit(self.task, models)
        else:
            self.models_ready.emit(self.task, [])

class SettingsDialog(QWidget):
    def __init__(self, db: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db = db
        self.tasks = ["tutor", "practice", "exam", "study_guide", "analytics"]
        self.task_combos = {}
        self._init_ui()
        self._load_all_models()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(40, 40, 40, 40)
        
        lbl_title = QLabel("Settings & Configuration")
        lbl_title.setProperty("class", "PageTitle")
        layout.addWidget(lbl_title)
        
        self.settings = self.db.settings.get()
        self.providers = ["groq", "openai", "gemini", "ollama", "kaggle", "openrouter"]
        
        # ── API Keys ──
        grp_keys = QGroupBox("API Keys (Stored locally in Database)")
        form_keys = QFormLayout(grp_keys)
        
        self.le_groq = QLineEdit(self.settings.api_keys.get("groq", ""))
        self.le_groq.setEchoMode(QLineEdit.EchoMode.Password)
        self.le_openai = QLineEdit(self.settings.api_keys.get("openai", ""))
        self.le_openai.setEchoMode(QLineEdit.EchoMode.Password)
        self.le_gemini = QLineEdit(self.settings.api_keys.get("gemini", ""))
        self.le_gemini.setEchoMode(QLineEdit.EchoMode.Password)
        self.le_openrouter = QLineEdit(self.settings.api_keys.get("openrouter", ""))
        self.le_openrouter.setEchoMode(QLineEdit.EchoMode.Password)
        self.le_kaggle = QLineEdit(self.settings.api_keys.get("kaggle", ""))
        
        form_keys.addRow("Groq API Key:", self.le_groq)
        form_keys.addRow("OpenAI API Key:", self.le_openai)
        form_keys.addRow("Gemini API Key:", self.le_gemini)
        form_keys.addRow("OpenRouter API Key:", self.le_openrouter)
        form_keys.addRow("Kaggle URL:", self.le_kaggle)
        layout.addWidget(grp_keys)

        # ── Task Models ──
        grp_tasks = QGroupBox("Task Model Assignments")
        form_tasks = QFormLayout(grp_tasks)
        
        for task in self.tasks:
            assignment = self.settings.task_models.get(task)
            provider = assignment.provider if assignment else "ollama"
            model = assignment.model if assignment else "llama3.2:1b"
            
            cb_prov = QComboBox()
            cb_prov.addItems(self.providers)
            cb_prov.setCurrentText(provider)
            
            cb_model = QComboBox()
            cb_model.addItem(model)
            
            # Use default argument binding to capture current task
            cb_prov.currentTextChanged.connect(lambda text, t=task: self._load_models_for_task(t))
            
            self.task_combos[task] = {"prov": cb_prov, "model": cb_model, "current_model": model}
            
            row_layout = QHBoxLayout()
            row_layout.addWidget(cb_prov)
            row_layout.addWidget(cb_model)
            form_tasks.addRow(task.replace("_", " ").title() + ":", row_layout)
            
        layout.addWidget(grp_tasks)
        
        # ── Save Button ──
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_save = QPushButton("Save Settings")
        self.btn_save.setProperty("class", "PrimaryButton")
        self.btn_save.clicked.connect(self._save_settings)
        btn_layout.addWidget(self.btn_save)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        
        # Style groups
        for grp in [grp_keys, grp_tasks]:
            grp.setStyleSheet("""
                QGroupBox {
                    font-weight: bold;
                    color: #F8FAFC;
                    border: 1px solid rgba(255,255,255,0.1);
                    border-radius: 8px;
                    margin-top: 20px;
                    padding-top: 25px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }
                QLineEdit, QComboBox {
                    padding: 8px;
                    border-radius: 6px;
                    background-color: #0B1020;
                    border: 1px solid rgba(255,255,255,0.1);
                    color: white;
                }
            """)

    def _get_api_key(self, provider: str) -> str:
        if provider == "groq": return self.le_groq.text().strip()
        if provider == "openai": return self.le_openai.text().strip()
        if provider == "gemini": return self.le_gemini.text().strip()
        if provider == "openrouter": return self.le_openrouter.text().strip()
        if provider == "kaggle": return self.le_kaggle.text().strip()
        return ""

    def _load_all_models(self):
        for task in self.tasks:
            self._load_models_for_task(task)

    def _load_models_for_task(self, task: str):
        combos = self.task_combos[task]
        prov = combos["prov"].currentText()
        api_key = self._get_api_key(prov)
        
        combos["model"].clear()
        combos["model"].addItem("Fetching...")
        
        fetcher = ModelFetcher(task, prov, api_key)
        # Prevent garbage collection of fetcher
        setattr(self, f"fetcher_{task}", fetcher)
        fetcher.models_ready.connect(self._on_models_ready)
        fetcher.start()

    def _on_models_ready(self, task: str, models: list[str]):
        combos = self.task_combos[task]
        cb_model = combos["model"]
        cb_model.clear()
        if models:
            cb_model.addItems(models)
            if combos["current_model"] in models:
                cb_model.setCurrentText(combos["current_model"])
        else:
            cb_model.addItem("Error or no models found")

    def _save_settings(self):
        # Update keys
        self.settings.api_keys["groq"] = self.le_groq.text().strip()
        self.settings.api_keys["openai"] = self.le_openai.text().strip()
        self.settings.api_keys["gemini"] = self.le_gemini.text().strip()
        self.settings.api_keys["openrouter"] = self.le_openrouter.text().strip()
        self.settings.api_keys["kaggle"] = self.le_kaggle.text().strip()
        
        # Update assignments
        from src.core.schemas import ModelAssignment
        for task in self.tasks:
            combos = self.task_combos[task]
            prov = combos["prov"].currentText()
            model = combos["model"].currentText()
            if "Fetching" in model or "Error" in model:
                model = combos["current_model"]
            self.settings.task_models[task] = ModelAssignment(provider=prov, model=model)
            combos["current_model"] = model
            
        try:
            self.db.settings.save(self.settings)
            QMessageBox.information(self, "Success", "Settings saved successfully! Models are updated dynamically and will take effect immediately.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")
