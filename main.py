"""
Main entry point for the Brand Name Generator application
"""
import sys
import os

# Add the current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui import BrandGeneratorGUI


def main():
    """Main application entry point"""
    try:
        # Create and run the GUI
        app = BrandGeneratorGUI()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication terminated by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()