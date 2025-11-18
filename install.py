# import json
# import os
# import sys
# from jupyter_client.kernelspec import install_kernel_spec
# from IPython.utils.tempdir import TemporaryDirectory
#
# kernel_json = {
#     "argv": [sys.executable, "-m", "your_language_kernel", "-f", "{connection_file}"],
#     "display_name": "Your Language",
#     "language": "your_language",
# }
#
# def install_my_kernel():
#     with TemporaryDirectory() as td:
#         with open(os.path.join(td, 'kernel.json'), 'w') as f:
#             json.dump(kernel_json, f, sort_keys=True)
#         install_kernel_spec(td, 'your_language', user=True, replace=True)
#
# if __name__ == '__main__':
#     install_my_kernel()

import json
import os
import sys
from jupyter_client.kernelspec import install_kernel_spec
from IPython.utils.tempdir import TemporaryDirectory

def install_kernel():
    kernel_json = {
        "argv": [
            sys.executable,
            "-c",
            """
import sys
sys.path.insert(0, '/home/chief9/projects/algrus-core')
from kernel import YourLanguageKernel
YourLanguageKernel.launch_instance()
            """.strip(),
            "-f",
            "{connection_file}"
        ],
        "display_name": "Algrus Language",
        "language": "algrus",
    }

    with TemporaryDirectory() as td:
        with open(os.path.join(td, 'kernel.json'), 'w') as f:
            json.dump(kernel_json, f, sort_keys=True)

        install_kernel_spec(td, 'algrus', user=True, replace=True)
        print("Kernel installed successfully!")

if __name__ == '__main__':
    install_kernel()
