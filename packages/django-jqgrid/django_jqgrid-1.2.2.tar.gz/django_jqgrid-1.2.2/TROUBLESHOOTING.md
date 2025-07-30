# Troubleshooting PyPI Upload Errors

## Common `twine upload` Errors and Solutions

### 1. **Error: The credentials were not found or were invalid**

**Symptoms:**
```
HTTPError: 403 Forbidden from https://upload.pypi.org/legacy/
Invalid or non-existent authentication information.
```

**Solutions:**
- Ensure you're using an API token, not username/password
- Check token format: should start with `pypi-`
- Verify token is in `.pypi_tokens.conf`
- For Windows, check token doesn't have extra spaces or line breaks

**Fix:**
```cmd
# Windows
set TWINE_USERNAME=__token__
set TWINE_PASSWORD=pypi-YOUR-TOKEN-HERE
python -m twine upload dist/*
```

### 2. **Error: HTTPError: 400 Bad Request**

**Symptoms:**
```
HTTPError: 400 Bad Request from https://upload.pypi.org/legacy/
Invalid distribution file
```

**Solutions:**
- Run `python -m twine check dist/*`
- Rebuild the package: `python -m build --wheel --sdist`
- Check for invalid characters in package metadata

### 3. **Error: Package already exists**

**Symptoms:**
```
HTTPError: 400 Bad Request from https://upload.pypi.org/legacy/
File already exists
```

**Solutions:**
- You can't upload the same version twice
- Bump the version: `publish.bat -b patch`
- Delete old files from `dist/` folder

### 4. **Error: SSL Certificate verification failed**

**Symptoms:**
```
SSL: CERTIFICATE_VERIFY_FAILED
```

**Solutions for Windows:**
```cmd
# Update certificates
pip install --upgrade certifi

# Or disable SSL verification (NOT recommended for production)
set TWINE_CERT=/path/to/cert.pem
```

### 5. **Error: Connection timeout**

**Symptoms:**
```
requests.exceptions.ConnectTimeout
```

**Solutions:**
- Check internet connection
- Check proxy settings
- Try using a different network
- For corporate networks:
  ```cmd
  set HTTP_PROXY=http://proxy.company.com:8080
  set HTTPS_PROXY=http://proxy.company.com:8080
  ```

### 6. **Error: Invalid token format**

**Symptoms:**
```
HTTPError: 401 Unauthorized
```

**Solutions:**
- Ensure token starts with `pypi-`
- No extra spaces or quotes around token
- Token hasn't expired
- Using correct token for correct repository (PyPI vs TestPyPI)

## Debug Commands for Windows

### 1. Test with verbose output:
```cmd
python -m twine upload --verbose --repository testpypi dist/*
```

### 2. Check package validity:
```cmd
python -m twine check dist/*
```

### 3. Manual upload with token:
```cmd
# Set environment variables
set TWINE_USERNAME=__token__
set TWINE_PASSWORD=pypi-AgEIcHlwaS5vcmcCJGI0MjcxY2QtMzcyYS00YTJmLThh...

# Upload
python -m twine upload --repository testpypi dist/*
```

### 4. Test with config file:
```cmd
# Create .pypirc in user home directory
echo [distutils] > %USERPROFILE%\.pypirc
echo index-servers = >> %USERPROFILE%\.pypirc
echo     pypi >> %USERPROFILE%\.pypirc
echo     testpypi >> %USERPROFILE%\.pypirc
echo. >> %USERPROFILE%\.pypirc
echo [pypi] >> %USERPROFILE%\.pypirc
echo username = __token__ >> %USERPROFILE%\.pypirc
echo password = pypi-YOUR-TOKEN-HERE >> %USERPROFILE%\.pypirc
echo. >> %USERPROFILE%\.pypirc
echo [testpypi] >> %USERPROFILE%\.pypirc
echo repository = https://test.pypi.org/legacy/ >> %USERPROFILE%\.pypirc
echo username = __token__ >> %USERPROFILE%\.pypirc
echo password = pypi-YOUR-TEST-TOKEN-HERE >> %USERPROFILE%\.pypirc
```

### 5. Run debug script:
```cmd
# Use the debug script
python debug_upload.py

# Or on Windows
debug_upload.bat
```

## Quick Checklist

Before uploading, ensure:

1. ✓ Package builds without errors: `python -m build`
2. ✓ Package passes checks: `python -m twine check dist/*`
3. ✓ Token is correctly formatted (starts with `pypi-`)
4. ✓ Using `__token__` as username
5. ✓ No old versions in `dist/` folder
6. ✓ Version number is unique
7. ✓ Internet connection is working
8. ✓ Using correct repository URL

## Getting More Help

If you still have issues:

1. Run the debug script: `python debug_upload.py`
2. Check PyPI status: https://status.python.org/
3. Try TestPyPI first: https://test.pypi.org/
4. Check token permissions on PyPI website
5. Create a new token if needed

## Example Successful Upload

Here's what a successful upload looks like:

```
Uploading distributions to https://upload.pypi.org/legacy/
Uploading django_jqgrid-1.0.0-py3-none-any.whl
100%|████████████████████| 1.20M/1.20M [00:02<00:00, 564kB/s]
Uploading django_jqgrid-1.0.0.tar.gz
100%|████████████████████| 1.06M/1.06M [00:01<00:00, 612kB/s]

View at:
https://pypi.org/project/django-jqgrid/1.0.0/
```