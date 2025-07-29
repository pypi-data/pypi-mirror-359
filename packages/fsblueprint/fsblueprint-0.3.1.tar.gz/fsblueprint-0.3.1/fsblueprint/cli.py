import argparse
import sys
from pathlib import Path

from fsblueprint.core.scaffold import create_from_yaml
from fsblueprint.core.blueprint import create_yaml_from_structure, create_structure_preview
from fsblueprint.core.ignore_patterns import DEFAULT_IGNORE_PATTERNS

def main():
    parser = argparse.ArgumentParser(
        description="FSBlueprint - YAML ↔ Directory Structure Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  fsblueprint scaffold project.yaml ./my_app                  # Create structure from YAML
  fsblueprint blueprint ./my_app                              # Show structure as tree (default)
  fsblueprint blueprint ./my_app blueprint.yaml --with-content  # Save structure & content as YAML
  fsblueprint blueprint ./my_app --no-ignore                  # Show all files in preview
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Scaffold command
    scaffold_parser = subparsers.add_parser('scaffold', help='Create directory structure from YAML')
    scaffold_parser.add_argument('yaml_file', help='Input YAML file')
    scaffold_parser.add_argument('target_dir', help='Target directory to create structure')

    # Blueprint command
    blueprint_parser = subparsers.add_parser(
    'blueprint',
    help='Generate and view a blueprint (tree or YAML) from a project structure'
)

    blueprint_parser.add_argument('source_dir', help='Directory to scan')
    blueprint_parser.add_argument(
    'yaml_file',
    nargs='?',
    help='(Optional) Output YAML file – required when using --with-content'
)

    blueprint_parser.add_argument('--no-ignore', action='store_true', help='Include all files (disable ignore patterns)')
    blueprint_parser.add_argument('--ignore', nargs='+', help='Additional patterns to ignore')
    blueprint_parser.add_argument('--with-content', action='store_true', help='Include file content in the YAML output')
    

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == 'scaffold':
            if not Path(args.yaml_file).exists():
                print(f"Error: YAML file '{args.yaml_file}' not found")
                sys.exit(1)

            create_from_yaml(args.yaml_file, args.target_dir)
            print(f"✅ Structure created at '{args.target_dir}'")

        elif args.command == 'blueprint':
            if not Path(args.source_dir).exists():
                print(f"Error: Directory '{args.source_dir}' not found")
                sys.exit(1)

            ignore_patterns = None if args.no_ignore else DEFAULT_IGNORE_PATTERNS.copy()
            if args.ignore:
                if ignore_patterns:
                    ignore_patterns.update(args.ignore)
                else:
                    ignore_patterns = set(args.ignore)

            if args.with_content:
                if not args.yaml_file:
                    print("❌ Error: --with-content requires a YAML output file")
                    sys.exit(1)

                create_yaml_from_structure(
                    args.source_dir,
                    args.yaml_file,
                    ignore_patterns,
                    include_content=True
                )
                print(f"✅ Blueprint with content saved to '{args.yaml_file}'")
            else:
                preview = create_structure_preview(args.source_dir, ignore_patterns)
                dir_name = Path(args.source_dir).name.capitalize()
                print(f"📂 {dir_name} Structure Preview:\n")
                print(preview)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
