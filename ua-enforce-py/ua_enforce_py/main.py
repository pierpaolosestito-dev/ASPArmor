import getpass
import os
import re
import sys
from collections import defaultdict

pattern_has_include = re.compile(r"^\s*include\s+if\s+exists\s+<\s*.usr.bin.clingo/mappings\s*>\s*$")
pattern_selectable_line = re.compile(r"^\s*#@selectable\s*\{\s*(?P<alias>[A-Za-z0-9_-]+)\s*}\s*(?P<content>\S.*)$")
pattern_removable_line = re.compile(r"^(?P<content>.*)\s*#@removable\s*\{\s*(?P<alias>[A-Za-z0-9_-]+)\s*}\s*$")
pattern_selectable_block_begin = re.compile(r"^\s*#@selectable\s*\{\s*(?P<alias>[A-Za-z0-9_-]+)\s*}\s*$")
pattern_selectable_block_content = re.compile(r"^\s*#(?P<content>[^@].*)?$")
pattern_selectable_block_end = re.compile(r"^\s*#@end\s*$")
pattern_select = re.compile(r"^\s*#@select\s*:\s*(?P<alias>[A-Za-z0-9_-]+)?(?:\s*(?P<aliases>[A-Za-z0-9_-]+))*\s*$")
pattern_remove = re.compile(r"^\s*#@remove\s*:\s*(?P<alias>[A-Za-z0-9_-]+)?(?:\s*(?P<aliases>[A-Za-z0-9_-]+))*\s*$")


def enforce(binary, profile_file, profile_dir_relative_path, profile):
    pattern_is_starting_the_profile = re.compile(r"^.*(profile\s+)?" + binary + r"\s*\{\s*(?P<content>.*)$", re.DOTALL)

    has_include = False
    selectable_block = None
    selectable = defaultdict(list)
    removable = defaultdict(list)
    base_rules = []

    with open(profile_file, 'r') as pf:
        profile_file_text = pf.read()
        match = pattern_is_starting_the_profile.match(profile_file_text)
        if not match:
            raise ValueError("Invalid profile file content")
        profile_file_content = match.group('content')
        profile_file_content = profile_file_content[:profile_file_content.rindex('}')]

        for line_index, line in enumerate(profile_file_content.split('\n')):
            if selectable_block:
                match = pattern_selectable_block_content.match(line)
                if not match:
                    match = pattern_selectable_block_end.match(line)
                    if not match:
                        raise ValueError("Unterminated block! All lines in the block must start with #")
                    selectable_block = None
                content = (match.group('content') or '') if match.groups() else ''
                selectable[selectable_block].append(content)
                continue

            if pattern_has_include.match(line):
                has_include = True
                continue

            match = pattern_selectable_line.match(line)
            if match:
                alias = match.group("alias")
                content = match.group("content")
                selectable[alias].append(content)
                continue

            match = pattern_removable_line.match(line)
            if match:
                alias = match.group("alias")
                content = match.group("content") or ''
                base_rules.append(line)
                removable[alias].append(line_index)
                continue

            match = pattern_selectable_block_begin.match(line)
            if match:
                if selectable_block:
                    raise ValueError("Nested selectable blocks are not permitted!")
                selectable_block = match.group("alias")
                continue

            if line is not None:
                base_rules.append(line)

    if not has_include:
        with open(profile_file, 'w') as pf:
            index = profile_file_text.rindex('}')
            pf.write(f"{profile_file_text[:index]}\n    include if exists <{profile_dir_relative_path}/mappings>\n{profile_file_text[index:]}")

    mapping_content = []
    profile_dir = f"/etc/apparmor.d/{profile_dir_relative_path}"
    users = [f.name for f in os.scandir(profile_dir) if f.is_file() and f.name != "mappings"]
    for user in users:
        remove = set()
        with open(f"{profile_dir}/{user}", 'r') as pf:
            match = re.match(r"^(?P<prefix>\s*profile\s+" + user + r"\s*\{\s*)(?P<content>.*)$", pf.read(), re.DOTALL)
            if not match:
                raise ValueError("Invalid profile file content for user " + user)
            prefix = match.group('prefix')
            content = match.group('content')
            mapping_content.append(prefix)

            lines = content.split('\n')
            for line in lines:
                match = pattern_remove.match(line)
                if match:
                    for alias in match.groups():
                        remove.update(removable[alias])

            mapping_content.extend([rule for index, rule in enumerate(base_rules) if index not in remove])
            for line in lines:
                match = pattern_select.match(line)
                mapping_content.append(line)
                if match:
                    for alias in match.groups():
                        mapping_content.extend(selectable[alias])

    with open(f"{profile_dir}/mappings", 'w') as pf:
        pf.write("\n".join(mapping_content))


def main():
    try:
        if len(sys.argv) != 2 or not sys.argv[1].startswith('/'):
            sys.exit("The first argument must be the absolute path to the command to execute")
        profile_dir = sys.argv[1].replace('/', '.')
        enforce(sys.argv[1], f"/etc/apparmor.d/{profile_dir[1:]}", profile_dir, f"{sys.argv[1]}//{getpass.getuser()}")
    except Exception as e:
        print(e)
        sys.exit(1)


if __name__ == '__main__':
    main()
