from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    model_artifact_path: str = "../ml/artifacts/risk_decision_tree.joblib"

    app_name: str = "Adaptive Edge-IoT Simulation"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./edge_iot.db"
    dashboard_passphrase: str = "Pass1234"  # override via .env — single shared operator passphrase, not a user system
    tick_interval_seconds: float = 1.0

settings = Settings()