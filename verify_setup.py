
import os
import sys
from src.library_manager import LibraryGenerator

def main():
    print("Starting verification...")
    samples_dir = os.path.join(os.getcwd(), "Samples")
    
    if not os.path.exists(samples_dir):
        print(f"ERROR: Samples directory not found at {samples_dir}")
        return

    gen = LibraryGenerator()
    df = gen.process_directory(samples_dir)
    
    print("\n--- Processing Summary ---")
    print(df[['file_path', 'doi', 'status']].head())
    print("\n--------------------------")
    
    output_xml = "TestLibrary.xml"
    gen.save_library(output_xml)
    
    if os.path.exists(output_xml):
        print(f"SUCCESS: Generated {output_xml}")
        # quick check content
        with open(output_xml, 'r', encoding='utf-8') as f:
            content = f.read()
            if "<xml>" in content and "<records>" in content:
                print("Validation: XML structure seems correct.")
            else:
                print("Validation: XML structure seems INVALID.")
    else:
        print("ERROR: Output XML was not created.")

if __name__ == "__main__":
    main()
