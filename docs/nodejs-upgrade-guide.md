# Node.js Upgrade Guide for Chrome DevTools MCP

## Current Status
- **Current Version**: Node.js v20.10.0
- **Required Version**: Node.js v22.12.0 or newer
- **Installation Location**: /usr/local/bin/node

## Upgrade Options

### Option 1: Using Node Version Manager (nvm) - Recommended
```bash
# Install nvm if not already installed
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.4/install.sh | bash

# Reload shell configuration
source ~/.bashrc  # or ~/.zshrc

# Install and use Node.js 22
nvm install 22
nvm use 22
nvm alias default 22

# Verify installation
node --version  # Should show v22.x.x
```

### Option 2: Direct Installation from Official Site
1. Visit [nodejs.org](https://nodejs.org/)
2. Download Node.js v22.x.x LTS
3. Run the installer
4. Restart terminal

### Option 3: Using Homebrew (macOS)
```bash
# Update homebrew
brew update

# Install Node.js 22
brew install node@22

# Link the new version
brew link node@22 --force

# Verify installation
node --version  # Should show v22.x.x
```

## After Upgrade

### 1. Update MCP Configurations
```bash
# Run the workflow to update all MCP configs
cd /Users/markshaw/Desktop/git/itms-developer-setup
python3 itms_workflow.py
# Select option 25: Update MCP Configurations
```

### 2. Test Chrome DevTools MCP
```bash
# Test the Chrome DevTools MCP server
npx -y chrome-devtools-mcp@latest --help
```

### 3. Verify MCP Status
- Check Cursor MCP status (should show green dot for chrome-devtools)
- Check Augment MCP status
- Check Kilo Code MCP status

## Troubleshooting

### If nvm command not found:
```bash
# Add nvm to your shell profile
echo 'export NVM_DIR="$HOME/.nvm"' >> ~/.zshrc
echo '[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"' >> ~/.zshrc
echo '[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"' >> ~/.zshrc
source ~/.zshrc
```

### If brew command not found:
```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

## Why Chrome DevTools MCP?
- **Official Google Solution**: Built and maintained by Google
- **More Features**: Full Chrome DevTools Protocol access
- **Better Performance**: Direct Chrome integration
- **Active Development**: Regular updates and improvements
- **Comprehensive Testing**: Lighthouse, Performance, Accessibility, etc.

## Chrome DevTools MCP Capabilities
- Performance profiling
- Network analysis
- Accessibility audits
- SEO optimization
- Progressive Web App testing
- Core Web Vitals measurement
- Screenshot capture
- PDF generation