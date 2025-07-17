from django.core.management.base import BaseCommand
from apps.dsa.models import DSAQuestion

class Command(BaseCommand):
    help = 'Load sample DSA questions'

    def handle(self, *args, **kwargs):
        questions = [
            {
                'title': 'Two Sum',
                'description': 'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.',
                'difficulty': 'easy',
                'category': 'array',
                'examples': 'Input: nums = [2,7,11,15], target = 9\nOutput: [0,1]\nExplanation: nums[0] + nums[1] == 9',
                'constraints': '2 <= nums.length <= 10^4\n-10^9 <= nums[i] <= 10^9',
                'time_complexity': 'O(n)',
                'space_complexity': 'O(n)'
            },
            {
                'title': 'Valid Parentheses',
                'description': 'Given a string s containing just the characters (, ), {, }, [ and ], determine if the input string is valid.',
                'difficulty': 'easy',
                'category': 'string',
                'examples': 'Input: s = "()"\nOutput: true',
                'constraints': '1 <= s.length <= 10^4',
                'time_complexity': 'O(n)',
                'space_complexity': 'O(n)'
            },
            {
                'title': 'Merge Two Sorted Lists',
                'description': 'You are given the heads of two sorted linked lists list1 and list2. Merge the two lists in a one sorted list.',
                'difficulty': 'easy',
                'category': 'linkedlist',
                'examples': 'Input: list1 = [1,2,4], list2 = [1,3,4]\nOutput: [1,1,2,3,4,4]',
                'constraints': 'The number of nodes in both lists is in the range [0, 50].',
                'time_complexity': 'O(n + m)',
                'space_complexity': 'O(1)'
            },
            {
                'title': 'Maximum Subarray',
                'description': 'Given an integer array nums, find the contiguous subarray which has the largest sum and return its sum.',
                'difficulty': 'medium',
                'category': 'array',
                'examples': 'Input: nums = [-2,1,-3,4,-1,2,1,-5,4]\nOutput: 6\nExplanation: [4,-1,2,1] has the largest sum = 6.',
                'constraints': '1 <= nums.length <= 10^5\n-10^4 <= nums[i] <= 10^4',
                'time_complexity': 'O(n)',
                'space_complexity': 'O(1)'
            },
            {
                'title': 'Longest Palindromic Substring',
                'description': 'Given a string s, return the longest palindromic substring in s.',
                'difficulty': 'medium',
                'category': 'string',
                'examples': 'Input: s = "babad"\nOutput: "bab"\nExplanation: "aba" is also a valid answer.',
                'constraints': '1 <= s.length <= 1000',
                'time_complexity': 'O(n^2)',
                'space_complexity': 'O(1)'
            },
            {
                'title': 'Binary Tree Inorder Traversal',
                'description': 'Given the root of a binary tree, return the inorder traversal of its nodes\' values.',
                'difficulty': 'medium',
                'category': 'tree',
                'examples': 'Input: root = [1,null,2,3]\nOutput: [1,3,2]',
                'constraints': 'The number of nodes in the tree is in the range [0, 100].',
                'time_complexity': 'O(n)',
                'space_complexity': 'O(n)'
            },
            {
                'title': 'Median of Two Sorted Arrays',
                'description': 'Given two sorted arrays nums1 and nums2 of size m and n respectively, return the median of the two sorted arrays.',
                'difficulty': 'hard',
                'category': 'array',
                'examples': 'Input: nums1 = [1,3], nums2 = [2]\nOutput: 2.00000\nExplanation: merged array = [1,2,3] and median is 2.',
                'constraints': 'nums1.length == m\nnums2.length == n\n0 <= m <= 1000\n0 <= n <= 1000',
                'time_complexity': 'O(log(min(m,n)))',
                'space_complexity': 'O(1)'
            },
            {
                'title': 'Trapping Rain Water',
                'description': 'Given n non-negative integers representing an elevation map where the width of each bar is 1, compute how much water it can trap after raining.',
                'difficulty': 'hard',
                'category': 'array',
                'examples': 'Input: height = [0,1,0,2,1,0,1,3,2,1,2,1]\nOutput: 6\nExplanation: The above elevation map (black section) is represented by array [0,1,0,2,1,0,1,3,2,1,2,1]. In this case, 6 units of rain water (blue section) are being trapped.',
                'constraints': 'n == height.length\n1 <= n <= 2 * 10^4\n0 <= height[i] <= 3 * 10^4',
                'time_complexity': 'O(n)',
                'space_complexity': 'O(1)'
            },
            {
                'title': 'Longest Common Subsequence',
                'description': 'Given two strings text1 and text2, return the length of their longest common subsequence.',
                'difficulty': 'medium',
                'category': 'dp',
                'examples': 'Input: text1 = "abcde", text2 = "ace"\nOutput: 3\nExplanation: The longest common subsequence is "ace" and its length is 3.',
                'constraints': '1 <= text1.length, text2.length <= 1000',
                'time_complexity': 'O(m * n)',
                'space_complexity': 'O(m * n)'
            },
            {
                'title': 'Quick Sort',
                'description': 'Implement the quicksort algorithm to sort an array of integers.',
                'difficulty': 'medium',
                'category': 'sorting',
                'examples': 'Input: [3,6,8,10,1,2,1]\nOutput: [1,1,2,3,6,8,10]',
                'constraints': '1 <= arr.length <= 10^4\n-10^4 <= arr[i] <= 10^4',
                'time_complexity': 'O(n log n) average, O(n^2) worst',
                'space_complexity': 'O(log n)'
            }
        ]
        
        for q in questions:
            DSAQuestion.objects.create(**q)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully loaded {len(questions)} questions'))