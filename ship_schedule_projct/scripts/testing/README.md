# Testing Scripts

Collection of testing and verification scripts for the ship schedule project.

## API Testing Scripts
- `test_api_*.py` - API endpoint testing scripts
- `test_cabin_*.py` - Cabin-related API tests
- `test_permission_*.py` - Permission system tests
- `test_cnshk_*.py` - Specific route testing scripts

## Verification Scripts
- `verify_*.py` - Logic verification and validation
- `simple_*.py` - Simple test cases and quick checks
- `final_verification.py` - Comprehensive system verification

## Test Runners
- `run_api_test.sh` - Automated API test runner script

## Usage

All scripts should be run from the project root directory:

```bash
# Activate virtual environment
source .venv/bin/activate

# Run specific test
python3 scripts/testing/test_api_permission_direct.py

# Run test suite
bash scripts/testing/run_api_test.sh
```

## Test Categories

### Permission Tests
- User permission verification
- Role-based access control
- API endpoint authorization

### API Functionality Tests
- Cabin grouping logic
- Price calculation verification
- Schedule availability checks

### Integration Tests
- End-to-end API workflows
- Cross-module functionality
- Data consistency checks
