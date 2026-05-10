<div align="center">

```
  ███╗   ██╗███████╗ ██████╗ ██╗     ██╗███████╗██╗  ██╗
  ████╗  ██║██╔════╝██╔════╝ ██║     ██║██╔════╝██║  ██║
  ██╔██╗ ██║█████╗  ██║  ███╗██║     ██║███████╗███████║
  ██║╚██╗██║██╔══╝  ██║   ██║██║     ██║╚════██║██╔══██║
  ██║ ╚████║███████╗╚██████╔╝███████╗██║███████║██║  ██║
  ╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚══════╝╚═╝╚══════╝╚═╝  ╚═╝
```

**Neglish v4.2** — A natural English-like programming language  
*Write code the way you speak. No symbols. No cryptic syntax. Just English.*

`Python 3.8+` · `Zero dependencies` · `Built-in GUI` · `Native networking` · `Own module system` · `PATH installable`

</div>

---

## Table of Contents

1. [What is Neglish?](#what-is-neglish)
2. [What's New in v4.2](#whats-new-in-v42)
3. [Getting Started](#getting-started)
4. [Language Tour](#language-tour)
   - [Output](#output)
   - [Variables](#variables)
   - [Conditions](#conditions)
   - [Loops](#loops)
   - [Functions](#functions)
   - [Classes & OOP](#classes--oop)
   - [Lists](#lists)
   - [Dictionaries](#dictionaries)
   - [String Operations](#string-operations)
   - [Math Operations](#math-operations)
   - [Error Handling](#error-handling)
   - [File I/O](#file-io)
   - [JSON](#json)
   - [User Input](#user-input)
   - [Pattern Matching](#pattern-matching)
   - [Data Pipelines](#data-pipelines)
   - [Async & Timers](#async--timers)
   - [Events](#events)
   - [Watchers](#watchers)
   - [Testing Framework](#testing-framework)
   - [Benchmarking](#benchmarking)
   - [Modules](#modules)
   - [Frozen Constants](#frozen-constants)
   - [Closures & Lambdas](#closures--lambdas)
   - [Type System](#type-system)
5. [GUI Programming](#gui-programming)
   - [Windows](#windows)
   - [Buttons](#buttons)
   - [Labels](#labels)
   - [Text Entries](#text-entries)
   - [Textareas](#textareas)
   - [Checkboxes](#checkboxes)
   - [Dropdowns](#dropdowns)
   - [Progress Bars](#progress-bars)
   - [Tables](#tables)
   - [Canvas Drawing](#canvas-drawing)
   - [Tabs](#tabs)
   - [Dialogs](#dialogs)
   - [Toast Notifications](#toast-notifications)
   - [Status Bar](#status-bar)
   - [Themes](#themes)
6. [Networking](#networking)
   - [HTTP GET](#http-get)
   - [HTTP POST / PUT / DELETE](#http-post--put--delete)
   - [Fetch JSON APIs](#fetch-json-apis)
   - [File Download](#file-download)
   - [URL Utilities](#url-utilities)
7. [System & OS](#system--os)
8. [Colored Terminal Output](#colored-terminal-output)
9. [Debugging](#debugging)
10. [Built-in Function Reference](#built-in-function-reference)
11. [Standard Library Modules](#standard-library-modules)
12. [Full Example Programs](#full-example-programs)
13. [CLI Reference](#cli-reference)
14. [VS Code Extension](#vs-code-extension)
15. [Language Design Philosophy](#language-design-philosophy)
16. [Known Limitations](#known-limitations)

---

## What is Neglish?

Neglish is a **general-purpose programming language** with English-like syntax. You write code the way you'd describe a task in plain English — no semicolons, no brackets, no boilerplate.

Instead of:
```python
for i in range(1, 11):
    if i % 2 == 0:
        print(f"Even: {i}")
```

You write:
```
for i from 1 to 10
    if i mod 2 is equal to 0 then
        show "Even: " + i
    end
end
```

Neglish is **fully independent**. The Python runtime is just the engine — like how a car runs on an engine you never think about. The code you write never touches Python:

- **Its own syntax** — structured English sentences, not symbols
- **Its own standard library** — written in Neglish itself (`math.neg`, `strings.neg`, `collections.neg`, `io.neg`)
- **Its own module system** — `import math as m` loads a `.neg` file
- **Its own GUI framework** — create modern dark-themed windows in plain English
- **Its own networking layer** — HTTP requests, JSON APIs, file downloads
- **Its own test runner** — `describe`, `test`, `expect`, `check`
- **170+ built-in functions** — math, strings, lists, files, time, system, JSON, regex, networking

---

## What's New in v4.2

| Feature | Details |
|---|---|
| **Install to PATH** | `neglish --install` adds `neglish.exe` to your user PATH — run Neglish from any terminal or directory |
| **Path-based imports** | `use "libs/utils.neg"` or `use "C:/project/helpers.neg"` — import by relative or absolute path |
| **String interpolation** | `"Hello ${name}, you are ${age} years old!"` — embed any expression inside `${}` |
| **Default parameters** | `define greet with name = "World"` — parameters can have fallback values |
| **Null coalescing `??`** | `x ?? "default"` — returns left side if not null, otherwise right |
| **Pipe operator `\|>`** | `value \|> funcName` — pass a value into a function as its first argument |
| **Indexed for-each** | `for each item, idx in list` — loop with both value and zero-based index |
| **`stdlib` bundled in exe** | `neglish.spec` packs the stdlib inside the built exe so it works from any directory |
| **`install.bat` / `uninstall.bat`** | One-click PATH setup and removal scripts included |
| **Tabs & Tab Groups** | `create tab_group` and `create tab` for multi-page GUIs |
| **Native Charts** | `create chart` to instantly render bar charts |
| **Image Rendering** | `create image` natively loads and scales pictures in GUI |
| **Key Bindings** | `bind_key "Return" in window` for hotkey triggers |
| **Toast notifications** | Animated fade-in/out toasts with custom color and duration |
| **Canvas drawing** | Draw rectangles, ovals, lines, text on a canvas widget |
| **Safer networking** | Domain whitelist via `NEGLISH_ALLOWED_DOMAINS` env var |
| **JSON API fetching** | `fetch json from url` → parsed dict directly |
| **Permissive parser** | Missing glue keywords (`then`, `do`, `to`) are inferred by default |
| **AST/module cache** | Faster re-run and import with source-hash cache |

---

## Getting Started

### Option A — Standalone EXE (recommended, Windows)

Build once and run `.neg` files from **anywhere** on your system:

```bat
:: 1. Build the exe (requires Python + PyInstaller)
build_neglish_runtime.bat

:: 2. Install to PATH (adds neglish.exe to %LOCALAPPDATA%\Neglish)
install.bat
::    or build + install in one step:
build_neglish_runtime.bat --install

:: 3. Now run any .neg file from any directory, any terminal
neglish hello.neg
neglish --repl
neglish --version
```

To remove from PATH later:
```bat
uninstall.bat
```

### Option B — Run from source (Python required)

**Requirements:** Python 3.8 or newer. No pip installs needed.

```bash
# Run a program
python main.py hello.neg

# Interactive REPL
python main.py --repl

# Strict parser mode (no syntax inference)
python main.py hello.neg --strict
```

### Full-stack HTML/CSS/JS with Neglish backend

```text
host "webroot" on port 8080 as app
create window "Neglish Web App" width 1200 height 800
webview "http://127.0.0.1:8080/index.html" in window "Neglish Web App"
```

Stop hosted server:

```text
stop_server app
```

**Your first program** — create `hello.neg`:
```
show "Hello, World!"
set name to "Alice"
show "Hello, " + name + "!"
```

Run it:
```bash
python main.py hello.neg
```

---

## Language Tour

### Output

```
show "Hello!"
say "Hello!"       # synonym
print "Hello!"     # synonym
log "Hello!"       # synonym

# With variables
set x to 42
show "The answer is " + x

# Template-style (string concatenation)
set name to "Bob"
show "Hi " + name + ", you are " + age + " years old"

# Colored output
show colored "green" "Success!"
show colored "red" "Error!"
show colored "cyan" "Info"
```

### Variables

```
set x to 10
let y to 20          # 'let' is a synonym for 'set'
set name to "Alice"
set items to list 1 2 3

# Augmented assignment
increase x by 5      # x = x + 5
decrease y by 3      # y = y - 3

# Constants (cannot be changed after creation)
const PI to 3.14159
const MAX_SIZE to 100

# Global variables (accessible inside functions)
global count to 0
```

### Conditions

```
if x is greater than 10 then
    show "big"
end

if x > 5 then
    show "more than five"
elseif x is equal to 5 then
    show "exactly five"
else
    show "less than five"
end

# 'unless' is 'if not'
unless x is 0 then
    show "x is non-zero"
end

# Compound conditions
if x > 0 and y > 0 then
    show "both positive"
end

if x is null or y is null then
    show "one is missing"
end
```

### Loops

```
# Counted loop
repeat 5 times
    show "hello"
end

# For range
for i from 1 to 10
    show i
end

# For range with step
for i from 0 to 100 step 10
    show i
end

# For each item in list
set colors to list "red" "green" "blue"
for each color in colors
    show color
end

# While loop
set n to 1
while n is less than or equal to 10
    show n
    increase n by 1
end

# Until loop (runs while condition is false)
set count to 0
repeat until count is equal to 5
    increase count by 1
end

# Infinite loop with break
loop
    set input to ask "Enter 'quit' to stop"
    if input is equal to "quit" then
        break
    end
end

# break and continue work in all loops
for i from 1 to 20
    if i mod 2 is equal to 0 then
        continue
    end
    if i is greater than 15 then
        break
    end
    show i
end
```

### Functions

```
# Define a function
define greet with name
    show "Hello, " + name + "!"
end

# Call it
call greet with "Alice"

# Function with return value
define add with a and b
    return a + b
end

set result to call add with 3 and 4
show result    # 7

# Default-style optional logic
define describe with animal
    if animal is equal to "cat" then
        return "furry and quiet"
    end
    return "some animal"
end

# Recursive function
define factorial with n
    if n is less than or equal to 1 then
        return 1
    end
    return n * call factorial with n - 1
end

show call factorial with 10    # 3628800
```

### Classes & OOP

```
class Animal
    has name
    has sound

    define speak
        show self.name + " says " + self.sound
    end
end

class Dog inherit Animal
    has tricks

    constructor with name
        set self.name to name
        set self.sound to "Woof"
        set self.tricks to list
    end

    define learn with trick
        add trick to self.tricks
    end

    define show_tricks
        for each t in self.tricks
            show self.name + " can " + t
        end
    end
end

set rex to new Dog with "Rex"
call rex.speak
call rex.learn with "sit"
call rex.learn with "shake"
call rex.show_tricks

# Check type
if rex instanceof Dog then
    show "Rex is a dog"
end
```

### Lists

```
set fruits to list "apple" "banana" "cherry"

# Add / remove
add "date" to fruits
remove "banana" from fruits
insert "avocado" at 0 in fruits

# Access
set first to first of fruits
set last  to last of fruits
set third to fruits at 2       # zero-indexed

# Length
set n to length of fruits
set n to count of fruits       # synonym

# Search
if fruits contains "apple" then
    show "found it"
end

set idx to index of "cherry" in fruits

# Slicing
set sub to slice fruits from 1 to 3

# Sorting
sort fruits
sort fruits descending          # sort_desc

# Functional operations
set nums to list 1 2 3 4 5 6
set evens   to filter nums where each x is x mod 2 equal to 0
set doubled to map nums using each x to x * 2
set total   to reduce nums using each acc x to acc + x

# Other operations
set u to unique of fruits
set r to reverse of fruits
set f to flatten of nested_list

# List math
set s to sum of nums
set avg to average of nums
set mx  to max of nums
set mn  to min of nums
set med to median of nums

# Combine
set a to list 1 2 3
set b to list 4 5 6
set c to union of a and b
set i to intersection of a and b
set d to difference of a and b
```

### Dictionaries

```
set person to dict
    set person.name to "Alice"
    set person.age  to 30
    set person.city to "London"

# Access
show person.name
show person at "age"

# Check key
if dict_has person "email" then
    show "has email"
end

# Keys / values
set ks to keys of person
set vs to values of person

# Size
set n to dict_size of person

# Merge two dicts
set merged to dict_merge of a and b

# Convert to list of pairs
set pairs to dict_to_list of person

# Delete a key
remove "city" from person
```

### String Operations

```
set s to "Hello, World!"

show uppercase s          # "HELLO, WORLD!"
show lowercase s          # "hello, world!"
show titlecase s          # "Hello, World!"
show trim "  hello  "     # "hello"
show length of s

# Split / join
set words to split s by " "
set joined to join words with "-"

# Replace
set s2 to replace "World" with "Neglish" in s

# Substring
set sub to substring s from 0 to 5    # "Hello"

# Check
if s starts with "Hello" then  show "greeting"  end
if s ends with "!"       then  show "exclamation"  end
if s contains "World"    then  show "found"  end

# Regex
if s matches "[A-Z][a-z]+" then  show "has capitalized word"  end
set all to find_all "[A-Z][a-z]+" in s
set replaced to replace_regex "[0-9]+" with "NUM" in s

# Other
show char_at s at 0           # "H"
set code to char_code "A"     # 65
set ch   to from_code 65      # "A"
show pad_left "5" with "0" to 3     # "005"
show pad_right "hi" with "." to 10  # "hi........"
show count_of "l" in s        # 3
show camelcase "hello world"  # "helloWorld"
show snakecase "Hello World"  # "hello_world"
show number_format 1234567    # "1,234,567"
show pluralize "apple" count 3   # "apples"
```

### Math Operations

```
show sqrt 16          # 4
show abs -7           # 7
show floor 3.9        # 3
show ceil  3.1        # 4
show round 3.567 to 2 # 3.57
show power 2 to 10    # 1024
show mod 17 by 5      # 2
show log10 1000       # 3
show log2  8          # 3
show sin 0            # 0
show cos 0            # 1
show pi               # 3.141592653589793
show random from 1 to 100
show max 3 and 7      # 7
show min 3 and 7      # 3
show clamp 15 between 0 and 10    # 10
show lerp 0.5 from 0 to 100       # 50
show gcd 12 and 8     # 4
show lcm 4 and 6      # 12
show is_prime 17      # true
show is_even 8        # true
show factorial 6      # 720
show fibonacci 10     # 55
set deg to degrees pi           # 180.0
set rad to radians 180          # 3.14159...
```

### Error Handling

```
try
    set result to 10 / 0
    show result
catch error
    show "Caught: " + error
end

# Throw your own error
try
    if age < 0 then
        throw "Age cannot be negative"
    end
catch e
    show "Error: " + e
end

# Assert (throws if condition is false)
assert x > 0 else "x must be positive"
```

### File I/O

```
# Write
write "Hello, file!" to "output.txt"
append "More content\n" to "output.txt"

# Read
set content to read file "output.txt"
show content

# Convenience wrappers
write_file "data.txt" "some data"
set data to read_file "data.txt"

# File system
if file_exists "output.txt" then
    show "exists"
end

show file_size "output.txt"
show file_ext  "output.txt"    # ".txt"
show file_name "path/to/foo.txt"  # "foo.txt"
show file_dir  "path/to/foo.txt"  # "path/to"
set files to list_dir "."
set full to path_join "dir" "file.txt"

# Delete
delete file "temp.txt"
```

### JSON

```
# Parse JSON string → dict/list
set data to json_parse '{"name":"Alice","age":30}'
show data.name

# Stringify dict → JSON string
set json_str to json_stringify data
show json_str

# Pretty print
show json_pretty data

# Save/load JSON files directly
save data to "person.json"
set loaded to load from "person.json"
```

### User Input

```
# Console input
set name to ask "What is your name?"
set age  to ask "How old are you?"

# GUI input dialog (when inside a GUI program)
set answer to ask "Enter your name:"

# Store input in variable
ask "Enter value:" store result
```

### Pattern Matching

```
set day to "Monday"

match day
    when "Monday" then
        show "Start of work week"
    end
    when "Friday" then
        show "End of work week"
    end
    when "Saturday" or "Sunday" then
        show "Weekend!"
    end
    default
        show "Midweek"
    end
end

# Match with number ranges
match score
    when score >= 90 then  show "A"  end
    when score >= 80 then  show "B"  end
    when score >= 70 then  show "C"  end
    default              show "F"  end
end
```

### Data Pipelines

```
set nums to list 1 2 3 4 5 6 7 8 9 10

# filter → map → reduce pipeline
set result to nums
    pipe filter using each n to n mod 2 equal to 0
    pipe map using each n to n * n
    pipe reduce using each acc n to acc + n

show result    # 220

# Grouping
set people to list
add dict name "Alice" dept "Eng"  to people
add dict name "Bob"   dept "HR"   to people
add dict name "Carol" dept "Eng"  to people

set by_dept to group_by people by "dept"

# Ordering
set sorted to order_by people by "name"

# Take / drop
set first3 to take 3 from nums
set rest   to drop 3 from nums

# Chunk
set batches to chunk nums by 3    # [[1,2,3],[4,5,6],[7,8,9],[10]]

# Zip
set pairs to zip_pairs list 1 2 3 and list "a" "b" "c"
# [[1,"a"],[2,"b"],[3,"c"]]
```

### Async & Timers

```
# Run code after a delay
after 2 seconds
    show "2 seconds passed"
end

# Run code every N seconds
every 1 second
    show "tick"
end

# Spawn a background thread
spawn
    set data to call heavy_computation
    show "Done: " + data
end

# Sleep
sleep 1 second
wait 500 milliseconds
```

### Events

```
# Define an event handler
on "user_login"
    show "User logged in: " + event_data
end

# Emit an event
emit "user_login" with "Alice"

# Multiple handlers on same event
on "data_ready"
    show "Handler 1: " + event_data
end
on "data_ready"
    show "Handler 2: " + event_data
end

emit "data_ready" with result
```

### Watchers

```
set counter to 0
watch counter
    show "counter changed to " + counter
end

# Now any assignment to 'counter' triggers the watch block
increase counter by 1    # prints "counter changed to 1"
increase counter by 1    # prints "counter changed to 2"
```

### Testing Framework

```
describe "Math functions"
    test "addition works"
        expect call add with 2 and 3 to equal 5
        check call add with 0 and 0 is 0
    end

    test "string concat"
        expect "Hello" + " World" to equal "Hello World"
    end

    test "list operations"
        set nums to list 1 2 3
        add 4 to nums
        expect length of nums to equal 4
        expect nums at 3 to equal 4
    end
end
```

Run with: `python main.py tests.neg --test`

### Benchmarking

```
benchmark "List sort 10000 items"
    set nums to range_list 1 to 10000
    sort nums
end
```

### String Interpolation

Embed any expression directly inside a string using `${}`:

```
set name to "Alice"
set age to 30
show "Hello ${name}, you are ${age} years old!"
# → Hello Alice, you are 30 years old!

set items to list 1 2 3
show "List has ${length items} items"

set x to 10
show "Double: ${x * 2}, Square: ${x * x}"
```

### Default Parameter Values

Parameters can declare fallback values used when no argument is passed:

```
define greet with name = "World"
  show "Hello, ${name}!"
end

call greet              # Hello, World!
call greet with "Alice" # Hello, Alice!

define power with base, exp = 2
  return base ** exp
end

show call power with 3        # 9  (exp defaults to 2)
show call power with 3, 3     # 27
```

### Null Coalescing (`??`)

Return the left value if it's not null, otherwise return the right:

```
set user_name to null
show user_name ?? "Guest"        # Guest

set score to 0
show score ?? "no score"         # 0  (0 is not null)

set config to null
set port to config ?? 8080
show "Running on port ${port}"   # Running on port 8080
```

### Pipe Operator (`|>`)

Pass a value into a function as its first argument, chain operations:

```
set result to "  hello world  " |> trim
show result        # hello world

set nums to list 1 2 3 4 5
# Chain: sum the list
set total to nums |> sum
show total         # 15

# Chain multiple pipes
define double with x
  return x * 2
end

set val to 5 |> double
show val           # 10
```

### Indexed For-Each

Access both the item and its zero-based index in a loop:

```
set fruits to list "apple" "banana" "cherry"
for each fruit, idx in fruits
  show "${idx}: ${fruit}"
end
# 0: apple
# 1: banana
# 2: cherry

# Works with dicts too (idx = position)
set scores to dict name: "Alice" score: 95
for each key, idx in scores
  show "${idx}. ${key} = ${call scores.get with key}"
end
```

### Modules

#### Name-based import (stdlib or local directory)
```
use math
use strings as str

set result to call math.sqrt with 16
show result
```

#### Path-based import (any directory)
```
# Resolved relative to the currently-running file
use "libs/utils.neg"
use "C:/myproject/shared/helpers.neg" as helpers
use "../common/validators.neg" as val

# Alias is auto-derived from filename; override with 'as'
use "tools/formatter.neg" as fmt
call fmt.format_table with data
```

#### Creating a module
```
# libs/utils.neg
define square with x
  return x * x
end

define add with a, b = 0
  return a + b
end

export square
export add
```

#### Using the module
```
use "libs/utils.neg"

show call utils.square with 5     # 25
show call utils.add with 3        # 3  (b defaults to 0)
show call utils.add with 3, 4     # 7
```


### Frozen Constants

```
const MAX to 100
const PI  to 3.14159265

# Any attempt to reassign raises a runtime error
set MAX to 200    # ✗ Error: 'MAX' is frozen
```

### Closures & Lambdas

```
# Lambda expression
set double to lambda x to x * 2
show call double with 5    # 10

# Multi-param lambda
set add to lambda a b to a + b
show call add with 3 and 7    # 10

# Closure — function that captures outer scope
define make_counter
    set count to 0
    define increment
        increase count by 1
        return count
    end
    return increment
end

set counter to call make_counter
show call counter    # 1
show call counter    # 2
show call counter    # 3

# Memoised function (cached results)
memo define fib with n
    if n < 2 then return n end
    return call fib with n - 1 + call fib with n - 2
end
```

### Type System

```
show type "hello"        # "string"
show type 42             # "number"
show type list 1 2       # "list"
show type true           # "bool"
show type null           # "null"

show is_string "hi"      # true
show is_number 5         # true
show is_list   items     # true
show is_dict   data      # true
show is_null   x         # true/false
show is_bool   flag      # true/false

# Conversions
set n to number "42"     # string → number
set s to string 42       # number → string
set b to to_bool 0       # 0 → false
set l to to_list "abc"   # string → ["a","b","c"]
```

---

## GUI Programming

Neglish includes a modern dark-themed GUI framework using tkinter. GUI programs auto-detect when windows are needed — you don't need any special flag.

### Windows

```
create window "My App" width 800 height 600

# With options
create window "Settings" width 500 height 400

# Show/hide
show window "My App"
close window "My App"
```

### Buttons

```
create button "Click Me" in window "My App"

# Colored buttons
create button "Save"   in window "My App" with color green
create button "Delete" in window "My App" with color red
create button "Info"   in window "My App" with color blue

# Available colors: green, blue, red, gray, purple, orange, cyan,
#                   dark, yellow, teal, pink, white, ghost

# With position
create button "OK" in window "My App" with x 50 y 100

# With grid layout
create button "A" in window "My App" with row 0 column 0
create button "B" in window "My App" with row 0 column 1

# With tooltip
create button "Help" in window "My App" with tooltip "Click for help"

# With size
create button "Big" in window "My App" with size 16

# Handle click
when "Click Me" is clicked
    show "Button was pressed!"
    set label_text to "Clicked!"
    update label "status" to label_text
end

# Enable/disable
enable button "Submit"
disable button "Submit"
```

### Labels

```
create label "Welcome!" in window "My App"

# Styled
create label "Title" in window "My App" with size 24 bold true color "#58a6ff"
create label "Dimmed" in window "My App" with color "#8b949e" italic true

# Named label (for later updates)
create label "Loading..." in window "My App" as "status_lbl"
update label "status_lbl" to "Ready"
set label "status_lbl" color "#3fb950"
```

### Text Entries

```
create entry "Username" in window "My App"
create entry "Password" in window "My App" with password true

# With placeholder
create entry "Email" in window "My App" with placeholder "you@example.com"

# Read value
set name to get entry "Username"

# Set value
set entry "Username" to "Alice"

# Clear
clear entry "Username"

# On submit (bind enter key via button)
when "Login" is clicked
    set user to get entry "Username"
    set pass to get entry "Password"
    show "Logging in as: " + user
end
```

### Textareas

```
create textarea "Notes" in window "My App"
create textarea "Log"   in window "My App" with rows 15

# Get / set
set text to get textarea "Notes"
set textarea "Notes" to "Hello World"

# Append (useful for log output)
append "Line added\n" to textarea "Log"
```

### Checkboxes

```
create checkbox "Remember me" in window "My App"
create checkbox "agree" in window "My App" with label "I agree to terms"

# Read value (true/false)
set checked to get checkbox "Remember me"
set checkbox "agree" to true
```

### Dropdowns

```
create dropdown "Language" in window "My App" with options "English" "Spanish" "French"

# Read selected value
set lang to get dropdown "Language"

# Set value
set dropdown "Language" to "Spanish"
```

### Progress Bars

```
create progress "Download" in window "My App"

# Set value (0-100)
set progress "Download" to 0

repeat 100 times
    increase prog_val by 1
    set progress "Download" to prog_val
    sleep 20 milliseconds
end
```

### Tables

```
create table "Results" in window "My App" with columns "Name" "Score" "Grade"

# Add rows
table add row to "Results" with values "Alice" 95 "A"
table add row to "Results" with values "Bob"   82 "B"
table add row to "Results" with values "Carol" 71 "C"

# Clear all rows
table clear "Results"

# Get selected rows
set selected to table get selected "Results"
```

### Canvas Drawing

```
create canvas "Drawing" in window "My App" width 600 height 400

# Draw shapes
canvas draw rect    on "Drawing" from 10 10 to 200 100 fill "#58a6ff"
canvas draw oval    on "Drawing" from 50 50 to 150 150 fill "#3fb950"
canvas draw line    on "Drawing" from 0 0 to 600 400 color "#f85149" width 3
canvas draw text    on "Drawing" at 300 200 text "Hello Canvas" size 18

# Clear
canvas clear "Drawing"
```

### Tabs

```
create tab panel "Tabs" in window "My App"
add tab "Overview" to panel "Tabs"
add tab "Settings" to panel "Tabs"
add tab "Help"     to panel "Tabs"
```

### Dialogs

```
# Alert
alert "File saved successfully!"

# Confirm (returns true/false)
set ok to confirm "Are you sure you want to delete this?"
if ok then
    show "Deleting..."
end

# Input dialog
set name to ask "Enter your name:"

# File picker
set path to ask file open
set path to ask file save

# Color picker
set col to ask color
show "Chosen color: " + col
```

### Toast Notifications

```
# Quick non-blocking notification
toast "File saved!"
toast "Error occurred" with color red duration 5000
toast "Copied to clipboard" with duration 2000
```

### Status Bar

```
# Every window has a built-in status bar at the bottom
set statusbar of "My App" to "Ready"
set statusbar of "My App" to "Loading data..."
set statusbar of "My App" to "Done — 42 records loaded"
```

### Themes

```
set theme to "dark"       # default — GitHub dark
set theme to "midnight"   # deeper black
set theme to "light"      # light mode
```

### Complete GUI Example

```
create window "Todo App" width 500 height 600

create label "My Todo List" in window "Todo App" with size 20 bold true color "#58a6ff"
create entry "Task" in window "Todo App" with placeholder "Enter a task..."
create button "Add Task" in window "Todo App" with color green
create table "Todos" in window "Todo App" with columns "Task" "Done"

set task_count to 0

when "Add Task" is clicked
    set task to get entry "Task"
    if task is not equal to "" then
        table add row to "Todos" with values task "No"
        increase task_count by 1
        clear entry "Task"
        set statusbar of "Todo App" to task_count + " tasks"
        toast "Task added!"
    end
end
```

---

## Networking

Neglish v4.1 includes a full HTTP networking layer. No external packages needed.

### HTTP GET

```
# Simple GET — stores response body as string
fetch "https://api.example.com/data" into result
show result

# With full response info (status, headers, body)
fetch "https://api.example.com/users" into response with full_response true
show response.status
show response.body

# As a builtin function
set resp to http_get "https://httpbin.org/get"
show resp.status     # 200
show resp.ok         # true
show resp.body
```

### HTTP POST / PUT / DELETE

```
# POST with form data
set resp to http_post "https://httpbin.org/post" with data dict
    set data.name to "Alice"
    set data.age  to 30
end

show resp.status
show resp.body

# POST with JSON body
set payload to dict
set payload.username to "alice"
set payload.password to "secret"

set resp to http_post "https://api.example.com/login" with json payload
if resp.ok then
    show "Logged in!"
else
    show "Login failed: " + resp.status
end

# Custom headers
set resp to http_get "https://api.example.com/me" with headers dict
    set headers.Authorization to "Bearer my_token_here"
    set headers.Accept to "application/json"
end
```

### Fetch JSON APIs

```
# Fetch and auto-parse JSON in one step
set data to fetch json from "https://api.github.com/users/torvalds"
show data.name
show data.public_repos
show data.bio

# Handle errors
if dict_has data "error" then
    show "API error: " + data.error
end

# Fetch a list
set posts to fetch json from "https://jsonplaceholder.typicode.com/posts"
show length of posts    # 100

for each post in posts
    show post.title
end
```

### File Download

```
# Download a file
download "https://example.com/file.pdf" to "local_copy.pdf"
show "Download complete"

# Check success
set ok to download "https://example.com/data.csv" to "data.csv"
if ok then
    show "Downloaded successfully"
else
    show "Download failed"
end
```

### URL Utilities

```
# Encode / decode URL components
set encoded to url_encode "hello world & more"   # "hello%20world%20%26%20more"
set decoded to url_decode "hello%20world"         # "hello world"

# Base64
set b64 to base64_encode "Hello, World!"
set original to base64_decode b64

# Parse a URL into parts
set parts to parse_url "https://example.com/path?q=hello#section"
show parts.scheme   # "https"
show parts.netloc   # "example.com"
show parts.path     # "/path"
show parts.query    # "q=hello"
show parts.fragment # "section"
```

### Full Networking Example

```
# Fetch weather data from a public API
set city to ask "Enter city name:"
set url  to "https://wttr.in/" + url_encode city + "?format=j1"

set weather to fetch json from url

if dict_has weather "error" then
    show "Could not fetch weather: " + weather.error
else
    set current to weather.current_condition at 0
    show "Weather in " + city + ":"
    show "  Temperature: " + current.temp_C + "°C"
    show "  Feels like:  " + current.FeelsLikeC + "°C"
    show "  Description: " + current.weatherDesc at 0 at "value"
end
```

---

## System & OS

```
show platform         # "linux", "windows", "darwin"
show username         # current OS user
show hostname         # machine hostname
show pid              # process ID
show cwd              # current working directory
show sep              # path separator ("/" or "\")

set val to env_get "HOME"    # read environment variable
set files to list_dir "."    # list files in directory

# Run a shell command
set output to run_cmd "ls -la"
show output

exit     # quit the program
clear    # clear terminal
```

---

## Colored Terminal Output

```
show colored "red"     "Error message"
show colored "green"   "Success message"
show colored "yellow"  "Warning message"
show colored "blue"    "Info message"
show colored "cyan"    "Debug message"
show colored "magenta" "Special message"
show colored "white"   "Normal message"
show colored "bold"    "Bold text"
show colored "dim"     "Dimmed text"
show colored "underline" "Underlined"
show colored "bg_red"  "Red background"
show colored "bg_green" "Green background"
```

---

## Debugging

```
debug x               # print variable name + value + type
inspect person        # deep-inspect any value (lists, dicts, objects)
trace "reached here"  # labelled debug print with line info

# Runtime info
show type x
show __file__         # current script path
show __version__      # "4.1"
```

---

## Built-in Function Reference

### Output & Input
| Function | Description |
|---|---|
| `show` / `say` / `print` / `log` | Print to terminal |
| `ask "prompt"` | Prompt for input |
| `colored color text` | Colored terminal output |
| `debug x` | Print var name + value + type |
| `inspect x` | Deep inspection print |

### Math
| Function | Description |
|---|---|
| `sqrt x` | Square root |
| `abs x` | Absolute value |
| `floor x` / `ceil x` / `round x` | Rounding |
| `power a to b` | `a^b` |
| `mod a by b` | Modulo |
| `log10 x` / `log2 x` | Logarithms |
| `sin x` / `cos x` / `tan x` | Trig (radians) |
| `asin x` / `acos x` / `atan x` | Inverse trig |
| `degrees x` / `radians x` | Angle conversion |
| `pi` | 3.14159... |
| `random from a to b` | Random integer in range |
| `max a and b` / `min a and b` | Maximum/minimum |
| `clamp v between lo and hi` | Clamp value |
| `lerp t from a to b` | Linear interpolation |
| `gcd a and b` / `lcm a and b` | GCD/LCM |
| `is_prime n` | Primality test |
| `is_even n` / `is_odd n` | Parity check |
| `factorial n` / `fibonacci n` | Sequences |
| `sign x` | -1, 0, or 1 |

### Strings
| Function | Description |
|---|---|
| `uppercase s` / `lowercase s` / `titlecase s` | Case conversion |
| `trim s` | Strip whitespace |
| `length of s` | String length |
| `split s by delim` | Split string |
| `join list with delim` | Join list |
| `replace old with new in s` | Replace substring |
| `substring s from a to b` | Slice string |
| `starts with` / `ends with` / `contains` | Checks |
| `char_at s at i` | Character at index |
| `char_code c` / `from_code n` | ASCII conversions |
| `pad_left s with c to n` | Left-pad |
| `pad_right s with c to n` | Right-pad |
| `camelcase s` / `snakecase s` | Case conversion |
| `number_format n` | Format with commas |
| `count_of sub in s` | Count occurrences |
| `regex pattern` / `matches` | Regex testing |
| `find_all pattern in s` | Regex find all |
| `replace_regex pattern with r in s` | Regex replace |

### Lists
| Function | Description |
|---|---|
| `length of / count of` | List length |
| `first of / last of` | First/last element |
| `list at i` | Element at index |
| `add x to list` | Append |
| `remove x from list` | Remove by value |
| `insert x at i in list` | Insert at index |
| `sort list` / `sort list descending` | Sort |
| `reverse of list` | Reverse |
| `unique of list` | Deduplicate |
| `flatten of list` | Flatten one level |
| `contains` | Membership test |
| `index of x in list` | Find index |
| `slice list from a to b` | Sublist |
| `sum of / average of / median of` | Stats |
| `max of / min of` | Extremes |
| `stdev of / variance of` | Statistics |
| `union / intersection / difference` | Set ops |
| `zip_pairs` | Zip two lists |
| `enumerate_list` | Add indices |
| `range_list from a to b` | Create range |
| `chunk list by n` | Split into chunks |
| `sample list n` | Random sample |
| `choice list` | Random element |
| `pluck key from list` | Extract field from dicts |
| `group_by list by key` | Group by field |

### Dictionaries
| Function | Description |
|---|---|
| `keys of / values of` | Get keys/values |
| `dict_has d key` | Key existence |
| `dict_size of d` | Number of keys |
| `dict_merge of a and b` | Merge dicts |
| `dict_to_list of d` | List of [k,v] pairs |

### Files
| Function | Description |
|---|---|
| `read file / read_file` | Read text file |
| `write x to / write_file` | Write text file |
| `append x to / append_file` | Append to file |
| `file_exists / is_file / is_dir` | File checks |
| `file_size / file_ext / file_name / file_dir` | File info |
| `list_dir path` | Directory listing |
| `path_join a b` | Join paths |
| `delete file` | Delete file |

### JSON
| Function | Description |
|---|---|
| `json_parse s` | Parse JSON string |
| `json_stringify x` | Serialize to JSON |
| `json_pretty x` | Pretty-print JSON |
| `save x to file` | Save as JSON file |
| `load from file` | Load JSON file |

### Time
| Function | Description |
|---|---|
| `now` | Current datetime string |
| `today` | Today's date string |
| `timestamp` | Unix timestamp (float) |
| `time_ms` | Milliseconds since epoch |
| `year / month / day / hour / minute / second` | Date parts |
| `weekday` | Day name |
| `sleep N seconds` | Pause execution |
| `wait N milliseconds` | Short pause |

### Networking (v4.1)
| Function | Description |
|---|---|
| `http_get url` | HTTP GET → `{body, status, ok}` |
| `http_post url with data/json` | HTTP POST → `{body, status, ok}` |
| `fetch_json url` | Fetch + parse JSON → dict/list |
| `download url to path` | Download file, returns bool |
| `url_encode s` | Percent-encode URL component |
| `url_decode s` | Decode percent-encoded string |
| `base64_encode s` | Base64 encode |
| `base64_decode s` | Base64 decode |
| `parse_url url` | Parse URL → dict of parts |

### System
| Function | Description |
|---|---|
| `platform` | OS name |
| `username` | Current user |
| `hostname` | Machine name |
| `pid` | Process ID |
| `cwd` | Working directory |
| `env_get key` | Environment variable |
| `run_cmd cmd` | Shell command output |
| `uuid` | Generate UUID v4 |
| `hash_of s` | SHA-256 hash |
| `exit` | Exit program |
| `clear` | Clear terminal |

### Type Checks
| Function | Description |
|---|---|
| `type x` | Type name string |
| `is_string / is_number / is_list / is_dict / is_null / is_bool` | Type tests |
| `number s` / `string n` | Type conversion |
| `to_bool x` / `to_list x` | Type coercion |

---

## Standard Library Modules

Located in `stdlib/`. Import with `import math as m`.

### `math.neg`
Extended math: `quadratic`, `is_perfect_square`, `prime_factors`, `digit_sum`, `digit_count`, `reverse_number`, `is_palindrome_num`, `celsius_to_fahrenheit`, `fahrenheit_to_celsius`

### `strings.neg`
String utilities: `count_words`, `is_palindrome`, `longest_word`, `word_frequency`, `caesar_cipher`, `sentence_to_words`, `words_to_sentence`

### `collections.neg`
Data structures: `new_stack`, `stack_push`, `stack_pop`, `stack_peek`, `new_queue`, `enqueue`, `dequeue`, `new_set`, `set_add`, `set_has`

### `io.neg`
I/O helpers: `read_lines`, `write_lines`, `read_json_file`, `write_json_file`, `file_line_count`, `grep`

---

## Full Example Programs

### Calculator (GUI)

```
create window "Calculator" width 320 height 480

create label "0" in window "Calculator" with size 28 bold true color "#58a6ff" as "display"

set expression to ""

define button_press with val
    if val is equal to "=" then
        try
            set result to eval expression
            update label "display" to result
            set expression to string result
        catch err
            update label "display" to "Error"
            set expression to ""
        end
    elseif val is equal to "C" then
        set expression to ""
        update label "display" to "0"
    else
        set expression to expression + val
        update label "display" to expression
    end
end

set buttons to list "7" "8" "9" "/" "4" "5" "6" "*" "1" "2" "3" "-" "0" "." "=" "+"

set r to 1
set c to 0
for each btn in buttons
    create button btn in window "Calculator" with row r column c size 14
    when btn is clicked
        call button_press with btn
    end
    increase c by 1
    if c is equal to 4 then
        set c to 0
        increase r by 1
    end
end

create button "C" in window "Calculator" with row 0 column 0 color red
when "C" is clicked
    call button_press with "C"
end
```

### Weather App (Networking + GUI)

```
create window "Weather" width 500 height 400

create label "🌤  Live Weather" in window "Weather" with size 20 bold true
create entry "City" in window "Weather" with placeholder "Enter city name..."
create button "Get Weather" in window "Weather" with color blue
create label "" in window "Weather" as "result"

when "Get Weather" is clicked
    set city to get entry "City"
    if city is equal to "" then
        alert "Please enter a city name"
    else
        update label "result" to "Fetching..."
        set statusbar of "Weather" to "Requesting data..."
        set url to "https://wttr.in/" + url_encode city + "?format=3"
        set resp to http_get url
        if resp.ok then
            update label "result" to resp.body
            set statusbar of "Weather" to "Updated"
            toast "Weather loaded!" with color "#3fb950"
        else
            update label "result" to "Failed to fetch weather"
            set statusbar of "Weather" to "Error " + resp.status
        end
    end
end
```

### REST API Client (Console)

```
# Fetch and display GitHub user info
set username to ask "GitHub username:"
set resp to http_get "https://api.github.com/users/" + username

if resp.ok then
    set user to json_parse resp.body
    show colored "cyan" "=== GitHub Profile ==="
    show colored "bold" user.name
    show "  Username:  @" + user.login
    show "  Repos:     " + user.public_repos
    show "  Followers: " + user.followers
    show "  Bio:       " + user.bio
    show "  Location:  " + user.location
else
    show colored "red" "User not found (status " + resp.status + ")"
end
```

---

## CLI Reference

Once installed to PATH (`install.bat` or `neglish --install`), run from **any directory**:

```
neglish <file.neg>              Run a program
neglish <file.neg> --nogui      Run without GUI
neglish <file.neg> --check      Check syntax only
neglish <file.neg> --tokens     Dump token stream (debug)
neglish <file.neg> --ast        Dump AST as JSON (debug)
neglish <file.neg> --profile    Show parse/exec timing
neglish <file.neg> --strict     Enable strict parser mode
neglish --repl                  Interactive REPL
neglish --version               Show version info
neglish --install               Install to user PATH (Windows)
neglish --uninstall             Remove from user PATH (Windows)
```

When running from source:
```bash
python main.py <file.neg> [flags]
```

### REPL Commands

```
>>>  exit / quit        Leave the REPL
>>>  help               Show help
>>>  vars               List defined variables
>>>  clear              Clear screen
>>>  load <file.neg>    Load and run a file
```
---

## VS Code Extension

Located in `vscode-extension/`. Provides:
- Syntax highlighting for `.neg` files
- Three themes: Neglish Dark, Neglish Midnight, Neglish Light
- Code snippets for all major constructs
- Bracket/quote matching configuration
- Hover docs, completions, diagnostics, and symbol outline
- Settings for strict mode, IntelliSense toggle, and completion limit

**Package and install `.vsix`:**
1. `cd vscode-extension`
2. `npm install -g @vscode/vsce`
3. `vsce package`
4. `code --install-extension neglish-language-4.2.0.vsix`

If you add `negextension.ico` to `vscode-extension/`, it is used as the extension icon.

## Build & Install (Windows)

### Build `neglish.exe` (standalone runtime)

```bat
:: Build the runtime exe (stdlib is bundled inside)
build_neglish_runtime.bat

:: Build and install to PATH in one step
build_neglish_runtime.bat --install
```

### Install to PATH manually

```bat
:: After building, run install.bat to add neglish to your user PATH
install.bat

:: Now open a new terminal — neglish works from anywhere:
neglish hello.neg
neglish --repl
```

### Uninstall

```bat
uninstall.bat
```

### Build a standalone `.neg` program as its own `.exe`

Use this to distribute a single `.neg` program as a self-contained executable:

```bat
build_neg_exe.bat your_program.neg
:: Output: dist\your_program.exe
```

Optional custom name:
```bat
build_neg_exe.bat your_program.neg MyApp
:: Output: dist\MyApp.exe
```

### Register `.neg` file type (Windows)

Double-click any `.neg` file in Explorer to run it:

```bat
register_neg_filetype.bat
```
---

## Language Design Philosophy

Neglish is built around one idea: **code should read like instructions you'd write to a colleague.**

- **No semicolons** — lines end at newlines, blocks end at `end`
- **No brackets for conditions** — `if x > 5 then` not `if (x > 5) {`
- **Natural keywords** — `say`, `show`, `ask`, `create`, `repeat`
- **Synonym-friendly** — `show`/`say`/`print`/`log` all work the same
- **Articles optional** — `the`, `a`, `an` are silently consumed
- **English logic words** — `and`, `or`, `not`, `both`, `either`
- **Readable comparisons** — `is greater than`, `is equal to`, `is less than`
- **No Python bleed** — you never need to know Python to write Neglish

The goal is a language approachable enough that someone who has never programmed can write useful programs within an hour.

---

## Known Limitations

- **No package manager** — modules must be placed in `stdlib/`, next to the script, or imported by path
- **Tkinter required for GUI** — comes with Python on most platforms; on some Linux distros: `sudo apt install python3-tk`
- **No async/await for networking** — HTTP calls are synchronous; use `spawn` for background requests
- **No WebSocket client** — planned for v4.3
- **REPL has no arrow-key history** — use `load <file>` for longer programs
- **No type annotations** — planned for v5.0
- **`--install` is Windows-only** — on Linux/macOS, add the directory containing `neglish` to your `$PATH` manually
