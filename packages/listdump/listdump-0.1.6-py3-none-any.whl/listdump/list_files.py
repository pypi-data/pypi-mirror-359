import os
import sys
import fnmatch

def show_help():
    print("""
Usage:
  python list_files.py [includes] [-x excludes] [-no-sub] [-out=filename] [-dir=path] [-no-gitignore] [-include-hidden]

Arguments:
  includes            List of extensions or glob patterns to include (e.g. txt py log_*_202*.log)
  -x, --exclude       List of extensions or glob patterns to exclude
  -no-sub             Exclude subfolders
  -out=FILE           Output file name (default: output.md)
  -dir=DIR            Starting directory (default: current)
  -no-gitignore       Do not respect .gitignore rules
  -include-hidden     Include normally excluded files: .git, .gitignore, listdump.md, and license files (LICENCE, LICENSE)
  -h, --help          Show this help message
Examples:
  python list_files.py txt py -x log tmp
  python list_files.py log_*_202*.log -no-sub -out=logs.md
  python list_files.py py -dir=src -x test_*.py -no-gitignore -include-hidden
""")
    sys.exit(0)

def parse_args(args):
    if not args or any(arg in ['-h', '--help'] for arg in args):
        show_help()

    include_patterns = []
    exclude_patterns = []
    include_subfolders = True
    start_dir = "."
    output_file = "listdump.md"
    respect_gitignore = True
    ignore_git_and_listdump = True

    i = 0
    mode = 'include'
    while i < len(args):
        arg = args[i]
        if arg in ['-x', '--exclude']:
            mode = 'exclude'
        elif arg == '-no-sub':
            include_subfolders = False
        elif arg == '-no-gitignore':
            respect_gitignore = False
        elif arg == '-include-hidden':
            ignore_git_and_listdump = False
        elif arg.startswith('-out='):
            output_file = arg.split("=", 1)[1]
        elif arg.startswith('-dir='):
            start_dir = arg.split("=", 1)[1]
        elif arg.startswith('-'):
            print(f"Unknown argument: {arg}")
            show_help()
        else:
            if '.' not in arg and '*' not in arg:
                arg = f'*.{arg}'
            elif not any(c in arg for c in ['*', '?']):
                arg = f'*{arg}'
            (include_patterns if mode == 'include' else exclude_patterns).append(arg)
        i += 1

    return include_patterns, exclude_patterns, include_subfolders, start_dir, output_file, respect_gitignore, ignore_git_and_listdump

def matches_patterns(filename, patterns):
    return any(fnmatch.fnmatch(filename, pattern) for pattern in patterns)

def collect_files(start_path, include_patterns, exclude_patterns, include_subfolders, respect_gitignore, ignore_git_and_listdump):
    output = []
    listed_files = []

    if ignore_git_and_listdump:
        exclude_patterns.extend([".git", ".gitignore", "listdump.md", "LICENCE", "LICENSE"])

    # Add pathspec for .gitignore handling
    spec = None
    if respect_gitignore:
        try:
            from pathspec import PathSpec
            from pathspec.patterns.gitwildmatch import GitWildMatchPattern
            gitignore_path = os.path.join(start_path, '.gitignore')
            if os.path.exists(gitignore_path):
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    spec = PathSpec.from_lines(GitWildMatchPattern, f)
        except ImportError:
            print("Warning: pathspec module not found. .gitignore entries will not be ignored.")

    for root, dirs, files in os.walk(start_path):
        dirs[:] = [d for d in dirs if not matches_patterns(d, exclude_patterns)]

        if not include_subfolders:
            dirs.clear()
        for file in files:
            path = os.path.join(root, file)
            rel_path = os.path.relpath(path, start_path).replace('\\', '/')

            if spec and spec.match_file(rel_path):
                continue
            if include_patterns and not matches_patterns(file, include_patterns):
                continue
            if exclude_patterns and matches_patterns(file, exclude_patterns):
                continue
            listed_files.append(path)
            print(path)
            output.append(f"File: {path}\n```")
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    output.append(f.read())
            except Exception as e:
                output.append(f"(Could not read file: {e})")
            output.append("```\n")

    return output

def main():
    include_patterns, exclude_patterns, include_subfolders, start_dir, output_file, respect_gitignore, ignore_git_and_listdump = parse_args(sys.argv[1:])
    results = collect_files(start_dir, include_patterns, exclude_patterns, include_subfolders, respect_gitignore, ignore_git_and_listdump)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(results))

    print(f"\n✓ Output saved to: {output_file}")

if __name__ == "__main__":
    main()
