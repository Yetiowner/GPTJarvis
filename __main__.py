import argparse
import src.config as config

def main():
    parser = argparse.ArgumentParser(description='Configure personal preferences for Jarvis, including personal information and API keys.')
    parser.add_argument('module', choices=["config"], help='Function to run')
    parser.add_argument('function', choices=['key', 'info'], help='Function to run')
    parser.add_argument('-fromfile', dest='fromfile', action='store_true', help='Whether or not to interpret the data as a file name and load the data from the file.')
    parser.add_argument('data', help='The data to be permanently added to the personal Jarvis configuration.')

    args = parser.parse_args()

    if args.module == "config":

        if args.function == 'key':
            if args.fromfile:
                config.loadApiKeyFromFile(args.data)
            else:
                config.setKey(args.data)
        elif args.function == "info":
            if args.fromfile:
                config.loadInfoFromFile(args.data)
            else:
                config.setPersonalInfo(args.data)

if __name__ == '__main__':
    main()