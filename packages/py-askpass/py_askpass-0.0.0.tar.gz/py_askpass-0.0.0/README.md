# PSSH - SSH Wrapper with Password and TOTP Support

PSSH is a Python-based SSH wrapper that provides automatic password and TOTP (Time-based One-Time Password) support for SSH connections.

## Features

- Automatic password authentication using stored credentials
- TOTP support for two-factor authentication
- Non-interactive SSH connections using SSH_ASKPASS
- Interactive SSH wrapper with automatic credential injection
- Secure credential storage in `~/.ssh/.sshpt`

## Installation

### From Source

1. Clone the repository:
```bash
git clone <repository-url>
cd pssh
```

2. Install the package:
```bash
pip install -e .
```

This will:
- Install the Python package
- Create a `wssh` executable in the project directory
- Install the `pssh` command-line tool

## Configuration

Create a configuration file at `~/.ssh/.sshpt` with your credentials:

```json
{
    "example.com": {
        "password": "your_password_here",
        "totp": "your_totp_secret_here"
    },
    "another-server.com": {
        "password": "another_password"
    }
}
```

### Configuration Options

- `password`: The password for the SSH connection
- `totp`: The TOTP secret key for two-factor authentication

## Usage

### Method 1: Using the wssh executable

The `wssh` executable works as a drop-in replacement for `ssh`:

```bash
./wssh user@example.com
```

This will:
1. Set `SSH_ASKPASS` to use the Python script
2. Automatically provide passwords and TOTP codes when prompted
3. Fall back to interactive prompts if credentials are not configured

### Method 2: Using the pssh command

```bash
pssh user@example.com
```

This runs the interactive SSH wrapper that automatically injects credentials.

### Method 3: Manual SSH_ASKPASS setup

You can also set up SSH_ASKPASS manually:

```bash
export SSH_ASKPASS="python /path/to/pssh/main.py"
ssh user@example.com
```

## How It Works

1. **SSH_ASKPASS Mode**: When SSH prompts for a password, the Python script is called with the SSH arguments. It parses the hostname and looks up credentials in the configuration file.

2. **Interactive Mode**: The script spawns an SSH process and automatically responds to password and TOTP prompts using stored credentials.

3. **Credential Storage**: Credentials are stored in JSON format in `~/.ssh/.sshpt`. Make sure this file has appropriate permissions (600).

## Security Considerations

- Store the configuration file with restricted permissions: `chmod 600 ~/.ssh/.sshpt`
- Consider using a password manager or encrypted storage for sensitive credentials
- The TOTP secret should be kept secure and not shared

## Requirements

- Python 3.9+
- pexpect
- pyotp

## License

MIT License
