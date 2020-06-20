
def sort_summary_by_key(summary_list, objProperty, reverse=False):
    return sorted(summary_list, key=lambda device_summary: device_summary[objProperty], reverse=reverse)

