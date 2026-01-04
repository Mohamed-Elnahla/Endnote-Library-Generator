import webview
import threading
import os
import sys
import time

# Ensure src is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.endnote_generator.library_manager import LibraryGenerator

class Api:
    def __init__(self):
        # Pywebview inspects all public attributes. Storing complex objects like 
        # the generator (which contains a DataFrame) as a public attribute causes
        # "unhashable type: 'DataFrame'" errors during inspection.
        # We rename it to private `_generator` or just instantiate it when needed, 
        # but `_generator` is safer as pywebview ignores methods/props starting with _.
        self._generator = LibraryGenerator()
        self._window = None

    def select_folder(self):
        # Open folder selection dialog
        result = self._window.create_file_dialog(webview.FOLDER_DIALOG)
        if result and len(result) > 0:
            return result[0]
        return None

    def select_save_file(self):
        # Open save file dialog
        result = self._window.create_file_dialog(webview.SAVE_DIALOG, save_filename='MyLibrary.xml', file_types=('XML Files (*.xml)', 'All files (*.*)'))
        if result:
            # result might be a string or list depending on version/OS, but SAVE_DIALOG usually returns str or None?
            # pywebview spec: returns a tuple/list of strings
            if isinstance(result, (list, tuple)) and len(result) > 0:
                return result[0]
            if isinstance(result, str):
                return result
        return None

    def start_processing(self, folder_path, output_path):
        # Run in a separate thread to not block UI
        t = threading.Thread(target=self._process_thread, args=(folder_path, output_path))
        t.start()

    def _process_thread(self, folder_path, output_path):
        try:
            self._window.evaluate_js(f'updateProgress(0, "Initializing scan...")')
            
            def progress(current, total, message):
                percent = int((current / total) * 100)
                # Escape potential quote issues in message
                safe_msg = message.replace('"', '\\"').replace("'", "\\'")
                # Update UI
                self._window.evaluate_js(f'updateProgress({percent}, "{safe_msg}")')

            # Run processing
            df = self._generator.process_directory(folder_path, progress_callback=progress)
            
            # Save
            self._window.evaluate_js(f'updateProgress(100, "Saving XML file...")')
            self._generator.save_library(output_path)
            
            count = len(df)
            success_count = len(df[df['status'] == 'Success'])
            msg = f"Processed {count} files. {success_count} success. Saved to {os.path.basename(output_path)}"
            self._window.evaluate_js(f'processingComplete("{msg}")')
            
        except Exception as e:
            print(f"Error: {e}")
            self._window.evaluate_js(f'setStatus("Error: {str(e)}", true)')

def main():
    api = Api()
    html_path = os.path.join(os.getcwd(), 'gui', 'index.html')
    # Use abspath
    html_url = f"file://{os.path.abspath(html_path)}"
    
    api._window = webview.create_window(
        'EndNote Library Generator', 
        url=html_url,
        js_api=api,
        width=900,
        height=700,
        resizable=True
    )
    
    webview.start(debug=False)

if __name__ == '__main__':
    main()
