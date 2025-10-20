Always run the run.py file after activating the virtual environment because the some packeges raise an ImportError even if they're correctly installed.

To activate the virtual environment, run:
    
    # on Windows: 
        # Command Prompt:
            venv\Scripts\activate.bat
        # Powershell:
            venv\Scripts\Activate.ps1
        # Git Bash:
            source venv\Scripts\activate
            
        # If activation fails in Powershell, run:
            Set-ExecutionPolicy RemoteSigned

    # on Linux/ Mac, run:
        source venv/bin/activate

