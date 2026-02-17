import os
import mimetypes
from collections import defaultdict

def scan_folder(folder_path):
    total_size = 0
    file_count = 0
    category_size = defaultdict(int)

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)

            try:
                size = os.path.getsize(file_path)
                total_size += size
                file_count += 1

                mime_type, _ = mimetypes.guess_type(file_path)

                if mime_type:
                    main_type = mime_type.split("/")[0]
                else:
                    main_type = "others"

                category_size[main_type] += size

            except Exception:
                continue

    storage_tb = total_size / (1024**4)

    return {
        "total_bytes": total_size,
        "storage_tb": storage_tb,
        "file_count": file_count,
        "category_breakdown": dict(category_size)
    }
