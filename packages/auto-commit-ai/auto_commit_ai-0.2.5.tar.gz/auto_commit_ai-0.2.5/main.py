import sys

from auto_commit_ai import AIProviderFactory, AutoCommitAI, Config


def basic_example():
    """Basic example of generating a commit message."""
    print("=== Basic example ===")

    try:
        # Load configuration from environment variables
        config = Config.from_env()

        # Create the commit message generator
        generator = AutoCommitAI(config)

        # Generate and commit changes (uses default provider and only staged files)
        generator.generate_and_commit()

    except Exception as e:
        print(f"Error: {e}")


def params_example():
    """Example with parameters."""
    print("=== Example with parameters ===")

    try:
        # Load configuration from environment variables
        config = Config.from_env()

        # Create the commit message generator
        generator = AutoCommitAI(config)

        # Use Google Gemini as the provider and include all files (staged and unstaged)
        generator.generate_and_commit(
            provider_name="google",  # Use Gooogle instead of default OpenAI
            include_all=True,  # Add all files (staged and unstaged) to the commit
        )

    except Exception as e:
        print(f"Error: {e}")


def custom_configuration_example():
    """Example using a custom configuration without .env."""
    print("=== Example using a custom configuration ===")

    try:
        # Create a custom configuration (without .env)
        config = Config(
            openai_api_key="your_openai_api_key",
            openai_model="gpt-4",
            default_provider="openai",
            max_tokens=200,
            temperature=0.5,
        )

        # Create the commit message generator with the custom configuration
        generator = AutoCommitAI(config)

        # Generate and commit changes using the custom configuration
        generator.generate_and_commit()

    except Exception as e:
        print(f"Error: {e}")


def example_only_generate_message():
    """Example of generating only the commit message without committing."""
    print("=== Only generate message ===")

    try:
        # Load configuration from environment variables
        config = Config.from_env()

        # Create the AI provider instance
        ai_provider = AIProviderFactory.create_provider("openai", config)

        # Simulate a diff content (this would normally be obtained from git)
        diff_content = """
        diff --git a/example.py b/example.py
        index 1234567..abcdefg 100644
        --- a/example.py
        +++ b/example.py
        @@ -1,3 +1,6 @@
         def hello():
        -    print("Hello")
        +    print("Hello, world!")
        +
        +def goodbye():
        +    print("Goodbye")
        """

        # Only generate the commit message
        mensaje = ai_provider.generate_commit_message(diff_content)
        print(f"Generated message: {mensaje}")

    except Exception as e:
        print(f"Error: {e}")


def check_configuration_example():
    """Example of checking the configuration of AI providers."""
    print("=== Check configuration ===")

    config = Config.from_env()

    providers = ["openai", "google", "azure"]

    for provider in providers:
        try:
            provider_instance = AIProviderFactory.create_provider(provider, config)
            if provider_instance.is_configured():
                print(f"✅ {provider.upper()}: Successfully configured")
            else:
                print(f"❌ {provider.upper()}: Wrong configuration")
        except Exception as e:
            print(f"❌ {provider.upper()}: Error - {e}")


def interactive_menu():
    """Interactive menu for examples."""
    while True:
        print("\n" + "=" * 50)
        print("AUTO COMMIT GENERATOR - EXAMPLE")
        print("=" * 50)
        print("1. Basic example")
        print("2. Parameters example")
        print("3. Custom configuration example")
        print("4. Only generate commit message example")
        print("5. Check configuration example")
        print("6. Exit")

        opcion = input("\nSelect an option (1-6): ").strip()

        if opcion == "1":
            basic_example()
        elif opcion == "2":
            params_example()
        elif opcion == "3":
            custom_configuration_example()
        elif opcion == "4":
            example_only_generate_message()
        elif opcion == "5":
            check_configuration_example()
        elif opcion == "6":
            print("¡Goodbye!")
            break
        else:
            print("Invalid option. Please select a valid option (1-6).")


if __name__ == "__main__":
    # If no arguments are passed, show the interactive menu
    if len(sys.argv) == 1:
        interactive_menu()
    else:
        # If an argument is passed, execute the corresponding example
        if sys.argv[1] == "basic":
            basic_example()
        elif sys.argv[1] == "params":
            params_example()
        elif sys.argv[1] == "custom":
            custom_configuration_example()
        elif sys.argv[1] == "message":
            example_only_generate_message()
        elif sys.argv[1] == "check":
            check_configuration_example()
        else:
            print("Usage: python main.py [basic|params|custom|message|check]")
