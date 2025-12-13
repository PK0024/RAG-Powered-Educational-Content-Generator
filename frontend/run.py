"""Simple entry point to run Streamlit app."""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Now run streamlit
if __name__ == "__main__":
    import streamlit.web.cli as stcli
    
    sys.argv = ["streamlit", "run", "src/streamlit_app/main.py"]
    stcli.main()

