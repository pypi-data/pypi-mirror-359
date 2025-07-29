"""
Command Line Interface for Langchain LLM Config
"""

import argparse
import sys
import os
from pathlib import Path
from typing import Optional

from .config import init_config, get_default_config_path, load_config


def init_command(args: argparse.Namespace) -> int:
    """Initialize a new configuration file"""
    try:
        config_path = init_config(args.config_path)
        print(f"✅ Configuration file created at: {config_path}")
        print("\n📝 Next steps:")
        print("1. Edit the configuration file with your API keys and settings")
        print("2. Set up your environment variables (e.g., OPENAI_API_KEY)")
        print("3. Start using the package in your Python code")
        return 0
    except Exception as e:
        print(f"❌ Error creating configuration file: {e}")
        return 1


def validate_command(args: argparse.Namespace) -> int:
    """Validate an existing configuration file"""
    try:
        config_path = args.config_path or get_default_config_path()
        config = load_config(str(config_path))
        print(f"✅ Configuration file is valid: {config_path}")
        print(f"📊 Default chat provider: {config['default']['chat_provider']}")
        print(
            f"📊 Default embedding provider: {config['default']['embedding_provider']}"
        )
        return 0
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return 1


def setup_env_command(args: argparse.Namespace) -> int:
    """Set up environment variables and create .env file"""
    try:
        # Get the configuration to see what environment variables are needed
        config_path = args.config_path or get_default_config_path()
        
        if not config_path.exists():
            print(f"❌ Configuration file not found: {config_path}")
            print("💡 Run 'llm-config init' first to create a configuration file")
            return 1
        
        # Load config in non-strict mode to see what env vars are referenced
        config = load_config(str(config_path), strict=False)
        
        # Find all environment variable references
        env_vars_needed = set()
        
        def find_env_vars(obj):
            if isinstance(obj, dict):
                for value in obj.values():
                    find_env_vars(value)
            elif isinstance(obj, list):
                for item in obj:
                    find_env_vars(item)
            elif isinstance(obj, str) and obj.startswith("${") and obj.endswith("}"):
                env_vars_needed.add(obj[2:-1])
        
        find_env_vars(config)
        
        if not env_vars_needed:
            print("✅ No environment variables needed in your configuration")
            return 0
        
        # Create .env file
        env_file_path = Path.cwd() / ".env"
        
        if env_file_path.exists() and not args.force:
            print(f"⚠️  .env file already exists at {env_file_path}")
            print("💡 Use --force to overwrite it")
            return 1
        
        # Create .env file with placeholders
        env_content = "# Environment variables for langchain-llm-config\n"
        env_content += "# Copy this file to .env and fill in your actual API keys\n\n"
        
        for env_var in sorted(env_vars_needed):
            env_content += f"# {env_var} - Get your API key from the provider's website\n"
            env_content += f"{env_var}=your-api-key-here\n\n"
        
        with open(env_file_path, "w") as f:
            f.write(env_content)
        
        print(f"✅ Created .env file at: {env_file_path}")
        print("\n📝 Next steps:")
        print("1. Edit the .env file and replace 'your-api-key-here' with your actual API keys")
        print("2. Never commit the .env file to version control (it should be in .gitignore)")
        print("3. The package will automatically load these environment variables")
        
        print(f"\n🔑 Environment variables needed:")
        for env_var in sorted(env_vars_needed):
            print(f"   • {env_var}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error setting up environment variables: {e}")
        return 1


def info_command(args: argparse.Namespace) -> int:
    """Show information about the package and supported providers"""
    print("🤖 Langchain LLM Config")
    print("=" * 50)
    print("\n📦 Supported Chat Providers:")
    print("  • OpenAI - GPT models via OpenAI API")
    print("  • VLLM - Local and remote VLLM servers")
    print("  • Gemini - Google Gemini models")

    print("\n🔗 Supported Embedding Providers:")
    print("  • OpenAI - text-embedding models")
    print("  • VLLM - Local embedding models")
    print("  • Infinity - Fast embedding inference")

    print("\n🚀 Quick Start:")
    print("  1. llm-config init                                                      # Initialize config file")
    print("  2. llm-config setup-env                                                 # Set up environment variables")
    print("  3. Edit .env with your API keys, api.yaml with your provider settings   # Configure API keys and provider settings")
    print("  4. pip install langchain-llm-config                                     # Install package")
    print("  5. Use in your code:")
    print("     from langchain_llm_config import create_assistant")

    return 0


def main() -> int:
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog="llm-config",
        description="Langchain LLM Config - Manage LLM provider configurations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        Examples:
            llm-config init                    # Initialize config in current directory
            llm-config init ~/.config/api.yaml # Initialize config in specific location
            llm-config setup-env               # Set up environment variables
            llm-config validate                # Validate current config
            llm-config info                    # Show package information
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Init command
    init_parser = subparsers.add_parser(
        "init", help="Initialize a new configuration file"
    )
    init_parser.add_argument(
        "config_path",
        nargs="?",
        help="Path where to create the configuration file (default: ./api.yaml)",
    )
    init_parser.set_defaults(func=init_command)

    # Setup env command
    setup_env_parser = subparsers.add_parser(
        "setup-env", help="Set up environment variables and create .env file"
    )
    setup_env_parser.add_argument(
        "config_path",
        nargs="?",
        help="Path to configuration file (default: ./api.yaml)",
    )
    setup_env_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing .env file",
    )
    setup_env_parser.set_defaults(func=setup_env_command)

    # Validate command
    validate_parser = subparsers.add_parser(
        "validate", help="Validate configuration file"
    )
    validate_parser.add_argument(
        "config_path",
        nargs="?",
        help="Path to configuration file to validate (default: ./api.yaml)",
    )
    validate_parser.set_defaults(func=validate_command)

    # Info command
    info_parser = subparsers.add_parser("info", help="Show package information")
    info_parser.set_defaults(func=info_command)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
