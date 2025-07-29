from argparse import *

def _check_value(self, action, value):
    # This can also be done at a higher level
    typed_choices = [self._get_value(action, v) for v in action.choices] if action.choices \
        else []
    # converted value must be one of the choices (if specified)
    if (action.choices is not None and 
        value not in action.choices and 
        value not in typed_choices):
        args = {'value': value,
                'choices': ', '.join(map(repr, action.choices))}
        msg = _('invalid choice: %(value)r (choose from %(choices)s)')
        raise ArgumentError(action, msg % args)

ArgumentParser._check_value = _check_value
