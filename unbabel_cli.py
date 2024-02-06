import json
import argparse
import os
from datetime import datetime, timedelta

def parse_arguments():
    """
    Parses command-line arguments.
    
    Returns:
        Namespace: An object containing the parsed arguments
    """

    parser = argparse.ArgumentParser(description='Calculate moving average delivery time.')
    
    parser.add_argument('--input_file', type=str, help='Path to the input file', required=True)
    parser.add_argument('--window_size', type=int, help='Window size for moving average (must be a positive integer)', required=True)
    parser.add_argument('--output_file', type=str, default='moving_averages_result.json', help='Path to the output file', required=False)
    
    args = parser.parse_args()

    try:
        # Check if window size is a positive integer
        if args.window_size <= 0:
            raise argparse.ArgumentTypeError("Window size must be a positive integer")
        
        # Check if input file exists
        if not os.path.isfile(args.input_file):
            raise argparse.ArgumentTypeError("Input file does not exist")
    except argparse.ArgumentTypeError as e:
        parser.error(str(e))
    
    return args

def calculate_moving_average(events: list, window_size: int):
    """
    Calculates the moving average delivery time.
    
    Args:
        events (list): A list of events
        window_size (int): The window size for calculating the moving average
        
    Returns:
        list: A list containing the calculated moving averages for each minute
    """

    events_timestamps = [datetime.strptime(event["timestamp"], "%Y-%m-%d %H:%M:%S.%f") for event in events] # Extract timestamps from events and convert them to datetime objects

    moving_averages = []

    earliest_timestamp = min(events_timestamps).replace(second=0).replace(microsecond=0) # Round down earliest timestamp
    latest_timestamp = max(events_timestamps).replace(second=0).replace(microsecond=0)+timedelta(minutes=1) # Round up latest timestamp

    while earliest_timestamp <= latest_timestamp:
        window_start = earliest_timestamp - timedelta(minutes=window_size)

        events_in_window = [event for event in events_timestamps if window_start <= event <= earliest_timestamp] # Filter for events in the defined time window

        if events_in_window:
            average_delivery_time = sum(event["duration"] for event in events if datetime.strptime(event["timestamp"], "%Y-%m-%d %H:%M:%S.%f") in events_in_window) / len(events_in_window)
        else:
            average_delivery_time = 0

        # Append the values to the moving_averages list. Also remove the decimal of the average_delivery_time if it's an integer
        moving_averages.append({"date": earliest_timestamp.strftime("%Y-%m-%d %H:%M:%S"), "average_delivery_time": int(average_delivery_time) if average_delivery_time.is_integer() else average_delivery_time})

        earliest_timestamp += timedelta(minutes=1)

    return moving_averages

def main():
    args = parse_arguments()

    # Read input file
    with open(args.input_file, 'r') as file:
        events = json.load(file)

    moving_averages = calculate_moving_average(events, args.window_size)

    # Save moving averages to output file
    with open(args.output_file, 'w') as file:
        json.dump(moving_averages, file, indent=4)

if __name__ == "__main__":
    main()
