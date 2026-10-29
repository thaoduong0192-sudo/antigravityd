import os
import sys
import shutil
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("Usage: python 05_init_channel.py <path_to_channel_config.yaml>")
        sys.exit(1)
        
    config_path = Path(sys.argv[1])
    if not config_path.exists():
        print(f"Error: Config file not found at {config_path}")
        sys.exit(1)

    # Base paths
    script_dir = Path(__file__).parent.resolve()
    base_dir = script_dir.parent.parent.parent.parent.resolve() # Assuming we are in skills/youtube-factory/scripts
    pipeline_dir = base_dir / "pipeline" # Default pipeline dir
    
    # Actually create output dir in current working directory for now
    cwd = Path.cwd()
    output_dir = cwd / "output_factory"
    
    # Create directory structure
    dirs_to_create = [
        "long_videos",
        "short_videos",
        "metadata",
        "uploaded",
        "sources",
        "ebook",
        "fonts"
    ]
    
    print(f"Creating output structure in {output_dir}")
    for d in dirs_to_create:
        (output_dir / d).mkdir(parents=True, exist_ok=True)
        print(f"  - Created {d}")
        
    # Copy .env template if not exists
    env_path = cwd / ".env"
    template_env = script_dir.parent / "templates" / ".env.template"
    if not env_path.exists() and template_env.exists():
        shutil.copy(template_env, env_path)
        print("Created .env from template.")
        
    # Create Login_YouTube_Bot.bat
    bat_path = cwd / "Login_YouTube_Bot.bat"
    chrome_profile_path = cwd / "chrome_profile_bot"
    with open(bat_path, "w") as f:
        f.write('@echo off\n')
        f.write('echo === DANG NHAP YOUTUBE STUDIO ===\n')
        f.write('echo Mo Chrome voi profile rieng. Hay dang nhap tai khoan YouTube.\n')
        f.write('echo Sau khi dang nhap xong, dong Chrome lai.\n')
        f.write('echo.\n')
        f.write(f'"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --user-data-dir="{chrome_profile_path.resolve()}" "https://studio.youtube.com"\n')
    
    print("Created Login_YouTube_Bot.bat")
    
    # Print checklist
    print("\n" + "="*40)
    print("CHANNEL INITIALIZATION SUCCESSFUL!")
    print("="*40)
    print("Checklist of next steps:")
    print(f"[ ] 1. Edit {env_path} and fill in the credentials.")
    print(f"[ ] 2. Run Login_YouTube_Bot.bat and login to YouTube Studio. Close Chrome when done.")
    print(f"[ ] 3. Run NotebookLM login if not done yet.")
    print(f"[ ] 4. Check {config_path} for correct channel settings.")
    print("="*40)

if __name__ == "__main__":
    main()
