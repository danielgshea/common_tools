# Test Suite for Common Tools

Comprehensive integration tests for filesystem, Gmail, and Google Calendar tools.

## Setup

### 1. Install Test Dependencies

```bash
uv pip install pytest python-dotenv
```

### 2. Configure Credentials

Create a `.env` file in the project root with your Google API credentials path:

```bash
# .env
GOOGLE_CREDENTIALS_PATH=/path/to/your/credentials.json
```

### 3. Enable Required APIs

Ensure these APIs are enabled in Google Cloud Console:
- Gmail API: https://console.cloud.google.com/apis/library/gmail.googleapis.com
- Calendar API: https://console.cloud.google.com/apis/library/calendar-json.googleapis.com

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Only Integration Tests

```bash
pytest -m integration
```

### Run Tests for Specific Module

```bash
# Filesystem tests only
pytest tests/integration/test_filesystem_integration.py

# Gmail tests only
pytest tests/integration/test_gmail_integration.py

# Calendar tests only
pytest tests/integration/test_gcalendar_integration.py
```

### Run Read-Only Tests (Skip Data Modification)

By default, tests run in **safe mode** which skips tests that modify real data.

To run all tests including those that modify data:

```bash
TEST_SAFE_MODE=false pytest
```

### Skip Slow Tests

```bash
pytest -m "not slow"
```

### Skip Tests That Modify Data

```bash
pytest -m "not modifies_data"
```

## Test Categories

### Filesystem Tests (`test_filesystem_integration.py`)

Tests file operations in a temporary directory:
- ✅ Create, read, write, delete files
- ✅ File existence checks
- ✅ Directory listing with patterns
- ✅ Recursive file operations
- ✅ Error handling

**Safe**: Yes - uses temporary directories, no real data modified

### Gmail Tests (`test_gmail_integration.py`)

Tests Gmail API with your real email data:
- ✅ List messages (with subject, from, date, snippet)
- ✅ Get message details
- ✅ List labels
- ✅ Search emails
- ✅ Filter by labels
- ⚠️ Mark as read/unread (skipped in safe mode)
- ⚠️ Create drafts (skipped in safe mode)

**Safe Mode**: Most tests are read-only. Tests that modify data are marked with `@pytest.mark.modifies_data` and skipped in safe mode.

### Calendar Tests (`test_gcalendar_integration.py`)

Tests Calendar API with your real calendar:
- ✅ List calendars
- ✅ List events
- ✅ Get event details
- ✅ Search events
- ⚠️ Create/update/delete test events (cleans up after itself)

**Safe Mode**: Read tests run normally. Create/update/delete tests clean up test events but still modify your calendar temporarily.

## Test Output

### Successful Test Run

```
tests/integration/test_filesystem_integration.py::TestFileSystemIntegration::test_create_and_read_file PASSED
tests/integration/test_gmail_integration.py::TestGmailIntegration::test_list_messages PASSED
✅ Retrieved 5 messages
   Sample: Meeting notes... from john@example.com

tests/integration/test_gcalendar_integration.py::TestGoogleCalendarIntegration::test_list_calendars PASSED
✅ Retrieved 3 calendars
   Primary: john@gmail.com
```

### Skipped Tests (Safe Mode)

```
tests/integration/test_gmail_integration.py::TestGmailIntegration::test_mark_as_read_unread SKIPPED
Reason: Skipped in safe mode - would modify email data
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_CREDENTIALS_PATH` | Path to credentials.json | Required |
| `TEST_SAFE_MODE` | Skip tests that modify data | `true` |
| `TEST_VERBOSE` | Enable verbose test output | `false` |

## Troubleshooting

### Tests Skip with "Credentials not configured"

Make sure `GOOGLE_CREDENTIALS_PATH` is set in your `.env` file and the file exists:

```bash
echo $GOOGLE_CREDENTIALS_PATH
ls -la $GOOGLE_CREDENTIALS_PATH
```

### Tests Fail with "API not enabled"

Enable the required APIs in Google Cloud Console (see links in Setup section).

### Tests Hang During Authentication

If token.json is invalid or expired:

```bash
rm /path/to/token.json
pytest  # Will re-authenticate
```

### Import Errors

Make sure you're running from the project root:

```bash
cd /Users/danielshea/projects/personal/tools
pytest
```

## CI/CD Integration

To run tests in CI/CD (GitHub Actions, etc.):

1. Store credentials as secrets
2. Set `TEST_SAFE_MODE=true` to skip data-modifying tests
3. Use service account credentials for production

Example GitHub Actions:

```yaml
- name: Run tests
  env:
    GOOGLE_CREDENTIALS_PATH: ${{ secrets.GOOGLE_CREDENTIALS_PATH }}
    TEST_SAFE_MODE: true
  run: pytest -m "not modifies_data"
```

## Test Coverage

To generate coverage reports (requires pytest-cov):

```bash
uv pip install pytest-cov
pytest --cov=. --cov-report=html --cov-report=term
open htmlcov/index.html
```

## Contributing

When adding new tests:

1. Use appropriate markers (`@pytest.mark.integration`, `@pytest.mark.modifies_data`)
2. Add docstrings explaining what the test does
3. Use fixtures from `conftest.py` for clients
4. Clean up any test data created
5. Prefix test events/emails with `[TEST]` for easy identification
