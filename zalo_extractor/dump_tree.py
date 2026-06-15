import uiautomation as auto

def get_zalo_window():
    win_by_class = auto.WindowControl(searchDepth=1, ClassName='ZaloMainWnd')
    if win_by_class.Exists(0, 0):
        return win_by_class
    for win in auto.GetRootControl().GetChildren():
        if win.Name == "Zalo":
            return win
    return None

def print_tree(control, depth, max_depth, file_obj):
    if depth > max_depth:
        return
    try:
        line = "  " * depth + f"Type: {control.ControlTypeName} | Name: '{control.Name}' | Class: '{control.ClassName}'"
        file_obj.write(line + "\n")
    except Exception:
        pass
    for child in control.GetChildren():
        print_tree(child, depth + 1, max_depth, file_obj)

zalo = get_zalo_window()
if zalo:
    with open('zalo_tree.txt', 'w', encoding='utf-8') as f:
        print_tree(zalo, 0, 7, f)
    print("Dump completed.")
else:
    print("Zalo window not found.")
