class Solution:
    def is_valid_parenthesis(self, s: str) -> str:
        annotation = [' '] * len(s)
        stk_left = []           # stack for pos of unmatched left parenthesis
        mismatched_right = []   # pos of mismatched right parenthesis
        for i, c in enumerate(s):
            if c == '(':
                stk_left.append(i)
            elif c == ')':
                if stk_left:
                    stk_left.pop()
                else:
                    mismatched_right.append(i)
        # Annotate the result list for unmatched parenthesis
        for idx in stk_left:
            annotation[idx] = 'x'
        for idx in mismatched_right:
            annotation[idx] = '?'
        return ''.join(annotation)
    

def run_tests():
    solution = Solution()
    test_cases = {
        'bge)))))))))': '   ?????????',
        '((IIII))))))': '        ????',
        '()()()()(uuu': '        x   ',
        '))))UUUU((()': '????    xx  '
    }

    for case, expected_annotation in test_cases.items():
        actual_annotation = solution.is_valid_parenthesis(case)
        assert actual_annotation == expected_annotation, \
            f'ERROR in case {case}: expected {expected_annotation}, got {actual_annotation}'
        print('[PASSED]')
        print(f'\'{case}\'\n\'{actual_annotation}\'\n')

run_tests()