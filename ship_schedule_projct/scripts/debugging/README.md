# Debugging Scripts

Debug and analysis tools for troubleshooting the ship schedule system.

## Price Debugging
- `debug_cabin_price.py` - Cabin pricing logic debugging
- `debug_price_calculation.py` - Price calculation analysis
- `debug_price_simple.py` - Simplified price debugging

## Analysis Scripts
- `analyze_plan_open.py` - Plan opening logic analysis
- `analyze_price_issue.py` - Price-related issue investigation

## Usage

Run from project root with virtual environment activated:

```bash
source .venv/bin/activate
python3 scripts/debugging/debug_cabin_price.py
```

## Common Debug Scenarios

### Price Calculation Issues
1. Use `debug_price_simple.py` for quick price checks
2. Use `debug_price_calculation.py` for detailed analysis
3. Use `analyze_price_issue.py` for systematic investigation

### Availability Logic Problems
1. Check `debug_cabin_price.py` for cabin-specific issues
2. Use `analyze_plan_open.py` for plan opening logic

## Debug Output

Debug scripts typically output:
- Detailed execution traces
- Variable state information
- SQL query logs
- Error stack traces
- Performance metrics
