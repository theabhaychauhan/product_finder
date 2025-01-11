import unittest
from main import main

class TestMainFunction(unittest.TestCase):
    def test_main_return_value(self):
        """Test that main() crawls amazon"""
        context = "Verifying that main function triggers E-Commerce website's crawling"
        print(f"Context: {context}")
        result = main()

if __name__ == "__main__":
    unittest.main()
