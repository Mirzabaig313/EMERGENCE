"""
Tests for EMERGENCE art asset system.

Covers sprites, animations, colors, UI components, terrain, effects,
and the unified ArtAssetManager.
"""

import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from emergence.art_assets import ArtAssetManager, get_asset_manager
from emergence.sprites import SpriteLibrary, create_progress_bar, create_sparkline
from emergence.animations import AnimationLibrary, AnimationEngine, AnimationType
from emergence.colors import ColorScheme, ThemeManager, get_creature_color
from emergence.ui_elements import BoxDrawing, BoxStyle, UIComponents, PanelLayout
from emergence.terrain import TerrainTextures, render_scene, list_scenes
from emergence.effects import EffectLibrary, EffectManager, EffectType


class SpriteTests(unittest.TestCase):
    """Sprite library tests."""

    def test_herbivore_sprites(self) -> None:
        self.assertEqual(SpriteLibrary.get_herbivore_sprite('standard'), '🐰')
        self.assertEqual(SpriteLibrary.get_herbivore_sprite('fast'), '🐇')

    def test_carnivore_sprites(self) -> None:
        self.assertEqual(SpriteLibrary.get_carnivore_sprite('standard'), '🦊')
        self.assertEqual(SpriteLibrary.get_carnivore_sprite('apex'), '🐺')

    def test_plant_sprites(self) -> None:
        self.assertEqual(SpriteLibrary.get_plant_sprite(0.5), '·')
        self.assertEqual(SpriteLibrary.get_plant_sprite(1.5), '🌱')
        self.assertEqual(SpriteLibrary.get_plant_sprite(4.5), '🌾')

    def test_status_sprites(self) -> None:
        self.assertEqual(SpriteLibrary.get_status_sprite('sleeping'), '💤')
        self.assertEqual(SpriteLibrary.get_status_sprite('eating'), '😋')

    def test_progress_bar(self) -> None:
        bar = create_progress_bar(75, 100, width=10)
        self.assertEqual(len(bar), 10)
        self.assertIn('█', bar)

    def test_sparkline(self) -> None:
        sparkline = create_sparkline([10, 20, 30, 40], width=20)
        self.assertLessEqual(len(sparkline), 20)


class AnimationTests(unittest.TestCase):
    """Animation library and engine tests."""

    def test_animation_library(self) -> None:
        idle = AnimationLibrary.get_herbivore_animation('idle')
        self.assertEqual(len(idle), 10)
        self.assertIn('🐰', idle)

        hunt = AnimationLibrary.get_carnivore_animation('hunt')
        self.assertEqual(len(hunt), 10)

    def test_animation_engine(self) -> None:
        engine = AnimationEngine(fps=10)
        animation = AnimationLibrary.create_animation('herbivore_idle')
        self.assertIsNotNone(animation)

        engine.register_animation('test_anim', animation)
        activated = engine.activate_animation('test_anim')
        self.assertTrue(activated)
        self.assertIsNotNone(engine.get_frame('test_anim'))

    def test_animation_types(self) -> None:
        loop_anim = AnimationLibrary.create_animation('herbivore_idle', AnimationType.LOOP)
        self.assertEqual(loop_anim.animation_type, AnimationType.LOOP)

        once_anim = AnimationLibrary.create_animation('herbivore_eat', AnimationType.ONCE)
        self.assertEqual(once_anim.animation_type, AnimationType.ONCE)


class ColorTests(unittest.TestCase):
    """Color scheme and theme manager tests."""

    def test_color_scheme_constants(self) -> None:
        self.assertIsNotNone(ColorScheme.HERBIVORE_HEALTHY)
        self.assertIsNotNone(ColorScheme.CARNIVORE_NORMAL)
        self.assertIsNotNone(ColorScheme.UI_BORDER)

    def test_theme_manager(self) -> None:
        manager = ThemeManager('default')
        self.assertEqual(manager.current_theme, 'default')
        themes = manager.list_themes()
        self.assertIn('default', themes)
        self.assertIn('cyberpunk', themes)

    def test_creature_color_helper(self) -> None:
        color = get_creature_color('herbivore', age=100, health=90, energy=70)
        self.assertIsNotNone(color)


class UITests(unittest.TestCase):
    """UI component tests."""

    def test_box_drawing(self) -> None:
        box = BoxDrawing.draw_box(40, 10, BoxStyle.LIGHT)
        self.assertEqual(len(box), 10)
        self.assertTrue(all(len(line) == 40 for line in box))

    def test_menu_component(self) -> None:
        menu = UIComponents.create_menu(["New", "Load", "Quit"], selected=0, width=25)
        self.assertTrue(menu)
        self.assertIn('▸', menu[1])

    def test_progress_component(self) -> None:
        bar = UIComponents.create_progress_bar("HP", 75, 100, width=20, bar_width=10)
        self.assertIn("HP", bar)
        self.assertIn("75", bar)

    def test_tabs(self) -> None:
        tabs = UIComponents.create_tabs(["World", "Stats"], active=0, width=40)
        self.assertTrue(tabs)

    def test_dashboard_layout(self) -> None:
        dashboard = PanelLayout.dashboard_layout(120, 40)
        self.assertIn("EMERGENCE", dashboard)


class TerrainTests(unittest.TestCase):
    """Terrain and scene rendering tests."""

    def test_terrain_textures(self) -> None:
        plains = TerrainTextures.get_texture('plains')
        forest = TerrainTextures.get_texture('forest_dense')
        self.assertTrue(plains)
        self.assertTrue(forest)

    def test_render_texture(self) -> None:
        rendered = TerrainTextures.render_texture('plains', width=10, height=5)
        self.assertEqual(len(rendered), 5)

    def test_scenes(self) -> None:
        scenes = list_scenes()
        self.assertIn('campfire', scenes)
        self.assertIn('dashboard_hud', scenes)

        campfire = render_scene('campfire')
        self.assertTrue(any('🔥' in line for line in campfire))


class EffectTests(unittest.TestCase):
    """Visual effect tests."""

    def test_effect_library(self) -> None:
        birth_frames = EffectLibrary.get_effect_frames(EffectType.BIRTH)
        death_frames = EffectLibrary.get_effect_frames(EffectType.DEATH)
        self.assertTrue(birth_frames)
        self.assertTrue(death_frames)

    def test_effect_manager(self) -> None:
        manager = EffectManager()
        effect = manager.create_effect(EffectType.BIRTH, (100, 100), duration=1.0)
        self.assertTrue(effect.active)
        self.assertEqual(manager.count_effects(), 1)

        # Fast-forward time to expire effect without sleeping
        effect.start_time -= effect.duration
        manager.update(effect.start_time + effect.duration)
        self.assertEqual(manager.count_effects(), 0)


class AssetManagerTests(unittest.TestCase):
    """ArtAssetManager tests."""

    def setUp(self) -> None:
        self.manager = ArtAssetManager()

    def test_get_sprite(self) -> None:
        self.assertEqual(self.manager.get_sprite('herbivore'), '🐰')

    def test_animate_entity(self) -> None:
        frame = self.manager.animate_entity('demo', state='idle', species='herbivore')
        self.assertIsInstance(frame, str)

    def test_progress_bar(self) -> None:
        bar = self.manager.create_progress_bar("HP", 75, 100, width=10)
        self.assertIn("HP", bar)

    def test_effect_creation(self) -> None:
        effect = self.manager.create_effect('birth', (0.0, 0.0), duration=0.5)
        self.assertIsNotNone(effect)

    def test_theme_switch(self) -> None:
        self.assertTrue(self.manager.set_theme('cyberpunk'))

    def test_render_scene(self) -> None:
        scene = self.manager.render_scene('campfire')
        self.assertTrue(scene)

    def test_get_info(self) -> None:
        info = self.manager.get_info()
        self.assertIn('fps', info)
        self.assertIn('theme', info)

    def test_logo(self) -> None:
        logo = self.manager.get_logo()
        mini = self.manager.get_mini_logo()
        self.assertTrue(logo)
        self.assertTrue(mini)

    def test_singleton(self) -> None:
        global_manager = get_asset_manager()
        self.assertIs(get_asset_manager(), global_manager)

    def test_integration(self) -> None:
        menu = self.manager.create_menu(["A", "B"], selected=0, width=20)
        stats = self.manager.create_stat_panel("STATS", {"HP": "80"}, width=20)
        dashboard = self.manager.create_dashboard_layout(120, 40)
        self.assertTrue(menu)
        self.assertTrue(stats)
        self.assertTrue(dashboard)


if __name__ == "__main__":
    unittest.main(verbosity=2)
