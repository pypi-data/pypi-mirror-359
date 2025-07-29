import sys
import redis
import psycopg
from cyborgdb_service.core.config import settings


def print_usage_and_exit():
    """Print usage instructions for the CyborgDB Service"""
    print("\n" + "="*60)
    print("CyborgDB Service")
    print("="*60)
    
    print("\nUsage: cyborgdb-service [options]")
    
    print("\nOptions:")
    print("  -init, --init     Initialize the service and install packages")
    print("  --help, -h        Show this help message")
    
    print("\nExamples:")
    print("  cyborgdb-service -init")
    print("  cyborgdb-service --verbose")
    
    print("\n" + "="*60)
    print("Required Environment Variables:")
    print("="*60)
    print("  export CYBORGDB_API_KEY='your_api_key'")
    print("  export CYBORGDB_DB_TYPE='redis|postgres'")
    print("  export CYBORGDB_CONNECTION_STRING='your_connection_string'")
    
    print("\nConnection String Examples:")
    print("  Redis:")
    print("    \"host:localhost,port:6379,db:0\"")
    
    print("\n  PostgreSQL:")
    print("    \"host=localhost port=5432 dbname=dbname user=user password=''\"")
    
    print("\n Get your API key: https://cyborgdb.co/")
    print(" Documentation: https://docs.cyborgdb.co/")
    print("")
    
    sys.exit(0)

def test_connection(connection_string, db_type):
    """Test database connection based on type"""
    try:
        if db_type.lower() == 'redis':
            # Check for URI format (not allowed)
            if connection_string.startswith(('redis://', 'rediss://')):
                return False, "Redis URI format not supported."
            
            # Parse redis connection string
            config = {}
            for pair in connection_string.split(','):
                if ':' in pair:
                    key, value = pair.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    if key in ['port', 'db']:
                        config[key] = int(value)
                    else:
                        config[key] = value

            if 'host' not in config or 'port' not in config:
                return False, "Incomplete redis connection string format. 'host' and 'port' are required."

            # Test redis connection
            client = redis.Redis(
                host=config['host'],
                port=config['port'],
                db=config.get('db', 0),
                password=config.get('password'),
                socket_connect_timeout=5
            )
            client.ping()
            client.close()
            return True, "Connection Successful"
        
        elif db_type.lower() == 'postgres':
            conn = psycopg.connect(connection_string)
            conn.close()
            return True, "Connection successful"
        
        else:
            return False, f"Unsupported database type: {db_type}"
    
    except redis.RedisError as e:
        return False, f"Redis connection failed: {str(e)}"
    except psycopg.OperationalError as e:
        return False, f"PostgreSQL connection failed: {str(e)}"
    except Exception as e:
        return False, f"Connection test failed: {str(e)}"

def print_error_section(title, description, commands):
    """Print a formatted error section"""
    print(f"\n\033[91m[ERROR] {title}\033[0m")
    print(f"   {description}")
    if len(commands) == 0:
        return
    print("\n   Solution:")
    if isinstance(commands, list):
        for cmd in commands:
            print(f"      {cmd}")
    else:
        print(f"      {commands}")

def print_connection_examples():
    """Print detailed connection string examples"""
    print("\n   Solution:")
    print("       PostgreSQL:")
    print("         export CYBORGDB_CONNECTION_STRING=\"host=localhost port=5432 dbname=dbname user=user password=''\"")
    
    print("       Redis:")
    print("         export CYBORGDB_CONNECTION_STRING=\"host:localhost,port:6379,db:0\"")

def ensure_environment_variables():
    """Ensure all required environment variables are set"""
    should_exit = False

    # Check API key
    if not settings.CYBORGDB_API_KEY:
        print_error_section(
            "Missing API Key",
            "CYBORGDB_API_KEY environment variable not set.",
            "export CYBORGDB_API_KEY='your_api_key_here'"
        )
        print("       Get your API key from: https://cyborgdb.co/")
        should_exit = True

    # Check Database Type
    db_locations = [
        settings.INDEX_LOCATION,
        settings.CONFIG_LOCATION,
        settings.ITEMS_LOCATION
    ]
    location_missing = False
    invalid_db_types = []
    for location in db_locations:
        if not location:
            location_missing = True
            
        else:
            db_type = location.lower()
            if db_type not in ['redis', 'postgres']:
                invalid_db_types.append(db_type)
                

    if location_missing:
        print_error_section(
            "Missing Database Type", 
            "CYBORGDB_DB_TYPE environment variable is not set.",
            [
                "export CYBORGDB_DB_TYPE='redis'      # For Redis",
                "export CYBORGDB_DB_TYPE='postgres'   # For PostgreSQL"
            ]
        )
        should_exit = True
    if len(invalid_db_types) > 0:
        print_error_section(
            "Invalid Database Type",
            f"Database type set to {str(invalid_db_types)} but only 'redis' and 'postgres' are supported.",
            [
                "export CYBORGDB_DB_TYPE='redis'      # For Redis",
                "export CYBORGDB_DB_TYPE='postgres'   # For PostgreSQL"
            ]                
        )
        should_exit = True

    # Check Connection String
    connection_strings = [
        [settings.INDEX_CONNECTION_STRING, settings.INDEX_LOCATION],
        [settings.CONFIG_CONNECTION_STRING, settings.CONFIG_LOCATION],
        [settings.ITEMS_CONNECTION_STRING, settings.ITEMS_LOCATION]
    ]
    connection_string_missing = False
    error_messages = []
    for conn in connection_strings:
        if not conn[0]:
            connection_string_missing = True
            
        else:
            connection_string = conn[0]
            db_type = conn[1]

            if db_type and db_type in ['redis', 'postgres']:
                success, message = test_connection(connection_string, db_type)
                
                if not success:
                    error_messages.append(message)
    
    if connection_string_missing:
        print_error_section(
            "Missing Connection String",
            "CYBORGDB_CONNECTION_STRING environment variable is not set.",
            []
        )
        print_connection_examples()
        should_exit = True
    if len(error_messages) > 0:
        print("\n[ERROR] Connection Test Failed")
        for message in error_messages:
            print(f"\n   - {message}")
        print_connection_examples()
        should_exit = True

    if should_exit:
        print(f"\n{'='*60}")
        print("  Environment Setup Incomplete")
        print(f"{'='*60}")
        print("Please fix the issues above and run again.")
        print("Need help? Check the documentation or contact support.\n")
        sys.exit(1)