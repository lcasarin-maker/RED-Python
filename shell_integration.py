import os
import sys
import winreg

def register_context_menu():
    """Adds 'Scan with RED-Python' to the Windows Context Menu for directories."""
    try:
        # Path to the executable or python script
        if getattr(sys, 'frozen', False):
            # Running as exe
            exe_path = sys.executable
            command = f'"{exe_path}" --scan "%1"'
        else:
            # Running as script
            python_exe = sys.executable
            script_path = os.path.abspath(sys.argv[0])
            command = f'"{python_exe}" "{script_path}" --scan "%1"'

        key_path = r"Directory\shell\RED-Python"
        
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, key_path) as key:
            winreg.SetValue(key, "", winreg.REG_SZ, "Scan with RED-Python")
            # Optional: Add an icon if available
            # winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, exe_path)
            
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f"{key_path}\\command") as key:
            winreg.SetValue(key, "", winreg.REG_SZ, command)
            
        return True, "Context menu registered successfully."
    except Exception as e:
        return False, str(e)

def unregister_context_menu():
    """Removes 'Scan with RED-Python' from the Windows Context Menu."""
    try:
        key_path = r"Directory\shell\RED-Python"
        
        # winreg.DeleteKey doesn't work if there are subkeys, so we delete command first
        try:
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, f"{key_path}\\command")
        except FileNotFoundError:
            pass
            
        winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, key_path)
        return True, "Context menu unregistered successfully."
    except FileNotFoundError:
        return True, "Already unregistered."
    except Exception as e:
        return False, str(e)

def is_registered():
    """Checks if the context menu is already registered."""
    try:
        key_path = r"Directory\shell\RED-Python"
        winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, key_path)
        return True
    except FileNotFoundError:
        return False
    except Exception:
        return False
