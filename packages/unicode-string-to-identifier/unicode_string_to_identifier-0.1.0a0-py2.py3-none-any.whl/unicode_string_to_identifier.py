from unicodedata import category

class CharacterTypes:
    LETTER_OR_UNDERSCORE = 0
    DECIMAL_DIGIT = 1
    SPACE_OR_CONTROL = 2
    OTHER = 3


def get_character_type(unicode_character):
    unicode_character_category = category(unicode_character)

    if unicode_character_category.startswith('L') or unicode_character == u'_':
        return CharacterTypes.LETTER_OR_UNDERSCORE
    elif unicode_character_category == 'Nd':
        return CharacterTypes.DECIMAL_DIGIT
    elif unicode_character_category.startswith('Z') or unicode_character_category == 'Cc':
        return CharacterTypes.SPACE_OR_CONTROL
    else:
        return CharacterTypes.OTHER


class States:
    START = 0
    AFTER_SUBIDENTIFIER = 1
    AFTER_SPACE_CONTROL_SEQUENCE = 2


def unicode_string_to_identifier_unicode_characters(unicode_string):
    state = States.START
    for c in unicode_string:
        c_type = get_character_type(c)
        if state == States.START:
            if c_type == CharacterTypes.LETTER_OR_UNDERSCORE:
                yield c
                state = States.AFTER_SUBIDENTIFIER
            elif c_type == CharacterTypes.DECIMAL_DIGIT:
                yield u'_'
                yield c
                state = States.AFTER_SUBIDENTIFIER
            elif c_type == CharacterTypes.SPACE_OR_CONTROL:
                state = States.AFTER_SPACE_CONTROL_SEQUENCE
            else:
                yield u'_'
                state = States.AFTER_SUBIDENTIFIER
        elif state == States.AFTER_SUBIDENTIFIER:
            if c_type == CharacterTypes.LETTER_OR_UNDERSCORE or c_type == CharacterTypes.DECIMAL_DIGIT:
                yield c
                state = States.AFTER_SUBIDENTIFIER
            elif c_type == CharacterTypes.SPACE_OR_CONTROL:
                state = States.AFTER_SPACE_CONTROL_SEQUENCE
            else:
                yield u'_'
                state = States.AFTER_SUBIDENTIFIER
        else:
            if c_type == CharacterTypes.LETTER_OR_UNDERSCORE or c_type == CharacterTypes.DECIMAL_DIGIT:
                yield u'_'
                yield c
                state = States.AFTER_SUBIDENTIFIER
            elif c_type == CharacterTypes.SPACE_OR_CONTROL:
                state = States.AFTER_SPACE_CONTROL_SEQUENCE
            else:
                yield u'_'
                yield u'_'
                state = States.AFTER_SUBIDENTIFIER

    if state != States.AFTER_SUBIDENTIFIER:
        yield u'_'


def unicode_string_to_identifier(unicode_string):
    return u''.join(unicode_string_to_identifier_unicode_characters(unicode_string))
