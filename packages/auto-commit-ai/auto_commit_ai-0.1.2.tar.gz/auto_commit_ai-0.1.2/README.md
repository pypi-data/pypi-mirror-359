# AutoCommit AI

Generate conventional commit messages with AI, directly from your terminal.

## 🚀 Features

- **AI-Powered commit messages**: Automatically generates commit messages based on your staged or all changes using advanced AI models.
- **Push changes**: Automatically pushes your committed changes to the remote repository.
- **Multiple AI provider support**: Seamlessly switch between OpenAI, Google Gemini, and Azure OpenAI.
- **Configurable**: Easily configure your AI provider, model, and other settings via environment variables.
- **Language support**: Generate commit messages in various languages (defaulting to English).
- **User confirmation**: Always prompts for user confirmation before committing or pushing changes.

## 📦 Installation

You can install `AutoCommit AI` directly from PyPI using pip:

```bash
pip install auto-commit-ai
```

Alternatively, you can clone the repository and install directly from source:

```bash
git clone https://gitlab.com/tmllull/auto-commit-ai.git
cd auto-commit-ai
pip install .
```

## ⚙️ Configuration

`AutoCommit AI` loads its configuration from environment variables. You can set these variables in a `.auto_commit_ai.env` file located in your current working directory (where your git repository is) or your home directory (`~/.auto_commit_ai.env`).

NOTE: If you add the file to your working directory, remember to add it to your `.gitignore` file.

The contents of the `.auto_commit_ai.env` can be found in the `.auto_commit_ai.env.template` file.

## 🚀 Usage

`AutoCommit AI` is a command-line tool. Navigate to your Git repository and run one of the following commands:

```bash
auto-commit-ai
```

or

```bash
acai
```

This is the default command, and it will generate a commit message for your **staged changes only**.

### Command Line Arguments

You can customize the behavior using the following arguments:

- `-h` or `--help`: Displays the help message.
- `--provider` or `-p`: Specifies the AI provider to use for generating commit messages. Overrides the `DEFAULT_AI_PROVIDER` environment variable.
  - Choices: `openai`, `google`, `azure`
  - Example: `auto-commit-ai --provider google`
- `--all` or `-a`: Adds all files (staged and unstaged) to the commit. By default, only staged changes are included.
  - Example: `acai --all`
- `--language` or `-l`: Sets the language for the generated commit message (e.g., 'en' for English, 'es' for Spanish) in ISO 639-1 format. Defaults to 'en'.
  - Example: `acai --language es`

### Usage Examples:

In the following examples, both `auto-commit-ai` and `acai` are valid commands.

```bash
# Generate a commit message for staged changes (default)
auto-commit-ai

# Include all files (staged and unstaged) in the commit
acai --all

# Use Google Gemini as the AI provider
auto-commit-ai --provider google

# Generate commit message in Spanish
auto-commit-ai --language es
```

## 🤝 Contributing

Contributions are welcome\! Please feel free to open issues or any feature requests.

## 📄 License

This project is licensed under the [GNU Affero General Public License v3](https://www.gnu.org/licenses/agpl-3.0.en.html).
