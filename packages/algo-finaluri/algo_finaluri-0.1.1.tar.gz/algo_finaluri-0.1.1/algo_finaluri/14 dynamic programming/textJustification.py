from typing import List

class Solution:
    def fullJustify(self, words: List[str], maxWidth: int) -> List[str]:
        res = []
        i = 0
        width = 0
        cur_line = []

        while i < len(words):
            cur_word = words[i]

            if width + len(cur_word) <= maxWidth:
                cur_line.append(cur_word)
                width += len(cur_word) + 1
                i += 1
            else:
                spaces = maxWidth - width + len(cur_line)
                added = 0
                j = 0

                while added < spaces:
                    if j >= len(cur_line) - 1:
                        j = 0
                    cur_line[j] += " "
                    added += 1
                    j += 1

                res.append("".join(cur_line))
                cur_line = []
                width = 0

        for word in range(len(cur_line) - 1):
            cur_line[word] += " "

        cur_line[-1] += " " * (maxWidth - width + 1)
        res.append("".join(cur_line))

        return res


def run_examples():
    solution = Solution()

    examples = [
        {
            "words": ["This", "is", "an", "example", "of", "text", "justification."],
            "maxWidth": 16
        },
        {
            "words": ["What","must","be","acknowledgment","shall","be"],
            "maxWidth": 16
        },
        {
            "words": ["Science","is","what","we","understand","well","enough","to","explain","to","a","computer.","Art","is","everything","else","we","do"],
            "maxWidth": 20
        }
    ]

    for idx, example in enumerate(examples, 1):
        print(f"Example {idx}:")
        output = solution.fullJustify(example["words"], example["maxWidth"])
        for line in output:
            print(f'"{line}"')
        print("-" * 40)


run_examples()
