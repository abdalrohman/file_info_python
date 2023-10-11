import argparse
import os
import platform
import stat
import time

import tabulate

# Constants
UNITS_1000 = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB']
UNITS_1024 = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB']


def calculate_size(size, units):
    """
    Calculate the size in a human-readable format.

    Args:
        size (int): The size to be converted.
        units (str): The unit of measurement to be used in the conversion. Must be either "UNITS_1000" or "UNITS_1024".

    Returns:
        str: The size in a human-readable format, with the appropriate unit of measurement.
    """
    if size <= 0: return "0 B"
    from math import log2
    base = 1000 if units == UNITS_1000 else 1024
    i = int(log2(size) / log2(base))
    return f"{size / (base ** i):.1f} {units[i]}"


def get_size(path):
    """
    Returns the total size of a file or directory.

    Args:
        path (str): The path to the file or directory.

    Returns:
        int: The total size in bytes.
    """
    if os.path.isfile(path):
        return os.stat(path).st_size
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                total_size += os.path.getsize(fp)
            except OSError as e:
                print(f"Error: {e}")
    return total_size


def stat_size(path, multiplier=1000):
    """
    Calculate the size of a file or directory.

    Args:
        path (str): The path to the file or directory.
        multiplier (int, optional): The multiplier to use for calculating the size. Defaults to 1000.

    Returns:
        int: The calculated size of the file or directory.

    Raises:
        FileNotFoundError: If the specified path does not exist.
    """
    if not os.path.exists(path):
        print("Error: Path does not exist.")
        return
    size = get_size(path)
    units = UNITS_1000 if multiplier == 1000 else UNITS_1024
    return calculate_size(size, units)


class FileCount:
    def __init__(self):
        self.dirs = 0
        self.files = 0
        self.links = 0


def count_file(path, counts):
    """
    Count the number of files, directories, and symbolic links in a given path.

    Args:
        path (str): The path to the directory to be counted.
        counts (Counts): An object that keeps track of the number of files, directories, and symbolic links.
    """
    try:
        for entry in os.scandir(path):
            if entry.is_symlink():
                counts.links += 1
            elif entry.is_dir():
                counts.dirs += 1
                count_file(entry.path, counts)
            elif entry.is_file():
                counts.files += 1
    except OSError as e:
        print(f"Cannot open directory: {path}. Error: {e}")


def line_count(filename):
    """
    Counts the number of lines in a given file.

    Args:
        filename (str): The name of the file to count the lines in.

    Returns:
        int: The total number of lines in the file.

    Raises:
        OSError: If there was an error while opening the file.
    """
    try:
        with open(filename, 'r') as file:
            return sum(1 for _ in file)
    except OSError as e:
        print(f"Could not open file {filename}. Error: {e}")


def print_mod_time(stats):
    """
    Generate a formatted string representing the modification time of a file.

    Args:
        stats (os.stat_result): The result of calling os.stat() on the file.

    Returns:
        str: A formatted string representing the modification time of the file.
    """
    return time.strftime("%d %m-%Y %H:%M", time.localtime(stats.st_ctime))


def print_permissions(stats):
    """
    Print the permissions of a file or directory.

    Args:
        stats (os.stat_result): A named tuple containing the file or directory
            statistics.

    Returns:
        str: The file mode as a string representation.
    """
    return stat.filemode(stats.st_mode)


def print_color(text, fg=None, bg=None, attr=None):
    """
    Prints the given text with specified color and attribute codes.

    Args:
        text (str): The text to print.
        fg (int, optional): The foreground color code. Defaults to None.
        bg (int, optional): The background color code. Defaults to None.
        attr (int, optional): The attribute code. Defaults to None.
    """
    # fg: foreground color code
    # bg: background color code
    # attr: attribute code
    # text: the text to print

    # create an empty string to store the escape sequence
    esc_seq = '\033['

    # if attribute is given, add it to the escape sequence
    if attr:
        esc_seq += str(attr) + ';'

    # if foreground color is given, add it to the escape sequence
    if fg:
        esc_seq += str(fg) + ';'

    # if background color is given, add it to the escape sequence
    if bg:
        esc_seq += str(bg) + ';'

    # remove the last ';' if any
    esc_seq = esc_seq.rstrip(';')

    # end the escape sequence with 'm'
    esc_seq += 'm'

    # print the text with the escape sequence and reset it at the end
    print(esc_seq + text + '\033[0m')


# def short_mod(pathname):
#     try:
#         stats = os.stat(pathname)
#         size = stat_size(pathname)
#         mod_time = print_mod_time(stats)
#         permissions = print_permissions(stats)
#         basename = os.path.basename(pathname)
#
#         if os.path.isdir(pathname):
#             counts = FileCount()
#             count_file(pathname, counts)
#             print(
#                 f"{permissions}, {size}, {counts.files:6d}F: {counts.dirs:d}D: {counts.links:d}S, {mod_time}\t{basename}")
#         elif os.path.isfile(pathname):
#             lines = line_count(pathname)
#             print(f"{permissions}, {size}, {lines:10d} lines, {mod_time}\t{basename}")
#         elif os.path.islink(pathname):
#             link_to = os.readlink(pathname)
#             print(f"{permissions}, {size}, {mod_time}\t'{basename}' -> '{link_to}'")
#     except OSError as e:
#         print(f"Error: {e}")


def short_mod(pathname):
    """
    Retrieves and prints information about a file or directory.

    Args:
        pathname (str): The path to the file or directory.

    Returns:
        None
    """
    try:
        stats = os.stat(pathname)
        size = stat_size(pathname)
        mod_time = print_mod_time(stats)
        permissions = print_permissions(stats)
        basename = os.path.basename(pathname)
        if os.path.islink(pathname):
            link_to = os.readlink(pathname)
            print_color(
                f"{permissions}, {size}, {mod_time}\t{basename} -> {link_to}",
                fg=35)  # magenta foreground
        elif os.path.isdir(pathname):
            counts = FileCount()
            count_file(pathname, counts)
            print_color(
                f"{permissions}, {size}, F:{counts.files:<6d}, D:{counts.dirs:<6d}, S:{counts.links:<6d}, {mod_time}\t{basename}",
                fg=32)  # green foreground
        elif os.path.isfile(pathname):
            lines = line_count(pathname)
            print_color(
                f"{permissions}, {size}, {lines:>23d} lines, {mod_time}\t{basename}",
                fg=34)  # blue foreground

    except OSError as e:
        print(f"Error: {e}")


# def long_mod(pathname):
#     try:
#         stats = os.stat(pathname)
#         uid = stats.st_uid
#         gid = stats.st_gid
#         grp_info = grp.getgrgid(gid)
#         pw_info = pwd.getpwuid(uid)
#         size = stat_size(pathname)
#         mod_time = time.ctime(stats.st_mtime)
#         inode = stats.st_ino
#
#         if os.path.isdir(pathname):
#             counts = FileCount()
#             count_file(pathname, counts)
#             print(
#                 f"Folder name: {pathname}\n\tCounts:\t\t\t{{ {counts.files} files, {counts.dirs} directories, {counts.links} symlink }}\n\tPermissions:\t\t{oct(stats.st_mode)[-3:]}\n\tUsr/Grp:\t\t( {pw_info.pw_name} / {grp_info.gr_name} )\n\tGid/Uid:\t\t( {pw_info.pw_gid} / {pw_info.pw_uid} )\n\tSize:\t\t\t{size}\n\tModified:\t\t{mod_time}\n\tInode:\t\t\t{inode}")
#         elif os.path.isfile(pathname):
#             lines = line_count(pathname)
#             print(
#                 f"File name: {pathname}\n\tLine count:\t\t{lines} lines\n\tPermissions:\t\t{oct(stats.st_mode)[-3:]}\n\tUsr/Grp:\t\t( {pw_info.pw_name} / {grp_info.gr_name} )\n\tGid/Uid:\t\t( {pw_info.pw_gid} / {pw_info.pw_uid} )\n\tSize:\t\t\t{size}\n\tModified:\t\t{mod_time}\n\tInode:\t\t\t{inode}")
#         elif os.path.islink(pathname):
#             link_to = os.readlink(pathname)
#             print(
#                 f"File name: {pathname}\n\tPermissions:\t\t{oct(stats.st_mode)[-3:]}\n\tUsr/Grp:\t\t( {pw_info.pw_name} / {grp_info.gr_name} )\n\tGid/Uid:\t\t( {pw_info.pw_gid} / {pw_info.pw_uid} )\n\tSize:\t\t\t{size}\n\tModified:\t\t{mod_time}\n\tInode:\t\t\t{inode}\n\tSymbolic link to:\t{link_to}")
#     except OSError as e:
#         print(f"Error: {e}")

def long_mod(pathname):
    """
    Generate the metadata of a file or directory at the given pathname.

    Args:
        pathname (str): The path to the file or directory.

    Returns:
        None
    """
    try:
        stats = os.stat(pathname)
        size = stat_size(pathname)
        mod_time = time.ctime(stats.st_mtime)
        inode = stats.st_ino

        # create a list of headers for the table
        headers = ["Name", "Counts", "Permissions", "Usr/Grp", "Gid/Uid", "Size", "Modified", "Inode", "Link"]

        # create an empty list to store the data for the table
        data = []

        # get the operating system name
        os_name = platform.system()

        # if the operating system is Windows
        if os_name == 'Windows':
            # import the wmi module
            import wmi
            # create a wmi object
            c = wmi.WMI()
            # get the computer system information
            my_system = c.Win32_ComputerSystem()[0]
            # get the user and group name from the computer system information
            user_name = my_system.UserName
            group_name = my_system.Domain

            if os.path.isdir(pathname):
                counts = FileCount()
                count_file(pathname, counts)
                # append a list of values for the directory to the data list
                data.append([pathname, f"{counts.files} files, {counts.dirs} directories, {counts.links} symlink",
                             oct(stats.st_mode)[-3:], f"{user_name} / {group_name}",
                             None, size, mod_time, inode, None])
            elif os.path.isfile(pathname):
                lines = line_count(pathname)
                # append a list of values for the file to the data list
                data.append([pathname, f"{lines} lines", oct(stats.st_mode)[-3:], f"{user_name} / {group_name}",
                             None, size, mod_time, inode, None])
            elif os.path.islink(pathname):
                link_to = os.readlink(pathname)
                # append a list of values for the link to the data list
                data.append([pathname, None, oct(stats.st_mode)[-3:], f"{user_name} / {group_name}",
                             None, size, mod_time, inode, link_to])

        # if the operating system is Linux
        elif os_name == 'Linux':
            import pwd
            import grp
            uid = stats.st_uid
            gid = stats.st_gid
            grp_info = grp.getgrgid(gid)
            pw_info = pwd.getpwuid(uid)
            user_name = pw_info.pw_name
            group_name = grp_info.gr_name

            if os.path.isdir(pathname):
                counts = FileCount()
                count_file(pathname, counts)
                # append a list of values for the directory to the data list
                data.append([pathname, f"{counts.files} files, {counts.dirs} directories, {counts.links} symlink",
                             oct(stats.st_mode)[-3:], f"{user_name} / {group_name}",
                             f"{pw_info.pw_gid} / {pw_info.pw_uid}", size, mod_time, inode, None])
            elif os.path.isfile(pathname):
                lines = line_count(pathname)
                # append a list of values for the file to the data list
                data.append([pathname, f"{lines} lines", oct(stats.st_mode)[-3:], f"{user_name} / {group_name}",
                             f"{pw_info.pw_gid} / {pw_info.pw_uid}", size, mod_time, inode, None])
            elif os.path.islink(pathname):
                link_to = os.readlink(pathname)
                # append a list of values for the link to the data list
                data.append([pathname, None, oct(stats.st_mode)[-3:], f"{user_name} / {group_name}",
                             f"{pw_info.pw_gid} / {pw_info.pw_uid}", size, mod_time, inode, link_to])

        # print the table using tabulate with a simple format
        print(tabulate.tabulate(data, headers=headers, tablefmt="simple"))

    except OSError as e:
        print(f"Error: {e}")


def main():
    parser = argparse.ArgumentParser(prog='program_name')
    parser.add_argument('-s', action='store_true', help='Short mode')
    parser.add_argument('-l', action='store_true', help='Long mode')
    parser.add_argument('paths', nargs='*', default=['.'], help='Paths to process')
    args = parser.parse_args()

    for path in args.paths:
        try:
            if args.s:
                short_mod(path)

            elif args.l:
                long_mod(path)

            else:
                short_mod(path)

        except OSError as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
