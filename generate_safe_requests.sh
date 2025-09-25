#!/bin/bash

# Simple Bash version for generating safe requests
# Uses curl instead of Python requests library

BASE_URL="http://localhost:3000"
TOTAL_REQUESTS=10000

echo "🛡️ Safe Request Generator (Bash Version)"
echo "========================================"
echo "📊 Target: $TOTAL_REQUESTS safe requests"
echo "🌐 Server: $BASE_URL"
echo ""

# Test server connectivity
echo "🔍 Testing server connectivity..."
if curl -s "$BASE_URL/" > /dev/null 2>&1; then
    echo "✅ Server is responding"
else
    echo "❌ Server connection failed. Please start the webserver first."
    exit 1
fi

echo ""
echo "🚀 Starting request generation..."

# Safe endpoints array
safe_endpoints=(
    "/"
    "/user/1" "/user/2" "/user/3" "/user/4" "/user/5"
    "/user/10" "/user/15" "/user/20" "/user/25" "/user/30"
    "/file/document.pdf" "/file/image.jpg" "/file/report.xlsx"
    "/file/readme.txt" "/file/config.json" "/file/data.csv"
)

# User agents array
user_agents=(
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/604.1"
)

# Login data array
login_data=(
    '{"username":"john_doe","password":"password123"}'
    '{"username":"jane_smith","password":"mypassword"}'
    '{"username":"admin","password":"admin123"}'
    '{"username":"testuser","password":"test123"}'
    '{"username":"guest","password":"guest"}'
)

# Regular data payloads
data_payloads=(
    '{"name":"John Doe","email":"john@example.com","age":30}'
    '{"product":"laptop","price":999.99,"category":"electronics"}'
    '{"title":"Meeting Notes","content":"Discussed project timeline"}'
    '{"search":"python programming","filter":"recent"}'
    '{"message":"Hello World","timestamp":"2024-09-26"}'
)

success_count=0
error_count=0
start_time=$(date +%s)

# Function to show progress
show_progress() {
    local current=$1
    local total=$2
    local percent=$((current * 100 / total))
    local bar_length=50
    local filled=$((bar_length * current / total))
    
    printf "\r🚀 Progress: ["
    for ((i=0; i<filled; i++)); do printf "█"; done
    for ((i=filled; i<bar_length; i++)); do printf "-"; done
    printf "] %3d%% (%d/%d) ✅ Success: %d ❌ Errors: %d" \
           $percent $current $total $success_count $error_count
}

# Generate requests
for ((i=1; i<=TOTAL_REQUESTS; i++)); do
    # Random request type (1=GET, 2=POST_LOGIN, 3=POST_DATA)
    request_type=$((RANDOM % 3 + 1))
    
    # Random user agent
    ua_index=$((RANDOM % ${#user_agents[@]}))
    user_agent="${user_agents[$ua_index]}"
    
    if [ $request_type -eq 1 ]; then
        # GET request
        endpoint_index=$((RANDOM % ${#safe_endpoints[@]}))
        endpoint="${safe_endpoints[$endpoint_index]}"
        
        if curl -s -H "User-Agent: $user_agent" \
                -H "Accept: application/json" \
                "$BASE_URL$endpoint" > /dev/null 2>&1; then
            ((success_count++))
        else
            ((error_count++))
        fi
        
    elif [ $request_type -eq 2 ]; then
        # POST login request
        data_index=$((RANDOM % ${#login_data[@]}))
        data="${login_data[$data_index]}"
        
        if curl -s -X POST \
                -H "User-Agent: $user_agent" \
                -H "Content-Type: application/json" \
                -d "$data" \
                "$BASE_URL/login" > /dev/null 2>&1; then
            ((success_count++))
        else
            ((error_count++))
        fi
        
    else
        # POST data request
        data_index=$((RANDOM % ${#data_payloads[@]}))
        data="${data_payloads[$data_index]}"
        
        if curl -s -X POST \
                -H "User-Agent: $user_agent" \
                -H "Content-Type: application/json" \
                -d "$data" \
                "$BASE_URL/data" > /dev/null 2>&1; then
            ((success_count++))
        else
            ((error_count++))
        fi
    fi
    
    # Show progress every 50 requests
    if [ $((i % 50)) -eq 0 ]; then
        show_progress $i $TOTAL_REQUESTS
    fi
    
    # Small delay to not overwhelm server
    sleep 0.01
done

# Final progress
show_progress $TOTAL_REQUESTS $TOTAL_REQUESTS

end_time=$(date +%s)
elapsed_time=$((end_time - start_time))
requests_per_second=$((TOTAL_REQUESTS / elapsed_time))

echo ""
echo ""
echo "========================================"
echo "🎉 Request generation completed!"
echo ""
echo "📊 Summary:"
echo "   Total Requests: $TOTAL_REQUESTS"
echo "   ✅ Successful: $success_count"
echo "   ❌ Failed: $error_count"
echo "   ⏱️  Total Time: ${elapsed_time} seconds"
echo "   🚄 Rate: ${requests_per_second} requests/second"

success_rate=$((success_count * 100 / TOTAL_REQUESTS))
echo "   📈 Success Rate: ${success_rate}%"

if [ $success_rate -gt 95 ]; then
    echo ""
    echo "🎯 Excellent! Your server handled the load well."
elif [ $success_rate -gt 85 ]; then
    echo ""
    echo "👍 Good performance with acceptable error rate."
else
    echo ""
    echo "⚠️  High error rate detected. Check server capacity."
fi

echo ""
echo "💡 Next steps:"
echo "   1. Check parsed_logs.jsonl for new entries"
echo "   2. Run your anomaly detection model"  
echo "   3. Verify these requests score as SAFE/benign"
echo "   4. Compare with malicious request scores"