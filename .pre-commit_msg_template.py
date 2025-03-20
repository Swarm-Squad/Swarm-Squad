import re
import sys

VALID_TYPES = [
    "fix",
    "feat",
    "docs",
    "style",
    "refactor",
    "perf",
    "test",
    "build",
    "ci",
    "chore",
    "revert",
]

TEMPLATE = """
Available commit message types:
    - `fix`: A bug fix. Correlates with PATCH in SemVer
    - `feat`: A new feature. Correlates with MINOR in SemVer
    - `docs`: Documentation only changes
    - `style`: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
    - `refactor`: A code change that neither fixes a bug nor adds a feature
    - `perf`: A code change that improves performance
    - `test`: Adding missing or correcting existing tests
    - `build`: Changes that affect the build system or external dependencies (example scopes: pip, docker, npm)
    - `ci`: Changes to CI configuration files and scripts (example scopes: GitLabCI)
    - `chore`: General maintenance tasks, dependency updates, etc.
    - `revert`: Reverts a previous commit.
Invalid commit message format!
Commit message must follow the format:
    git commit -m "<type>: <description>"
where <type> must be one of: {}
""".format(", ".join(VALID_TYPES))


def main():
    commit_msg_filepath = sys.argv[1]
    with open(commit_msg_filepath, "r") as f:
        commit_msg = f.read()

    # Check if message starts with valid type
    pattern = r"^(" + "|".join(VALID_TYPES) + r"):"
    if not re.match(pattern, commit_msg):
        print(TEMPLATE)
        sys.exit(1)


if __name__ == "__main__":
    main()
