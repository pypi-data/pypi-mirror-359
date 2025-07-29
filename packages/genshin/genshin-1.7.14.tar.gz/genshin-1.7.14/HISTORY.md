# [1.7.14](https://github.com/seriaati/genshin.py/compare/v1.7.13..v1.7.14) - 2025-07-01

## Bug Fixes

- Fix nox coverage report - ([680dd6a](https://github.com/seriaati/genshin.py/commit/680dd6a8c4bfdfcf522e4ade4a5fa5559b0ac3d2))
- Fix some classes not being exported to __all__ in starrail/character.py - ([e10404f](https://github.com/seriaati/genshin.py/commit/e10404f7c9276e786ea0b475f7a6f98667e83733))
- Prevent enum validation errors in ZZZTempleRunning - ([699ae90](https://github.com/seriaati/genshin.py/commit/699ae905ec8c8f273168e400499506ec9412027e))
- Type hint loggers - ([abb12d9](https://github.com/seriaati/genshin.py/commit/abb12d941c71fe5b8ab18835728d1c65aa990b5c))
- Fix branch name - ([862184e](https://github.com/seriaati/genshin.py/commit/862184e3ce93086e494973c40c78fdeb964cafa4))
- Fix return typing of get_stygian_onslaught - ([0a0e8fa](https://github.com/seriaati/genshin.py/commit/0a0e8fae1e262d55f74f140ea691fb60fd6c1f89))
- Set type of HardChallengeData.best_record to optional - ([25eb7dd](https://github.com/seriaati/genshin.py/commit/25eb7dd4d68e3da7ce1842bdf2eac48c9b30f6a3))
- Fix HardChallengeBestRecord.icon containing invalid values - ([3bc20c2](https://github.com/seriaati/genshin.py/commit/3bc20c2f9cf22a045ba429087a96e1c4ec02090c))

## Continuous Integrations

- Allow running test by issue comment - ([0ac18a7](https://github.com/seriaati/genshin.py/commit/0ac18a76fe226a718b3db96c0ebcd88a0523f7e9))
- Enable coverage workflow - ([ff478a1](https://github.com/seriaati/genshin.py/commit/ff478a132852e16f9b9bee590c80f5fa10e82569))
- Fix nox workflows - ([bff4dfe](https://github.com/seriaati/genshin.py/commit/bff4dfea1129ff70e4929d704a354675ef163823))
- Try to fix coverage workflow - ([f9295bf](https://github.com/seriaati/genshin.py/commit/f9295bf9bf12975935d6ec240d17a96113d07f6c))
- Disable coverage report - ([0a54ede](https://github.com/seriaati/genshin.py/commit/0a54ede26b483123010ddffcaf624aeb1c1d7317))
- Update coverage artifact upload configuration ([#263](https://github.com/seriaati/genshin.py/issues/263)) - ([88dc231](https://github.com/seriaati/genshin.py/commit/88dc231270169129b9c27850a7995ab6d84a4629))
- Use qlty cloud for coverage report - ([1664ab2](https://github.com/seriaati/genshin.py/commit/1664ab2c5b814b10fd4efb0b9831c73f77022369))
- Enable upload-coverage - ([5ad6714](https://github.com/seriaati/genshin.py/commit/5ad6714ef1e6d1999cabb373c3db512e41ccf354))
- Fix missing dependencies - ([92babff](https://github.com/seriaati/genshin.py/commit/92babfff586e1d55fb6e62780eb3f778627de3cb))
- Combine coverage reports before making lcov report - ([79d054c](https://github.com/seriaati/genshin.py/commit/79d054c2fc7a28306b4013bb1cea1695dc88c4f3))
- Fix coverage lcov file name - ([9f4ab64](https://github.com/seriaati/genshin.py/commit/9f4ab6431f7b4c58000087a6d39882cc453cd036))
- Update workflow triggers for checks and docs to specify paths - ([0b9bffe](https://github.com/seriaati/genshin.py/commit/0b9bffe872046c22183858d890f2e6d75e1948aa))
- Use pyright-action - ([618782f](https://github.com/seriaati/genshin.py/commit/618782f6615c71bfbbbb10442b04fbad09f4f2bd))
- Make release workflow only watch for pyproject.toml changes - ([a30342b](https://github.com/seriaati/genshin.py/commit/a30342bc69fca09d51021d78b46a9445483d2c2d))

## Documentation

- Update codecov badge - ([a5401b6](https://github.com/seriaati/genshin.py/commit/a5401b6a4aee669b67aa84de4c2bb2adbeb0829d))
- Update CLI usage in authentication.md ([#264](https://github.com/seriaati/genshin.py/issues/264)) - ([61c44fb](https://github.com/seriaati/genshin.py/commit/61c44fb4f11ecf092eb86d6842051c11b07e07ad))

## Features

- Add spiral abyss enemies - ([e394c70](https://github.com/seriaati/genshin.py/commit/e394c703291413300ba91ac559ace312e3746fb7))
- Export 'SpiralAbyssEnemy' to models - ([6a169f4](https://github.com/seriaati/genshin.py/commit/6a169f44602982178b06fea7201275c34a2b4813))
- Add new models for ZZZ battle chronicle  ([#262](https://github.com/seriaati/genshin.py/issues/262)) - ([a8ed6b8](https://github.com/seriaati/genshin.py/commit/a8ed6b83b1ae5d4b6e03845ce46610b9284f7d79))
- Add Support for Stygian Onslaught ([#266](https://github.com/seriaati/genshin.py/issues/266)) - ([9a5260b](https://github.com/seriaati/genshin.py/commit/9a5260bba9569254ffe9722ef394900abff1cf79))
- Allow fetching raw stygian_onslaught data - ([17fa3c6](https://github.com/seriaati/genshin.py/commit/17fa3c6bde09d715e485f81c9a929124d1fc6474))
- Support multiplayer data in Stygian Onslaugh - ([f30fdeb](https://github.com/seriaati/genshin.py/commit/f30fdeb2bffa8f28a411c0d3cb7d81c545724307))
- Add theater and stygian stats - ([050383b](https://github.com/seriaati/genshin.py/commit/050383bfcd464536f78e6682b34a966c6c0e7825))

## Improvements

- HSR lineup simulator enhancements ([#260](https://github.com/seriaati/genshin.py/issues/260)) - ([8b25d2a](https://github.com/seriaati/genshin.py/commit/8b25d2afef9c37f5208a08801d7b4a3f8c1586f8))

## Miscellaneous Chores

- Add 'authors' and 'maintainers' fields to project config - ([a8bb43a](https://github.com/seriaati/genshin.py/commit/a8bb43a8bd02f0e13fefbc6387dda5d616139a58))

## Refactoring

- Use prevent_enum_error to streamline enum validation - ([eba6e9b](https://github.com/seriaati/genshin.py/commit/eba6e9bab590dda800aeed8c67265a033a1db46d))
- Remove redundant field validator for currency fields in ZZZTempleRunning - ([00729ef](https://github.com/seriaati/genshin.py/commit/00729ef4eb72da590ac93e526f9e38b8ddec0382))
- Replace manual enum validation with prevent_enum_error in multiple models - ([277a873](https://github.com/seriaati/genshin.py/commit/277a8735dd78fac4123a90e7f875c802945f9659))

## Revert

- Revert "ci: Use pyright-action" - ([45c5c0d](https://github.com/seriaati/genshin.py/commit/45c5c0d0c6dbe4acd07c105dced6dd529bb8299a))

## Style

- Correct string formatting - ([85a3ba9](https://github.com/seriaati/genshin.py/commit/85a3ba988bcae026f13051416794d23555b97b3e))

