import json
import csv
import random
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.panel import Panel

console = Console()

def load_questions(filename):
    try:
        with open(filename, 'r', encoding='utf-8', newline='') as f:
            questions = json.load(f)
            return questions
    except FileNotFoundError:
        console.print("[bold red]Error: Questions file not found.[/bold red]")
        return []
    except json.JSONDecodeError:
        console.print("[bold red]Error: Invalid JSON format.[/bold red]")
        return []

def load_high_scores(filename):
    try:
        with open(filename, 'r', encoding='utf-8', newline='') as f:
            reader = csv.reader(f)
            high_scores = list(reader)

            # Sort by score descending, preserve insertion order for ties
            sorted_scores = sorted(high_scores, key=lambda x: -int(x[1]))

            # Keep only top 5
            top_five = sorted_scores[:5]

        # Optional: clean up the file to reflect valid state
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(top_five)

        return top_five

    except FileNotFoundError:
        with open(filename, 'w', encoding='utf-8') as f:
            pass
        return []

    except (csv.Error, ValueError, IndexError):
        print("Error: Invalid high scores file format.")
        return []


def get_category_questions(questions, category):
    return [q for q in questions if q['category'] == category]

def ask_question(question, index, total):
    console.rule(f"[bold blue]Question {index} of {total}")
    console.print(Panel.fit(question['question'], style="bold"))

    answers = question['answers']
    random.shuffle(answers)

    for i, answer in enumerate(answers, 1):
        console.print(f"[cyan]{i}.[/cyan] {answer}")

    user_input = console.input("\n[bold]Enter the number of your answer:[/bold] ")
    try:
        choice = int(user_input) - 1
        if choice < 0 or choice >= len(answers):
            console.print("[red]Invalid answer. Please try again.[/red]")
            return ask_question(question, index, total)
    except ValueError:
        console.print("[red]Invalid input. Please enter a number.[/red]")
        return ask_question(question, index, total)

    correct = answers[choice] == question['correct']
    if correct:
        console.print("[bold green]✔ Correct![/bold green]\n")
    else:
        console.print(f"[bold red]✘ Sorry, the correct answer was: [yellow]{question['correct']}[/yellow][/bold red]\n")
    return correct


def play_round(questions, category):
    category_questions = get_category_questions(questions, category)
    if not category_questions:
        console.print("[red]No questions available for this category.[/red]")
        return 0
    selected_questions = random.sample(category_questions, min(5, len(category_questions)))
    score = 0
    correct_answers = 0
    for idx, question in enumerate(selected_questions, 1):
        if ask_question(question, idx, len(selected_questions)):
            correct_answers += 1
            score += 3
    console.print(f"\n[bold green]✔ You got {correct_answers} out of {len(selected_questions)} correct![/bold green]")
    console.print(f"[bold cyan]⭐ Total Score: {score} points[/bold cyan]")
    return score

def view_stats(high_scores):
    if not high_scores:
        console.print("[yellow]No high scores available.[/yellow]")
        return

    table = Table(title="🏆 High Scores", header_style="bold magenta")
    table.add_column("Rank", justify="right")
    table.add_column("Username", style="cyan")
    table.add_column("Score", justify="right", style="green")

    for i, (name, score) in enumerate(high_scores, 1):
        table.add_row(str(i), name, score)

    console.print(table)

def update_high_scores(high_scores, username, score):
    user_scores = [entry for entry in high_scores if entry[0] == username]
    if user_scores:
        existing_score = int(user_scores[0][1])
        if score > existing_score:
            high_scores.remove(user_scores[0])
            high_scores.append([username, str(score)])
    else:
        high_scores.append([username, str(score)])

    # Sort by score (descending), preserve insertion order for ties
    sorted_scores = sorted(high_scores, key=lambda x: -int(x[1]))

    # change this number to keep more or less top scores
    top_five = sorted_scores[:5]

    with open('high_scores.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(top_five)
    
    return top_five


def main():
    questions = load_questions('questions.json')
    if not questions:
        return
    high_scores = load_high_scores('high_scores.csv')
    categories = list(set(q['category'] for q in questions))

    console.print(Panel.fit("🎉 Welcome to the [bold cyan]Trivia Game[/bold cyan]! 🎉", style="bold white on blue"))
    username = Prompt.ask("Enter your username")

    while True:
        console.print("\n[bold]Main Menu[/bold]")
        console.print("[blue]1.[/blue] Play Game")
        console.print("[blue]2.[/blue] View Stats")
        console.print("[blue]3.[/blue] Quit")

        choice = Prompt.ask("Enter your choice", choices=["1", "2", "3"])

        if choice == '1':
            console.print("\n[bold]Available Categories:[/bold]")
            for i, category in enumerate(categories):
                console.print(f"[cyan]{i+1}.[/cyan] {category}")
            try:
                category_choice = int(Prompt.ask("Enter the number of your chosen category")) - 1
                if 0 <= category_choice < len(categories):
                    score = play_round(questions, categories[category_choice])
                    high_scores = update_high_scores(high_scores, username, score)
                else:
                    console.print("[red]Invalid category choice. Please try again.[/red]")
            except ValueError:
                console.print("[red]Invalid input. Please enter a number.[/red]")

        elif choice == '2':
            view_stats(high_scores)
        elif choice == '3':
            console.print("\n[bold green]Thanks for playing! Goodbye! 👋[/bold green]")
            break

if __name__ == '__main__':
    main()

