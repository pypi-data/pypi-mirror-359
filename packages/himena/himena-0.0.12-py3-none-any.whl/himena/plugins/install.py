from __future__ import annotations

import logging
import traceback
from importlib import import_module
from typing import TYPE_CHECKING
from pathlib import Path
from timeit import default_timer as timer
from app_model.types import KeyBindingRule
from dataclasses import dataclass, field

if TYPE_CHECKING:
    from himena.profile import AppProfile
    from himena._app_model import HimenaApplication

_LOGGER = logging.getLogger(__name__)


def install_plugins(
    app: HimenaApplication, plugins: list[str]
) -> list[PluginInstallResult]:
    """Install plugins to the application."""
    from himena.plugins import AppActionRegistry
    from himena.profile import load_app_profile

    reg = AppActionRegistry.instance()
    results = []
    show_import_time = app.attributes.get("print_import_time", False)
    if show_import_time:
        print("==================")
        print("Plugin import time")
        print("==================")
    for name in plugins:
        if name in reg._installed_plugins:
            continue
        _time_0 = timer()
        _exc = None
        if isinstance(name, str):
            if name.endswith(".py"):
                if not Path(name).exists():
                    _LOGGER.error(
                        f"Plugin file {name} does not exists but is listed in the "
                        "application profile."
                    )
                    continue
                import runpy

                runpy.run_path(name)
            else:
                try:
                    import_module(name)
                except ModuleNotFoundError:
                    _LOGGER.error(
                        f"Plugin module {name} is not installed but is listed in the "
                        "application profile."
                    )
                    continue
                except Exception as e:
                    msg = "".join(
                        traceback.format_exception(type(e), e, e.__traceback__)
                    )
                    _LOGGER.error(
                        f"Error installing plugin {name}, traceback follows:\n{msg}"
                    )
                    _exc = e
        else:
            raise TypeError(f"Invalid plugin type: {type(name)}")
        _msec = (timer() - _time_0) * 1000
        if show_import_time and _exc is None:
            color = _color_for_time(_msec)
            print(f"{color}{name}\t{_msec:.3f} msec\033[0m")
        results.append(PluginInstallResult(name, _msec, _exc))
    reg.install_to(app)
    reg._installed_plugins.extend(plugins)
    prof = load_app_profile(app.name)

    for k, cfg in reg._plugin_default_configs.items():
        prof.plugin_configs.setdefault(k, cfg.as_dict())

    prof.save()
    return results


def override_keybindings(app: HimenaApplication, prof: AppProfile) -> None:
    """Override keybindings in the application."""
    for ko in prof.keybinding_overrides:
        if kb := app.keybindings.get_keybinding(ko.command_id):
            app.keybindings._keybindings.remove(kb)
        app.keybindings.register_keybinding_rule(
            ko.command_id,
            KeyBindingRule(primary=ko.key),
        )


@dataclass
class PluginInstallResult:
    plugin: str
    time: float = field(default=0.0)
    error: Exception | None = None


def _color_for_time(msec: float) -> str:
    """Return a color code for the given time in milliseconds."""
    if msec < 80:
        return "\033[92m"  # green
    elif msec < 700:
        return "\033[93m"  # yellow
    else:
        return "\033[91m"  # red
