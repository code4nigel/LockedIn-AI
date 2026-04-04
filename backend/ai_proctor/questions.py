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
            "python_test": "\nif __name__ == '__main__':\n    s = Solution()\n    assert s.containsDuplicate([1,2,3,1]) == True, 'Test 1 Failed: [1,2,3,1]'\n    assert s.containsDuplicate([1,2,3,4]) == False, 'Test 2 Failed: [1,2,3,4]'\n    print('ALL TESTS PASSED')",
            "java_test": "public class Main {\n    public static void main(String[] args) {\n        Solution s = new Solution();\n        if(s.containsDuplicate(new int[]{1,2,3,1}) != true) throw new RuntimeException(\"Test 1 Failed: [1,2,3,1]\");\n        if(s.containsDuplicate(new int[]{1,2,3,4}) != false) throw new RuntimeException(\"Test 2 Failed: [1,2,3,4]\");\n        System.out.println(\"ALL TESTS PASSED\");\n    }\n}"
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
            "python_test": "\nif __name__ == '__main__':\n    s = Solution()\n    assert sorted(s.twoSum([2,7,11,15], 9)) == [0,1], 'Test 1 Failed'\n    assert sorted(s.twoSum([3,2,4], 6)) == [1,2], 'Test 2 Failed'\n    print('ALL TESTS PASSED')",
            "java_test": "import java.util.Arrays;\npublic class Main {\n    public static void main(String[] args) {\n        Solution s = new Solution();\n        int[] res1 = s.twoSum(new int[]{2,7,11,15}, 9);\n        Arrays.sort(res1);\n        if(!Arrays.equals(res1, new int[]{0,1})) throw new RuntimeException(\"Test 1 Failed\");\n        System.out.println(\"ALL TESTS PASSED\");\n    }\n}"
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