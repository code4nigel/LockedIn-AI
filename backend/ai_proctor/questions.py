# NeetCode 250 Seed Data - Core Patterns
# Categories: Arrays, Two Pointers, Sliding Window, Stack, Binary Search

QUESTIONS = {
    1: [
        {"id": 1, "title": "Contains Duplicate", "difficulty": 1, "category": "Arrays", "description": "Given an integer array nums, return true if any value appears at least twice.", "example": "Input: nums = [1,2,3,1]\nOutput: true"},
        {"id": 2, "title": "Concatenation of Array", "difficulty": 1, "category": "Arrays", "description": "Given an array nums, create an array ans of length 2n where ans[i] == nums[i].", "example": "Input: nums = [1,2,1]\nOutput: [1,2,1,1,2,1]"}
    ],
    2: [
        {"id": 3, "title": "Valid Anagram", "difficulty": 2, "category": "Arrays", "description": "Given two strings s and t, return true if t is an anagram of s.", "example": "Input: s = 'rat', t = 'car'\nOutput: false"},
        {"id": 4, "title": "Replace Elements with Greatest on Right", "difficulty": 2, "category": "Arrays", "description": "Replace every element in the array with the greatest element among the elements to its right.", "example": "Input: arr = [17,18,5,4,6,1]\nOutput: [18,6,6,6,1,-1]"}
    ],
    3: [
        {"id": 5, "title": "Two Sum", "difficulty": 3, "category": "Arrays", "description": "Return indices of the two numbers such that they add up to target.", "example": "Input: nums = [2,7,11,15], target = 9\nOutput: [0,1]"},
        {"id": 6, "title": "Length of Last Word", "difficulty": 3, "category": "Arrays", "description": "Return the length of the last word in the string.", "example": "Input: s = 'Hello World'\nOutput: 5"}
    ],
    4: [
        {"id": 7, "title": "Group Anagrams", "difficulty": 4, "category": "Arrays", "description": "Group the anagrams together from an array of strings.", "example": "Input: strs = ['eat','tea','tan']\nOutput: [['eat','tea'],['tan']]"},
        {"id": 8, "title": "Longest Common Prefix", "difficulty": 4, "category": "Arrays", "description": "Find the longest common prefix string amongst an array of strings.", "example": "Input: strs = ['flower','flow','flight']\nOutput: 'fl'"}
    ],
    5: [
        {"id": 9, "title": "Top K Frequent Elements", "difficulty": 5, "category": "Arrays", "description": "Return the k most frequent elements in an array.", "example": "Input: nums = [1,1,1,2,2,3], k = 2\nOutput: [1,2]"},
        {"id": 10, "title": "Valid Palindrome", "difficulty": 5, "category": "Two Pointers", "description": "Check if a string is a palindrome, ignoring non-alphanumeric characters.", "example": "Input: s = 'race a car'\nOutput: false"}
    ],
    6: [
        {"id": 11, "title": "Product of Array Except Self", "difficulty": 6, "category": "Arrays", "description": "Return an array where each element is the product of all elements except itself.", "example": "Input: nums = [1,2,3,4]\nOutput: [24,12,8,6]"},
        {"id": 12, "title": "Two Sum II", "difficulty": 6, "category": "Two Pointers", "description": "Same as Two Sum, but the input array is already sorted.", "example": "Input: numbers = [2,7,11,15], target = 9\nOutput: [1,2]"}
    ],
    7: [
        {"id": 13, "title": "3Sum", "difficulty": 7, "category": "Two Pointers", "description": "Find all unique triplets in the array that sum up to zero.", "example": "Input: nums = [-1,0,1,2,-1,-4]\nOutput: [[-1,-1,2],[-1,0,1]]"},
        {"id": 14, "title": "Container With Most Water", "difficulty": 7, "category": "Two Pointers", "description": "Find two lines that together with the x-axis forms a container that holds the most water.", "example": "Input: height = [1,8,6,2,5,4,8,3,7]\nOutput: 49"}
    ],
    8: [
        {"id": 15, "title": "Best Time to Buy and Sell Stock", "difficulty": 8, "category": "Sliding Window", "description": "Find the maximum profit you can achieve from a single buy and sell.", "example": "Input: prices = [7,1,5,3,6,4]\nOutput: 5"},
        {"id": 16, "title": "Longest Substring Without Repeating Characters", "difficulty": 8, "category": "Sliding Window", "description": "Find the length of the longest substring without repeating characters.", "example": "Input: s = 'abcabcbb'\nOutput: 3"}
    ],
    9: [
        {"id": 17, "title": "Valid Parentheses", "difficulty": 9, "category": "Stack", "description": "Check if brackets (), {}, [] are closed in the correct order.", "example": "Input: s = '()[]{}'\nOutput: true"},
        {"id": 18, "title": "Binary Search", "difficulty": 9, "category": "Binary Search", "description": "Search target in a sorted array in O(log n) time.", "example": "Input: nums = [-1,0,3,5,9,12], target = 9\nOutput: 4"}
    ],
    10: [
        {"id": 19, "title": "Min Stack", "difficulty": 10, "category": "Stack", "description": "Design a stack that supports push, pop, top, and retrieving the minimum element in constant time.", "example": "Methods: push(-2), push(0), push(-3), getMin() -> -3"},
        {"id": 20, "title": "Search a 2D Matrix", "difficulty": 10, "category": "Binary Search", "description": "Efficiently search for a value in an m x n matrix where each row is sorted.", "example": "Input: matrix = [[1,3,5,7],[10,11,16,20]], target = 3\nOutput: true"}
    ]
}

def get_question_by_difficulty(level, index=0):
    max_level = max(QUESTIONS.keys())
    target_level = min(max(1, level), max_level)
    level_questions = QUESTIONS.get(target_level, QUESTIONS[1])
    return level_questions[index % len(level_questions)]