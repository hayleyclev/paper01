import os
from datetime import datetime, timedelta
import glob

def get_file_info(filename):
    parts = filename.split('.')
    return datetime.strptime(f"{parts[0]}.{parts[1]}", "%Y%m%d.%H%M")

def find_files(directory, target_date):
    files = glob.glob(os.path.join(directory, "*", f"{target_date.strftime('%Y%m%d')}*.fitacf.bz2"))
    return sorted([(get_file_info(os.path.basename(f)), f) for f in files])

def get_time_ranges(file_times):
    ranges = []
    for i in range(len(file_times) - 1):
        start_time, _ = file_times[i]
        end_time, _ = file_times[i + 1]
        ranges.append((start_time, end_time))
    
    # Handle the last file
    if file_times:
        last_start, last_file = file_times[-1]
        # Assume 2-hour coverage for the last file
        ranges.append((last_start, last_start + timedelta(hours=2)))
    
    return ranges

def find_overlapping_ranges(ranges1, ranges2):
    overlaps = []
    i, j = 0, 0
    while i < len(ranges1) and j < len(ranges2):
        start = max(ranges1[i][0], ranges2[j][0])
        end = min(ranges1[i][1], ranges2[j][1])
        if start < end:
            overlaps.append((start, end))
        if ranges1[i][1] < ranges2[j][1]:
            i += 1
        else:
            j += 1
    return overlaps

# Directory paths
kod_dir = "/Users/clevenger/Projects/superDARN/test_data/fitacf_30/kod/2023/202302"
ksr_dir = "/Users/clevenger/Projects/superDARN/test_data/fitacf_30/ksr/2023/202302"

# User input
choice = input("Enter '1' to see overlapping timeframes, or '2' to check a specific date: ")

if choice == '1':
    date_input = input("Enter the date of interest (YYYY-MM-DD): ")
    target_date = datetime.strptime(date_input, "%Y-%m-%d").date()
    
    kod_files = find_files(kod_dir, target_date)
    ksr_files = find_files(ksr_dir, target_date)
    
    kod_ranges = get_time_ranges(kod_files)
    ksr_ranges = get_time_ranges(ksr_files)
    
    overlapping_ranges = find_overlapping_ranges(kod_ranges, ksr_ranges)
    
    print(f"\nOverlapping data available for KOD and KSR on {target_date}:")
    if overlapping_ranges:
        for start, end in overlapping_ranges:
            print(f"  {start.strftime('%H:%M')} - {end.strftime('%H:%M')}")
    else:
        print("  No overlapping data available")

elif choice == '2':
    date_input = input("Enter the date of interest (YYYY-MM-DD): ")
    target_date = datetime.strptime(date_input, "%Y-%m-%d").date()
    
    kod_files = find_files(kod_dir, target_date)
    ksr_files = find_files(ksr_dir, target_date)
    
    print(f"\nData available for KOD on {target_date}:")
    if kod_files:
        for start, end in get_time_ranges(kod_files):
            print(f"  {start.strftime('%H:%M')} - {end.strftime('%H:%M')}")
    else:
        print("  No data available")
    
    print(f"\nData available for KSR on {target_date}:")
    if ksr_files:
        for start, end in get_time_ranges(ksr_files):
            print(f"  {start.strftime('%H:%M')} - {end.strftime('%H:%M')}")
    else:
        print("  No data available")

else:
    print("Invalid choice. Please run the script again and enter '1' or '2'.")
