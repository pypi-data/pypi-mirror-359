# ContentType Plugin Beta Test Files

This directory contains test files specifically designed for beta testing the new ContentType plugin interactive features.

## 📋 Test File Categories

### 🔴 Files That Need Fixing

These files have content type issues that the plugin should detect and offer to fix:

| File | Issue | Expected Fix |
|------|-------|--------------|
| `missing_content_type.adoc` | No content type attribute | Add `:_mod-docs-content-type: PROCEDURE` |
| `empty_content_type.adoc` | Empty content type value | Add appropriate content type value |
| `commented_content_type.adoc` | Content type is commented out | Uncomment and fix if needed |
| `wrong_content_type.adoc` | Deprecated content type format | Update to modern format |

### 🟢 Files That Should Be Ignored

These files have correct content type attributes and should not trigger any changes:

| File | Reason | 
|------|--------|
| `correct_procedure.adoc` | Has valid `:_mod-docs-content-type: PROCEDURE` |
| `correct_concept.adoc` | Has valid `:_mod-docs-content-type: CONCEPT` |
| `correct_reference.adoc` | Has valid `:_mod-docs-content-type: REFERENCE` |

## 🧪 Quick Testing Commands

### Test Individual Files
```bash
# Test review mode (shows issues without fixing)
asciidoc-dita-toolkit ContentType --mode review --file missing_content_type.adoc

# Test auto mode (automatically fixes issues)
asciidoc-dita-toolkit ContentType --mode auto --file missing_content_type.adoc

# Test interactive mode (prompts for each fix)
asciidoc-dita-toolkit ContentType --mode interactive --file missing_content_type.adoc
```

### Test All Files at Once
```bash
# Review all files in this directory
asciidoc-dita-toolkit ContentType --mode review --directory .

# Auto-fix all files (be careful!)
asciidoc-dita-toolkit ContentType --mode auto --directory . --dry-run

# Interactive mode for all files
asciidoc-dita-toolkit ContentType --mode interactive --directory .
```

### Docker Testing
```bash
# From this directory, test with Docker
docker run --rm -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit:beta \
  ContentType --mode review --directory /workspace

docker run --rm -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit:beta \
  ContentType --mode interactive --file missing_content_type.adoc
```

## 📝 How to Use These Files

### Option 1: Install via PyPI (includes test files)
```bash
pip install asciidoc-dita-toolkit==0.1.7b2
# Test files are automatically available in your Python site-packages
python -c "import asciidoc_dita_toolkit; print('Test files installed with package!')"
```

### Option 2: Use Docker (includes test files)
```bash
# Test files are already available in the container at /app/beta-testing/
docker run --rm rolfedh/asciidoc-dita-toolkit:beta ls /app/beta-testing/
```

### Option 3: Download or clone this directory
1. **Download or clone** this directory
2. **Make copies** of the files before testing (the plugin will modify them)
3. **Test different modes** on each file type
4. **Compare results** with the expected behavior described above
5. **Report any unexpected behavior** in GitHub issues

## 🔄 Resetting Test Files

After testing, you can restore the original files:

### If you downloaded files:
```bash
# Re-download to get fresh copies
curl -L https://github.com/rolfedh/asciidoc-dita-toolkit/archive/refs/heads/main.zip -o test-files.zip
unzip -o test-files.zip
cp asciidoc-dita-toolkit-main/beta-testing/*.adoc .
```

### If you cloned the repository:
```bash
git checkout -- *.adoc
```

### Manual reset:
Simply delete the modified files and re-download individual files from:
**https://github.com/rolfedh/asciidoc-dita-toolkit/tree/main/beta-testing**

## 🎯 What to Look For

- ✅ **Correct detection**: Does the plugin identify the right issues?
- ✅ **Appropriate fixes**: Are the suggested/applied fixes correct?
- ✅ **No false positives**: Are correct files left unchanged?
- ✅ **Good user experience**: Are prompts clear and helpful?
- ✅ **Performance**: Does it handle multiple files efficiently?

Happy testing! 🚀
