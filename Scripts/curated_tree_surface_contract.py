"""Conservative source-named bark/leaf slot resolver for UE4.27 curated trees.

A tree with guessed or extra material slots stays in review rather than
being painted uniformly green to satisfy an asset-count check.
"""

TREE_SURFACE_GROUPS = {
    'Bark': 'Nature/T_Sh_Bark',
    'LeafGreen': 'Nature/T_Sh_LeafGreen',
    'LeafAutumn': 'Nature/T_Sh_LeafAutumn',
}
TREE_FAMILIES = ('tree_apple', 'tree_elm', 'tree_oak', 'tree_willow')

# Explicit literal Blender authoring names from blender_nature.py:
# M_Sh_Bark=(0.24,0.14,0.07), M_Sh_Leaf=(0.16,0.39,0.11) [GREEN],
# M_Sh_Flower=(0.61,0.35,0.44). No guessed generic material indices.
SOURCE_MATERIAL_ALIASES = {
    'M_Sh_Bark': 'Bark',
    'M_Sh_Leaf': 'LeafGreen',
}



def resolve_tree_slots(slot_rows):
    """Return {surface: slot_index} only for two uniquely labelled source slots."""
    if not isinstance(slot_rows, list) or len(slot_rows) != 2:
        return None
    slots = {}
    indices = set()
    for row in slot_rows:
        if not isinstance(row, dict) or type(row.get('index')) is not int:
            return None
        index = row['index']
        if index < 0 or index in indices:
            return None
        indices.add(index)
        names = set()
        for key in ('slot_name', 'imported_name'):
            name = row.get(key)
            if not isinstance(name, str):
                continue
            if name.startswith('T_Sh_'):
                name = name[len('T_Sh_'):]
            name = SOURCE_MATERIAL_ALIASES.get(name, name)
            if name in TREE_SURFACE_GROUPS:
                names.add(name)
        if len(names) != 1:
            return None
        surface = names.pop()
        if surface in slots:
            return None
        slots[surface] = index
    if 'Bark' not in slots or len(slots) != 2:
        return None
    if not ({'LeafGreen', 'LeafAutumn'} & set(slots)):
        return None
    return slots
