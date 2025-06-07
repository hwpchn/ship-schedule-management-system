# Maintenance Scripts

System maintenance and administrative utilities.

## User Management
- `reset_user_password.py` - Reset user passwords
- `check_user_permissions.py` - Verify user permission assignments

## Data Verification
- `check_api_structure.py` - Validate API structure integrity
- `check_vessel_info_data.py` - Verify vessel information data
- `check_permission_data.py` - Validate permission system data

## Data Management
- `add_test_price_data.py` - Add test pricing data to system

## Usage

Run maintenance scripts from project root:

```bash
source .venv/bin/activate
python3 scripts/maintenance/check_user_permissions.py
```

## Maintenance Categories

### User Administration
- Password resets
- Permission auditing
- User account management

### Data Integrity
- Structure validation
- Data consistency checks
- Reference integrity verification

### System Health
- API endpoint validation
- Database connection checks
- Configuration verification

## Safety Notes

- Always backup data before running maintenance scripts
- Test scripts in development environment first
- Review script output carefully before applying changes
- Some scripts may require administrator privileges
