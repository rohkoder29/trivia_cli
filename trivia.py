import json
import csv
import random

def load_questions(filename):
    try:
        with open(filename, 'r') as f:
            questions = json.load(f)
            return questions
    except FileNotFoundError:
        print("Error: Questions file not found.")
        return []
    except json.JSONDecodeError:
        print("Error: Invalid JSON format.")
        return []

def load_high_scores(filename):
    try:
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            high_scores = list(reader)
            return high_scores
    except FileNotFoundError:
        with open(filename, 'w') as f:
            pass
        return []
    except csv.Error:
        print("Error: Invalid high scores file format.")
        return []

def get_category_questions(questions, category):
    return [q for q in questions if q['category'] == category]

def ask_question(question):
    print(question['question'])
    answers = question['answers']
    random.shuffle(answers)
    for i, answer in enumerate(answers):
        print(f"{i+1}. {answer}")
    while True:
        user_answer = input("Enter the number of your answer: ")
        try:
            user_answer = int(user_answer)
            if user_answer < 1 or user_answer > len(answers):
                print("Invalid answer. Please enter a valid number.")
            else:
                break
        except ValueError:
            print("Invalid input. Please enter a number.")
    correct = answers[user_answer - 1] == question['correct']
    if correct:
        print("Correct!")
    else:
        print(f"Sorry, the correct answer is {question['correct']}.")
    return correct

def play_round(questions, category):
    category_questions = get_category_questions(questions, category)
    if not category_questions:
        print("No questions available for this category.")
        return
    random_questions = random.sample(category_questions, 5)
    score = 0
    correct_answers = 0
    for question in random_questions:
        if ask_question(question):
            correct_answers += 1
            score += 3
    print(f"You got {correct_answers} correct answers out of 5 questions.")
    print(f"Your total score is {score} points.")
    return score

def view_stats(high_scores):
    if not high_scores:
        print("No high scores available.")
        return
    print("\nHigh Scores:")
    print("----------------")
    sorted_scores = sorted(high_scores, key=lambda x: int(x[1]), reverse=True)
    for i, score in enumerate(sorted_scores):
        print(f"{i+1}. {score[0]} - {score[1]} points")
    print("----------------\n")

def update_high_scores(high_scores, username, score):
    user_scores = [score for score in high_scores if score[0] == username]
    if user_scores:
        if int(user_scores[0][1]) < score:
            high_scores.remove(user_scores[0])
            high_scores.append([username, str(score)])
    else:
        high_scores.append([username, str(score)])
    sorted_scores = sorted(high_scores, key=lambda x: int(x[1]), reverse=True)
    with open('high_scores.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(sorted_scores)

def main():
    questions = load_questions('questions.json')
    if not questions:
        return
    high_scores = load_high_scores('high_scores.csv')
    categories = list(set(q['category'] for q in questions))
    print("Welcome to the trivia game!")
    username = input("Enter your username: ")
    while True:
        print("\n1. Play game")
        print("2. View stats")
        print("3. Quit")
        choice = input("Enter your choice: ")
        if choice == '1':
            print("Categories:")
            for i, category in enumerate(categories):
                print(f"{i+1}. {category}")
            category_choice = input("Enter the number of your chosen category: ")
            try:
                category_choice = int(category_choice) - 1
                if category_choice < 0 or category_choice >= len(categories):
                    print("Invalid category choice. Please try again.")
                    continue
            except ValueError:
                print("Invalid input. Please enter a number.")
                continue
            score = play_round(questions, categories[category_choice])
            update_high_scores(high_scores, username, score)
        elif choice == '2':
            view_stats(high_scores)
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == '__main__':
    main()