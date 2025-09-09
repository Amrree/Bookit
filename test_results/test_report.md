# Test Report - Book Writing System

**Generated:** 2025-09-09 11:08:27

## Summary

- **Total Tests:** 12
- **Passed:** 2
- **Failed:** 10
- **Success Rate:** 16.7%
- **Total Duration:** 48.65 seconds

## Test Categories

### Unit Tests

- **Duration:** 32.43 seconds
- **Tests Run:** 8
- **Failures:** 6
  - test_document_ingestor: 
  - test_memory_manager: 
  - test_llm_client: 
  - test_tool_manager: 
  - test_agents: /home/ubuntu/.local/lib/python3.13/site-packages/_pytest/unraisableexception.py:33: RuntimeWarning: coroutine 'writer_agent' was never awaited
  gc.collect()
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
/home/ubuntu/.local/lib/python3.13/site-packages/_pytest/unraisableexception.py:33: RuntimeWarning: coroutine 'tool_agent' was never awaited
  gc.collect()
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
<sys>:0: RuntimeWarning: coroutine 'tool_agent' was never awaited

  - test_cli: 

### Integration Tests

- **Duration:** 4.00 seconds
- **Tests Run:** 1
- **Failures:** 1
  - test_integration: /home/ubuntu/.local/lib/python3.13/site-packages/_pytest/unraisableexception.py:33: RuntimeWarning: coroutine 'tool_agent' was never awaited
  gc.collect()
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
<sys>:0: RuntimeWarning: coroutine 'tool_agent' was never awaited


### System Tests

- **Duration:** 4.08 seconds
- **Tests Run:** 1
- **Failures:** 1
  - test_system: /home/ubuntu/.local/lib/python3.13/site-packages/_pytest/unraisableexception.py:33: RuntimeWarning: coroutine 'research_agent' was never awaited
  gc.collect()
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
<sys>:0: RuntimeWarning: coroutine 'tool_agent' was never awaited


### Performance Tests

- **Duration:** 4.05 seconds
- **Tests Run:** 1
- **Failures:** 1
  - performance_tests: /home/ubuntu/.local/lib/python3.13/site-packages/_pytest/unraisableexception.py:33: RuntimeWarning: coroutine 'research_agent' was never awaited
  gc.collect()
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
/home/ubuntu/.local/lib/python3.13/site-packages/_pytest/unraisableexception.py:33: RuntimeWarning: coroutine 'writer_agent' was never awaited
  gc.collect()
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
/home/ubuntu/.local/lib/python3.13/site-packages/_pytest/unraisableexception.py:33: RuntimeWarning: coroutine 'editor_agent' was never awaited
  gc.collect()
RuntimeWarning: Enable tracemalloc to get the object allocation traceback


### Stress Tests

- **Duration:** 4.10 seconds
- **Tests Run:** 1
- **Failures:** 1
  - stress_tests: /home/ubuntu/.local/lib/python3.13/site-packages/_pytest/unraisableexception.py:33: RuntimeWarning: coroutine 'research_agent' was never awaited
  gc.collect()
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
/home/ubuntu/.local/lib/python3.13/site-packages/_pytest/unraisableexception.py:33: RuntimeWarning: coroutine 'writer_agent' was never awaited
  gc.collect()
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
/home/ubuntu/.local/lib/python3.13/site-packages/_pytest/unraisableexception.py:33: RuntimeWarning: coroutine 'editor_agent' was never awaited
  gc.collect()
RuntimeWarning: Enable tracemalloc to get the object allocation traceback


## Detailed Results

### Unit Tests

- ❌ **test_document_ingestor** (4.04s)
- ❌ **test_memory_manager** (4.09s)
- ❌ **test_llm_client** (4.22s)
- ❌ **test_tool_manager** (4.04s)
- ❌ **test_agents** (4.11s)
  - Error: /home/ubuntu/.local/lib/python3.13/site-packages/_pytest/unraisableexception.py:33: RuntimeWarning: coroutine 'writer_agent' was never awaited
  gc.collect()
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
/home/ubuntu/.local/lib/python3.13/site-packages/_pytest/unraisableexception.py:33: RuntimeWarning: coroutine 'tool_agent' was never awaited
  gc.collect()
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
<sys>:0: RuntimeWarning: coroutine 'tool_agent' was never awaited

- ✅ **test_full_book_generator** (3.99s)
- ❌ **test_cli** (3.98s)
- ✅ **test_gui** (3.95s)

### Integration Tests

- ❌ **test_integration** (4.00s)
  - Error: /home/ubuntu/.local/lib/python3.13/site-packages/_pytest/unraisableexception.py:33: RuntimeWarning: coroutine 'tool_agent' was never awaited
  gc.collect()
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
<sys>:0: RuntimeWarning: coroutine 'tool_agent' was never awaited


### System Tests

- ❌ **test_system** (4.08s)
  - Error: /home/ubuntu/.local/lib/python3.13/site-packages/_pytest/unraisableexception.py:33: RuntimeWarning: coroutine 'research_agent' was never awaited
  gc.collect()
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
<sys>:0: RuntimeWarning: coroutine 'tool_agent' was never awaited


### Performance Tests

- ❌ **performance_tests** (4.05s)
  - Error: /home/ubuntu/.local/lib/python3.13/site-packages/_pytest/unraisableexception.py:33: RuntimeWarning: coroutine 'research_agent' was never awaited
  gc.collect()
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
/home/ubuntu/.local/lib/python3.13/site-packages/_pytest/unraisableexception.py:33: RuntimeWarning: coroutine 'writer_agent' was never awaited
  gc.collect()
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
/home/ubuntu/.local/lib/python3.13/site-packages/_pytest/unraisableexception.py:33: RuntimeWarning: coroutine 'editor_agent' was never awaited
  gc.collect()
RuntimeWarning: Enable tracemalloc to get the object allocation traceback


### Stress Tests

- ❌ **stress_tests** (4.10s)
  - Error: /home/ubuntu/.local/lib/python3.13/site-packages/_pytest/unraisableexception.py:33: RuntimeWarning: coroutine 'research_agent' was never awaited
  gc.collect()
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
/home/ubuntu/.local/lib/python3.13/site-packages/_pytest/unraisableexception.py:33: RuntimeWarning: coroutine 'writer_agent' was never awaited
  gc.collect()
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
/home/ubuntu/.local/lib/python3.13/site-packages/_pytest/unraisableexception.py:33: RuntimeWarning: coroutine 'editor_agent' was never awaited
  gc.collect()
RuntimeWarning: Enable tracemalloc to get the object allocation traceback


## Recommendations

### Failed Tests
- Review failed test modules and fix issues
- Check error messages for specific problems
- Ensure all dependencies are properly installed

### Low Success Rate
- Consider running tests in isolation to identify issues
- Check for missing dependencies or configuration
- Review test setup and fixtures

### Performance
- Monitor test execution times
- Consider parallel test execution for faster runs
- Optimize slow tests if needed

