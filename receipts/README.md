# Build receipts

Each file is a `receipt.json` (or `data-receipt.json`) exactly as the build
wrote it, byte for byte (its SHA-256 is in the table), kept here because the
build output itself is not committed. `repository_commit` is the commit that
was built; the receipt is committed after it.

| File | Build | Where | Receipt SHA-256 |
|---|---|---|---|
| `1-build-open5-stove_build.json` | Cradle `stove_build` of `58dec50`, target `.` (jobs `j20261103T025001-db880e` and `j20261103T025154-9a8613`, the same bytes) | Cradle's `os32-gcc16` stove (open5) | `82b90c17a9c976f8f49279705ea881780dea751f5122221bb844ed4954db8fb5` |
| `1-data.json` | Cradle `stove_build` of `58dec50`, target `runtime-data` (job `j20261103T025109-1f031a`) | Cradle (open5) | `462d98e15a3c29c6e72794e154137533af544fde1ae651c560373f02f0a3a06c` |
