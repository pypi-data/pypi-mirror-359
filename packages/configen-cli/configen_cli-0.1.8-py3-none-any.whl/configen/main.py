from rich.console import Console
from rich.prompt import Prompt
import asyncio
import typer

from configen import system, api, property, runner

app = typer.Typer()
console = Console()


def server_error(http_code, http_body):
    if http_code != 200:
        console.print(f"❌ [bold red]Server error:[/bold red] [italic]{http_body}[/italic]")
        return True
    return False


async def run_repl():
    if not system.has_internet():
        console.print("❌ [bold red]No internet connection![/bold red] [dim]🔌 Please check your network and try again.[/dim]")
        return None

    if not property.CONFIGEN_API_KEY:
        console.print("🚫 [bold red]Missing API Key![/bold red] [dim]🔐 Set it in your .env [/dim] [green]💡 Tip: Generate it from your user dashboard[/green] [link=https://dashboard.configen.ai][underline]https://dashboard.configen.ai[/underline][/link]")
        return None

    http_code, http_body = await api.start_session()
    if server_error(http_code, http_body):
        return None

    session_id = http_body['session_id']
    prompt_max_attempts = int(http_body['prompt_max_attempts'])

    console.print(f"🚀 [bold green]Welcome to Configen CLI (v{property.CONFIGEN_APP_VERSION})[/bold green]")
    console.print("🤖 Configen is a tool that configures your system using natural language. For example, type [bold]Install openjdk[/bold] and it will handle the rest.")
    console.print("ℹ️ Enter [bold]/help[/bold] to view commands. Use [bold]/new[/bold] to restart. Exit with [bold]/exit[/bold] or [bold]Ctrl+C[/bold].")
    console.print("_" * 50)
    console.print("👋 Hi boss! What do you need done today?")

    while True:
        try:
            user_ask = Prompt.ask("configen").strip()
            if not user_ask:
                continue
            if user_ask == "/exit":
                console.print("👋 Goodbye boss!")
                break
            elif user_ask == "/help":
                console.print("""
[bold cyan]Available commands:[/bold cyan]

  [bold]/help[/bold]  Show this help message  
  [bold]/new[/bold]   Restart the session  
  [bold]/exit[/bold]  Exit the CLI
""")
            elif user_ask == "/new":
                console.print("🔄 Restarting Configen session...")
                return await run_repl()
            else:
                http_code, http_body = await api.add_conversation(session_id, user_ask, property.CLI_INPUT_USR_ASK)
                if server_error(http_code, http_body):
                    return None

                pma = prompt_max_attempts
                completed = False

                while not completed and pma > 0:
                    if "commands" in http_body:
                        for command in http_body["commands"]:
                            console.print(f"{command["description"]}")
                            console.print(f"▶️ [bold]Running:[/bold] [italic]{command["command"]}[/italic]")
                            code, stdout = runner.run_with_subprocess(command["command"])
                            if code == 10:
                                console.print(f"[bold red]{stdout}[/bold red]")
                                return None
                            elif code == 1:
                                cli_input = f"When running the command {command["command"]}, the following error occurred: {stdout}"
                                http_code, http_body = await api.add_conversation(session_id, cli_input, property.CLI_INPUT_CMD_ERROR)
                                if server_error(http_code, http_body):
                                    return None
                                else:
                                    continue
                            elif command["output_required"]:
                                cli_input = f'You requested the output of "{command["command"]}". Here it is:\n{stdout}'
                                http_code, http_body = await api.add_conversation(session_id, cli_input, property.CLI_INPUT_CMD_OUTPUT)
                                if server_error(http_code, http_body):
                                    return None
                                else:
                                    continue
                    elif "question" in http_body:
                        console.print(f"❓ [bold]Question:[/bold] {http_body["question"]}")
                        user_answer = Prompt.ask("answer").strip()
                        cli_input = f'You asked: "{http_body["question"]}", user has responded with: "{user_answer}".'
                        http_code, http_body = await api.add_conversation(session_id, cli_input, property.CLI_INPUT_USR_ANSWER)
                        if server_error(http_code, http_body):
                            return None
                        else:
                            continue
                    elif "completed" in http_body:
                        if http_body["completed"]:
                            console.print(f"✅ [bold green]{http_body["message"]}[/bold green]")
                        else:
                            console.print(f"❌ [bold red]{http_body["message"]}[/bold red]")
                        completed = True
                        break
                    pma -= 1

                if not completed and pma == 0:
                    console.print(f"🤷‍♂️ [bold yellow]Tried {prompt_max_attempts} times but couldn’t complete the task. Try asking more specifically.[/bold yellow]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n👋 Goodbye boss!")
            break


@app.command()
def main():
    asyncio.run(run_repl())


if __name__ == "__main__":
    app()
