import sublime

# The plugin loading is designed to handle errors gracefully.
#
# When upgrading the plugin, changes to the plugin structure can cause import
# errors. In these cases we want to notify the user about needing to restart
# Sublime Text to finish the upgrade.
#
# In the case of any errors we also don't want to leave the normal functioning
# of the editor unusable. We can't access the sublime api until the
# plugin_loaded() hook is called, so we need to catch any exceptions and run
# cleanup operations when the plugin_loaded() hook is called.

try:
    _EXCEPTION = None

    from .lib.state import init_state

    from .lib.commands import *  # noqa: F401,F403

    # TODO Organise all commands into a single module e.g. lib.commands.
    from .lib.cmds.ex_actions import *  # noqa: F401,F403
    from .lib.cmds.vi_actions import *  # noqa: F401,F403
    from .lib.cmds.vi_motions import *  # noqa: F401,F403

    # Why are the plugins in a directory named "extra" rather than "plugins"?
    # The plugins were not placed in a directory named "plugins" because of a
    # bug in Sublime Text that caused loading issues with anything named
    # "plugins" e.g. modules, sub-modules, attributes, classes, functions. See
    # https://github.com/NeoVintageous/NeoVintageous/commit/f29727. This issue
    # has since been fixed in Sublime Text (build 3153). See
    # https://github.com/SublimeTextIssues/Core/issues/1991.
    # TODO Organise plugins into a directory named "plugs".
    # TODO Organise plugins into a directory named "plugins" (requires Sublime
    # Text build >= 3153).
    # See https://github.com/SublimeTextIssues/Core/issues/1991.
    from .lib.extras.surround import *      # noqa: F401,F403
    from .lib.extras.unimpaired import *    # noqa: F401,F403
    from .lib.extras.abolish import *       # noqa: F401,F403

    # TODO [review] Should events be imported ala `from .lib.events import *`
    # like the commands and plugins above?
    from .lib.events import NeoVintageousEvents  # noqa: F401

except Exception as e:
    _EXCEPTION = e
    import traceback
    traceback.print_exc()


def _update_ignored_packages():

    # Updates the list of ignored packages with packages that are redundant,
    # obsolete, or cause problems due to conflicts e.g. Vintage, Vintageous,
    # etc.

    settings = sublime.load_settings('Preferences.sublime-settings')
    ignored_packages = settings.get('ignored_packages', [])
    conflict_packages = [x for x in ['Six', 'Vintage', 'Vintageous'] if x not in ignored_packages]
    if conflict_packages:
        print('NeoVintageous: update ignored packages with conflicts {}'.format(conflict_packages))
        ignored_packages = sorted(ignored_packages + conflict_packages)
        settings.set('ignored_packages', ignored_packages)
        sublime.save_settings('Preferences.sublime-settings')


def _cleanup_views():

    # Resets cursor and mode. In the case of errors loading the plugin this can
    # help prevent the normal functioning of editor becoming unusable e.g. the
    # cursor getting stuck in a block shape or the mode getting stuck in normal
    # or visual mode.

    for window in sublime.windows():
        for view in window.views():
            settings = view.settings()
            settings.set('command_mode', False)
            settings.set('inverse_caret_state', False)
            settings.erase('vintage')


def plugin_loaded():

    # Handles errors gracefully.

    try:
        pc_event = None
        from package_control import events
        if events.install('NeoVintageous'):
            pc_event = 'install'
        if events.post_upgrade('NeoVintageous'):
            pc_event = 'post_upgrade'
    except ImportError:
        pass  # Package Control isn't available
    except Exception:
        import traceback
        traceback.print_exc()

    try:
        _update_ignored_packages()
    except Exception:
        import traceback
        traceback.print_exc()

    try:
        _exception = None

        view = sublime.active_window().active_view()

        # We can't always expect a valid view to be returned from
        # `sublime.Window.active_view()`, especially at startup, e.g. at startup
        # if the active view is an image then `sublime.Window.active_view()`
        # will return None, because images are not represented by a
        # `sublime.View`, but by a `sublime.Sheet`.
        # See https://github.com/SublimeTextIssues/Core/issues/2116.
        if view:
            init_state(view, new_session=True)

    except Exception as e:
        _exception = e
        import traceback
        traceback.print_exc()

    if _EXCEPTION or _exception:

        try:
            _cleanup_views()
        except Exception:
            import traceback
            traceback.print_exc()

        if isinstance(_EXCEPTION, ImportError) or isinstance(_exception, ImportError):
            if pc_event == 'post_upgrade':
                message = "Failed to load some modules trying to upgrade NeoVintageous. "\
                          "Please restart Sublime Text to finish the upgrade."
            else:
                message = "Failed to load some NeoVintageous modules. "\
                          "Please restart Sublime Text."
        else:
            if pc_event == 'post_upgrade':
                message = "An error occurred trying to upgrade NeoVintageous. "\
                          "Please restart Sublime Text to finish the upgrade."
            else:
                message = "An error occurred trying to load NeoVintageous. "\
                          "Please restart Sublime Text."

        print('NeoVintageous:', message)
        sublime.message_dialog(message)


def plugin_unloaded():

    try:
        _cleanup_views()
    except Exception:
        import traceback
        traceback.print_exc()
