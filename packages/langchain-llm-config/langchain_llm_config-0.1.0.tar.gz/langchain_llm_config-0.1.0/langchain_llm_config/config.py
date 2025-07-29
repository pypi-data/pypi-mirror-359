from typing import Dict, Optional
import yaml
from pathlib import Path
import os
import warnings
from dotenv import load_dotenv


def get_default_config_path() -> Path:
    """
    Get the default configuration file path.

    Returns:
        Path to the default api.yaml file
    """
    # Try to find api.yaml in current working directory first
    cwd_config = Path.cwd() / "api.yaml"
    if cwd_config.exists():
        return cwd_config

    # Try to find api.yaml in user's home directory
    home_config = Path.home() / ".langchain-llm-config" / "api.yaml"
    if home_config.exists():
        return home_config

    # Return the current working directory as default location
    return cwd_config


def load_config(config_path: Optional[str] = None, strict: bool = False) -> Dict:
    """
    Load LLM configuration

    Args:
        config_path: Configuration file path, defaults to api.yaml in current directory
        strict: If True, raise ValueError for missing environment variables. 
                If False, use default values and show warnings.

    Returns:
        Processed configuration dictionary

    Raises:
        ValueError: Configuration file not found or environment variables not set (if strict=True)
    """
    # Load environment variables from .env file
    dotenv_path = Path.cwd() / ".env"
    if dotenv_path.exists():
        load_dotenv(dotenv_path=dotenv_path)

    if config_path is None:
        config_path = get_default_config_path()

    if not Path(config_path).exists():
        raise ValueError(f"Configuration file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Process environment variables
    llm_config = config["llm"]
    for provider_name, provider_config in llm_config.items():
        if provider_name == "default":
            continue

        for service_type, service_config in provider_config.items():
            for key, value in service_config.items():
                if (
                    isinstance(value, str)
                    and value.startswith("${")
                    and value.endswith("}")
                ):
                    env_var = value[2:-1]
                    env_value = os.getenv(env_var)
                    if env_value is None:
                        if strict:
                            raise ValueError(f"Environment variable {env_var} not set")
                        else:
                            # Use default values for common API keys
                            default_values = {
                                "OPENAI_API_KEY": "sk-demo-key-not-for-production",
                                "GEMINI_API_KEY": "demo-key-not-for-production",
                                "ANTHROPIC_API_KEY": "sk-ant-demo-key-not-for-production",
                            }
                            default_value = default_values.get(env_var, "")
                            service_config[key] = default_value
                            warnings.warn(
                                f"Environment variable {env_var} not set. Using default value. "
                                f"Set {env_var} in your environment or .env file for production use.",
                                UserWarning,
                                stacklevel=2
                            )
                    else:
                        service_config[key] = env_value

    return llm_config


def init_config(config_path: Optional[str] = None) -> Path:
    """
    Initialize a new configuration file with default settings.

    Args:
        config_path: Path where to create the configuration file

    Returns:
        Path to the created configuration file
    """
    if config_path is None:
        config_path = get_default_config_path()

    config_path = Path(config_path)

    # Create parent directory if it doesn't exist
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Get the template configuration
    template_path = Path(__file__).parent / "templates" / "api.yaml"

    if template_path.exists():
        # Copy template to target location
        import shutil

        shutil.copy2(template_path, config_path)
    else:
        # Create a basic configuration if template doesn't exist
        default_config = {
            "llm": {
                "openai": {
                    "chat": {
                        "api_base": "https://api.openai.com/v1",
                        "api_key": "${OPENAI_API_KEY}",
                        "model_name": "gpt-3.5-turbo",
                        "temperature": 0.7,
                        "max_tokens": 8192,
                        "connect_timeout": 30,
                        "read_timeout": 60,
                    },
                    "embeddings": {
                        "api_base": "https://api.openai.com/v1",
                        "api_key": "${OPENAI_API_KEY}",
                        "model_name": "text-embedding-ada-002",
                        "timeout": 30,
                    },
                },
                "vllm": {
                    "chat": {
                        "api_base": "http://localhost:8000/v1",
                        "api_key": "${OPENAI_API_KEY}",
                        "model_name": "meta-llama/Llama-2-7b-chat-hf",
                        "temperature": 0.6,
                        "top_p": 0.8,
                        "max_tokens": 8192,
                        "connect_timeout": 30,
                        "read_timeout": 60,
                    },
                    "embeddings": {
                        "api_base": "http://localhost:8000/v1",
                        "api_key": "${OPENAI_API_KEY}",
                        "model_name": "bge-m3",
                        "dimensions": 1024,
                        "timeout": 30,
                    },
                },
                "gemini": {
                    "chat": {
                        "api_key": "${GEMINI_API_KEY}",
                        "model_name": "gemini-pro",
                        "temperature": 0.7,
                        "max_tokens": 8192,
                    }
                },
                "infinity": {
                    "embeddings": {
                        "api_base": "http://localhost:7997/v1",
                        "model_name": "models/bge-m3",
                    }
                },
                "default": {"chat_provider": "openai", "embedding_provider": "openai"},
            }
        }

        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)

    return config_path
