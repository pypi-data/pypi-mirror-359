import typer
from typing import Annotated
from pathlib import Path
from . import k as identify_k

app = typer.Typer(invoke_without_command=True)

@app.command(name='k')
def k(
        bag: Annotated[Path, typer.Argument(help='Path to the bag file',)],
        interval: Annotated[float, typer.Option(help='Interval per step in seconds')] = None,
        k_max: Annotated[float, typer.Option(help='Maximum K value')] = 1.03,
        k_min: Annotated[float, typer.Option(help='Minimum K value')] = 0.97,
        tc_max: Annotated[float, typer.Option(help='Maximum time constant (tc)')] = 2.0,
        tc_min: Annotated[float, typer.Option(help='Minimum time constant (tc)')] = 0.01,
        delay_steps_max: Annotated[int, typer.Option(help='Maximum delay steps')] = 30,
        display: Annotated[bool, typer.Option(help='Display graphs')] = False,
):
    identify_k.main(bag, interval, k_max, k_min, tc_max, tc_min, delay_steps_max, display)

def main():
    app()

if __name__ == "__main__":
    main()
