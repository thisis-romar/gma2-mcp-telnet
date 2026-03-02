"""
Store Function Keywords for grandMA2 Command Builder

Store is used to save the programmer or current state to a specified object.
This is one of the most commonly used function keywords in grandMA2.

Included functions:
- store: Generic store command
- store_cue: Store cue
- store_group: Store group
- store_preset: Store preset
"""

from typing import Any

from ..constants import PRESET_TYPES
from ..helpers import _build_store_options


def store(
    object_type: str,
    object_id: int | str,
    name: str | None = None,
    **options: Any,
) -> str:
    """
    Construct a generic store command for any object type.

    Args:
        object_type: The type of object to store (e.g., "macro", "effect")
        object_id: The ID or identifier of the object
        name: Optional name for the stored object
        **options: Store options (merge, overwrite, noconfirm, etc.)

    Returns:
        str: MA command to store the object

    Examples:
        >>> store("macro", 5)
        'store macro 5'
        >>> store("macro", 5, name="Reset All")
        'store macro 5 "Reset All"'
    """
    cmd = f"store {object_type} {object_id}"

    if name:
        cmd += f' "{name}"'

    cmd += _build_store_options(**options)

    return cmd


def store_cue(
    cue_id: int | None = None,
    end: int | None = None,
    *,
    ranges: list[tuple[int, int]] | None = None,
    name: str | None = None,
    merge: bool = False,
    overwrite: bool = False,
    remove: bool = False,
    noconfirm: bool = False,
    trackingshield: bool = False,
    cueonly: bool | None = None,
    tracking: bool | None = None,
    keepactive: bool | None = None,
    addnewcontent: bool | None = None,
    originalcontent: bool | None = None,
    effects: bool | None = None,
    values: bool | None = None,
    valuetimes: bool | None = None,
    source: str | None = None,
    useselection: str | None = None,
) -> str:
    """
    Construct a store cue command with full option support.

    Args:
        cue_id: The cue number to store
        end: End cue number for range (cue_id thru end)
        ranges: List of (start, end) tuples for multiple ranges
        name: Optional name for the cue
        merge: Merge new values into existing
        overwrite: Remove stored values and store new values
        remove: Remove stored values for attributes with active values
        noconfirm: Suppress store confirmation pop-up
        trackingshield: Use tracking shield for store
        cueonly: Prevent changes to track forward (True/False)
        tracking: Store with tracking
        keepactive: Keep values active after store
        addnewcontent: Add new content
        originalcontent: Store original content
        effects: Filter or enable effect layer
        values: Filter or enable value layer
        valuetimes: Filter or enable value times layer
        source: Data source (Prog, Output, DmxIn)
        useselection: Selection mode

    Returns:
        str: MA command to store cue(s)

    Examples:
        >>> store_cue(7)
        'store cue 7'
        >>> store_cue(1, end=10)
        'store cue 1 thru 10'
        >>> store_cue(ranges=[(1, 10), (20, 30)])
        'store cue 1 thru 10 + 20 thru 30'
    """
    if ranges:
        range_parts = [f"{start} thru {end}" for start, end in ranges]
        cue_part = " + ".join(range_parts)
    elif cue_id is not None and end is not None:
        cue_part = f"{cue_id} thru {end}"
    elif cue_id is not None:
        cue_part = str(cue_id)
    else:
        raise ValueError("Must provide cue_id or ranges")

    cmd = f"store cue {cue_part}"

    if name:
        cmd += f' "{name}"'

    cmd += _build_store_options(
        merge=merge,
        overwrite=overwrite,
        remove=remove,
        noconfirm=noconfirm,
        trackingshield=trackingshield,
        cueonly=cueonly,
        tracking=tracking,
        keepactive=keepactive,
        addnewcontent=addnewcontent,
        originalcontent=originalcontent,
        effects=effects,
        values=values,
        valuetimes=valuetimes,
        source=source,
        useselection=useselection,
    )

    return cmd


def store_group(group_id: int) -> str:
    """
    Construct a command to store a group.

    Args:
        group_id: Group number

    Returns:
        str: MA command to store a group
    """
    return f"store group {group_id}"


def store_preset(
    preset_type: str,
    preset_id: int,
    *,
    global_scope: bool = False,
    selective: bool = False,
    universal: bool = False,
    auto: bool = False,
    embedded: bool = False,
    noconfirm: bool = False,
    merge: bool = False,
    overwrite: bool = False,
    presetfilter: bool | None = None,
    keepactive: bool | None = None,
    addnewcontent: bool | None = None,
    originalcontent: bool | None = None,
) -> str:
    """
    Construct a command to store a preset with full option support.

    Args:
        preset_type: Preset type (dimmer, position, gobo, color, beam, etc.)
        preset_id: Preset number
        global_scope: Store preset with global values
        selective: Store preset with selective values
        universal: Store preset with universal values
        auto: Store preset values with default preset scope
        embedded: Create embedded preset
        noconfirm: Suppress store confirmation pop-up
        merge: Merge new values into existing
        overwrite: Remove stored values and store new
        presetfilter: Set preset filter on or off
        keepactive: Keep values active
        addnewcontent: Add new content
        originalcontent: Store original content

    Returns:
        str: MA command to store a preset

    Examples:
        >>> store_preset("dimmer", 3)
        'store preset 1.3'
        >>> store_preset("dimmer", 3, global_scope=True)
        'store preset 1.3 /global'
    """
    type_num = PRESET_TYPES.get(preset_type.lower(), 1)
    cmd = f"store preset {type_num}.{preset_id}"

    cmd += _build_store_options(
        **{"global": global_scope},
        selective=selective,
        universal=universal,
        auto=auto,
        embedded=embedded,
        noconfirm=noconfirm,
        merge=merge,
        overwrite=overwrite,
        presetfilter=presetfilter,
        keepactive=keepactive,
        addnewcontent=addnewcontent,
        originalcontent=originalcontent,
    )

    return cmd
