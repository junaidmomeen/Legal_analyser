#!/bin/sh
set -e

echo "================================"
echo "Legal Document Analyzer - Startup"
echo "================================"
echo ""

# Verify OCR installation
echo "Checking OCR dependencies..."
if command -v tesseract >/dev/null 2>&1; then
    TESSERACT_VERSION=$(tesseract --version 2>&1 | head -n1)
    echo "✓ Tesseract OCR: $TESSERACT_VERSION"

    # Check for language data
    if tesseract --list-langs >/dev/null 2>&1; then
        LANGS=$(tesseract --list-langs 2>&1 | tail -n +2 | tr '\n' ', ' | sed 's/,$//')
        echo "✓ Available languages: $LANGS"
    else
        echo "⚠ Warning: No Tesseract language data found"
    fi
else
    echo "⚠ WARNING: Tesseract OCR not found - image processing will be disabled"
fi

# Check libmagic
if ldconfig -p | grep -q libmagic; then
    echo "✓ libmagic installed"
else
    echo "⚠ WARNING: libmagic not found - file type detection may fail"
fi

echo ""
echo "Starting application..."
echo "================================"
echo ""

# Start the application with dynamic port
exec python -m uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}" --workers 4
