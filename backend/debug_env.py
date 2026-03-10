import sys
print(sys.executable)
print(sys.path)
try:
    import fastapi
    print("fastapi imported successfully:", fastapi.__version__)
except ImportError:
    print("fastapi NOT found")
