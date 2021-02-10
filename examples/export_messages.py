from openstuder import SIGatewayClient, SIStatus
import argparse
import datetime

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Export datalog values to CSV files.')
    parser.add_argument('-H', '--host', type=str, default='localhost', help='Host to connect to, defaults to localhost.')
    parser.add_argument('-P', '--port', type=int, default=1987, help='TCP port to use, defaults to 1987.')
    parser.add_argument('-u', '--user', type=str, default=None, help='Username for authorizing.')
    parser.add_argument('-p', '--password', type=str, default=None, help='Password for authorizing.')
    parser.add_argument('-s', '--start', type=datetime.datetime, default=None, help='Start point from which to query for data.')
    parser.add_argument('-e', '--end', type=datetime.datetime, default=None, help='End point to which to query for data.')
    parser.add_argument('-l', '--limit', type=int, default=None, help='Maximal number of value entries to query.')
    parser.add_argument('-f', '--file', type=str, default=None, help='Filename to use, defaults to messages.csv.')
    args = parser.parse_args()

    # Create connection to gateway.
    client = SIGatewayClient()
    client.connect(args.host, args.port, args.user, args.password)

    # Query messages.
    status, count, messages = client.read_messages(args.start, args.end, args.limit)

    # Check if the datalog could be retrieved.
    if status == SIStatus.SUCCESS:
        if count > 0:
            filename = args.file or 'messages.csv'
            print(f'Received {count} messages, writing them to file "{filename}"...')
            with open(filename, 'w') as file:
                for message in messages:
                    file.write(f'{message.timestamp.isoformat()},{message.access_id},{message.device_id},{message.message_id},{message.message}\n')
        else:
            print('Successfully read datalog, but no values were returned')
    else:
        print(f'Error reading datalog: {status}')
