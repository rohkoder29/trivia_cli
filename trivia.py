import json
import csv
import random
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

def load_questions(filename):
    try:
        with open(filename, 'r') as f:
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
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            return list(reader)
    except FileNotFoundError:
        with open(filename, 'w') as f:
            pass
        return []
    except csv.Error:
        console.print("[bold red]Error: Invalid high scores file format.[/bold red]")
        return []

def get_category_questions(questions, category):
    return [q for q in questions if q['category'] == category]

def ask_question(question):
    console.print(Panel.fit(f"[bold yellow]{question['question']}[/bold yellow]", title="Question", style="cyan"))
    answers = question['answers']
    random.shuffle(answers)

    for i, answer in enumerate(answers):
        console.print(f"[bold blue]{i+1}.[/bold blue] {answer}")

    while True:
        user_input = Prompt.ask("Enter the number of your answer")
        try:
            user_answer = int(user_input) - 1
            if 0 <= user_answer < len(answers):
                break
            else:
                console.print("[red]Invalid answer number. Try again.[/red]")
        except ValueError:
            console.print("[red]Invalid input. Please enter a number.[/red]")

    correct = answers[user_answer] == question['correct']
    if correct:
        console.print("[bold green]✅ Correct![/bold green]")
    else:
        console.print(f"[bold red]❌ Sorry, the correct answer is: [bold yellow]{question['correct']}[/bold yellow][/bold red]")
    return correct

def play_round(questions, category):
    category_questions = get_category_questions(questions, category)
    if not category_questions:
        console.print("[red]No questions available for this category.[/red]")
        return 0
    selected_questions = random.sample(category_questions, min(5, len(category_questions)))
    score = 0
    correct_answers = 0
    for index, question in enumerate(selected_questions, 1):
        console.print(f"\n[bold underline]Question {index}[/bold underline]")
        if ask_question(question):
            correct_answers += 1
            score += 3
    console.print(f"\n[bold green]✔ You got {correct_answers} out of {len(selected_questions)} correct![/bold green]")
    console.print(f"[bold cyan]⭐ Total Score: {score} points[/bold cyan]")
    return score

def view_stats(high_scores):
    if not high_scores:
        console.print("[yellow]No high scores available.[/yellow]")
        return
    table = Table(title="🏆 High Scores", box=box.ROUNDED, show_lines=True)
    table.add_column("Rank", justify="right", style="cyan", no_wrap=True)
    table.add_column("Username", style="magenta")
    table.add_column("Score", justify="right", style="green")

    sorted_scores = sorted(high_scores, key=lambda x: int(x[1]), reverse=True)
    for i, score in enumerate(sorted_scores):
        table.add_row(str(i+1), score[0], score[1])

    console.print(table)

def update_high_scores(high_scores, username, score):
    user_scores = [s for s in high_scores if s[0] == username]
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
                    update_high_scores(high_scores, username, score)
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

