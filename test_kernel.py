import sys
import os

# Добавьте путь к вашей папке
sys.path.insert(0, '/home/chief9/projects/algrus-core')

try:
    from algrus_core.kernel import YourLanguageKernel
    print("✅ Kernel imported successfully!")

    # Проверьте что зависимости работают
    from algrus_core.lexer import Lexer
    from algrus_core.parser import Parser
    print("✅ All dependencies imported!")

except ImportError as e:
    print(f"❌ Import error: {e}")
    print(f"Current path: {sys.path}")
