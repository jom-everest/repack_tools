import subprocess
from pathlib import Path

def converter():
    root_path = Path("../1/")
    for png_file in root_path.rglob("*.png"):
        webp_path = png_file.with_suffix(".webp")
        jxl_path = png_file.with_suffix(".jxl")
        
        subprocess.run([
            '../bin/cwebp.exe',
            str(png_file), 
            '-o', str(webp_path),
            '-lossless',
            '-z', '9'
        ], capture_output=True, check=True)

def restore():
    root_path = Path("../1/")
    for webp_file in root_path.rglob("*.webp"):
        png_path = webp_file.with_suffix(".png")
        
        subprocess.run([
            '../bin/dwebp.exe',
            str(webp_file), 
            '-o', str(png_path),
        ], capture_output=True, check=True)

#converter()

restore()
