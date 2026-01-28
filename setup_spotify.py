import tkinter as tk
from tkinter import simpledialog, messagebox
import webbrowser
import os

def setup():
    root = tk.Tk()
    root.withdraw() # Hide main window

    # Check if keys are already set
    config_path = os.path.join(os.path.dirname(__file__), "config.py")
    with open(config_path, "r") as f:
        content = f.read()
            
    # Simple check for filled keys
    import re
    id_match = re.search(r'SPOTIPY_CLIENT_ID\s*=\s*"(.+?)"', content)
    secret_match = re.search(r'SPOTIPY_CLIENT_SECRET\s*=\s*"(.+?)"', content)

    if id_match and secret_match and len(id_match.group(1)) > 5:
        # Keys found, skip wizard
        print("Spotify keys found. Skipping setup.")
        return

    # If we get here, keys are missing. Start Wizard.
    messagebox.showinfo("Spotify Setup", "Spotify keys are missing!\n\nI will open the dashboard for you to get them.")
    webbrowser.open("https://developer.spotify.com/dashboard")

    # Ask for Client ID
    client_id = simpledialog.askstring("Input", "Paste your Spotify CLIENT ID here:")
    if not client_id:
        messagebox.showwarning("Cancelled", "Setup cancelled.")
        return

    # Ask for Client Secret
    client_secret = simpledialog.askstring("Input", "Paste your Spotify CLIENT SECRET here:")
    if not client_secret:
        messagebox.showwarning("Cancelled", "Setup cancelled.")
        return

    # Read config.py
    config_path = os.path.join(os.path.dirname(__file__), "config.py")
    with open(config_path, "r") as f:
        lines = f.readlines()

    # Update lines
    new_lines = []
    for line in lines:
        if "SPOTIPY_CLIENT_ID =" in line:
            new_lines.append(f'SPOTIPY_CLIENT_ID = "{client_id.strip()}" \n')
        elif "SPOTIPY_CLIENT_SECRET =" in line:
            new_lines.append(f'SPOTIPY_CLIENT_SECRET = "{client_secret.strip()}"\n')
        else:
            new_lines.append(line)

    # Write back
    with open(config_path, "w") as f:
        f.writelines(new_lines)

    messagebox.showinfo("Success", "Keys saved to config.py! \n\nPlease Restart SAMi (close and run main.py again).")

if __name__ == "__main__":
    setup()
