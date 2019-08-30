# Installing
## From prebuilt wheel
1. Download `*.whl` from the latest [release](https://github.com/integralads/migrator/releases)
2. Install with:
```
pip install --upgrade path_to_wheel.whl 
```

## From sources
```
rm -r build dist
python setup.py bdist_wheel
pip install --upgrade dist/*.whl
```

## Usage
`python -m migrator --help`  

### statistics

Counts multiple migration-related statistics on project. 
The main purpose is to help to understand the amount of work to be done.

`python -m migrator statistics --help`

### smart2to3

Applies groups of `2to3` fixers and commits changes into different commits.

`python -m migrator smart2to3 --help`  

Groups can be reconfigured if needed. 
Default configuration can be found 
[here](https://github.com/integralads/migrator/blob/master/migrator/common/resources/default-groups.yaml).  

Allowed properties for each group:
- `name: str` - group name, will be used in commit
- `fixers: List[str]` - list of fixers to apply
- `description: Optional[str]` - description, will be added to commit
- `params: Optional[List[str]]` - additional flags, that will be added to 2to3
- `only_on_write_params: Optional[List[str]]` - similar to `params`,
 but will be added only if called with `--write` flag

## Issues

Please report any issues. Make sure to include `~/.migrator_full_log` file, 
which contains a full log of *the latest* run.

### smart2to3
#### "Can't parse ..."

Some fixers (like `print`) can change sources in a way they are no longer parsable by lib2to3.
This results in error, similar to:

>RefactoringTool: Can't parse ...: ParseError: bad input: type=...

Please open an issue on such behaviour. The solution may be moving such fixer to the last group.
