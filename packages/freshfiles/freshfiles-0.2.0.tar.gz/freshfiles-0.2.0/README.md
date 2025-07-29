## Installation with UV

`uv tool install freshfiles`

## Sample use-case in bash

### Checking the age

```shell
# `./update_files.sh` is invoked if any of these files are missing or more than 1 hour old
freshfiles check --max-age-seconds 3600 file1 file2 || ./update_files.sh



freshfiles check --max-age-seconds 3600 .authfile && echo "no auth needed" || { 
    echo "authenticating" # replace with actual authentication
    touch .authfile
}
```


### Checking that target files are more recent that any of the source files used to generate the target


```shell
freshfiles compare -s src1 -s src2 -t dest || echo "update dest from src1 and src2" 
```

## Using justfiles

Project link: https://just.systems/man/en/introduction.html

```
[private]
_maybe_authenticate:
  #!/usr/bin/env bash
  set -euo pipefail
  freshfiles check --max-age-seconds 3 .authfile && echo "auth still valid" || { 
        echo "authenticating" # replace with actual authentication
        touch .authfile
  }

run: _maybe_authenticate
  @echo "... do work with valid auth"
```