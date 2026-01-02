#!/bin/bash
# Redis Monitor - Quick wrapper for monitoring Redis from Docker

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Change to project root directory (parent of scripts/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

COMPOSE_CMD="docker-compose -f docker-compose.yml -f docker-compose.dev.yml"

echo -e "${GREEN}Redis Monitor${NC}"
echo "============================================"
echo ""

# Check if Redis is running
if ! $COMPOSE_CMD ps redis | grep -q "Up"; then
    echo -e "${YELLOW}Warning: Redis container is not running${NC}"
    echo "Start it with: docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d redis"
    exit 1
fi

# Run the Python monitor script inside the backend container
$COMPOSE_CMD exec -T backend python -c "
import redis
import sys
from datetime import datetime, timedelta

try:
    r = redis.Redis(host='redis', port=6379, decode_responses=True, socket_connect_timeout=5)
    r.ping()
except Exception as e:
    print(f'❌ Failed to connect to Redis: {e}')
    sys.exit(1)

print('='*80)
print('🔍 REDIS MONITOR - Current State')
print('='*80)
print()

# Get server info
info = r.info()
print(f'📊 Redis Info:')
print(f'   Version: {info.get(\"redis_version\", \"N/A\")}')
print(f'   Uptime: {timedelta(seconds=info.get(\"uptime_in_seconds\", 0))}')
print(f'   Used Memory: {info.get(\"used_memory_human\", \"N/A\")}')
print(f'   Connected Clients: {info.get(\"connected_clients\", 0)}')
print(f'   Total Keys: {r.dbsize()}')
print()

# Get all keys
keys = r.keys('*')

if not keys:
    print('ℹ️  No keys found in Redis')
    print('   (Rate limit keys appear when users send chat messages)')
    print()
else:
    print(f'📦 Found {len(keys)} key(s):')
    print('─'*80)
    print()

    for key in sorted(keys):
        key_type = r.type(key)
        ttl = r.ttl(key)

        print(f'🔑 Key: {key}')
        print(f'   Type: {key_type}')

        # TTL
        if ttl >= 0:
            minutes = ttl // 60
            seconds = ttl % 60
            print(f'   TTL: {minutes}m {seconds}s ({ttl} seconds)')
        elif ttl == -1:
            print(f'   TTL: ∞ (no expiry)')
        else:
            print(f'   TTL: N/A')

        # Value based on type
        if key_type == 'zset':
            size = r.zcard(key)
            print(f'   Size: {size} items')

            members = r.zrange(key, 0, -1, withscores=True)
            if members:
                print(f'   📋 Values (sorted set):')
                for member, score in members:
                    timestamp = datetime.fromtimestamp(score).strftime('%Y-%m-%d %H:%M:%S')
                    print(f'      • {member}')
                    print(f'        Score: {int(score)} (time: {timestamp})')

        elif key_type == 'string':
            value = r.get(key)
            print(f'   Value: {value}')

        elif key_type == 'list':
            size = r.llen(key)
            print(f'   Size: {size} items')
            values = r.lrange(key, 0, 9)  # First 10 items
            if values:
                print(f'   Values: {values}')
                if size > 10:
                    print(f'   ... and {size - 10} more items')

        elif key_type == 'set':
            size = r.scard(key)
            print(f'   Size: {size} items')
            values = list(r.smembers(key))[:10]  # First 10 items
            if values:
                print(f'   Values: {values}')
                if size > 10:
                    print(f'   ... and {size - 10} more items')

        elif key_type == 'hash':
            size = r.hlen(key)
            print(f'   Size: {size} fields')
            fields = r.hgetall(key)
            if fields:
                print(f'   Fields:')
                for k, v in list(fields.items())[:10]:
                    print(f'      {k}: {v}')
                if size > 10:
                    print(f'   ... and {size - 10} more fields')

        print('─'*80)
        print()

print('✅ Done')
print()
" 2>&1
