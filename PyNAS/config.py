version_info = (2022, 4, 12)
version = '.'.join(str(c) for c in version_info[:-1])
version += f" {version_info[-1]}" if str(
    version_info[-1]).isdigit() == False else f".{version_info[-1]}"
__doc__ = ''
base_directory = ''
