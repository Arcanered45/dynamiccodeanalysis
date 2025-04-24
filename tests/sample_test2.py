import unittest
import time
import random

class TestStringProcessor(unittest.TestCase):
    def setUp(self):
        # Generate a large list of strings for testing
        self.test_strings = [''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=10)) 
                           for _ in range(1000)]
    
    def test_version1_string_processing(self):
        """Test the first version of string processing (using loops)"""
        start_time = time.time()
        
        # Version 1: Using traditional loops
        processed_strings = []
        for s in self.test_strings:
            # Convert to uppercase
            upper = s.upper()
            # Remove vowels
            no_vowels = ''.join([c for c in upper if c not in 'AEIOU'])
            # Add to result
            processed_strings.append(no_vowels)
        
        end_time = time.time()
        print(f"Version 1 execution time: {end_time - start_time:.4f} seconds")
        
        # Verify results
        self.assertEqual(len(processed_strings), len(self.test_strings))
        for s in processed_strings:
            self.assertTrue(s.isupper())
            self.assertTrue(all(c not in 'AEIOU' for c in s))
    
    def test_version2_string_processing(self):
        """Test the second version of string processing (using list comprehensions)"""
        start_time = time.time()
        
        # Version 2: Using list comprehensions and map
        processed_strings = [
            ''.join(c for c in s.upper() if c not in 'AEIOU')
            for s in self.test_strings
        ]
        
        end_time = time.time()
        print(f"Version 2 execution time: {end_time - start_time:.4f} seconds")
        
        # Verify results
        self.assertEqual(len(processed_strings), len(self.test_strings))
        for s in processed_strings:
            self.assertTrue(s.isupper())
            self.assertTrue(all(c not in 'AEIOU' for c in s))
    
    def test_version3_string_processing(self):
        """Test the third version of string processing (using optimized approach)"""
        start_time = time.time()
        
        # Version 3: Using optimized approach with set operations
        vowels = set('AEIOU')
        processed_strings = [
            ''.join(c for c in s.upper() if c not in vowels)
            for s in self.test_strings
        ]
        
        end_time = time.time()
        print(f"Version 3 execution time: {end_time - start_time:.4f} seconds")
        
        # Verify results
        self.assertEqual(len(processed_strings), len(self.test_strings))
        for s in processed_strings:
            self.assertTrue(s.isupper())
            self.assertTrue(all(c not in 'AEIOU' for c in s))

if __name__ == '__main__':
    unittest.main() 