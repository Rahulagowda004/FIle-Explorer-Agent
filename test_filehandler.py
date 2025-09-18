#!/usr/bin/env python3

import sys
import os

# Add the servers directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'servers'))

# Import the functions we need to test
def test_write_file(file_path, content, append=True):
    """Simulate the write_file function"""
    try:
        file_path = os.path.abspath(file_path)
        directory = os.path.dirname(file_path)
        
        # Ensure the directory exists
        os.makedirs(directory, exist_ok=True)
        
        # Check if file exists
        file_exists = os.path.exists(file_path)
        
        if file_exists and append:
            # Append to existing file with newline
            with open(file_path, 'a', encoding='utf-8') as file:
                file.write('\n' + content)
            operation = "appended"
            message = f"Content appended to existing file '{file_path}'"
        else:
            # Create new file or overwrite existing
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            if file_exists:
                operation = "overwritten"
                message = f"Content written to existing file '{file_path}' (overwritten)"
            else:
                operation = "created"
                message = f"New file created and content written to '{file_path}'"
        
        return {"success": True, "message": message, "file_path": file_path, "operation": operation}
        
    except Exception as e:
        return {"success": False, "message": f"Error writing to file '{file_path}': {str(e)}"}

def test_create_directory(directory_path):
    """Simulate the create_directory function"""
    try:
        directory_path = os.path.abspath(directory_path)
        
        if os.path.exists(directory_path):
            return {"success": False, "message": f"Directory '{directory_path}' already exists"}
        
        os.makedirs(directory_path, exist_ok=True)
        
        return {
            "success": True,
            "message": f"Directory created successfully: '{directory_path}'",
            "directory_path": directory_path
        }
    except Exception as e:
        return {"success": False, "message": f"Error creating directory: {str(e)}"}

def test_list_files(directory):
    """Simulate the list_files function"""
    try:
        if os.path.isfile(directory):
            return f"'{directory}' is a file, not a directory."
        if not os.path.exists(directory):
            return f"Directory '{directory}' does not exist."
        files = os.listdir(directory)
        return f"Files in '{directory}': {', '.join(files)}"
    except Exception as e:
        return f"no files found in '{directory}': {str(e)}"

def test_filehandler():
    print("🧪 Testing FileHandler functionality...")
    
    # Test 1: Create a directory
    print("\n1. Testing create_directory...")
    test_dir = "C:/temp/test_folder"
    result = test_create_directory(test_dir)
    print(f"   Result: {result['message']}")
    
    # Test 2: Create a Python file
    print("\n2. Testing create Python file...")
    py_file = "C:/temp/test_folder/hello.py"
    result = test_write_file(py_file, "print('Hello World from Python!')", append=False)
    print(f"   Result: {result['message']}")
    
    # Test 3: Create a CSV file
    print("\n3. Testing create CSV file...")
    csv_file = "C:/temp/test_folder/data.csv"
    csv_content = "name,age,city\nJohn,25,New York\nJane,30,Los Angeles"
    result = test_write_file(csv_file, csv_content, append=False)
    print(f"   Result: {result['message']}")
    
    # Test 4: Create a JSON file
    print("\n4. Testing create JSON file...")
    json_file = "C:/temp/test_folder/config.json"
    json_content = '{\n  "name": "My App",\n  "version": "1.0.0",\n  "debug": true\n}'
    result = test_write_file(json_file, json_content, append=False)
    print(f"   Result: {result['message']}")
    
    # Test 5: List files in directory
    print("\n5. Testing list_files...")
    result = test_list_files("C:/temp/test_folder")
    print(f"   Result: {result}")
    
    # Test 6: Check if files exist and their extensions
    print("\n6. Testing file extensions...")
    files_to_check = [py_file, csv_file, json_file]
    for file_path in files_to_check:
        if os.path.exists(file_path):
            ext = os.path.splitext(file_path)[1]
            size = os.path.getsize(file_path)
            print(f"   ✅ {os.path.basename(file_path)} - Extension: {ext}, Size: {size} bytes")
        else:
            print(f"   ❌ {os.path.basename(file_path)} - File not found")
    
    print("\n✅ All tests completed!")
    print("\n📁 Check the C:/temp/test_folder directory to see the created files!")

if __name__ == "__main__":
    test_filehandler()