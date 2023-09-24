from typing import Sequence


def user_choice(prompt: str, options: Sequence[str]) -> int:
    """
    Prompts the user to choose from a list of options.

    :param prompt: Question to ask the user
    :param options: List of options to choose from
    :return: Index of chosen option
    """

    print(prompt)

    # Display the options
    for i, label in enumerate(options):
        print("{idx}: {label}".format(idx=i, label=label))

    # Prompt user until a valid answer is given
    while True:
        answer = input("Choice: ")
        int_answer = int(answer)
        if 0 <= int_answer < len(options):
            return int_answer
        print("Invalid answer")