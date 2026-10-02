"""TUI smoke tests (skipped when textual isn't installed)."""

import asyncio

import numpy as np
import pytest

pytest.importorskip("textual")

from emergence.tui_app import EmergenceApp, MainGameScreen  # noqa: E402
from emergence.world import World  # noqa: E402


def run(coro):
    return asyncio.run(coro)


async def _with_main(fn):
    app = EmergenceApp(world=World(rng=np.random.default_rng(1)))
    async with app.run_test(size=(160, 50)) as pilot:
        app.push_screen("main")
        await pilot.pause()
        screen = app.screen
        assert isinstance(screen, MainGameScreen)
        await fn(app, screen, pilot)


def test_commands_do_not_crash_or_exit():
    async def body(app, screen, pilot):
        name = screen.world.herbivores[0].name
        for cmd in (f"show_brain {name}", "simulate abc", "simulate 5", "brain connectome", "brain",
                    "compare_brains", "disease on", f"follow {name}", "reward x nan", "edit", "qq"):
            screen.execute_command(cmd)
            await pilot.pause()
        assert app.is_running
        count = len(screen.world.herbivores)
        screen.execute_command("start")  # fuzzy match for start_mode must not reset the world
        await pilot.pause()
        assert len(screen.world.herbivores) == count

    run(_with_main(body))


def test_world_view_rerenders_after_create():
    async def body(app, screen, pilot):
        view = screen.query_one("#world_view")
        view.render()
        before = view.render_cache
        screen.execute_command("create herbivore zed")
        await pilot.pause()
        assert view.render_cache is not before

    run(_with_main(body))


def test_command_output_opens_in_modal():
    from emergence.tui_app import OutputScreen

    async def body(app, screen, pilot):
        screen.execute_command("top")
        await pilot.pause()
        assert isinstance(app.screen, OutputScreen)
        assert "Top" in app.screen._body.plain
        await pilot.press("escape")
        await pilot.pause()
        assert app.screen is screen

    run(_with_main(body))


def test_sim_crash_is_reported_and_stops_playing(monkeypatch):
    async def body(app, screen, pilot):
        def boom(*a, **k):
            raise RuntimeError("kaboom")

        monkeypatch.setattr(screen.world, "simulate", boom)
        screen.action_toggle_play()
        await pilot.pause(0.3)
        assert not screen.is_playing
        assert any("kaboom" in n.message for n in app._notifications)

    run(_with_main(body))


def test_speed_runs_ticks_per_frame():
    async def body(app, screen, pilot):
        screen.speed_multiplier = 10.0
        start = screen.world.tick_count
        screen.action_toggle_play()
        await pilot.pause(1.0)
        screen.action_toggle_play()
        assert screen.world.tick_count - start >= 50  # 10x = 100 ticks/s target, generous floor

    run(_with_main(body))


def test_world_grid_fills_widget_and_rows_align():
    from rich.cells import cell_len

    async def body(app, screen, pilot):
        view = screen.query_one("#world_view")
        view.render_cache = None
        panel = view.render()
        w, h = view.content_size
        assert view.viewport_width * view.CELL_W >= w - 2 * view.PAD_X - 1
        assert view.viewport_height == h - view.CHROME_ROWS
        rows = panel.renderable.plain.split("\n")[: view.viewport_height]
        assert {cell_len(r) for r in rows} == {view.viewport_width * view.CELL_W}

        # A creature's cell maps back to it through the same offsets the mouse uses.
        target = screen.world.herbivores[0]
        cx = int(target.position[0] * view.viewport_width / screen.world.config.width)
        cy = int(target.position[1] * view.viewport_height / screen.world.config.height)
        assert view._find_creature_at_position(cx, cy) is not None

    run(_with_main(body))
