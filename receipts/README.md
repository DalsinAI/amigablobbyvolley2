# Build receipts

Each file is a `receipt.json` (or `data-receipt.json`) exactly as the build
wrote it, byte for byte (its SHA-256 is in the table), kept here because the
build output itself is not committed. `repository_commit` is the commit that
was built; the receipt is committed after it.

| File | Build | Where | Receipt SHA-256 |
|---|---|---|---|
| `1-build-open5-stove_build.json` | Cradle `stove_build` of `58dec50`, target `.` (jobs `j20261103T025001-db880e` and `j20261103T025154-9a8613`, the same bytes) | Cradle's `os32-gcc16` stove (open5) | `82b90c17a9c976f8f49279705ea881780dea751f5122221bb844ed4954db8fb5` |
| `1-data.json` | Cradle `stove_build` of `58dec50`, target `runtime-data` (job `j20261103T025109-1f031a`) | Cradle (open5) | `462d98e15a3c29c6e72794e154137533af544fde1ae651c560373f02f0a3a06c` |
| `2-presentation-open5-stove_build.json` | Cradle `stove_build` of `4110cfd`, target `.` (job `j20261103T032131-ea4501`) | Cradle's `os32-gcc16` stove (open5) | `ed8fa5fafeb5856903cd10b09a6500c0d5b86992af210fdb567b771ce7477a16` |
| `2-data.json` | Cradle `stove_build` of `4110cfd`, target `runtime-data` (job `j20261103T032351-579a8d`) | Cradle (open5) | `b6da9a4489f8a5bf5aa49eb808a5d054da177b4582d56b17a7257f74d1daa794` |
| `3-input-open5-stove_build.json` | Cradle `stove_build` of `8c1fcd8`, target `.` (job `j20261103T033354-cfff1a`) | Cradle's `os32-gcc16` stove (open5) | `649dad635be1813b35bb3923d906b1a8c6b9e60861d9c5a97ba10c623d10860e` |
| `3-data.json` | Cradle `stove_build` of `8c1fcd8`, target `runtime-data` (job `j20261103T033437-3c50a9`) | Cradle (open5) | `fd4a9f1c735f23df04898484d23610ef6bea729a0de2c445ee92bdb36eedc8a5` |
| `4-sound-open5-stove_build.json` | Cradle `stove_build` of `e4a2ad4`, target `.` (job `j20261103T034436-8ab34b`) | Cradle's `os32-gcc16` stove (open5) | `b277843c408c1cac32ada334b84a90a246bfb6e8a7dd6edb7066af2c0b7e64b9` |
| `6-package-open5-stove_build.json` | Cradle `stove_build` of `165e9a2`, target `package` (job `j20261103T035627-058ea7`) | Cradle's `os32-gcc16` stove (open5) | `e7a9c92f7254b073793269dc14ced2f8c83fdc74de05b0199a9488bfe57dcfad` |
| `6-data.json` | the same job's data | Cradle (open5) | `c85baf05ce6f9cdbdd9e5dea603da26daed815558430bf51e08a554514083d0f` |
