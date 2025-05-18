import json
import csv
import random
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.panel import Panel

console = Console()

def load_config(filepath="config.json"):
    default_config = {
        "num_questions": 5,
        "points_per_correct_answer": 3,
        "top_high_scores": 5,
    }
    config_path = Path(filepath)
    if config_path.is_file():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                user_config = json.load(f)
            return {**default_config, **user_config}
        except (json.JSONDecodeError, TypeError):
            pass  # fall back to default if corrupted
    return default_config

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

def sanitize_username(username):
    return username.strip()

def sanitize_score(score_input):
    try:
        score = int(str(score_input).strip())
        return str(score)
    except (ValueError, AttributeError):
        return None

def load_high_scores(filename):
    valid_scores = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) != 2:
                    continue  # Skip malformed rows
                username = sanitize_username(row[0])
                score = sanitize_score(row[1])
                if score is not None:
                    valid_scores.append([username, score])
    except FileNotFoundError:
        with open(filename, 'w', encoding='utf-8') as f:
            pass  # Create the file if it doesn't exist
    except csv.Error:
        print("Error: Invalid high scores file format.")

    return valid_scores

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
    selected_questions = random.sample(category_questions, min(NUM_QUESTIONS, len(category_questions)))
    score = 0
    correct_answers = 0
    for idx, question in enumerate(selected_questions, 1):
        if ask_question(question, idx, len(selected_questions)):
            correct_answers += 1
            score += POINTS_PER_CORRECT_ANSWER
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
        table.add_row(str(i), sanitize_username(name), sanitize_score(score))

    console.print(table)

def update_high_scores(high_scores, username, score, filename='high_scores.csv'):
    # Check if user already has a score
    existing = [entry for entry in high_scores if entry[0] == username]
    if existing:
        existing_score = existing[0][1]
        if score > existing_score:
            high_scores.remove(existing[0])
            high_scores.append([username, score])
    else:
        high_scores.append([username, score])

    # Sort descending, keep top 5
    sorted_scores = sorted(high_scores, key=lambda x: -int(x[1]))
    top_high_scores = sorted_scores[:TOP_HIGH_SCORES]

    # Write top 5 back to file
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        for row in top_high_scores:
            writer.writerow(row)

    return top_high_scores

def main():
    questions = load_questions('questions.json')
    if not questions:
        return
    high_scores = load_high_scores('high_scores.csv')
    categories = list(set(q['category'] for q in questions))

    console.print(Panel.fit("🎉 Welcome to the [bold cyan]Trivia Game[/bold cyan]! 🎉", style="bold white on blue"))
    username = sanitize_username(Prompt.ask("Enter your username"))

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
    CONFIG = load_config()
    NUM_QUESTIONS = CONFIG.get("num_questions", 5)
    POINTS_PER_CORRECT_ANSWER = CONFIG.get("points_per_correct_answer", 3)
    TOP_HIGH_SCORES = CONFIG.get("top_high_scores", 5)
    main()
