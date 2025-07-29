# AutoCommitAI 🤖

Automatic commit message generator using AI. With some extra features.

## 🚀 Features

- 🧠 **Multiple AI providers**: OpenAI, Google Gemini and Azure OpenAI. Other integrations will be added in the future
- 🌍 **Multi-language support**: Generate commits in Spanish, English, French, German, etc.
- 📋 **Interactive staging**: Select which files to include in the commit
- 👀 **Preview mode**: Generate messages without committing. Yes, the "final" message will be different, but you can see an approach
- 📊 **Repository information**: Status, history, branches
- 🔄 **Automation**: Auto-confirm mode for CI/CD
- 📱 **JSON output**: Structured format for tool integration

**⚠️ DISCLAIMER for Ollama**: The Ollama integration is experimental and may not work as expected, as there are a lot of models, and some of theme are very limited. It is recommended to use OpenAI or Google Gemini for production use.

## 📦 Installation

You can install **AutoCommit AI** directly from PyPI using pip:

```bash
pip install auto-commit-ai
```

Alternatively, you can clone the repository and install directly from source:

```bash
git clone https://gitlab.com/tmllull/auto-commit-ai.git
cd auto-commit-ai
pip install .
```

## 🔧 Configuration

**AutoCommit AI** loads its configuration from environment variables file. You can set these variables in a `.auto_commit_ai.env` file located in your current working directory (where your git repository is) or your home directory (~/.auto_commit_ai.env).

NOTE: If you add the file to your working directory, remember to add it to your `.gitignore` file.

The contents of the `.auto_commit_ai.env` can be found in the `.auto_commit_ai.env.template` file.

## 🎯 Basic Usage

**AutoCommit AI** is a command-line tool. Navigate to your Git repository and run one of the following commands:

```bash
# Default command
auto-commit-ai
```

or

```bash
# Alias for the default command
acai
```

This is the default command, and it will generate a commit message for your **staged changes only**.

Both commands, `auto-commit-ai` and `acai`, are equivalent and can be used interchangeably.

### Basic commands

```bash
# Include all changes (staged + unstaged + untracked)
acai --all

# Use specific provider
acai --provider google

# Generate in Spanish
acai --language es
```

### Preview message

```bash
# Preview without committing
auto-commit-ai --preview

# Preview including all changes
acai --preview --all
```

### Interactive staging

```bash
# Select files for staging
acai --stage
```

## 📊 Repository information

```bash
# Repository status
acai --status

# Commit history
auto-commit-ai --history

# Branch information
acai --branches
```

## 🛠️ Advanced options

### Automation

```bash
# Automatic mode (no confirmations)
acai --auto-confirm

# JSON output for scripts
auto-commit-ai --output json

# Specific repository
auto-commit-ai --repo /path/to/repo
```

### Output control

```bash
# Don't show status before commit
acai --no-status

# Verbose mode for debugging
acai --verbose
```

## 🌍 Supported languages

The system supports ISO 639-1 language codes:

- `en` - English (default)
- `es` - Spanish
- `fr` - French
- `de` - German
- `it` - Italian
- `pt` - Portuguese
- `ja` - Japanese
- `zh` - Chinese
- `ru` - Russian
- And many more... As you use the ISO 639-1 codes, the system will adapt to your needs.

## 📋 Usage Examples

### Typical workflow

```bash
# 1. Check repository status
acai --status

# 2. Interactive file staging
acai --stage

# 3. Preview message
acai --preview

# 4. Generate final commit
acai
```

### CI/CD automation

```bash
# Automatic commit in pipeline
acai --all --auto-confirm --output json
```

### Working with specific repository

```bash
# Work with another repository
acai --repo /path/to/project --status
acai --repo /path/to/project --all
```

## 🔄 Workflow

1. **Analysis**: Detects repository changes (staged, unstaged, untracked)
2. **Generation**: Uses AI to analyze diffs and generate descriptive message
3. **Review**: Shows generated message for confirmation
4. **Commit**: Creates commit with generated message
5. **Optional push**: Offers to push automatically

## 📝 Message format

Generated messages follow best practices:

- **Title**: Concise line describing the main change
- **Description**: Additional details when necessary
- **Conventions**: Follows standards like _Conventional Commits_ when appropriate

## 🚨 Error handling

The system gracefully handles:

- ❌ Non-Git repositories
- ❌ No changes to commit
- ❌ AI API errors
- ❌ Connectivity issues
- ❌ Incorrect configuration

## 📄 License

This project is licensed under the GNU General Public License v3.0. See `LICENSE` file for more details.

## 🆘 Support

To report bugs or request features, please open an issue on the GitHub repository.

---

_Made with ❤️ for developers who value quality commits_
