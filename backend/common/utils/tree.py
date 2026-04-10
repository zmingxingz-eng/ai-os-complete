def build_tree(items, parent_key="parent_id", id_key="id"):
    mapping = {item[id_key]: {**item, "children": []} for item in items}
    roots = []
    for item in items:
        node = mapping[item[id_key]]
        pid = item.get(parent_key)
        if pid and pid in mapping:
            mapping[pid]["children"].append(node)
        else:
            roots.append(node)
    return roots
