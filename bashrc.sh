# Minimal container .bashrc for NB_USER
export PATH="$HOME/.local/bin:$PATH"

# Activate conda base if present
if [ -f /opt/conda/etc/profile.d/conda.sh ]; then
  . /opt/conda/etc/profile.d/conda.sh
  conda activate base
fi

# useful aliases
alias ll='ls -la'
