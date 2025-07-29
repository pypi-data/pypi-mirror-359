A tool that converts arbitrary text (like user input or file names) into valid Python identifiers while preserving as much of the original meaning as possible.

## Example Usage

```python
from __future__ import print_function
from unicode_string_to_identifier import unicode_string_to_identifier

print(unicode_string_to_identifier(u""))
# u"_"
print(unicode_string_to_identifier(u" \r\n\t"))
# u"_"
print(unicode_string_to_identifier(u"123abc"))
# u"_123abc"
print(unicode_string_to_identifier(u"&abc 123"))
# u"_abc_123"
print(unicode_string_to_identifier(u"  hello  world  $"))
# u"_hello_world__"
print(unicode_string_to_identifier(u"测试@unicode"))
# u"测试_unicode"
```

## How It Works

First, `get_character_type()` categorizes each Unicode character into one of four types:

- `LETTER_OR_UNDERSCORE` (Unicode category starting with 'L' or underscore `_`)
- `DECIMAL_DIGIT` (Unicode category 'Nd')
- `SPACE_OR_CONTROL` (Unicode categories starting with 'Z' or 'Cc')
- `OTHER` (all other characters)

Then, it implements the following conversion rules using a state machine:

- The first character must be a letter/underscore. If the first character is a digit, prepend `_` to make it valid.
- Subsequent valid characters (letters/underscores/digits) are kept as-is.
- Other characters are replaced with underscores, but whitespace/control character sequences are collapsed into single underscores.
- Ensures the output is non-empty (appends `_` if empty).

## Contributing

Contributions are welcome! Please submit pull requests or open issues on the GitHub repository.

## License

This project is licensed under the [MIT License](LICENSE).
