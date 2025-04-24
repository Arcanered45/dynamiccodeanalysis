import pytest
import time

def inefficient_string_processor(text):
    # Inefficient string concatenation
    result = ""
    for char in text:
        result += char.upper()
    
    # Inefficient filtering
    vowels = []
    for char in result:
        if char in "AEIOU":
            vowels.append(char)
    
    return len(vowels)

def test_string_processing():
    # Create a long string
    text = "hello world" * 10000
    
    # Measure performance
    start_time = time.time()
    vowel_count = inefficient_string_processor(text)
    end_time = time.time()
    
    # Basic assertions
    assert isinstance(vowel_count, int)
    assert vowel_count > 0
    assert end_time - start_time < 0.1  # This should fail, showing the inefficiency