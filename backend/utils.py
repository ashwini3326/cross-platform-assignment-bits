def not_none_task_data(task_data):
    keys = list(task_data.keys())
    for key in keys:
        if key == "completed" or task_data.get(key):
            pass
        else:
            task_data.pop(key)
    return task_data

