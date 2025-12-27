import requests
from datetime import datetime, timedelta

def get_data(start_date, end_date=None):
    url = "https://www-app3.gfz-potsdam.de/kp_index/Kp_ap_Ap_SN_F107_since_1932.txt"
    response = requests.get(url)
    lines = response.text.split('\n')
    
    data = {}
    prev_day_f107obs = None
    
    for line in lines:
        if line.startswith('#') or not line.strip():
            continue
        
        parts = line.split()
        line_date = datetime(int(parts[0]), int(parts[1]), int(parts[2]))
        
        if end_date:
            if start_date <= line_date <= end_date:
                kp_values = [float(parts[i]) for i in range(7, 15)]
                data[line_date] = {
                    'avg_kp': sum(kp_values) / 8,
                    'kp_values': kp_values,
                    'ap': int(parts[23]),
                    'f107obs': float(parts[25]),
                    'f107adj': float(parts[26]),
                    'prev_day_f107obs': prev_day_f107obs
                }
        elif line_date == start_date:
            kp_values = [float(parts[i]) for i in range(7, 15)]
            data = {
                'avg_kp': sum(kp_values) / 8,
                'kp_values': kp_values,
                'ap': int(parts[23]),
                'f107obs': float(parts[25]),
                'f107adj': float(parts[26]),
                'prev_day_f107obs': prev_day_f107obs
            }
            break
        
        prev_day_f107obs = float(parts[25])
    
    return data

# Get user input
query_type = input("Enter '0' for single date or '1' for date range: ")

if query_type == '0':
    date_input = input("Enter date (YYYY-MM-DD): ")
    date = datetime.strptime(date_input, "%Y-%m-%d")
    result = get_data(date)
    
    if result:
        print(f"Date: {date.date()}")
        print(f"Average Kp: {result['avg_kp']:.2f}")
        print(f"Kp values: {', '.join(f'{kp:.2f}' for kp in result['kp_values'])}")
        print(f"Ap: {result['ap']}")
        print(f"F10.7obs: {result['f107obs']}")
        print(f"F10.7adj: {result['f107adj']}")
        print(f"Previous day F10.7obs: {result['prev_day_f107obs']}")
    else:
        print("Data not found for the given date.")

elif query_type == '1':
    start_date_input = input("Enter start date (YYYY-MM-DD): ")
    end_date_input = input("Enter end date (YYYY-MM-DD): ")
    start_date = datetime.strptime(start_date_input, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_input, "%Y-%m-%d")
    
    result = get_data(start_date, end_date)
    
    if result:
        sorted_dates = sorted(result.items(), key=lambda x: x[1]['avg_kp'], reverse=True)
        
        print("\nDates sorted by average Kp (highest to lowest):")
        for date, data in sorted_dates:
            print(f"\nDate: {date.date()}")
            print(f"Average Kp: {data['avg_kp']:.2f}")
            print(f"Kp values: {', '.join(f'{kp:.2f}' for kp in data['kp_values'])}")
            print(f"Ap: {data['ap']}")
            print(f"F10.7obs: {data['f107obs']}")
            print(f"F10.7adj: {data['f107adj']}")
            print(f"F10.7prev: {data['prev_day_f107obs']}")
    else:
        print("No data found for the given date range.")

else:
    print("Invalid input. Please run the script again and enter '1' or '2'.")
