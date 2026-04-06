# Adaptive Question Database with Test Cases

QUESTIONS = {
    1: [
        {
            "id": 1,
            "title": "Contains Duplicate",
            "difficulty": 1,
            "category": "Arrays",
            "description": "Given an integer array nums, return true if any value appears at least twice.",
            "example": "Input: nums = [1,2,3,1]\nOutput: true",
            "python_boilerplate": "class Solution:\n    def containsDuplicate(self, nums: list[int]) -> bool:\n        pass",
            "java_boilerplate": "class Solution {\n    public boolean containsDuplicate(int[] nums) {\n        return false;\n    }\n}",
            "javascript_boilerplate": "class Solution {\n    containsDuplicate(nums) {\n        return false;\n    }\n}",
            "python_test": "\nif __name__ == '__main__':\n    s = Solution()\n    assert s.containsDuplicate([1,2,3,1]) == True, 'Test 1 Failed'\n    assert s.containsDuplicate([1,2,3,4]) == False, 'Test 2 Failed'\n    print('ALL TESTS PASSED')",
            "java_test": "public class Main {\n    public static void main(String[] args) {\n        Solution s = new Solution();\n        if(s.containsDuplicate(new int[]{1,2,3,1}) != true) throw new RuntimeException(\"Test 1 Failed\");\n        if(s.containsDuplicate(new int[]{1,2,3,4}) != false) throw new RuntimeException(\"Test 2 Failed\");\n        System.out.println(\"ALL TESTS PASSED\");\n    }\n}",
            "js_test": "\nconst s = new Solution();\nif (s.containsDuplicate([1,2,3,1]) !== true) throw new Error('Test 1 Failed');\nif (s.containsDuplicate([1,2,3,4]) !== false) throw new Error('Test 2 Failed');\nconsole.log('ALL TESTS PASSED');"
        },
        {
            "id": 101,
            "title": "Valid Anagram",
            "difficulty": 1,
            "category": "Strings",
            "description": "Given two strings s and t, return true if t is an anagram of s, and false otherwise.",
            "example": "Input: s = \"anagram\", t = \"nagaram\"\nOutput: true",
            "python_boilerplate": "class Solution:\n    def isAnagram(self, s: str, t: str) -> bool:\n        pass",
            "java_boilerplate": "class Solution {\n    public boolean isAnagram(String s, String t) {\n        return false;\n    }\n}",
            "javascript_boilerplate": "class Solution {\n    isAnagram(s, t) {\n        return false;\n    }\n}",
            "python_test": "\nif __name__ == '__main__':\n    sol = Solution()\n    assert sol.isAnagram(\"anagram\", \"nagaram\") == True\n    assert sol.isAnagram(\"rat\", \"car\") == False\n    print('ALL TESTS PASSED')",
            "java_test": "public class Main {\n    public static void main(String[] args) {\n        Solution sol = new Solution();\n        if(!sol.isAnagram(\"anagram\", \"nagaram\")) throw new RuntimeException(\"Test 1 Failed\");\n        if(sol.isAnagram(\"rat\", \"car\")) throw new RuntimeException(\"Test 2 Failed\");\n        System.out.println(\"ALL TESTS PASSED\");\n    }\n}",
            "js_test": "\nconst sol = new Solution();\nif (sol.isAnagram(\"anagram\", \"nagaram\") !== true) throw new Error('Test 1 Failed');\nif (sol.isAnagram(\"rat\", \"car\") !== false) throw new Error('Test 2 Failed');\nconsole.log('ALL TESTS PASSED');"
        }
    ],
    2: [
        {
            "id": 2,
            "title": "Two Sum",
            "difficulty": 2,
            "category": "Arrays",
            "description": "Return indices of the two numbers such that they add up to target.",
            "example": "Input: nums = [2,7,11,15], target = 9\nOutput: [0,1]",
            "python_boilerplate": "class Solution:\n    def twoSum(self, nums: list[int], target: int) -> list[int]:\n        pass",
            "java_boilerplate": "class Solution {\n    public int[] twoSum(int[] nums, int target) {\n        return new int[]{};\n    }\n}",
            "javascript_boilerplate": "class Solution {\n    twoSum(nums, target) {\n        return [];\n    }\n}",
            "python_test": "\nif __name__ == '__main__':\n    s = Solution()\n    assert sorted(s.twoSum([2,7,11,15], 9)) == [0,1]\n    print('ALL TESTS PASSED')",
            "java_test": "import java.util.Arrays;\npublic class Main {\n    public static void main(String[] args) {\n        Solution s = new Solution();\n        int[] res = s.twoSum(new int[]{2,7,11,15}, 9);\n        Arrays.sort(res);\n        if(!Arrays.equals(res, new int[]{0,1})) throw new RuntimeException(\"Test Failed\");\n        System.out.println(\"ALL TESTS PASSED\");\n    }\n}",
            "js_test": "\nconst s = new Solution();\nconst res = s.twoSum([2,7,11,15], 9).sort((a,b)=>a-b);\nif (JSON.stringify(res) !== JSON.stringify([0,1])) throw new Error('Test Failed');\nconsole.log('ALL TESTS PASSED');"
        },
        {
            "id": 201,
            "title": "Palindrome Number",
            "difficulty": 2,
            "category": "Math",
            "description": "Given an integer x, return true if x is a palindrome, and false otherwise.",
            "example": "Input: x = 121\nOutput: true",
            "python_boilerplate": "class Solution:\n    def isPalindrome(self, x: int) -> bool:\n        pass",
            "java_boilerplate": "class Solution {\n    public boolean isPalindrome(int x) {\n        return false;\n    }\n}",
            "javascript_boilerplate": "class Solution {\n    isPalindrome(x) {\n        return false;\n    }\n}",
            "python_test": "\nif __name__ == '__main__':\n    sol = Solution()\n    assert sol.isPalindrome(121) == True\n    assert sol.isPalindrome(-121) == False\n    print('ALL TESTS PASSED')",
            "java_test": "public class Main {\n    public static void main(String[] args) {\n        Solution sol = new Solution();\n        if(!sol.isPalindrome(121)) throw new RuntimeException(\"Test 1 Failed\");\n        if(sol.isPalindrome(-121)) throw new RuntimeException(\"Test 2 Failed\");\n        System.out.println(\"ALL TESTS PASSED\");\n    }\n}",
            "js_test": "\nconst sol = new Solution();\nif (sol.isPalindrome(121) !== true) throw new Error('Test 1 Failed');\nif (sol.isPalindrome(-121) !== false) throw new Error('Test 2 Failed');\nconsole.log('ALL TESTS PASSED');"
        }
    ],
    3: [
        {
            "id": 301,
            "title": "Fibonacci Number",
            "difficulty": 3,
            "category": "DP",
            "description": "The Fibonacci numbers, commonly denoted F(n) form a sequence, such that each number is the sum of the two preceding ones.",
            "example": "Input: n = 4\nOutput: 3",
            "python_boilerplate": "class Solution:\n    def fib(self, n: int) -> int:\n        pass",
            "java_boilerplate": "class Solution {\n    public int fib(int n) {\n        return 0;\n    }\n}",
            "javascript_boilerplate": "class Solution {\n    fib(n) {\n        return 0;\n    }\n}",
            "python_test": "\nif __name__ == '__main__':\n    sol = Solution()\n    assert sol.fib(4) == 3\n    assert sol.fib(2) == 1\n    print('ALL TESTS PASSED')",
            "java_test": "public class Main {\n    public static void main(String[] args) {\n        Solution sol = new Solution();\n        if(sol.fib(4) != 3) throw new RuntimeException(\"Test Failed\");\n        System.out.println(\"ALL TESTS PASSED\");\n    }\n}",
            "js_test": "\nconst sol = new Solution();\nif (sol.fib(4) !== 3) throw new Error('Test Failed');\nconsole.log('ALL TESTS PASSED');"
        }
    ]
}

def get_question_by_difficulty(level, index=0):
    max_level = max(QUESTIONS.keys())
    target_level = min(max(1, level), max_level)
    level_questions = QUESTIONS.get(target_level, QUESTIONS[1])
    return level_questions[index % len(level_questions)]

def get_question_by_id(q_id):
    for level in QUESTIONS.values():
        for q in level:
            if q["id"] == q_id:
                return q
    return None
