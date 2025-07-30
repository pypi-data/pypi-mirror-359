# Robot Framework Test Repeater

**Test Repeater** is a listener plugin for Robot Framework that allows you to repeat each test case in a suite a specified number of times. 
This can be useful for scenarios where you want to execute the same test cases multiple times with different inputs or configurations.

## Installation

Ensure you have Python and Robot Framework installed.

```
pip install robotframework-testrepeater
```

## Usage

You can use Test Repeater by specifying it as a listener when running your Robot Framework tests. Here's how you can do it:

```
robot --listener TestRepeater:<count> <test-suite>
```

Replace `<count>` with the number of times you want each test case to be repeated, and `<test-suite>` with the path to your Robot Framework test suite.

For example:

```
robot --listener TestRepeater:2 example/example.robot
```

This command will repeat each test case in `example/example.robot` 2 times.


## License

Test Repeater is licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for details.

## Author

Test Repeater is maintained by reharish and abi-sheak.
