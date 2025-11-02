from __future__ import annotations

import shlex
import sys
import time
from pathlib import Path
from typing import List

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

from emergence.dashboard import Dashboard
from emergence.entities import Herbivore, Plant
from emergence.visualization import Visualizer
from emergence.world import World

# Import gameplay systems
try:
    from emergence.gameplay import GameplaySystem
    from emergence.game_modes import GameModeType, ChallengeType
    from emergence.progression import UnlockType
    GAMEPLAY_ENABLED = True
except ImportError:
    GAMEPLAY_ENABLED = False


class EmergenceCLI:
    """Interactive CLI interface for EMERGENCE simulator."""

    def __init__(self) -> None:
        self.console = Console()
        self.world = World()
        self.visualizer = Visualizer(self.world)
        self.dashboard = Dashboard(self.world, self.console)
        self.auto_mode = False
        self.speed_multiplier = 1.0
        self.gameplay: GameplaySystem | None = GameplaySystem(self.world, self.console) if GAMEPLAY_ENABLED else None
        self._bootstrap_ecosystem()

    def _bootstrap_ecosystem(self) -> None:
        for _ in range(40):
            self.world.spawn_plant()
        for _ in range(10):
            self.world.spawn_herbivore()

    def run(self) -> None:
        self.console.print(Panel("[bold cyan]Welcome to EMERGENCE[/bold cyan]\nType 'help' for commands."))
        while True:
            try:
                command_line = self.console.input("[bold green]>[/bold green] ")
            except (EOFError, KeyboardInterrupt):
                self.console.print("\n[red]Goodbye![/red]")
                break
            command_line = command_line.strip()
            if not command_line:
                continue
            args = shlex.split(command_line)
            command = args[0].lower()
            params = args[1:]

            handlers = {
                "help": self.command_help,
                "create": self.command_create,
                "observe": self.command_observe,
                "reward": self.command_reward,
                "punish": self.command_punish,
                "teach": self.command_teach,
                "feed": self.command_feed,
                "heal": self.command_heal,
                "breed": self.command_breed,
                "show_brain": self.command_show_brain,
                "show_lineage": self.command_show_lineage,
                "family_tree": self.command_family_tree,
                "simulate": self.command_simulate,
                "view": self.command_view,
                "stats": self.command_stats,
                "dashboard": self.command_dashboard,
                "graph": self.command_graph,
                "heatmap": self.command_heatmap,
                "timeline": self.command_timeline,
                "learning_curve": self.command_learning_curve,
                "compare_species": self.command_compare_species,
                "events": self.command_events,
                "top": self.command_top,
                "population": self.command_population,
                "save": self.command_save,
                "load": self.command_load,
                "snapshot": self.command_snapshot,
                "export_stats": self.command_export_stats,
                "speed": self.command_speed,
                "follow": self.command_follow,
                "auto_mode": self.command_auto_mode,
                "quit": self.command_quit,
                "exit": self.command_quit,
            }
            
            if self.gameplay:
                handlers.update(
                    {
                        "start_mode": self.command_start_mode,
                        "gameplay": self.command_gameplay_status,
                        "unlock": self.command_unlock,
                        "achievements": self.command_achievements,
                    }
                )

            handler = handlers.get(command)
            if handler is None:
                self.console.print(f"[red]Unknown command:[/red] {command}. Type 'help' for options.")
                continue
            try:
                handler(params)
            except Exception as exc:  # pragma: no cover - CLI resilience
                self.console.print(f"[red]Error:[/red] {exc}")

    # Command handlers --------------------------------------------------
    def command_help(self, _: List[str]) -> None:
        table = Table(title="Command Reference")
        table.add_column("Command", style="cyan")
        table.add_column("Description")
        table.add_row("create [species] [name]", "Spawn a new plant or herbivore")
        table.add_row("observe [name]", "Inspect creature stats")
        table.add_row("simulate [ticks]", "Run the simulation for N ticks")
        table.add_row("view [ticks]", "Animated visualization (default 200 ticks)")
        table.add_row("reward/punish [name]", "Reinforce or discourage recent actions")
        table.add_row("teach [name] [strength]", "Guide learning with a hint")
        table.add_row("feed/heal [name]", "Provide resources to a creature")
        table.add_row("breed [name1] [name2]", "Force reproduction between herbivores")
        table.add_row("show_brain [name]", "Display neural network details")
        table.add_row("show_lineage [name]", "View ancestry (simple)")
        table.add_row("family_tree [name]", "View detailed family tree")
        table.add_row("population", "List all living entities")
        table.add_row("stats", "Ecosystem metrics (simple)")
        table.add_row("", "")
        table.add_row("[bold]VISUALIZATIONS[/bold]", "")
        table.add_row("dashboard", "Main statistics dashboard")
        table.add_row("graph [type]", "Show graphs: population, fitness, age, energy")
        table.add_row("heatmap [type]", "Show heatmaps: births, deaths, food")
        table.add_row("timeline", "Evolution timeline")
        table.add_row("learning_curve [name]", "Individual learning progress")
        table.add_row("compare_species", "Compare species statistics")
        table.add_row("events [count] [type]", "Show recent events")
        table.add_row("top [count]", "Show top performers")
        table.add_row("", "")
        table.add_row("save/load [file]", "Persist or restore world state")
        table.add_row("snapshot [name]", "Create snapshot for comparison")
        table.add_row("export_stats [file]", "Export statistics to JSON/CSV")
        table.add_row("speed [multiplier]", "Adjust visualization speed")
        table.add_row("follow [name]", "Follow a creature in view mode")
        table.add_row("auto_mode on/off", "Toggle automatic resource management")
        if self.gameplay:
            table.add_row("start_mode [mode]", "Begin survival, challenge, sandbox, or speedrun mode")
            table.add_row("gameplay", "Show gameplay status and timeline")
            table.add_row("unlock [name]", "Spend EP on unlocks")
            table.add_row("achievements", "List achievement progress")
        table.add_row("quit", "Exit the simulator")
        self.console.print(table)

    def command_create(self, params: List[str]) -> None:
        if len(params) < 1:
            self.console.print("[red]Usage: create [species] [name][/red]")
            return
        species = params[0].lower()
        name = params[1] if len(params) > 1 else None
        if species in {"plant", "plants"}:
            plant = self.world.spawn_plant(name=name)
            self.console.print(f"[green]Spawned plant[/green] {plant.name} at {plant.position.round(1)}")
        elif species in {"herbivore", "herbivores"}:
            herb = self.world.spawn_herbivore(name=name)
            self.console.print(f"[cyan]Spawned herbivore[/cyan] {herb.name} at {herb.position.round(1)}")
        else:
            self.console.print(f"[red]Unknown species:[/red] {species}")

    def command_observe(self, params: List[str]) -> None:
        if not params:
            self.console.print("[red]Usage: observe [name][/red]")
            return
        name = params[0]
        for plant in self.world.plants:
            if plant.name == name:
                self.console.print(f"[green]{plant.name}[/green] - nutrients {plant.nutrients:.1f}, growth {plant.growth_stage:.1f}")
                return
        stats = self.world.creature_stats(name)
        if stats:
            table = Table(title=f"{name} Stats")
            for key, value in stats.items():
                table.add_row(key.title(), f"{value:.2f}" if isinstance(value, float) else str(value))
            self.console.print(table)
        else:
            self.console.print(f"[red]{name} not found[/red]")

    def command_reward(self, params: List[str]) -> None:
        if len(params) < 1:
            self.console.print("[red]Usage: reward [name] [amount][/red]")
            return
        name = params[0]
        amount = float(params[1]) if len(params) > 1 else 5.0
        if self.world.reward(name, amount):
            self.console.print(f"[green]Rewarded {name} with {amount} points[/green]")
        else:
            self.console.print(f"[red]{name} not found[/red]")

    def command_punish(self, params: List[str]) -> None:
        if len(params) < 1:
            self.console.print("[red]Usage: punish [name] [amount][/red]")
            return
        name = params[0]
        amount = float(params[1]) if len(params) > 1 else 5.0
        if self.world.punish(name, amount):
            self.console.print(f"[yellow]Punished {name} with {amount} points[/yellow]")
        else:
            self.console.print(f"[red]{name} not found[/red]")

    def command_teach(self, params: List[str]) -> None:
        if len(params) < 1:
            self.console.print("[red]Usage: teach [name] [strength][/red]")
            return
        name = params[0]
        strength = float(params[1]) if len(params) > 1 else 2.0
        if self.world.reward(name, strength):
            self.console.print(f"[cyan]Provided guidance to {name} (+{strength})[/cyan]")
        else:
            self.console.print(f"[red]{name} not found[/red]")

    def command_feed(self, params: List[str]) -> None:
        if len(params) < 1:
            self.console.print("[red]Usage: feed [name][/red]")
            return
        creature = self._find_herbivore(params[0])
        if not creature:
            self.console.print(f"[red]{params[0]} not found[/red]")
            return
        creature.energy = min(creature.max_energy, creature.energy + 30)
        self.console.print(f"[green]Fed {creature.name}. Energy now {creature.energy:.1f}")

    def command_heal(self, params: List[str]) -> None:
        if len(params) < 1:
            self.console.print("[red]Usage: heal [name][/red]")
            return
        creature = self._find_herbivore(params[0])
        if not creature:
            self.console.print(f"[red]{params[0]} not found[/red]")
            return
        creature.health = min(creature.max_health, creature.health + 40)
        self.console.print(f"[green]Healed {creature.name}. Health now {creature.health:.1f}")

    def command_breed(self, params: List[str]) -> None:
        if len(params) < 2:
            self.console.print("[red]Usage: breed [name1] [name2][/red]")
            return
        parent_a = self._find_herbivore(params[0])
        parent_b = self._find_herbivore(params[1])
        if not parent_a or not parent_b:
            self.console.print("[red]Both parents must be herbivores[/red]")
            return
        child = self.world.genetics.reproduce(
            parent_a,
            parent_b,
            name=f"herbivore_{self.world.next_id}",
            position=parent_a.position,
            rng=self.world.rng,
        )
        self.world.herbivores.append(child)
        self.world.next_id += 1
        parent_a.energy *= 0.7
        parent_b.energy *= 0.7
        self.console.print(f"[cyan]Bred {parent_a.name} + {parent_b.name} -> {child.name}[/cyan]")

    def command_show_brain(self, params: List[str]) -> None:
        if not params:
            self.console.print("[red]Usage: show_brain [name][/red]")
            return
        self.visualizer.print_brain(params[0])

    def command_show_lineage(self, params: List[str]) -> None:
        if not params:
            self.console.print("[red]Usage: show_lineage [name][/red]")
            return
        self.dashboard.show_family_tree(params[0], depth=5)

    def command_family_tree(self, params: List[str]) -> None:
        if not params:
            self.console.print("[red]Usage: family_tree [name] [depth][/red]")
            return
        name = params[0]
        depth = int(params[1]) if len(params) > 1 else 6
        self.dashboard.show_family_tree(name, depth=depth)

    def command_simulate(self, params: List[str]) -> None:
        ticks = int(params[0]) if params else 200
        stats = self.world.simulate(ticks, headless=True)
        panel = Panel(f"Simulated {ticks} ticks\n{stats}", title="Simulation Complete", expand=False)
        self.console.print(panel)

    def command_view(self, params: List[str]) -> None:
        ticks = int(params[0]) if params else 200
        delay = 0.1 / max(0.1, self.speed_multiplier)
        with Live(self.visualizer.render(), refresh_per_second=20, console=self.console) as live:
            for _ in range(ticks):
                self.world.simulate(1, headless=False)
                live.update(self.visualizer.render())
                time.sleep(delay)
        self.console.print("[green]View session ended.[/green]")

    def command_stats(self, params: List[str]) -> None:
        summary = self.world.stats.get_summary()
        current_pop = summary.get("current_population", {})
        current_fit = summary.get("current_fitness", {})

        table = Table(show_header=False, box=None)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Tick", str(self.world.tick_count))
        table.add_row("Generation", str(current_pop.get("generation", 0)))
        table.add_row("Herbivores", str(current_pop.get("herbivores", 0)))
        table.add_row("Plants", str(current_pop.get("plants", 0)))
        table.add_row("Avg Fitness", f"{current_fit.get('avg', 0.0):.1f}")
        table.add_row("Best Fitness", f"{current_fit.get('best', 0.0):.1f}")
        table.add_row("Total Births", str(summary.get("total_births", 0)))
        table.add_row("Total Deaths", str(summary.get("total_deaths", 0)))
        table.add_row("Plants Eaten", str(summary.get("total_plants_consumed", 0)))
        table.add_row("Tracked Creatures", str(summary.get("tracked_creatures", 0)))

        panel = Panel(table, title="Ecosystem Statistics", border_style="cyan")
        self.console.print(panel)

    def command_population(self, params: List[str]) -> None:
        table = Table(title="Population", show_header=True)
        table.add_column("Type", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Position", style="yellow")
        for plant in self.world.plants:
            if plant.alive:
                table.add_row("Plant", plant.name, f"({plant.position[0]:.1f}, {plant.position[1]:.1f})")
        for herbivore in self.world.herbivores:
            if herbivore.alive:
                table.add_row("Herbivore", herbivore.name, f"({herbivore.position[0]:.1f}, {herbivore.position[1]:.1f})")
        self.console.print(table)

    def command_save(self, params: List[str]) -> None:
        if not params:
            self.console.print("[red]Usage: save [filename][/red]")
            return
        path = Path(params[0]).expanduser()
        self.world.save(path)
        self.console.print(f"[green]Saved world to {path}[/green]")

    def command_load(self, params: List[str]) -> None:
        if not params:
            self.console.print("[red]Usage: load [filename][/red]")
            return
        path = Path(params[0]).expanduser()
        if not path.exists():
            self.console.print(f"[red]File not found:[/red] {path}")
            return
        self.world = World.load(path)
        self.visualizer = Visualizer(self.world)
        self.dashboard = Dashboard(self.world, self.console)
        self.console.print(f"[green]Loaded world from {path}[/green]")

    def command_dashboard(self, _: List[str]) -> None:
        self.dashboard.show_main_dashboard()

    def command_graph(self, params: List[str]) -> None:
        if not params:
            self.console.print("[red]Usage: graph [type] where type is: population, fitness, age, energy[/red]")
            return
        graph_type = params[0].lower()
        last_n = 100
        if len(params) > 1:
            try:
                last_n = int(params[1])
            except ValueError:
                self.console.print("[yellow]Window size must be an integer. Using default of 100.[/yellow]")

        if graph_type == "population":
            self.dashboard.show_population_graph(last_n=last_n)
        elif graph_type == "fitness":
            self.dashboard.show_fitness_graph(last_n=last_n)
        elif graph_type == "age":
            self.dashboard.show_age_distribution()
        elif graph_type == "energy":
            self.dashboard.show_energy_distribution()
        else:
            self.console.print(f"[red]Unknown graph type:[/red] {graph_type}")

    def command_heatmap(self, params: List[str]) -> None:
        if not params:
            self.console.print("[red]Usage: heatmap [type] where type is: births, deaths, food[/red]")
            return
        heatmap_type = params[0].lower()
        self.dashboard.show_heatmap(heatmap_type)

    def command_timeline(self, _: List[str]) -> None:
        self.dashboard.show_timeline()

    def command_learning_curve(self, params: List[str]) -> None:
        if not params:
            self.console.print("[red]Usage: learning_curve [name][/red]")
            return
        self.dashboard.show_learning_curve(params[0])

    def command_compare_species(self, _: List[str]) -> None:
        self.dashboard.show_species_comparison()

    def command_events(self, params: List[str]) -> None:
        count = 10
        event_type = None
        for param in params:
            if param.isdigit():
                count = int(param)
            else:
                event_type = param.lower()
        self.dashboard.show_recent_events(count=count, event_type=event_type)

    def command_top(self, params: List[str]) -> None:
        count = int(params[0]) if params else 10
        self.dashboard.show_top_performers(count=count)

    def command_snapshot(self, params: List[str]) -> None:
        if not params or params[0].lower() == "list":
            snapshots = self.world.stats.snapshots
            if not snapshots:
                self.console.print("[yellow]No snapshots saved yet.[/yellow]")
                return
            table = Table(title="Snapshots", show_header=True)
            table.add_column("Name", style="cyan")
            table.add_column("Tick", style="green")
            table.add_column("Herbivores", style="magenta")
            table.add_column("Births", style="yellow")
            table.add_column("Deaths", style="red")
            for name, data in snapshots.items():
                herd_count = len(data["state"].get("herbivores", []))
                table.add_row(
                    name,
                    str(data.get("tick", 0)),
                    str(herd_count),
                    str(data.get("total_births", 0)),
                    str(data.get("total_deaths", 0)),
                )
            self.console.print(table)
            return

        if params[0].lower() == "compare" and len(params) >= 3:
            self._compare_snapshots(params[1], params[2])
            return

        snapshot_name = params[0]
        self.world.stats.create_snapshot(snapshot_name, self.world.to_dict())
        self.console.print(f"[green]Created snapshot: {snapshot_name}[/green]")

    def command_export_stats(self, params: List[str]) -> None:
        if not params:
            self.console.print("[red]Usage: export_stats [filename][/red]")
            return
        path = Path(params[0]).expanduser()
        if path.suffix.lower() == ".csv":
            self.world.stats.export_to_csv(path)
        else:
            self.world.stats.export_to_json(path)
        self.console.print(f"[green]Exported statistics to {path}[/green]")

    def command_speed(self, params: List[str]) -> None:
        if not params:
            self.console.print(f"Current speed multiplier: {self.speed_multiplier}")
            return
        self.speed_multiplier = max(0.1, float(params[0]))
        self.console.print(f"[cyan]Speed multiplier set to {self.speed_multiplier}[/cyan]")

    def command_follow(self, params: List[str]) -> None:
        if not params:
            self.visualizer.follow_target = None
            self.console.print("[yellow]Stopped following any creature.[/yellow]")
            return
        name = params[0]
        if self._find_herbivore(name):
            self.visualizer.follow_target = name
            self.console.print(f"[green]Will follow {name} during view mode.[/green]")
        else:
            self.console.print(f"[red]{name} not found[/red]")

    def command_auto_mode(self, params: List[str]) -> None:
        if not params:
            self.console.print(f"Auto mode is {'on' if self.auto_mode else 'off'}")
            return
        flag = params[0].lower()
        if flag == "on":
            self.auto_mode = True
            self.console.print("[green]Auto mode enabled. Plants will spawn more frequently.")
            self.world.config.plant_spawn_rate = 0.1
        elif flag == "off":
            self.auto_mode = False
            self.console.print("[yellow]Auto mode disabled.")
            self.world.config.plant_spawn_rate = 0.05
        else:
            self.console.print("[red]Usage: auto_mode on/off[/red]")

    def command_quit(self, _: List[str]) -> None:
        self.console.print("[yellow]Exiting EMERGENCE. Farewell![/yellow]")
        sys.exit(0)

    # Helpers ------------------------------------------------------------
    def _find_herbivore(self, name: str) -> Herbivore | None:
        for herbivore in self.world.herbivores:
            if herbivore.name == name:
                return herbivore
        return None

    def _compare_snapshots(self, name1: str, name2: str) -> None:
        snapshots = self.world.stats.snapshots
        if name1 not in snapshots:
            self.console.print(f"[red]Snapshot {name1} not found[/red]")
            return
        if name2 not in snapshots:
            self.console.print(f"[red]Snapshot {name2} not found[/red]")
            return

        snap1 = snapshots[name1]
        snap2 = snapshots[name2]

        table = Table(title=f"Snapshot Comparison: {name1} vs {name2}", show_header=True)
        table.add_column("Metric", style="cyan")
        table.add_column(name1, style="green")
        table.add_column(name2, style="yellow")
        table.add_column("Change", style="magenta")

        tick1 = snap1.get("tick", 0)
        tick2 = snap2.get("tick", 0)
        herd1 = len(snap1["state"].get("herbivores", []))
        herd2 = len(snap2["state"].get("herbivores", []))
        births1 = snap1.get("total_births", 0)
        births2 = snap2.get("total_births", 0)
        deaths1 = snap1.get("total_deaths", 0)
        deaths2 = snap2.get("total_deaths", 0)

        table.add_row("Tick", str(tick1), str(tick2), f"{tick2-tick1:+d}")
        table.add_row("Herbivores", str(herd1), str(herd2), f"{herd2-herd1:+d}")
        table.add_row("Total Births", str(births1), str(births2), f"{births2-births1:+d}")
        table.add_row("Total Deaths", str(deaths1), str(deaths2), f"{deaths2-deaths1:+d}")

        self.console.print(table)

    # Gameplay commands -------------------------------------------------
    def command_start_mode(self, params: List[str]) -> None:
        if not self.gameplay:
            self.console.print("[red]Advanced gameplay system not available.[/red]")
            return
        if not params:
            self.console.print("[red]Usage: start_mode [survival|challenge|sandbox|speedrun] [challenge_name][/red]")
            return
        mode_name = params[0].lower()
        mode_map = {
            "survival": GameModeType.SURVIVAL,
            "challenge": GameModeType.CHALLENGE,
            "sandbox": GameModeType.SANDBOX,
            "speedrun": GameModeType.SPEEDRUN,
        }
        mode_type = mode_map.get(mode_name)
        if not mode_type:
            self.console.print(f"[red]Unknown mode:[/red] {mode_name}")
            return
        challenge = None
        if len(params) > 1:
            challenge_name = params[1].lower()
            challenge_map = {
                "drought": ChallengeType.DROUGHT,
                "invasion": ChallengeType.PREDATOR_INVASION,
                "ice_age": ChallengeType.ICE_AGE,
                "extinction": ChallengeType.EXTINCTION_EVENT,
            }
            challenge = challenge_map.get(challenge_name)
            if challenge is None:
                self.console.print(f"[yellow]Unknown challenge:[/yellow] {challenge_name}")
        message = self.gameplay.start_mode(mode_type, challenge)
        self.console.print(message)

    def command_gameplay_status(self, _: List[str]) -> None:
        if not self.gameplay:
            self.console.print("[red]Gameplay system not available.[/red]")
            return
        panel = self.gameplay.display_status_panel()
        timeline = self.gameplay.display_timeline()
        self.console.print(panel)
        self.console.print(timeline)

    def command_unlock(self, params: List[str]) -> None:
        if not self.gameplay:
            self.console.print("[red]Gameplay system not available.[/red]")
            return
        if not params:
            self.console.print("[red]Usage: unlock [name][/red]")
            return
        unlock_map = {
            "carnivores": UnlockType.CARNIVORES,
            "apex": UnlockType.APEX_PREDATORS,
            "scavengers": UnlockType.SCAVENGERS,
            "omnivores": UnlockType.OMNIVORES,
            "camouflage": UnlockType.CAMOUFLAGE,
            "mutation": UnlockType.MUTATION_BOOST,
            "teaching": UnlockType.ADVANCED_TEACHING,
            "divine": UnlockType.DIVINE_INTERVENTION,
            "weather": UnlockType.WEATHER_CONTROL,
            "timewarp": UnlockType.TIME_WARP,
            "drought": UnlockType.DROUGHT_CHALLENGE,
            "ice_age": UnlockType.ICE_AGE_CHALLENGE,
            "invasion": UnlockType.INVASION_CHALLENGE,
            "extinction": UnlockType.EXTINCTION_CHALLENGE,
        }
        key = params[0].lower()
        unlock_type = unlock_map.get(key)
        if not unlock_type:
            self.console.print(f"[red]Unknown unlock:[/red] {key}")
            return
        message = self.gameplay.purchase_unlock(unlock_type)
        self.console.print(message)

    def command_achievements(self, _: List[str]) -> None:
        if not self.gameplay:
            self.console.print("[red]Gameplay system not available.[/red]")
            return
        summary = self.gameplay.progression.get_achievements_summary()
        table = Table(title="Achievements", show_header=True)
        table.add_column("Achievement", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Progress", style="yellow")
        for achievement in self.gameplay.progression.achievements.values():
            status = "Unlocked" if achievement.unlocked else "Locked"
            progress = f"{min(achievement.progress, achievement.max_progress):.0f}/{achievement.max_progress}"
            table.add_row(achievement.name, status, progress)
        table.caption = f"Unlocked {summary['unlocked']} of {summary['total']}"  # type: ignore[index]
        self.console.print(table)


def main() -> None:
    cli = EmergenceCLI()
    cli.run()


if __name__ == "__main__":
    main()
