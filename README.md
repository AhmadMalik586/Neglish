<div align="center">

```
          ███╗   ██╗███████╗ ██████╗ ██╗     ██╗███████╗██╗  ██╗
          ████╗  ██║██╔════╝██╔════╝ ██║     ██║██╔════╝██║  ██║
          ██╔██╗ ██║█████╗  ██║  ███╗██║     ██║███████╗███████║
          ██║╚██╗██║██╔══╝  ██║   ██║██║     ██║╚════██║██╔══██║
          ██║ ╚████║███████╗╚██████╔╝███████╗██║███████║██║  ██║
          ╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚══════╝╚═╝╚══════╝╚═╝  ╚═╝
```

**Neglish v3** — A natural English-like programming language  
*Write code the way you speak. No symbols. No cryptic syntax. Just English.*

`Python 3.8+` · `No dependencies` · `Built-in GUI` · `Native modules`

</div>

---

## Table of Contents

1. [What is Neglish?](#what-is-neglish)
2. [What Can You Build With It?](#what-can-you-build-with-it)
3. [Getting Started](#getting-started)
4. [Language Tour](#language-tour)
   - [Output](#output)
   - [Variables](#variables)
   - [Conditions](#conditions)
   - [Loops](#loops)
   - [Functions](#functions)
   - [Lists](#lists)
   - [Dictionaries](#dictionaries)
   - [String Operations](#string-operations)
   - [Math Operations](#math-operations)
   - [Error Handling](#error-handling)
   - [File Input & Output](#file-input--output)
   - [JSON](#json)
   - [User Input](#user-input)
   - [Events](#events)
   - [Data Pipelines](#data-pipelines)
   - [Async & Timers](#async--timers)
   - [Watchers (Reactive Variables)](#watchers-reactive-variables)
   - [Benchmarking](#benchmarking)
   - [Testing Framework](#testing-framework)
   - [Modules (Native Neglish)](#modules-native-neglish)
   - [Frozen Constants](#frozen-constants)
   - [Memoised Functions](#memoised-functions)
   - [Closures](#closures)
   - [Type System](#type-system)
   - [GUI Programming](#gui-programming)
   - [System & OS](#system--os)
   - [Colored Terminal Output](#colored-terminal-output)
   - [Debugging](#debugging)
5. [Built-in Function Reference](#built-in-function-reference)
6. [Standard Library Modules](#standard-library-modules)
7. [Full Example Programs](#full-example-programs)
8. [CLI Reference](#cli-reference)
9. [VS Code Extension](#vs-code-extension)
10. [Language Design Philosophy](#language-design-philosophy)
11. [Limitations & Roadmap](#limitations--roadmap)

---

## What is Neglish?

Neglish is a **general-purpose programming language** with English-like syntax. Instead of writing:

```python
# Python
for i in range(1, 11):
    if i % 2 == 0:
        print(f"Even: {i}")
```

You write:

```
# Neglish
for i from 1 to 10
    if i is equal to i / 2 * 2 then
        show "Even: " + i
    end
end
```

Neglish compiles and runs entirely through a Python interpreter — but the code you write never touches Python. It is its own language with:

- **Its own syntax** — structured English sentences, not symbols
- **Its own standard library** — written in Neglish itself (`math.neg`, `strings.neg`, `collections.neg`, `io.neg`)
- **Its own module system** — `import math as m` loads a `.neg` file, not a Python module
- **Its own GUI framework** — create windows, buttons, labels, and entries in plain English
- **Its own test runner** — `describe`, `test`, `expect`, `check`
- **157 built-in functions** — math, strings, lists, files, time, system, JSON, regex, and more

The Python runtime is just the **engine under the hood** — like how a car runs on an engine you never think about.

---

## What Can You Build With It?

Neglish is designed for a wide range of real applications:

| Use Case | Example |
|---|---|
| **Teaching programming** | The English syntax makes logic visible to beginners |
| **Rapid prototyping** | Write apps quickly without memorizing syntax |
| **CLI tools & scripts** | Read files, process data, automate tasks |
| **Data processing** | Filter, map, reduce, group lists with pipeline syntax |
| **Desktop GUI apps** | Windows, buttons, forms, progress bars — all in plain English |
| **Configuration scripts** | Human-readable scripts that non-developers can edit |
| **Game logic** | State machines, scoring, conditionals in readable form |
| **Testing utilities** | Built-in `describe`/`expect` test framework |
| **Personal automation** | File management, JSON manipulation, system info |
| **Educational projects** | Any project where code needs to be read and understood by humans |

---

## Getting Started

### Requirements

- Python 3.8 or higher
- No pip installs needed — Neglish uses only Python's standard library
- Tkinter (for GUI programs) — already included with Python on Windows and macOS

```bash
# Linux only — install tkinter if needed
sudo apt-get install python3-tk
```

### Running a Program

```bash
python main.py hello.neg             # run a file
python main.py hello.neg --nogui     # force console-only mode (no GUI)
python main.py --repl                # interactive REPL shell
python main.py --check hello.neg     # syntax check only (no execution)
python main.py --version             # print version info
```

### Your First Program

Save this as `hello.neg`:

```
show "Hello, World!"

set name to "Ahmad"
show "Welcome, " + name + "!"

repeat 3 times
    show "Neglish is great!"
end
```

Run it:

```bash
python main.py hello.neg --nogui
```

---

## Language Tour

### Output

```
show "Hello, World!"
say  "Same as show"
print "Also the same"
log  "Also works"

# Show multiple values at once (separated by space)
show "Name:", name, "Score:", score

# Colored output in the terminal
colored red    "This is red"
colored green  "This is green"
colored yellow "Warning message"
colored blue   "Info message"
colored cyan   "Cyan text"
colored magenta "Purple text"
```

---

### Variables

```
# Set a variable
set name  to "Ahmad"
set score to 100
set pi    to 3.14159
set flag  to true
set empty to null

# Modify a variable
increase score by 10
decrease score by 5

# Compound assignment
score += 20
score -= 5
score *= 2
score /= 4

# Constants (cannot be changed after freeze)
set MAX_LIVES to 3
freeze MAX_LIVES

# Built-in constants (always available)
show PI      # 3.14159265358979
show E       # 2.71828182845905
show TAU     # 6.28318530717959
show INF     # infinity
show VERSION # "3.0"
show ARGS    # command-line arguments list
show NL      # newline character
show TAB     # tab character
```

---

### Conditions

```
if score is greater than 90 then
    show "Grade: A"
elseif score is greater than 80 then
    show "Grade: B"
elseif score is greater than 70 then
    show "Grade: C"
else
    show "Grade: F"
end

# All comparison forms
if x is equal to y then ... end
if x is not equal to y then ... end
if x is greater than y then ... end
if x is less than y then ... end
if x is greater than y then ... end   # also works: >  <  >=  <=  ==  !=

# Logic operators
if logged_in and not banned then ... end
if a or b then ... end
if not is_empty then ... end

# Null / empty checks
if value is equal to null then ... end
if items is empty then ... end

# String checks
if email contains "@" then ... end
if name starts with "A" then ... end
if filename ends with ".neg" then ... end

# Switch / match
switch day
    case "Monday" then
        show "Start of week"
    case "Friday" then
        show "TGIF!"
    default then
        show "Midweek"
end
```

---

### Loops

```
# Repeat N times
repeat 5 times
    show "Hello!"
end

# Repeat with index variable
repeat 10 times as i
    show "Step " + i
end

# While loop
set n to 1
while n is less than 100
    increase n by n
end

# For range (inclusive)
for i from 1 to 10
    show i
end

# For range with step
for i from 0 to 100 step 5
    show i
end

# For each (iterate a list)
create list fruits with "apple", "banana", "cherry"
for each fruit in fruits
    show fruit
end

# Infinite loop (use break to exit)
loop
    ask "Command:" and store in cmd
    if cmd is equal to "quit" then
        break
    end
end

# Break and continue
for i from 1 to 10
    if i is equal to 5 then
        continue
    end
    if i is equal to 8 then
        break
    end
    show i
end
```

---

### Functions

```
# Define a function
define function greet with name
    show "Hello, " + name + "!"
end

# Call it
call greet with "Ahmad"

# Function with return value
define function add with a, b
    return a + b
end

set result to call add with 10, 20
show result

# Multiple parameters
define function describe with name, age, city
    show name + " is " + age + " years old, from " + city
end

call describe with "Ahmad", 25, "Lahore"

# Recursive function
define function factorial with n
    if n is less than 2 then
        return 1
    end
    set prev to call factorial with n - 1
    return n * prev
end

show call factorial with 10

# Functions are first-class values
define function double with x
    return x * 2
end
set fn to double
show call fn with 5
```

---

### Lists

```
# Create a list
create list scores with 88, 92, 75, 67, 95

# Add / remove items
add 100 to scores
remove 67 from scores
insert 50 at 1 in scores
pop from scores store in last_item

# Access items (1-indexed)
show item 1 of scores
show first of scores
show last of scores

# List info
show length of scores
show sum of scores
show average of scores

# Sort and shuffle
sort scores
shuffle scores

# Search
if scores contains 95 then
    show "Found 95!"
end
show index of 95 in scores

# Slice (1-indexed, inclusive)
set top3 to slice of scores from 1 to 3

# Get unique values
set uniq to unique of scores

# Remove falsy values (null, false, 0, "")
set clean to compact of mixed_list

# List math
show max_of of scores
show min_of of scores
show median of scores

# Iterate
for each score in scores
    show score
end

# List literals
set matrix_row to [10, 20, 30, 40, 50]
show item 3 of matrix_row
```

---

### Dictionaries

```
# Create a map/dictionary
create map person with "name" as "Ahmad", "age" as 25, "city" as "Lahore"

# Access a value
show key "name" of person

# Set a value
set key "country" of person to "Pakistan"

# Get all keys / values
show join keys of person with ", "
show join values of person with ", "

# Check if key exists
if dict_has of person and "name" then
    show "Name exists"
end

# Empty map
create map empty_map with

# Merge two maps
create map defaults with "theme" as "dark", "lang" as "en"
create map user_prefs with "lang" as "ar"
set merged to dict_merge of defaults and user_prefs
```

---

### String Operations

```
set text to "  Hello, Neglish World!  "

# Case
show uppercase of text
show lowercase of text
show titlecase of text
show camelcase of "hello world"    # → helloWorld
show snakecase of "helloWorld"     # → hello_world

# Whitespace
show trim of text
show trim_left of text
show trim_right of text

# Info
show length of text

# Search and check
if text contains "Neglish" then ... end
if text starts with "Hello" then ... end
if text ends with "!" then ... end

# Extract
show substring of text from 3 to 7
show char_at of text and 1

# Modify
show replace in text find "World" with "Universe"
set words to split text by " "
set joined to join words with "-"
show reverse of "Neglish"

# Repeat
show repeat_str of "ha" and 3    # → hahaha

# Pad
show pad_left  of "42" and 6 and "0"   # → 000042
show pad_right of "hi" and 10 and "."  # → hi........

# Format
set msg to format_str of "Hello, {}! You are {} years old." and name and age

# Count
show count_of of "hello" and "l"   # → 2

# Regex
if matches of email and "[^@]+@[^@]+\.[^@]+" then
    show "Valid email"
end
set all_nums to find_all of text and "[0-9]+"

# Convert
show number_format of 1234567.89 and 2   # → 1,234,567.89
show pluralize of "cat" and 3             # → cats
show pluralize of "cat" and 1             # → cat
```

---

### Math Operations

```
# Arithmetic
set x to 10 + 5
set y to x * 3 - 2
set z to 100 / 4
set r to 17 mod 5       # modulo: r = 2

# Math builtins (use "of" syntax)
show sqrt of 144         # → 12.0
show abs of -42          # → 42
show floor of 3.9        # → 3
show ceil  of 3.1        # → 4
show round of 3.567      # → 4

# Power and roots
show power of 2 and 10   # → 1024

# Min / max
show max of 55 and 99    # → 99
show min of 55 and 99    # → 55

# Random
set dice to random between 1 and 6
set f    to random_float of 0 and 1    # decimal between 0.0 and 1.0

# Trigonometry (input in degrees)
show sin of 90     # → 1.0
show cos of 0      # → 1.0
show tan of 45     # → ~1.0

# Logarithms
show log10 of 1000   # → 3.0
show log2  of 8      # → 3.0

# Number theory
show gcd of 48 and 18     # → 6
show lcm of 4  and 6      # → 12
show is_prime of 97       # → True
show is_even of 4         # → True
show is_odd  of 7         # → True
show factorial of 10      # → 3628800
show fibonacci of 10      # → 55

# Interpolation / clamping
show clamp of 150 and 0 and 100    # → 100 (clamp between 0–100)
show lerp  of 0.5 and 0 and 100    # → 50.0 (linear interpolation)
show sign  of -42                  # → -1

# Constants
show PI    # 3.14159265358979
show E     # 2.71828182845905
show TAU   # 6.28318530717959
```

---

### Error Handling

```
# Try / catch
try
    set result to 10 / 0
    show result
catch error as e
    show "Caught: " + e
end

# Throw your own errors
try
    throw "File not found!"
catch error as err
    show "Error: " + err
end

# Assert (throws if condition is false)
assert score is greater than 0 otherwise "Score must be positive"

# Nested try
try
    try
        throw "Inner"
    catch error as e1
        show "Inner caught: " + e1
        throw "Outer"
    end
catch error as e2
    show "Outer caught: " + e2
end
```

---

### File Input & Output

```
# Write a file
open "output.txt" as f for write
write "Line 1" to f
write "Line 2" to f
close f

# Read a file
open "output.txt" as f for read
read f and store in content
close f
show content

# Append to a file
open "log.txt" as f for append
write "New entry" to f
close f

# Delete a file
delete file "temp.txt"

# Shorthand (builtin functions)
set data to read_file of "notes.txt"
write_file "output.txt" "Hello from Neglish"
append_file "log.txt" "Log entry"

# File info
show file_exists of "main.neg"    # → True
show file_size   of "main.neg"    # → bytes
show file_ext    of "main.neg"    # → .neg
show file_name   of "path/to/main.neg"  # → main.neg
show file_dir    of "path/to/main.neg"  # → path/to
show list_dir    of "."           # → list of filenames
show is_file     of "main.neg"    # → True
show is_dir      of "stdlib"      # → True
```

---

### JSON

```
# Save a variable to JSON
create map config with "version" as "3.0", "debug" as true, "maxUsers" as 100
save config to "config.json"

# Load JSON into a variable
load "config.json" in loaded
show key "version" of loaded

# Builtin JSON functions
set json_str to json_stringify of config      # compact JSON string
set pretty   to json_pretty    of config      # indented JSON string
set parsed   to json_parse     of json_str    # parse JSON string back to dict
```

---

### User Input

```
# Ask for input (stored automatically — strings auto-convert to numbers)
ask "Enter your name:"   and store in name
ask "Enter your age:"    and store in age
ask "Enter a number:"    and store in num

show "Hello, " + name + "! You are " + age + " years old."
show "Double your number: " + num * 2
```

---

### Events

Events let different parts of your program communicate without being directly connected.

```
# Register a listener
on score_changed
    show "Score is now: " + event_data
end

# Register multiple listeners for the same event
on score_changed
    if event_data is greater than 100 then
        colored green "High score achieved!"
    end
end

# Emit an event with data
emit score_changed with 150

# Events fire all registered listeners in order
on user_action
    show "Action: " + event_data
end

emit user_action with "login"
emit user_action with "purchase"
```

---

### Data Pipelines

Process lists with clean, readable pipeline syntax.

```
create list scores with 88, 45, 92, 67, 78, 95, 33, 81

# FILTER — keep items matching a condition
filter scores where score is greater than 75 as high_scores
show join high_scores with ", "   # → 88, 92, 78, 95, 81

# MAP — transform every item
map_fn scores with score as score * 2 store in doubled
show item 1 of doubled            # → 176

# COLLECT — like filter with a name for the loop variable
collect s from scores where s is less than 50 as low_scores
show join low_scores with ", "    # → 45, 33

# REDUCE — accumulate a result
reduce scores with 0 using s as acc + s store in total
show total                        # → 579

# PIPE — chain function calls
define function double with x
    return x * 2
end
define function add_ten with x
    return x + 10
end
pipe 5 through double, add_ten store in result
show result   # → 20
```

---

### Async & Timers

```
# Spawn a background task (runs in a separate thread)
define function send_email with address
    sleep 1 seconds
    show "Email sent to: " + address
end

spawn send_email with "user@example.com"
show "Email is being sent in background..."

# Run code after a delay
after 500 milliseconds
    show "Half a second has passed!"
end

# Run code on a repeating interval
every 2 seconds
    show "Tick: " + now of
end

# Sleep (pause execution)
sleep 1 seconds
sleep 500 milliseconds

# Wait for a spawned task
spawn my_task with args
set task to last_task
# task.join() is available if needed
```

---

### Watchers (Reactive Variables)

A watcher fires automatically whenever a variable changes value.

```
set temperature to 20

watch temperature
    show "Temperature changed → " + new_value
    if new_value is greater than 35 then
        colored red "ALERT: Overheating!"
    end
end

set temperature to 25   # → "Temperature changed → 25"
set temperature to 40   # → "Temperature changed → 40" + alert
set temperature to 18   # → "Temperature changed → 18"
```

---

### Benchmarking

```
benchmark "Sorting 10,000 items"
    create list big with
    repeat 10000 times
        add random between 1 and 1000 to big
    end
    sort big
end
# → [BENCHMARK] Sorting 10,000 items: 42.31 ms
```

---

### Testing Framework

Neglish has a built-in test framework — no external library needed.

```
describe "Calculator Tests"
    test "addition"
        expect 2 + 2 should be 4
        expect 10 + 0 should be 10
    end

    test "subtraction"
        set result to 10 - 3
        expect result should be 7
    end

    test "is prime"
        check is_prime of 17
        check is_prime of 97
        check not is_prime of 4
    end
end

describe "String Tests"
    test "palindrome detection"
        expect call str_lib.is_palindrome with "racecar" should be true
        expect call str_lib.is_palindrome with "hello"   should be false
    end
end

# Run with:
# python main.py tests.neg --nogui
# → prints PASS/FAIL for each test and a final summary
```

---

### Modules (Native Neglish)

Neglish has its own module system. Modules are `.neg` files — **pure Neglish code, not Python**.

```
# Import a module
import math        as m
import strings     as str_lib
import collections as col
import io          as files

# Use module contents
show m.PI
set result to call m.square with 7
set wc     to call str_lib.word_count with "Hello World"
set nums   to call col.range_list with 1 and 10
```

#### Writing Your Own Module

Save as `myutils.neg`:

```
# myutils.neg

export greet
export add_tax

define function greet with name
    show "Hello, " + name + "!"
end

define function add_tax with price
    return price * 1.15
end
```

Use it in your program:

```
import myutils as utils

call utils.greet with "Ahmad"
set total to call utils.add_tax with 50
show "Total with tax: " + total
```

Neglish searches for modules in:
1. The same folder as your `.neg` file
2. The `stdlib/` folder next to `main.py`

#### Included Standard Library

| Module | What it provides |
|---|---|
| `stdlib/math.neg` | `square`, `cube`, `hypotenuse`, `percent`, `map_range`, `collatz`, `digit_sum` |
| `stdlib/strings.neg` | `word_count`, `is_palindrome`, `count_vowels`, `truncate`, `slug_from`, `mask`, `repeat_text` |
| `stdlib/collections.neg` | `range_list`, `zip_lists`, `rotate_left`, `frequency_map`, `count_occurrences`, `group_by_first` |
| `stdlib/io.neg` | `read_text`, `write_text`, `read_lines`, `write_lines`, `read_json`, `write_json`, `read_csv`, `print_table` |

---

### Frozen Constants

```
set MAX_CONNECTIONS to 100
freeze MAX_CONNECTIONS

# Any attempt to change it throws an error
set MAX_CONNECTIONS to 200   # → Runtime Error: 'MAX_CONNECTIONS' is frozen
```

---

### Memoised Functions

A memoised function caches its results — calling it again with the same arguments returns instantly from cache.

```
memo function fibonacci with n
    if n is less than 2 then
        return n
    end
    set a to call fibonacci with n - 1
    set b to call fibonacci with n - 2
    return a + b
end

# First call computes, subsequent calls use cache
show call fibonacci with 30   # → 832040 (instant after first call)
show call fibonacci with 30   # → 832040 (from cache — microseconds)
```

---

### Closures

Functions can capture variables from their surrounding scope.

```
define function make_counter with start
    set count to start
    define function increment
        increase count by 1
        return count
    end
    return increment
end

set counter_a to call make_counter with 0
set counter_b to call make_counter with 100

show call counter_a   # → 1
show call counter_a   # → 2
show call counter_b   # → 101
show call counter_a   # → 3  (independent from counter_b)
```

---

### Type System

```
# Check types
show type of 42          # → number
show type of "hello"     # → string
show type of true        # → bool
show type of [1,2,3]     # → list
show type of null        # → null

# Type predicates
show is_number  of 42       # → True
show is_string  of "hi"     # → True
show is_list    of []       # → True
show is_dict    of {}       # → True
show is_null    of null     # → True
show is_bool    of false    # → True
show is_prime   of 17       # → True
show is_even    of 4        # → True
show is_odd     of 7        # → True

# Type conversion
set n  to number  of "42"       # string → number
set s  to string  of 3.14       # number → string
set b  to to_bool of 0          # any    → bool (0 → false)
set lst to to_list of "hello"   # string → list of chars
```

---

### GUI Programming

Neglish automatically detects whether your program uses GUI commands and starts Tkinter only when needed. All program output (show, print, etc.) always goes to the **terminal/command prompt** — there is no embedded console.

```
# Create a window
create window "My App" with width 800 height 600
show window

# Add a label
create label "Welcome to Neglish!" in window "My App" with size 18 bold true color "#58a6ff"

# Add a text input
create entry username in window "My App"
create entry password in window "My App"

# Add buttons
create button "Login"  in window "My App" with color "blue"
create button "Cancel" in window "My App" with color "gray"
create button "Delete" in window "My App" with color "red"

# Handle button clicks
when button "Login" is clicked
    show "Login button clicked!"
    # get entry value and store it
    get entry username store in typed_name
    show "Username typed: " + typed_name
end

when button "Cancel" is clicked
    alert "Cancelled!"
end

# Progress bar
create progress loading in window "My App"

# Dialogs
alert "File saved successfully!"
confirm "Are you sure?" store in answer
if answer then
    show "User confirmed"
end

# Update a label dynamically
create label "Score: 0" in window "My App"
# ... later ...
update label "Score: 0" with "Score: 100"
```

#### Button Color Options

| Color name | Appearance |
|---|---|
| `default` or `green` | GitHub green |
| `blue` | Bright blue |
| `red` | Alert red |
| `gray` / `grey` | Muted grey |
| `purple` | Rich purple |
| `orange` | Warm orange |
| `cyan` | Teal/cyan |
| `dark` | Dark card style |
| `yellow` | Amber yellow |

---

### System & OS

```
show platform of    # → "Windows" / "Linux" / "Darwin"
show cwd      of    # → current working directory
show username of    # → current user
show hostname of    # → machine name
show pid      of    # → process ID

# Time and date
show now      of    # → "14:32:05"
show today    of    # → "2026-04-21"
show weekday  of    # → "Tuesday"
show year     of    # → 2026
show month    of    # → 4
show day      of    # → 21
show hour     of    # → 14
show minute   of    # → 32
show timestamp of   # → Unix timestamp (integer)

# Run a shell command
run "ls -la" store in output
show output

# Environment variable
set home to env_get of "HOME"

# Exit the program
exit
```

---

### Colored Terminal Output

```
colored red     "Error: something went wrong"
colored green   "Success: operation complete"
colored yellow  "Warning: low disk space"
colored blue    "Info: connecting..."
colored cyan    "Debug: value = 42"
colored magenta "Trace: entering function"
colored white   "Normal white text"
```

---

### Debugging

```
# Print a variable's value with [DEBUG] prefix
debug score

# Inspect a variable's name, value, and type
inspect score     # → [INSPECT] score = 100 (number)
inspect fruits    # → [INSPECT] fruits = ['apple', ...] (list)

# See a snapshot of all variables in scope
trace

# Assert with a message
assert score is greater than 0 otherwise "Score must be positive"

# Benchmark a block
benchmark "Database query simulation"
    sleep 200 milliseconds
end
# → [BENCHMARK] Database query simulation: 200.xx ms

# UUID and hash generation (useful for debugging uniqueness)
show uuid    of ""
show hash_of of "my data"
```

---

## Built-in Function Reference

All 157 built-in functions. Call them with `fn of value` or `fn of a and b`.

### Math

| Function | Syntax | Description |
|---|---|---|
| `sqrt` | `sqrt of x` | Square root |
| `abs` | `abs of x` | Absolute value |
| `floor` | `floor of x` | Round down |
| `ceil` | `ceil of x` | Round up |
| `round` | `round of x` | Round to nearest int |
| `power` | `power of x and y` | x raised to y |
| `mod` | `mod of x and y` | Remainder of x ÷ y |
| `sign` | `sign of x` | -1, 0, or 1 |
| `clamp` | `clamp of v and lo and hi` | Clamp value to range |
| `lerp` | `lerp of t and a and b` | Linear interpolation |
| `max` | `max of a and b` | Larger of two values |
| `min` | `min of a and b` | Smaller of two values |
| `gcd` | `gcd of a and b` | Greatest common divisor |
| `lcm` | `lcm of a and b` | Least common multiple |
| `sin` | `sin of degrees` | Sine (input in degrees) |
| `cos` | `cos of degrees` | Cosine |
| `tan` | `tan of degrees` | Tangent |
| `log10` | `log10 of x` | Base-10 logarithm |
| `log2` | `log2 of x` | Base-2 logarithm |
| `degrees` | `degrees of radians` | Radians → degrees |
| `radians` | `radians of degrees` | Degrees → radians |
| `is_prime` | `is_prime of n` | True if n is prime |
| `is_even` | `is_even of n` | True if n is even |
| `is_odd` | `is_odd of n` | True if n is odd |
| `factorial` | `factorial of n` | n! |
| `fibonacci` | `fibonacci of n` | nth Fibonacci number |
| `random_between` | `random between 1 and 10` | Random integer in range |
| `random_float` | `random_float of lo and hi` | Random decimal in range |
| `percent` | `percent of part and total` | Percentage |
| `between` | `between of v and lo and hi` | True if lo ≤ v ≤ hi |

### Strings

| Function | Syntax | Description |
|---|---|---|
| `uppercase` | `uppercase of s` | ALL CAPS |
| `lowercase` | `lowercase of s` | all lowercase |
| `titlecase` | `titlecase of s` | Title Case |
| `camelcase` | `camelcase of s` | camelCase |
| `snakecase` | `snakecase of s` | snake_case |
| `trim` | `trim of s` | Remove leading/trailing spaces |
| `trim_left` | `trim_left of s` | Remove leading spaces |
| `trim_right` | `trim_right of s` | Remove trailing spaces |
| `reverse` | `reverse of s` | "hello" → "olleh" |
| `length` | `length of s` | Character count |
| `contains` | `s contains sub` | True if s has sub |
| `starts_with` | `s starts with prefix` | True if starts with |
| `ends_with` | `s ends with suffix` | True if ends with |
| `substring` | `substring of s from a to b` | Extract portion |
| `char_at` | `char_at of s and i` | Character at position i |
| `char_code` | `char_code of s` | ASCII code of first char |
| `from_code` | `from_code of n` | ASCII code → character |
| `split` | `split s by sep` | Split string to list |
| `split_lines` | `split_lines of s` | Split by newlines |
| `join` | `join list with sep` | Join list to string |
| `replace` | `replace in s find x with y` | Find and replace |
| `replace_regex` | `replace_regex of s and pattern and rep` | Regex replace |
| `matches` | `matches of s and pattern` | Full regex match |
| `find_all` | `find_all of s and pattern` | Find all regex matches |
| `pad_left` | `pad_left of s and n and ch` | Pad string on left |
| `pad_right` | `pad_right of s and n and ch` | Pad string on right |
| `repeat_str` | `repeat_str of s and n` | Repeat string n times |
| `count_of` | `count_of of s and sub` | Count occurrences |
| `index_of` | `index_of of val and lst` | First occurrence index |
| `number_format` | `number_format of n and dp` | Format number with commas |
| `pluralize` | `pluralize of word and n` | "cat" + 3 → "cats" |
| `format_str` | `format_str of template and args...` | `{}` placeholder format |
| `uuid` | `uuid of ""` | Generate UUID v4 |
| `hash_of` | `hash_of of s` | SHA-256 hash string |

### Lists

| Function | Syntax | Description |
|---|---|---|
| `length` | `length of lst` | Item count |
| `sum` | `sum of lst` | Sum of all numbers |
| `average` | `average of lst` | Arithmetic mean |
| `median` | `median of lst` | Middle value |
| `stdev` | `stdev of lst` | Standard deviation |
| `variance` | `variance of lst` | Variance |
| `max_of` | `max_of of lst` | Largest item |
| `min_of` | `min_of of lst` | Smallest item |
| `first` | `first of lst` | First item |
| `last` | `last of lst` | Last item |
| `sort` | `sort of lst` | Sorted copy (ascending) |
| `sort_desc` | `sort_desc of lst` | Sorted copy (descending) |
| `shuffle` | `shuffle of lst` | Randomly shuffle |
| `reverse` | `reverse of lst` | Reversed copy |
| `unique` | `unique of lst` | Remove duplicates |
| `flatten` | `flatten of lst` | Flatten one level |
| `flatten_deep` | `flatten_deep of lst` | Flatten all levels |
| `compact` | `compact of lst` | Remove falsy values |
| `take` | `take of lst and n` | First n items |
| `drop` | `drop of lst and n` | Skip first n items |
| `chunk` | `chunk of lst and n` | Split into sub-lists of size n |
| `zip_pairs` | `zip_pairs of a and b` | Zip two lists together |
| `enumerate_list` | `enumerate_list of lst` | Add 1-based index to each |
| `range_list` | `range_list of start and end` | List from start to end |
| `intersection` | `intersection of a and b` | Items in both lists |
| `difference` | `difference of a and b` | Items in a but not b |
| `union` | `union of a and b` | All items, no duplicates |
| `contains_all` | `contains_all of lst and items` | All items present? |
| `contains_any` | `contains_any of lst and items` | Any item present? |
| `is_empty` | `lst is empty` | True if list has 0 items |
| `pluck` | `pluck of lst and key` | Extract a key from list of dicts |

### Dictionaries

| Function | Syntax | Description |
|---|---|---|
| `dict_keys` | `keys of dict` | List of all keys |
| `dict_values` | `values of dict` | List of all values |
| `dict_has` | `dict_has of dict and key` | True if key exists |
| `dict_size` | `dict_size of dict` | Number of key-value pairs |
| `dict_merge` | `dict_merge of a and b` | Combine two dicts |
| `dict_to_list` | `dict_to_list of dict` | List of [key, value] pairs |

### Time & Date

| Function | Syntax | Result |
|---|---|---|
| `now` | `now of` | `"14:32:05"` |
| `today` | `today of` | `"2026-04-21"` |
| `timestamp` | `timestamp of` | Unix timestamp (int) |
| `time_ms` | `time_ms of` | Milliseconds since epoch |
| `year` | `year of` | `2026` |
| `month` | `month of` | `4` |
| `day` | `day of` | `21` |
| `hour` | `hour of` | `14` |
| `minute` | `minute of` | `32` |
| `second` | `second of` | `5` |
| `weekday` | `weekday of` | `"Tuesday"` |

### File System

| Function | Syntax | Description |
|---|---|---|
| `file_exists` | `file_exists of path` | True if file/dir exists |
| `is_file` | `is_file of path` | True if it's a file |
| `is_dir` | `is_dir of path` | True if it's a directory |
| `file_size` | `file_size of path` | Size in bytes |
| `file_ext` | `file_ext of path` | Extension (e.g. `.neg`) |
| `file_name` | `file_name of path` | Filename with extension |
| `file_dir` | `file_dir of path` | Parent directory |
| `list_dir` | `list_dir of path` | List files in directory |
| `read_file` | `read_file of path` | Read entire file as string |
| `write_file` | `write_file path content` | Overwrite file |
| `append_file` | `append_file path content` | Append to file |

### Type & Conversion

| Function | Syntax | Description |
|---|---|---|
| `type_of` | `type of x` | Returns type name as string |
| `is_number` | `is_number of x` | True if numeric |
| `is_string` | `is_string of x` | True if string |
| `is_list` | `is_list of x` | True if list |
| `is_dict` | `is_dict of x` | True if dict |
| `is_null` | `is_null of x` | True if null |
| `is_bool` | `is_bool of x` | True if boolean |
| `to_number` | `number of x` | Convert to number |
| `to_string` | `string of x` | Convert to string |
| `to_bool` | `to_bool of x` | Convert to boolean |
| `to_list` | `to_list of x` | Convert to list |

### Random & Choice

| Function | Syntax | Description |
|---|---|---|
| `random_between` | `random between 1 and 10` | Random int in range |
| `random_float` | `random_float of lo and hi` | Random float in range |
| `choice` | `choice of lst` | Pick random item from list |
| `sample` | `sample of lst and n` | Pick n random items |
| `weighted_choice` | `weighted_choice of items and weights` | Pick with probability |

### Misc

| Function | Syntax | Description |
|---|---|---|
| `uuid` | `uuid of ""` | Generate UUID v4 string |
| `hash_of` | `hash_of of s` | SHA-256 hash |
| `json_parse` | `json_parse of s` | Parse JSON string |
| `json_stringify` | `json_stringify of v` | Compact JSON string |
| `json_pretty` | `json_pretty of v` | Indented JSON string |
| `run_cmd` | `run "cmd" store in out` | Run shell command |
| `env_get` | `env_get of key` | Read environment variable |
| `sleep_ms` | `sleep_ms of ms` | Sleep N milliseconds |
| `platform` | `platform of` | OS name |
| `username` | `username of` | Current user |
| `hostname` | `hostname of` | Machine name |
| `pid` | `pid of` | Process ID |
| `cwd` | `cwd of` | Working directory |

---

## Standard Library Modules

### stdlib/math.neg

```
import math as m

call m.square with 7           # → 49
call m.cube with 4             # → 64
call m.hypotenuse with 3 and 4 # → 5.0
call m.percent with 45 and 200 # → 22.5
call m.collatz with 27         # → 111 (steps to reach 1)
call m.digit_sum with 12345    # → 15
call m.map_range with 0.5 and 0 and 1 and 0 and 100  # → 50.0
```

### stdlib/strings.neg

```
import strings as str_lib

call str_lib.word_count      with "Hello World"       # → 2
call str_lib.is_palindrome   with "racecar"            # → True
call str_lib.count_vowels    with "programming"        # → 3
call str_lib.count_consonants with "hello"             # → 3
call str_lib.slug_from       with "Hello World Page"   # → "hello world page"
call str_lib.truncate        with "Long text..." and 8 and "..."
call str_lib.mask            with "password" and "*"   # → "********"
call str_lib.repeat_text     with "ha" and 3           # → "hahaha"
```

### stdlib/collections.neg

```
import collections as col

set nums to call col.range_list with 1 and 10       # → [1,2,3,...,10]
set rot  to call col.rotate_left with list and 2    # → rotated left by 2
set freq to call col.frequency_map with data        # → {value: count, ...}
set cnt  to call col.count_occurrences with "a" and list
set zipped to call col.zip_lists with list_a and list_b
```

### stdlib/io.neg

```
import io as files

set data to call files.read_text  with "file.txt"
call files.write_text with "output.txt" and "content"
set lines to call files.read_lines with "file.txt"    # → list of lines
set cfg   to call files.read_json  with "config.json" # → dict
call files.write_json with "config.json" and config
set rows  to call files.read_csv   with "data.csv"    # → list of lists
call files.print_table with headers and rows
```

---

## Full Example Programs

### Todo List App (CLI)

```
create list todos with
set running to true

define function show_todos
    if todos is empty then
        show "  (no todos)"
        return
    end
    set i to 1
    for each todo in todos
        show i + ". " + todo
        increase i by 1
    end
end

while running is equal to true
    show ""
    call show_todos
    show ""
    ask "Command (add/remove/quit):" and store in cmd

    if cmd is equal to "add" then
        ask "Task:" and store in task
        add task to todos
        colored green "Added: " + task

    elseif cmd is equal to "remove" then
        ask "Number to remove:" and store in num
        set idx to number of num
        if idx is greater than 0 and idx is less than length of todos + 1 then
            set item_to_remove to item idx of todos
            remove item_to_remove from todos
            colored red "Removed: " + item_to_remove
        end

    elseif cmd is equal to "quit" then
        set running to false
    end
end

show "Goodbye!"
```

### Number Guessing Game

```
set secret to random between 1 and 100
set attempts to 0
set won to false

colored cyan "Guess the number between 1 and 100!"
show "You have 7 attempts."

while attempts is less than 7 and won is equal to false
    ask "Your guess:" and store in guess
    increase attempts by 1

    if guess is equal to secret then
        set won to true
        colored green "CORRECT! You got it in " + attempts + " attempts!"
    elseif guess is less than secret then
        colored yellow "Too low!"
    else
        colored yellow "Too high!"
    end
end

if won is equal to false then
    colored red "Game over! The number was " + secret
end
```

### Grade Calculator with Tests

```
import math as m

define function letter_grade with score
    if score is greater than 89 then return "A" end
    if score is greater than 79 then return "B" end
    if score is greater than 69 then return "C" end
    if score is greater than 59 then return "D" end
    return "F"
end

describe "Grade Tests"
    test "A grade"
        expect call letter_grade with 95 should be "A"
        expect call letter_grade with 90 should be "A"
    end
    test "F grade"
        expect call letter_grade with 50 should be "F"
        expect call letter_grade with 0  should be "F"
    end
end

create list grades with 88, 92, 75, 68, 95, 82, 91
show "Average: " + average of grades
show "Highest: " + max_of of grades
show "Grade:   " + call letter_grade with average of grades
```

---

## CLI Reference

```bash
python main.py file.neg              # Run a program
python main.py file.neg --nogui      # Run without GUI (console only)
python main.py file.neg arg1 arg2    # Pass arguments (available as ARGS)
python main.py --repl                # Interactive REPL
python main.py --check file.neg      # Syntax check only
python main.py --version             # Print version
```

### File Extension

Neglish programs use the `.neg` extension:

```
hello.neg
calculator.neg
my_app.neg
```

### Comments

```
# Single line comment
// Also single line
/* Multi-line
   comment */
```

---

## VS Code Extension

The included VS Code extension adds:

- **Full syntax highlighting** — keywords, strings, numbers, builtins all colored distinctly
- **Neglish Dark theme** — custom dark theme designed for `.neg` files
- **35+ code snippets** — type `def`, `if`, `fore`, `try`, `describe`, etc. then press Tab
- **Bracket auto-close** — `[`, `(`, `{`, `"`, `'` close automatically
- **Code folding** — fold `if`/`while`/`define`/`repeat` blocks
- **Run button** — status bar `▶ Run Neglish` button runs the current file

### Installation

1. Copy the `vscode-extension/` folder to:
   - **Windows**: `%USERPROFILE%\.vscode\extensions\neglish-language-3.0.0\`
   - **macOS/Linux**: `~/.vscode/extensions/neglish-language-3.0.0/`
2. Restart VS Code
3. Open any `.neg` file — syntax highlighting appears automatically
4. Apply the theme: `Ctrl+K Ctrl+T` → **Neglish Dark**

---

## Language Design Philosophy

Neglish is built around three principles:

**1. Readability over terseness**

Code should be self-documenting. When you read `show "Hello"`, you don't need to know what `print` is. When you read `filter scores where score is greater than 75`, the intent is immediately clear to anyone — programmer or not.

**2. English as structure, not free-form text**

Neglish is NOT natural language AI. It follows strict parsing rules. The syntax is English-shaped but deterministic — every sentence has one interpretation. `set name to "Ahmad"` always means exactly one thing. This makes programs predictable and debuggable.

**3. Independence from its runtime**

Python is the engine, not the language. Neglish programs never import Python, call Python functions, or think about Python. The standard library is written in Neglish itself. A future Neglish compiler could target any language — the `.neg` files stay exactly the same.

---

## Limitations & Roadmap

### Current Limitations

- **Performance**: Interpreted through Python — not suitable for CPU-heavy computation
- **No network I/O in stdlib yet**: `fetch` works for HTTP GET but no full HTTP library
- **OOP via dicts**: Full class/object syntax is partially implemented; dict-based objects are recommended
- **Single-file GUI**: Complex GUIs need multiple `create label`, `create button` calls without layout managers like grid/pack control
- **No `for` loop with variable step in all contexts**: Step loops work at top level and in most blocks

### Planned Features

- `class` / `object` OOP with `self.property` syntax
- Full network module (`stdlib/http.neg`)
- Database module (`stdlib/db.neg` using SQLite)
- Package manager (`neglish install package`)
- Compiled mode (transpile `.neg` to Python for faster execution)
- Better error messages with line highlighting
- VS Code language server (autocomplete, hover docs)
- Web framework module (`stdlib/web.neg`)

---

<div align="center">

**Neglish v3.0** · MIT License · Made with 💙

*"Write code the way you think. Then run it."*

</div>
