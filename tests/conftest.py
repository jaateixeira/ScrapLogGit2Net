# tests/conftest.py
import sys
import os

# Add the project root to sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'utils'))


print ("running conftest.py")
print (f"{sys.path=}")
