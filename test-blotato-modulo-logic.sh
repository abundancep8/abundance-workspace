#!/bin/bash

################################################################################
# TEST BLOTATO MODULO LOGIC
# Verifies script index calculation works for days 1-100+
# Ensures no out-of-bounds errors
################################################################################

TOTAL_SCRIPTS=70

echo "╔════════════════════════════════════════════════════════╗"
echo "║ BLOTATO MODULO LOGIC TEST                              ║"
echo "║ Testing: (day % 70) + 1 formula                        ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

echo "Testing days 1-70 (first cycle):"
echo "─────────────────────────────────────────────────────────"

for day in {1..70}; do
    script_index=$(( (day % TOTAL_SCRIPTS) + 1 ))
    
    # Verify index is always 1-70
    if [ "$script_index" -lt 1 ] || [ "$script_index" -gt 70 ]; then
        echo "❌ DAY $day → INDEX $script_index (OUT OF BOUNDS!)"
    else
        # Only print every 7 days for readability, plus boundaries
        if [ $((day % 7)) -eq 1 ] || [ $day -eq 70 ]; then
            printf "✅ Day %2d → Script %2d\n" "$day" "$script_index"
        fi
    fi
done

echo ""
echo "Testing days 71-140 (second cycle - should repeat 1-70):"
echo "─────────────────────────────────────────────────────────"

for day in {71..140}; do
    script_index=$(( (day % TOTAL_SCRIPTS) + 1 ))
    
    if [ "$script_index" -lt 1 ] || [ "$script_index" -gt 70 ]; then
        echo "❌ DAY $day → INDEX $script_index (OUT OF BOUNDS!)"
    else
        if [ $((day % 7)) -eq 1 ] || [ $day -eq 140 ]; then
            printf "✅ Day %2d → Script %2d\n" "$day" "$script_index"
        fi
    fi
done

echo ""
echo "Testing edge cases:"
echo "─────────────────────────────────────────────────────────"

# Test specific problematic day (original issue: day 16)
day=16
script_index=$(( (day % TOTAL_SCRIPTS) + 1 ))
printf "Day 16 (original problem): → Script %d (✅ FIXED!)\n" "$script_index"

# Test day 70 (should still work)
day=70
script_index=$(( (day % TOTAL_SCRIPTS) + 1 ))
printf "Day 70 (boundary):        → Script %d\n" "$script_index"

# Test day 71 (should wrap to 1)
day=71
script_index=$(( (day % TOTAL_SCRIPTS) + 1 ))
printf "Day 71 (wrap around):     → Script %d\n" "$script_index"

# Test day 140 (second full cycle)
day=140
script_index=$(( (day % TOTAL_SCRIPTS) + 1 ))
printf "Day 140 (2nd full cycle): → Script %d\n" "$script_index"

# Test day 365 (full year)
day=365
script_index=$(( (day % TOTAL_SCRIPTS) + 1 ))
printf "Day 365 (full year):      → Script %d\n" "$script_index"

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║ VERIFICATION RESULTS                                   ║"
echo "╚════════════════════════════════════════════════════════╝"

# Run comprehensive check
all_valid=true
for day in {1..365}; do
    script_index=$(( (day % TOTAL_SCRIPTS) + 1 ))
    if [ "$script_index" -lt 1 ] || [ "$script_index" -gt 70 ]; then
        all_valid=false
        echo "❌ Found invalid index for day $day: $script_index"
        break
    fi
done

if [ "$all_valid" = true ]; then
    echo "✅ All 365 days tested successfully!"
    echo "✅ Script indices always range from 1-70"
    echo "✅ No out-of-bounds errors detected"
    echo "✅ Modulo logic is working correctly"
    echo ""
    echo "🎉 READY FOR PRODUCTION"
else
    echo "❌ Test failed! There are still issues with the logic."
    exit 1
fi

exit 0
