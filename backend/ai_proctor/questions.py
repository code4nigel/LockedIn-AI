# A simple dataset of coding questions tagged by difficulty (1-10)
# In a real app, this would be in a database like SQLite or PostgreSQL.

QUESTION_BANK = [
    {
        "id": 1,
        "title": "Reverse a String",
        "description": "Write a function that reverses a string. Input: 'hello', Output: 'olleh'",
        "difficulty": 1,
        "topic": "Strings"
    },
    {
        "id": 2,
        "title": "Find Maximum in Array",
        "description": "Given an array of integers, find the largest element.",
        "difficulty": 2,
        "topic": "Arrays"
    },
    {
        "id": 3,
        "title": "Check Palindrome",
        "description": "Determine if a string reads the same forwards and backwards.",
        "difficulty": 3,
        "topic": "Strings"
    },
    {
        "id": 4,
        "title": "Two Sum",
        "description": "Find two numbers in an array that add up to a specific target.",
        "difficulty": 5,
        "topic": "Hashing"
    },
    {
        "id": 5,
        "title": "Binary Search",
        "description": "Implement an efficient search algorithm for a sorted array.",
        "difficulty": 6,
        "topic": "Algorithms"
    }
]

def get_question_by_difficulty(current_diff, performance_delta):
    """
    Logic: Next Difficulty = Current Level + Performance Adjustment
    performance_delta: +1 for good, -1 for struggle, 0 for neutral
    """
    target_diff = max(1, min(10, current_diff + performance_delta))
    
    # Find the closest question to target difficulty
    best_match = min(QUESTION_BANK, key=lambda x: abs(x['difficulty'] - target_diff))
    return best_match