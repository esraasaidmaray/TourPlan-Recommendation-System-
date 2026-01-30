#!/bin/bash
# Quick Test Commands for ai2.trekio.net
# ======================================

echo "🧪 Testing AI Travel Planner API on ai2.trekio.net"
echo "=================================================="

# Test 1: Health Check
echo "1. Testing Health Check..."
curl -s http://ai2.trekio.net:8000/health | python3 -m json.tool

echo -e "\n2. Testing Mobile API Health Check..."
curl -s http://ai2.trekio.net:8000/health | python3 -m json.tool

echo -e "\n3. Testing Get Themes..."
curl -s http://ai2.trekio.net:8000/themes | python3 -m json.tool

echo -e "\n4. Testing Generate Itinerary..."
curl -s -X POST http://ai2.trekio.net:8000/itinerary \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-mobile-app-api-key-here" \
  -d '{
    "city": "Cairo",
    "country": "Egypt",
    "theme": "cultural",
    "plan_size": 3
  }' | python3 -m json.tool

echo -e "\n5. Testing Quick Itinerary..."
curl -s "http://ai2.trekio.net:8000/itinerary/quick?city=Cairo&country=Egypt&theme=cultural&plan_size=3" | python3 -m json.tool

echo -e "\n✅ Basic tests completed!"
echo "📱 Your API is running at: http://ai2.trekio.net:8000"
